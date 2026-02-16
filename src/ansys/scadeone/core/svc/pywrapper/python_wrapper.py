# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
import shutil
import platform
from collections import namedtuple
from keyword import iskeyword
from pathlib import Path
import os
import re
from typing import List, Optional, Tuple, Union

import jinja2

from ansys.scadeone.core import ScadeOneException
from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.project import Project
from ansys.scadeone.core.svc.build_system import (
    BuildConfig,
    BuildSystem,
    Target,
    TargetKind,
)
import ansys.scadeone.core.svc.generated_code as gc

# flake8: noqa

PredefInfo = namedtuple("PredefInfo", ["type_name", "init_value"])

predefs_ctypes = {
    "int8": PredefInfo("ctypes.c_int8", "0"),
    "int16": PredefInfo("ctypes.c_int16", "0"),
    "int32": PredefInfo("ctypes.c_int32", "0"),
    "int64": PredefInfo("ctypes.c_int64", "0"),
    "uint8": PredefInfo("ctypes.c_uint8", "0"),
    "uint16": PredefInfo("ctypes.c_uint16", "0"),
    "uint32": PredefInfo("ctypes.c_uint32", "0"),
    "uint64": PredefInfo("ctypes.c_uint64", "0"),
    "bool": PredefInfo("ctypes.c_uint8", "0"),
    "char": PredefInfo("ctypes.c_int8", "0"),
    "float32": PredefInfo("ctypes.c_float", "0.0"),
    "float64": PredefInfo("ctypes.c_double", "0.0"),
    "size": PredefInfo("ctypes.c_int64", "0"),
}

predefs_native = {
    "int8": PredefInfo("int", "0"),
    "int16": PredefInfo("int", "0"),
    "int32": PredefInfo("int", "0"),
    "int64": PredefInfo("int", "0"),
    "uint8": PredefInfo("int", "0"),
    "uint16": PredefInfo("int", "0"),
    "uint32": PredefInfo("int", "0"),
    "uint64": PredefInfo("int", "0"),
    "bool": PredefInfo("bool", "False"),
    "char": PredefInfo("int", "0"),
    "float32": PredefInfo("float", "0.0"),
    "float64": PredefInfo("float", "0.0"),
    "size": PredefInfo("int", "0"),
}

predefs_values = {"false": "0", "true": "1"}


