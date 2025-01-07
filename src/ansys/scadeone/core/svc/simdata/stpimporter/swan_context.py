# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import OrderedDict
import functools
from pathlib import Path
from typing import Optional, Union, Tuple, cast
import re
from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model.model import Model
import ansys.scadeone.core.svc.simdata as sd
import ansys.scadeone.core.swan as swan

from .utils import ConverterLogger

from .sss_parser import SSSParser


class SwanContext:
    """Class for Swan context"""

    RenamingRe = re.compile(r"(?P<kind>\w+)\s+(?P<old>\S+)\s+is\s+now\s+(?P<new>\S+)")

    def __init__(
        self, project_path: str, s_one_path: Union[str, None], renamings: Union[str, None]
    ) -> None:
        self._s_one_install = s_one_path
        self._project_path = project_path
        self._renamings_path = renamings
        self._renaming_dict = {}
        self._operator: swan.Operator = None
        self._model: Model = None
        self._app: ScadeOne = None
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()
        self._module: swan.Module = None

    @property
    def s_one_install(self):
        return self._s_one_install

    @property
    def inputs(self) -> OrderedDict:
        return self._inputs

    @property
    def outputs(self) -> OrderedDict:
        return self._outputs

    @property
    def operator_module(self):
        # path of the module of the current root operator
        return self._module.get_full_path()

    @property
    def operator_path(self):
        return self._operator.get_full_path()

    @property
    def project_basename(self) -> str:
        return Path(self._project_path).stem

    def _load_renamings(self, renamings_path: str):
        with open(renamings_path, "r") as f:
            for line in f:
                m = SwanContext.RenamingRe.match(line.strip())
                if m is None:
                    continue
                kind = m.group("kind")
                if kind in ("function", "node"):
                    kind = "operator"
                if kind not in self._renaming_dict:
                    self._renaming_dict[kind] = {}
                self._renaming_dict[kind][m.group("old")] = m.group("new")

    def get_renamed(self, kind: str, name: str) -> Tuple[str, bool]:
        if not (self._renaming_dict) and self._renamings_path:
            self._load_renamings(self._renamings_path)
        try:
            return (self._renaming_dict[kind][name], True)
        except KeyError:
            # not found, add the project name if needed
            if name.find("::") == -1:
                name = self.project_basename + "::" + name
            return (name, False)

    def get_operator(self, op_name: str):
        ConverterLogger.getLogger("Loading operator")
        self._app = ScadeOne(install_dir=self.s_one_install) if self._s_one_install else ScadeOne()
        project = self._app.load_project(self._project_path)
        if not project:
            ConverterLogger.exception("Invalid project")
        self._model = project.model
        (full_name, is_renamed) = self.get_renamed("operator", op_name)
        module_part, name = swan.PathIdentifier.split(full_name)
        module = self._model.get_module_body(module_part)
        if module is None:
            ConverterLogger.exception(f"Cannot find module {module_part}")
        self._module = module
        operator = module.get_declaration(name)
        if operator is None or not isinstance(operator, swan.Operator):
            ConverterLogger.exception(f"Cannot find operator {op_name} (stp 'operator' attribute)")
        self._operator = operator

        for sig in operator.inputs:
            if isinstance(sig.type, swan.TypeGroupTypeExpression):
                sig_name = sig.id.value
                full_path_name = f"{operator.get_full_path()}/{sig_name}"
                type = self.get_sd_type_of_type_expr(sig.type.type, module)
                self._inputs[full_path_name] = type

        for sig in operator.outputs:
            if isinstance(sig.type, swan.TypeGroupTypeExpression):
                sig_name = sig.id.value
                full_path_name = f"{operator.get_full_path()}/{sig_name}"
                type = self.get_sd_type_of_type_expr(sig.type.type, module)
                self._outputs[full_path_name] = type

    def get_sensor_sd_type(self, sensor_path: str) -> Union[Tuple[str, sd.Type], None]:
        """Looks for a sensor in its module or in the project module.

        Returns its type , or None if not found."""

        for sensor in self._model.sensors:
            if sensor.get_full_path() == sensor_path:
                return self.get_sd_type_of_type_expr(sensor.type, self._module)
        return None

    def get_sd_type_of_type_expr(
        self, type_expr: swan.TypeExpression, module: swan.Module, name: Optional[str] = None
    ):
        if isinstance(type_expr, swan.ArrayTypeExpression):
            res = self.get_array_type(type_expr, module)
            if res is None:
                return None
            sd_type, dims = res
            sd_array_type = sd.create_array_type(sd_type, dims, name if name else "")
            return sd_array_type

        if isinstance(type_expr, swan.PredefinedType):
            # bool & cie
            sd_type = self.get_sd_predefined_type(type_expr)

            return sd_type

        if isinstance(type_expr, swan.TypeReferenceExpression):
            # type name: T1, M1::T
            type_name = type_expr.alias.as_string
            type_decl = module.get_declaration(type_name)
            return self.get_sd_type_of_type_decl(type_decl, type_decl.module)

        if isinstance(type_expr, swan.SizedTypeExpression):
            # signed<<expr>> or unsigned <<expr>>
            ConverterLogger.warning("Unsupported Sized Type was found for type expression.")
            return None

        if isinstance(type_expr, swan.VariableTypeExpression):
            # 'T: should never occur at top-level interface
            ConverterLogger.warning("Unsupported Variable Type was found for type expression.")
            return None

        ConverterLogger.error("Undefined Type was found for type expression.")
        return None

    @functools.cache
    def get_sd_type_of_type_decl(self, decl: swan.TypeDecl, module: swan.Module):
        name = decl.get_full_path()
        type_def = decl.definition

        if isinstance(type_def, swan.ExprTypeDefinition):
            sd_type = self.get_sd_type_of_type_expr(type_def.type, module, name)

        elif isinstance(type_def, swan.EnumTypeDefinition):
            enum_module, enum_type = swan.PathIdentifier.split(name)
            tags = [enum_module + "::" + i.value for i in type_def.tags]
            sd_type = sd.create_enum_type(tags, name)

        elif isinstance(type_def, swan.StructTypeDefinition):
            sd_fields = []
            for f in type_def.fields:
                field_value = self.get_sd_type_of_type_expr(f.type, module)
                if field_value is None:
                    return None
                field_name = f.id.value
                sd_fields.append((field_name, field_value))
            sd_type = sd.create_struct_type(sd_fields, name)

        else:
            ConverterLogger.error(f"Unsupported imported type: {name}")
            return None

        return sd_type

    def get_array_type(self, array_type: swan.ArrayTypeExpression, module: swan.Module):
        size = array_type.size
        if isinstance(size, swan.Literal) and size.is_integer:
            size = int(size.value)
        elif isinstance(size, swan.PathIdExpr):
            path = size.path_id.as_string
            size = self.get_constant_value(path, module)
            if not (isinstance(size, int) and size >= 0):
                ConverterLogger(f"Constant {path} value is not an integer")
                return None
        else:
            ConverterLogger.error(f"Cannot handle size: {size}")
            return None
        type = array_type.type
        if isinstance(type, swan.ArrayTypeExpression):
            res = self.get_array_type(type, module)
            if res is None:
                return None
            (sd_type, dims) = res
            dims.insert(0, size)
        else:
            sd_type = self.get_sd_type_of_type_expr(type, module)
            dims = [size]
        return (sd_type, dims)

    def get_sd_predefined_type(self, predefined):
        swan_type = str(predefined)
        if swan_type == "bool":
            return sd.Bool
        if swan_type == "int8":
            return sd.Int8
        if swan_type == "int16":
            return sd.Int16
        if swan_type == "int32":
            return sd.Int32
        if swan_type == "int64":
            return sd.Int64
        if swan_type == "uint8":
            return sd.UInt8
        if swan_type == "uint16":
            return sd.UInt16
        if swan_type == "uint32":
            return sd.UInt32
        if swan_type == "uint64":
            return sd.UInt64
        if swan_type == "float32":
            return sd.Float32
        if swan_type == "float64":
            return sd.Float64
        if swan_type == "char":
            return sd.Char
        ConverterLogger.error(f"Unknown Predefined Type: {swan_type}")
        return None

    def module_look_for(self, module_name, search_err_msg, search_fn):
        """Apply search_fn to find"""
        body = self._model.get_module_body(module_name)
        interface = self._model.get_module_interface(module_name)
        if not (body or interface):
            ConverterLogger.error(f"Module {module_name} not found for {search_err_msg}")
            return None
        if body:
            item = search_fn(body)
            if item:
                return item
        if interface:
            item = search_fn(interface)
            if item:
                return item
        return None

    def get_enum(self, name: str) -> Union[str, None]:
        """Look for an enum without module part"""
        full_name = name if name.find("::") != -1 else self.project_basename + "::" + name
        module_part, enum_tag = swan.PathIdentifier.split(full_name)
        # Look for renaming of the enum. Note this is a type renaming, so we need to look for
        # the module part in the type name
        for t in self._renaming_dict.get("type", {}).keys():
            (type_module, _) = swan.PathIdentifier.split(t)
            if type_module == module_part:
                (new_module, _) = swan.PathIdentifier.split(self._renaming_dict["type"][t])
                module_part = new_module
                break

        def search_fn(m: swan.Module):
            for typ in m.types:
                if not isinstance(typ.definition, swan.EnumTypeDefinition):
                    continue
                for tag in typ.definition.tags:
                    if tag.value == enum_tag:
                        return full_name
            return None

        enum = self.module_look_for(module_part, f"enum {name}", search_fn)

        return enum

    def _eval_constant_expr(self, cst_value: swan.Expression):
        if isinstance(cst_value, swan.Literal):
            if cst_value.is_bool:
                return cst_value.is_true
            elif cst_value.is_char:
                return SSSParser.to_char(cst_value.value)
            elif cst_value.is_integer:
                return int(cst_value.value)
            elif cst_value.is_float:
                return float(cst_value.value)
            else:
                None
        elif isinstance(cst_value, swan.UnaryExpr):
            unary = cast(swan.UnaryExpr, cst_value)
            value = self._eval_constant_expr(unary.expr)
            if not isinstance(value, (int, float)):
                return None
            return -value if unary.operator == swan.UnaryOp.Minus else value

    def get_constant(
        self, name: str, module: Optional[swan.Module] = None, no_const_ok: Optional[bool] = False
    ) -> Union[swan.Literal, None]:
        """Look for an enum without module part"""
        const_decl = None

        if module is None:
            # case of a constant from .sss
            (full_name, is_renamed) = self.get_renamed("constant", name)

            module_part, cst_name = swan.PathIdentifier.split(full_name)

            def search_fn(m: swan.Module):
                const_decl = None
                for const in m.constants:
                    if const.id.value != cst_name:
                        continue
                    const_decl = const
                    break
                return const_decl

            const_decl = self.module_look_for(module_part, f"constant {name}", search_fn)

        else:
            # get constant from given module
            const_decl = module.get_declaration(name)

        if const_decl is None and not no_const_ok:
            ConverterLogger.error(f"Constant {name} not found")

        return const_decl

    def get_constant_value(
        self, name: str, module: Optional[swan.Module] = None, no_const_ok: Optional[bool] = False
    ) -> Union[swan.Literal, None]:
        """Look for an enum without module part"""
        const_decl = self.get_constant(name, module, no_const_ok)
        if const_decl is None:
            return None
        if const_decl.value is None:
            ConverterLogger.error(f"Imported constant {name} is not supported")
            return None
        value = self._eval_constant_expr(const_decl.value)
        if value is None:
            ConverterLogger.error(
                f"Cannot evaluate constant: {name} (must be a numeric, bool or char value)"
            )
            return None
        return value