class PythonWrapper:
    """Scade One wrapper in Python.

    Parameters
    ----------
    project : Project
        Scade One project.
    job : str
        Swan Code Generation job name.
    output : str, optional
        Wrapper name. If not provided, the name is "root_wrapper".
    target_dir : Union[str, Path], optional
        Wrapper location. If not provided,the wrapper is generated in a
        directory named with the wrapper name located in the current directory.
    """

    def __init__(
        self,
        project: Project,
        job: str,
        output: Optional[str] = None,
        target_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self._banner = "{0} {1}".format(
            FormatVersions.description("wrapper"), FormatVersions.version("wrapper")
        )
        self._project = project
        self._code_gen = gc.GeneratedCode(project, job)
        self._model_ops = None
        self._out_name = output or "root_wrapper"
        self._lib_name = (
            f"{self._out_name}.dll" if platform.system() == "Windows" else f"lib{self._out_name}.so"
        )
        self._target_path = target_dir
        self._imports = []
        self._swan_lib = []

    def _init_data(self):
        """
        Initialize data
        """

        # Get all model operators
        _opts = self._code_gen.root_operators
        self._model_ops = [self._code_gen.get_model_operator(_opt) for _opt in _opts]

    def _find_elaboration(self) -> Tuple[bool, str]:
        """
        Find a "elaboration" is present in the mapping file
        Returns
        -------
        Tuple[bool, str]
            If "elaboration" is present, returns True and its value, otherwise, returns False and empty.
        """

        _ela = self._code_gen.get_elaboration_function()
        return (True, _ela.name) if _ela else (False, "")

    def _target_dir(self) -> Path:
        """
        Get a target dir

        Returns
        -------
        Path
            Return a Path
        """
        target_path = (
            Path(self._target_path) / self._out_name
            if self._target_path
            else Path.cwd() / self._out_name
        )
        if not target_path.is_absolute():
            target_path = Path.cwd() / target_path
        target_path.mkdir(parents=True, exist_ok=True)
        return target_path

    def _get_predef_info(self, c_type_name: str, native: bool) -> Optional[PredefInfo]:
        if native:
            return predefs_native[c_type_name] if c_type_name in predefs_native else None
        else:
            return predefs_ctypes[c_type_name] if c_type_name in predefs_ctypes else None

    def _get_python_name(self, name: str) -> str:
        return name + "_" if iskeyword(name) else name

    def _get_python_type_name(self, type_base: gc.TypeBase, native: bool = False) -> str:
        """
        Get Python type name

        Parameters
        ----------
        type_base : TypeBase
            An instance of TypeBase
        native : bool, optional
            A type native option, by default False
        sizes : _type_, optional
            An array size, by default None

        Returns
        -------
        str
            Returns type name
        """

        if type_base and (type_base.is_scalar or type_base.is_enum_type):
            pi = self._get_predef_info(type_base.m_name, native)
            assert pi, f"No predef info was found for predef type {type_base.m_name}"
            name = pi.type_name
            return self._get_python_name(name)
        elif type_base and type_base.is_structure:
            return type_base.path
        elif type_base and type_base.is_array:
            pi = self._get_predef_info(type_base.m_name, False)
            size = " * ".join([str(s) for s in type_base.sizes])
            return f"{pi.type_name} * {size}"
        else:
            # TODO with others
            return ""

    def _get_initial_value(self, type_base: gc.TypeBase, native: bool = False) -> str:
        """
        Get default value corresponding to a given type

        Parameters
        ----------
        type_base : TypeBase
            An instance of TypeBase
        native : bool, optional
            A type native option, by default False

        Returns
        -------
        str
            Returns type name
        """

        if type_base and (type_base.is_scalar or type_base.is_enum_type):
            pi = self._get_predef_info(type_base.m_name, native)
            return pi.init_value
        elif type_base and type_base.is_array:
            return "()"
        elif type_base and type_base.is_structure:
            return type_base.path + "()"
        else:
            return ""

    def _get_enum_name(self, type_base: gc.TypeBase) -> str:
        if type_base.is_enum_type:
            return type_base.enum_name
        return ""

    def _get_array_info(self, type_base: gc.TypeBase) -> str:
        if type_base.is_array:
            return "tuple"
        return ""

    def _is_array_types(self, io_data: list) -> bool:
        for _elm in io_data:
            if any(_in[4] for _in in _elm["inputs"]["parameters"]):
                return True
            if any(_out[5] for _out in _elm["outputs"]["parameters"]):
                return True
        return False

    def _get_operator_ios(
        self, model_op: gc.ModelOperator, _mapping: dict
    ) -> tuple[List[tuple[str]], List[tuple[str]]]:
        """
        Get inputs/outputs of an operator

        Parameters
        ----------
        _mapping : dict
            A dict of type mapping data

        Returns
        -------
        tuple[List[tuple[str]], List[tuple[str]]]
            A tuple of inputs/outputs
        """
        _inputs = []
        _outputs = []
        _io_dct = {}
        _ou_dct = {}

        for _elm in self._code_gen.get_field_value(
            self._code_gen.get_code_elem(model_op._id), "parameters"
        ):
            _io_dct[_elm["id"]] = _elm["type"]

        for _elm in [_in for _in in model_op.inputs]:
            if _elm._id in _io_dct:
                _typ = self._code_gen.get_type(_mapping[_io_dct[_elm._id]], _io_dct[_elm._id])
                _nm = self._get_python_type_name(_typ, True)
                _val = self._get_initial_value(_typ, True)
                _enum = self._get_enum_name(_typ)
                _array = self._get_array_info(_typ)
                _inputs.append((_elm.name, _nm, _val, _enum, _array))
        for _elm in self._code_gen.get_interface_file(model_op._id)["declarations"]:
            if _elm[0] == "struct":
                for _id in _elm[1]["fields"]:
                    _ou_dct[_id["id"]] = _id["type"]
        for _elm in [_ot for _ot in model_op.outputs]:
            if _elm._id in _ou_dct:
                _rtn = _ou_dct[_elm._id]
            else:
                _chk = self._code_gen.get_field_value(
                    self._code_gen.get_code_elem(model_op._id), "return_type"
                )
                if _chk:
                    # If "return_type" is available in the mapping file
                    _rtn = _chk
                else:
                    _rtn = _io_dct[_elm._id]
            _typ = self._code_gen.get_type(_mapping[_rtn], _rtn)
            _nm = self._get_python_type_name(_typ, True)
            _val = self._get_initial_value(_typ, True)
            _enum = self._get_enum_name(_typ)
            _array = self._get_array_info(_typ)
            _cty = self._get_python_type_name(_typ, False)
            _outputs.append((_elm.name, _nm, _val, _enum, _array, _cty))
        return _inputs, _outputs

    def _generate_ios_context(
        self, model_op: gc.ModelOperator, context_data: List[str], _mapping: dict
    ) -> List[str]:
        """
        Generate inputs/outputs context

        Parameters
        ----------
        context_data : List[str]
            List of context field names
        _mapping : dict
            A dict of type mapping data

        Returns
        -------
        List[str]
            Return a list of contexts
        """
        _rtn = []
        for _idx, _elm in enumerate(context_data):
            if (
                _elm["name"] not in [_elm.name for _elm in model_op.inputs]
                and self._code_gen.get_code_id(_elm["id"], "ContextType", True) == -1
            ):
                _typ = self._code_gen.get_type(_mapping[_elm["type"]], _elm["type"])
                _nm = self._get_python_type_name(_typ)
                if isinstance(_typ, gc.Array):
                    _nm = f"({_nm})"
                _rtn.append(f"self._{_elm['name']} = {_nm}.from_address(context + offsets[{_idx}])")
            elif _elm.get("pointer"):
                _typ = self._code_gen.get_type(_mapping[_elm["type"]], _elm["type"])
                _nm = self._get_python_type_name(_typ)
                _rtn.append(f"self._{_elm['name']} = {_nm}()")
        return _rtn

    def _generate_cycle_parameters(
        self, model_op: gc.ModelOperator, parameters: dict, _mapping: dict
    ) -> tuple[str, List[str]]:
        """
        Generate cycle parameters

        Parameters
        ----------
        parameters : dict
            A dict of parameters data
        _mapping : dict
            A dict of type data

        Returns
        -------
        tuple[List[str], List[str]]
            Return a tuple of parameters and parameter names
        """
        _param = []
        _params_name = []
        for _fld in parameters:
            if _fld["type"] in _mapping:
                if self._code_gen.get_role_type(model_op._id, _fld["type"]) == "ContextType":
                    _rtn = "ctypes.c_void_p"
                else:
                    _rtn = self._get_python_type_name(
                        self._code_gen.get_type(_mapping[_fld["type"]], _fld["type"])
                    )
                if _fld.get("pointer"):
                    _rtn = f"ctypes.POINTER({_rtn})"
                _param.append(_rtn)
        for _fld in parameters:
            if _fld["type"] in _mapping:
                if self._code_gen.get_role_type(model_op._id, _fld["type"]) == "ContextType":
                    _params_name.append("out_c")
                else:
                    if _fld["name"] in [_it.name for _it in model_op.inputs]:
                        _params_name.append(_fld["name"])
        return _param, _params_name

    def _generate_method_data(
        self, model_op: gc.ModelOperator, lst_method: List[str], save: dict
    ) -> None:
        """
        Generate method data

        Parameters
        ----------
        lst_method : List[str]
            A list of methods
        save : dict
            An output
        """
        for _role in lst_method:
            _name = "_".join([x.lower() for x in re.findall("[A-Z][^A-Z]*", _role)])
            _dta = self._code_gen.get_method_data(model_op._id, _role)
            save[_name] = _dta

    def _generate_def(self, def_pathname: Path) -> None:
        """
        Generate .def file for exported symbols.

        Parameters
        ----------
        def_pathname : Path
            Path of the .def file to generate
        """

        # Initialize exports data
        _exp = {}
        _id = 1
        for _model_op in self._model_ops:
            # Add cycle method data
            if _model_op.cycle_method:
                _exp[_model_op.cycle_method.name] = _id
                _id = _id + 1
            # Add init method data
            if _model_op.init_method:
                _exp[_model_op.init_method.name] = _id
                _id = _id + 1
            # Add reset method data
            if _model_op.reset_method:
                _exp[_model_op.reset_method.name] = _id
                _id = _id + 1
        # Add elaboration data
        _fnd, _elaboration = self._find_elaboration()
        if _fnd:
            _exp[_elaboration] = _id
        # Add sensors data
        for _code in self._code_gen.code:
            if _code["interface_file"] != "swan_sensors.h":
                continue
            for _decl in _code["declarations"]:
                if _decl[0] != "global":
                    continue
                _exp[_decl[1]["name"]] = _id
                _id = _id + 1
        # Create *.def file
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("exports_wrapper.j2")

        content = template.render(TOOL_WRAPPER=self._banner, EXP_DEF=_exp)

        def_pathname.write_text(content)

    def _generate_c_code(self, c_pathname: Path) -> None:
        """
        Generate *.c file

        Parameters
        ----------
        c_pathname : Path
            Path of the .c file to generate
        """

        _data = []
        _sns_data = {}
        for _model_op in self._model_ops:
            # Initialize operator data
            _op_dict = {}
            _op_dict["ios_declared"] = []
            _op_dict["init_c_name"] = ""
            _op_dict["reset_parameters"] = []
            _op_dict["opt_name"] = self._code_gen.get_operator_name(_model_op._id)
            _op_dict["opt_path"] = _model_op.path

            # Update the data for method
            self._generate_method_data(
                _model_op, ["InitMethod", "ResetMethod", "ContextType"], _op_dict
            )
            if _op_dict["init_method"]:
                _op_dict["init_c_name"] = self._code_gen.get_field_value(
                    _op_dict["init_method"], "name"
                )

            if _op_dict["reset_method"]:
                _op_dict["reset_parameters"] = self._code_gen.get_field_value(
                    _op_dict["reset_method"], "parameters"
                )

            if _op_dict["context_type"] and _model_op.cycle_method:
                _ios_declared = []
                for _fld in self._code_gen.get_field_value(_op_dict["context_type"], "fields"):
                    if _fld["id"] in self._code_gen.get_model_id_mapping():
                        _ios_declared.append(_fld["name"])
                _op_dict["ios_declared"] = _ios_declared
            _data.append(_op_dict)

        # Sensor data
        _type_mapping = self._code_gen.get_code_type_id_mapping()
        for _elm in self._code_gen.code:
            _inc = _elm.get("interface_file")
            if "sensor" in _inc:
                _sns_data["include"] = str(_inc)
                break
        _sns = self._code_gen.get_model_elements("sensor")
        _sns_data["elements"] = []
        for _, _elm in _sns:
            _dt = {}
            _dt["path"] = _elm["path"]
            _, _vl = _type_mapping[_elm["id"]]
            _dt["name"] = _vl["name"]
            _typ = self._code_gen.get_type(_type_mapping[_vl["type"]], _vl["type"])
            _dt["type"] = _typ.path
            _sns_data["elements"].append(_dt)

        # Create *.c code file
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("C_wrapper.j2")

        content = template.render(
            TOOL_WRAPPER=self._banner,
            OPERATORS_DATA=_data,
            SENSORS=_sns_data,
            OS_WINDOWS=platform.system() == "Windows",
        )

        c_pathname.write_text(content)

    def _generate_python(self, py_pathname: Path) -> None:
        """
        Generate *.py file

        Parameters
        ----------
        py_pathname : Path
            Path of the .py file to generate
        """

        _data = []
        _enum_data = {}
        _struct_data = {}
        _sns_data = []

        for _model_op in self._model_ops:
            # Initialize operator data
            _op_dict = {}
            _op_dict["ios_context"] = []
            _op_dict["op_name"] = self._code_gen.get_operator_name(_model_op._id)
            _op_dict["inputs"] = {"name": "Inputs", "parameters": []}
            _op_dict["outputs"] = {"name": "Outputs", "parameters": []}

            # Update the data for method
            _code_type_mapping = self._code_gen.get_code_type_id_mapping()
            _op_dict["inputs"]["parameters"], _op_dict["outputs"]["parameters"] = (
                self._get_operator_ios(_model_op, _code_type_mapping)
            )

            _op_dict["op_context"] = {}
            _ctx = []
            self._generate_method_data(
                _model_op, ["ResetMethod", "ContextType", "CycleMethod"], _op_dict
            )
            if _op_dict["context_type"] and _model_op.cycle_method:
                _op_dict["op_context"]["c_name"] = self._code_gen.get_operator_name(_model_op._id)
                _, _out = self._code_gen.get_function_parameters(_model_op._id, "ContextType")
                _op_dict["op_context"]["py_name"] = "_out_c" if _out else ""
                for _fld in self._code_gen.get_field_value(_op_dict["context_type"], "fields"):
                    if _fld["id"] in self._code_gen.get_model_id_mapping():
                        _ctx.append(_fld)
                _op_dict["op_context"]["len_context"] = len(_ctx)

            if _op_dict["reset_method"]:
                _op_dict["op_reset"] = {
                    "c_name": self._code_gen.get_field_value(_op_dict["reset_method"], "name"),
                    "parameters": self._code_gen.get_field_value(
                        _op_dict["reset_method"], "parameters"
                    ),
                }
            else:
                _op_dict["op_reset"] = {}

            _op_dict["ios_context"] = self._generate_ios_context(
                _model_op, _ctx, _code_type_mapping
            )
            _rtn = None
            cycle_method_content = _op_dict["cycle_method"]["content"]
            if cycle_method_content.get("return_type"):
                _rtn = _op_dict["outputs"]["parameters"][0]
            _op_dict["op_cycle"] = {
                "c_name": self._code_gen.get_field_value(_op_dict["cycle_method"], "name"),
                "parameter": "",
                "parameters_name": [],
                "return": _rtn,
            }
            (
                _op_dict["op_cycle"]["parameter"],
                _op_dict["op_cycle"]["parameters_name"],
            ) = self._generate_cycle_parameters(
                _model_op,
                self._code_gen.get_field_value(_op_dict["cycle_method"], "parameters"),
                _code_type_mapping,
            )

            _data.append(_op_dict)

        # Enumeration / Structure types
        _code_type_mapping = self._code_gen.get_code_type_id_mapping()
        _model_mapping = self._code_gen.get_model_id_mapping()
        _links = self._code_gen._get_mapping()

        for _elm in _code_type_mapping.values():
            if _elm[0] == "enum":
                enum_values = []
                for value in _elm[1]["values"]:
                    enum_values.append(value["name"])
                _enum_data[_elm[1]["name"]] = enum_values
            elif _elm[0] == "struct":
                struct_name = _elm[1].get("name")
                struct_values = []
                model_elt_id = _links.get(_elm[1]["id"])
                if model_elt_id in _model_mapping.keys():
                    for value in _elm[1]["fields"]:
                        _field_type_code_id = value["type"]
                        _field_type_model_id = _links.get(_field_type_code_id)
                        _field_type = "None"  # TODO change for complex structures
                        if _field_type_model_id:
                            _field_type_model_elt = self._code_gen.get_model_element(
                                _field_type_model_id, True
                            )
                            _field_type_name = _field_type_model_elt[1]["name"]
                            _field_type = self._get_predef_info(_field_type_name, False)[0]
                        struct_values.append([value["name"], _field_type])
                    _struct_data[struct_name] = struct_values

        # Sensor data
        _sns = self._code_gen.get_model_elements("sensor")
        for _, _elm in _sns:
            _, _vl = _code_type_mapping[_elm["id"]]
            _snm = _elm["path"].split("::")[1]
            _spt = _vl["name"]
            _typ = self._code_gen.get_type(_code_type_mapping[_vl["type"]], _vl["type"])
            _cty = self._get_python_type_name(_typ)
            _pty = self._get_python_type_name(_typ, True)
            _sns_data.append((_snm, _cty, _spt, _pty))

        # Elaboration data
        _, _ela = self._find_elaboration()

        # Create *.py code file
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("Py_wrapper.j2")

        content = template.render(
            LIB_NAME=self._lib_name,
            TOOL_WRAPPER=self._banner,
            OPERATORS_DATA=_data,
            ELABORATION=_ela,
            SENSORS=_sns_data,
            ENUM_TYPES=_enum_data,
            STRUCTURE_TYPES=_struct_data,
            IS_ARRAY_TYPES=self._is_array_types(_data),
        )

        py_pathname.write_text(content)

    def _generate_swan_config(self, config_pathname: Path) -> None:
        """
        Generate swan_config.h file

        Parameters
        ----------
        config_pathname : Path
            Path of the .h file to generate
        """

        # Create swan_config.h
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent.parent / "common/templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("swan_config_template.h")

        _includes = "\n".join([f'#include "{inc}"' for inc in self._swan_lib])
        swan_config = template.render(HOOK_BEGIN="", HOOK_END=_includes if _includes else "")

        config_pathname.write_text(swan_config)

    def _collect_imported_code_files(self) -> None:
        """
        Collect imported code files from the project resources and dependencies.
        """

        self._imports = [
            (self._project.directory / resource.path).resolve()
            for resource in (self._project.resources or [])
        ]

        scadeone_install = str(self._project.app.install_dir.resolve())
        for dependency in self._project.dependencies(True) or []:
            for dep in dependency.resources:
                resource_path = (dependency.directory / dep.path).resolve()
                # Check if the resource is a swan library
                if str(dependency.directory).startswith(scadeone_install):
                    self._swan_lib.append(resource_path.name)
                self._imports.append(resource_path)

    def _generate_declaration_files(self) -> List[str]:
        """
        Get all files generated

        Returns
        -------
        List[str]
            List of files generated
        """

        _lt = []
        for _elm in self._code_gen.code:
            if _elm.get("implementation_file"):
                _lt.append(_elm["implementation_file"])
            if _elm.get("interface_file"):
                _lt.append(_elm["interface_file"])
        return _lt

    def _build_wrapper(self):
        """
        Build wrapper using the C files generated by Swan CG
        and the C and DEF files generated by the wrapper. The temporary files are generated
        in a temporary directory called "build",
        located in the same wrapper directory. If the build is successful, the temporary directory
        is removed, otherwise, the directory is kept for debugging purposes.
        The builder uses the BuildSystem located in the Scade One installation.

        Note: it may happen that the "build" directory cannot be removed
        because some files are locked by the OS. In this case, the user should remove it.
        A message is logged in the pyscadeone.log file.
        """
        cfg = BuildConfig()
        build_dir = Path(self._target_dir()) / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        cfg.working_dir = str(build_dir)
        cfg.c_files = [str(file) for file in self._target_dir().glob("*.c")]
        cfg.c_files.extend(
            [str(file) for file in Path(self._code_gen.generated_code_dir).glob("*.c")]
        )
        cfg.include_dirs = [str(self._target_dir()), str(self._code_gen.generated_code_dir)]

        for imported_code in self._imports:
            if imported_code.suffix in [".h", ".c"]:
                if str(imported_code.parent) not in cfg.include_dirs:
                    cfg.include_dirs.append(str(imported_code.parent))
                if imported_code.suffix == ".c":
                    cfg.c_files.append(str(imported_code))

        if platform.system() == "Windows":
            cfg.o_files = [str(file) for file in self._target_dir().glob("*.def")]

        cfg.targets = [Target(self._out_name, TargetKind.SHARED_LIBRARY)]
        builder = BuildSystem(self._project.app.install_dir)
        result = builder.build(cfg)
        if not result.is_succeeded:
            raise ScadeOneException(f"Error building wrapper: {result.messages}")
        shutil.copy(build_dir / self._lib_name, self._target_dir())
        shutil.rmtree(
            build_dir,
            onerror=lambda f, p, e: LOGGER.error(f"Error removing build directory {p}: {e}"),
        )

    def generate(self) -> None:
        """
        Generate wrapper for Scade One project.
        """

        # Initialize data
        _files = []
        self._init_data()
        # Clean target dir before generating new files
        shutil.rmtree(self._target_dir())
        # Generate swan_cg_files.txt for files generated by KCG swan
        _swan_cg_file = self._target_dir() / "swan_cg_files.txt"
        _start = _swan_cg_file.parent.absolute()
        with _swan_cg_file.open("w") as f:
            # add files generated by Swan Code Generator
            for file_name in self._generate_declaration_files():
                f.write(
                    (self._target_dir() / file_name)
                    .absolute()
                    .relative_to(_start)
                    .as_posix()
                    .replace("\\", "/")
                    + "\n"
                )
        # Generate *.def file
        _def_pathname = self._target_dir() / (f"{self._out_name}.def")
        _files.append(_def_pathname)
        self._generate_def(_def_pathname)
        # Generate *.c file
        _c_pathname = self._target_dir() / (f"{self._out_name}.c")
        _files.append(_c_pathname)
        self._generate_c_code(_c_pathname)
        # Generate *.py file
        _py_pathname = self._target_dir() / (f"{self._out_name}.py")
        _files.append(_py_pathname)
        self._generate_python(_py_pathname)
        # Collect imported code files
        self._collect_imported_code_files()
        # Generate swan_config.h file
        _conf_pathname = self._target_dir() / "swan_config.h"
        self._generate_swan_config(_conf_pathname)
        _files.append(self._target_dir() / "swan_config.h")
        # Generate py_wrapper_files.txt
        _py_wrapper_files = self._target_dir() / "py_wrapper_files.txt"
        _start_file = _py_wrapper_files.parent.absolute()
        _cnt = "\n".join(
            Path(os.path.relpath(str(f.absolute()), _start_file)).as_posix() for f in _files
        )
        _py_wrapper_files.write_text(_cnt)
        # Build wrapper (DLL)
        self._build_wrapper()
