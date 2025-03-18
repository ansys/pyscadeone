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

from collections import namedtuple
from keyword import iskeyword
from pathlib import Path
import re
from typing import List, Tuple

import jinja2

from ansys.scadeone.core import ScadeOneException
from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.project import Project
from ansys.scadeone.core.svc.build_system import (
    BuildConfig,
    BuildSystem,
    Target,
    TargetKind,
)
import ansys.scadeone.core.svc.generated_code as GC

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
    """
    Generate a Scade One wrapper in Python.

    Parameters
    ----------
    project : Project
        Scade One project.

    code_gen : GeneratedCode
        Scade One generated code.

    opt_name : str
        Root operator name.

    out_name : str
        Wrapper name.
    """

    def __init__(
        self,
        project: Project,
        code_gen: GC.GeneratedCode,
        opt_name: str,
        out_name: str,
    ) -> None:
        self._banner = "{0} {1}".format(
            FormatVersions.description("wrapper"), FormatVersions.version("wrapper")
        )
        self._project = project
        self._code_gen = code_gen
        self._model_op = code_gen.get_model_operator(opt_name)
        self._out_name = out_name

    def _find_elaboration(self) -> Tuple[bool, str]:
        """
        Find a "elaboration" is present in the mapping file
        Returns
        -------
        Tuple[bool, str]
            If "elaboration" is present, returns True and its value, otherwise, returns False and empty.
        """
        _rtn: bool = False
        _val: str = ""
        for elm in self._code_gen.code:
            if "swan_elaboration.c" in elm.values():
                _rtn = True
                _val = "swan_elaboration"
                break

        return _rtn, _val

    def _target_dir(self) -> Path:
        """
        Get a target dir

        Returns
        -------
        Path
            Return a Path
        """
        return Path(self._code_gen.generated_code_dir)

    def _get_predef_info(self, c_type_name: str, native: bool) -> PredefInfo:
        if native:
            return predefs_native[c_type_name] if c_type_name in predefs_native else None
        else:
            return predefs_ctypes[c_type_name] if c_type_name in predefs_ctypes else None

    def _get_python_name(self, name: str) -> str:
        return name + "_" if iskeyword(name) else name

    def _get_python_type_name(self, type_base: GC.TypeBase, native: bool = False):
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

        if type_base and type_base.scalar:
            pi = self._get_predef_info(type_base.m_name, native)
            name = pi.type_name
            return self._get_python_name(name)
        else:
            # TODO with others, including Structure
            return ""

    def _get_initial_value(self, type_base: GC.TypeBase, native: bool = False) -> str:
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

        if type_base and type_base.scalar:
            pi = self._get_predef_info(type_base.m_name, native)
            return pi.init_value
        else:
            # TODO with others, including Structure
            return ""

    def _get_operator_ios(self, _mapping: dict) -> tuple[List[tuple[str]], List[tuple[str]]]:
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
            self._code_gen.get_code_elem(self._model_op._id), "parameters"
        ):
            _io_dct[_elm["id"]] = _elm["type"]

        for _elm in [_in for _in in self._model_op.inputs]:
            if _elm._id in _io_dct:
                _typ = self._code_gen.get_type(_mapping[_io_dct[_elm._id]], _io_dct[_elm._id])
                _nm = self._get_python_type_name(_typ, True)
                _val = self._get_initial_value(_typ, True)
                _inputs.append((_elm.name, _nm, _val))
        for _elm in self._code_gen.get_interface_file(self._model_op._id)["declarations"]:
            if _elm[0] == "struct":
                for _id in _elm[1]["fields"]:
                    _ou_dct[_id["id"]] = _id["type"]
        for _elm in [_ot for _ot in self._model_op.outputs]:
            if _elm._id in _ou_dct:
                _rtn = _ou_dct[_elm._id]
            else:
                _chk = self._code_gen.get_field_value(
                    self._code_gen.get_code_elem(self._model_op._id), "return_type"
                )
                if _chk:
                    # If "return_type" is available in the mapping file
                    _rtn = _chk
                else:
                    _rtn = _io_dct[_elm._id]
            _typ = self._code_gen.get_type(_mapping[_rtn], _rtn)
            _nm = self._get_python_type_name(_typ, True)
            _val = self._get_initial_value(_typ, True)
            _cty = self._get_python_type_name(_typ, False)
            _outputs.append((_elm.name, _nm, _val, _cty))
        return _inputs, _outputs

    def _generate_ios_context(self, context_data: List[str], _mapping: dict) -> List[str]:
        """
        Generate inputs/outputs context

        Parameters
        ----------
        context_data : List[str]
            _description_
        _mapping : dict
            _description_

        Returns
        -------
        List[str]
            Return a list of contexts
        """
        _rtn = []
        for _idx, _elm in enumerate(context_data):
            if (
                _elm["name"] not in [_elm.name for _elm in self._model_op.inputs]
                and self._code_gen.get_code_id(_elm["id"], "ContextType", True) == -1
            ):
                _typ = self._code_gen.get_type(_mapping[_elm["type"]], _elm["type"])
                _nm = self._get_python_type_name(_typ)
                _rtn.append(f"self._{_elm['name']} = {_nm}.from_address(context + offsets[{_idx}])")
            elif _elm["pointer"]:
                _typ = self._code_gen.get_type(_mapping[_elm["type"]], _elm["type"])
                _nm = self._get_python_type_name(_typ)
                _rtn.append(f"self._{_elm['name']} = {_nm}()")
        return _rtn

    def _generate_cycle_parameters(self, parameters: dict, _mapping: dict) -> tuple[str, List[str]]:
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
                if self._code_gen.get_role_type(self._model_op._id, _fld["type"]) == "ContextType":
                    _rtn = "ctypes.c_void_p"
                else:
                    _rtn = self._get_python_type_name(
                        self._code_gen.get_type(_mapping[_fld["type"]], _fld["type"])
                    )
                if _fld["pointer"]:
                    _rtn = f"ctypes.POINTER({_rtn})"
                _param.append(_rtn)
        for _fld in parameters:
            if _fld["type"] in _mapping:
                if self._code_gen.get_role_type(self._model_op._id, _fld["type"]) == "ContextType":
                    _params_name.append("out_c")
                else:
                    if _fld["name"] in [_it.name for _it in self._model_op.inputs]:
                        _params_name.append(_fld["name"])
        return _param, _params_name

    def _generate_method_data(self, lst_method: List[str], save: dict) -> None:
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
            _dta = self._code_gen.get_method_data(self._model_op._id, _role)
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
        # Add cycle method data
        if self._model_op.cycle_method:
            _exp[self._model_op.cycle_method.name] = _id
            _id = _id + 1
        # Add init method data
        if self._model_op.init_method:
            _exp[self._model_op.init_method.name] = _id
            _id = _id + 1
        # Add reset method data
        if self._model_op.reset_method:
            _exp[self._model_op.reset_method.name] = _id
            _id = _id + 1
        # Add elaboration data
        _fnd, _elaboration = self._find_elaboration()
        if _fnd:
            _exp[_elaboration] = _id
        # Create *.def file
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("exports_wrapper.def")

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

        # Initialize operator data
        _op_dict = {}
        _op_dict["ios_declared"] = []
        _op_dict["init_c_name"] = ""
        _op_dict["reset_parameters"] = []
        _op_dict["opt_name"] = self._code_gen.get_operator_name(self._model_op._id)
        _op_dict["opt_path"] = self._model_op.path

        # Update the data for method
        self._generate_method_data(["InitMethod", "ResetMethod", "ContextType"], _op_dict)
        if _op_dict["init_method"]:
            _op_dict["init_c_name"] = self._code_gen.get_field_value(
                _op_dict["init_method"], "name"
            )

        if _op_dict["reset_method"]:
            _op_dict["reset_parameters"] = self._code_gen.get_field_value(
                _op_dict["reset_method"], "parameters"
            )

        if _op_dict["context_type"] and self._model_op.cycle_method:
            _ios_declared = []
            for _fld in self._code_gen.get_field_value(_op_dict["context_type"], "fields"):
                if _fld["id"] in self._code_gen.get_model_id_mapping():
                    _ios_declared.append(_fld["name"])
            _op_dict["ios_declared"] = _ios_declared

        # Create *.c code file
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("C_wrapper.c")

        content = template.render(
            TOOL_WRAPPER=self._banner,
            OPERATOR_NAME=_op_dict["opt_name"],
            OPERATOR_PATH=_op_dict["opt_path"],
            OP_INIT=_op_dict["init_method"],
            INIT_NAME=_op_dict["init_c_name"],
            RESET_PARAMETERS=_op_dict["reset_parameters"],
            CONTEXT_TYPE=_op_dict["context_type"],
            IOS_DECLARED=_op_dict["ios_declared"],
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

        # Initialize operator data
        _op_dict = {}
        _op_dict["ios_context"] = []
        _nm = self._code_gen.get_operator_name(self._model_op._id)
        _op_dict["op_name"] = _nm.split("_")[0] if "_" in _nm else _nm
        # TODO: sensors not yet supported
        _op_dict["sensors"] = []
        # TODO: c_interface_typed related to sensors, not yet supported
        _op_dict["c_interface_typed"] = []
        # TODO: return type of CycleMethod
        _op_dict["inputs"] = {"name": "Inputs", "parameters": []}
        _op_dict["outputs"] = {"name": "Outputs", "parameters": []}

        # Update the data for method
        _type_mapping = self._code_gen.get_type_id_mapping()
        _op_dict["inputs"]["parameters"], _op_dict["outputs"]["parameters"] = (
            self._get_operator_ios(_type_mapping)
        )

        _op_dict["op_context"] = {}
        _ctx = []
        self._generate_method_data(["ResetMethod", "ContextType", "CycleMethod"], _op_dict)
        if _op_dict["context_type"] and self._model_op.cycle_method:
            _op_dict["op_context"]["c_name"] = self._code_gen.get_operator_name(self._model_op._id)
            _, _out = self._code_gen.get_function_ios(self._model_op._id, "ContextType")
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

        _op_dict["ios_context"] = self._generate_ios_context(_ctx, _type_mapping)

        _rtn = None
        if len(_op_dict["outputs"]["parameters"]) == 1:
            _rtn = _op_dict["outputs"]["parameters"][0]

        _op_dict["op_cycle"] = {
            "c_name": self._code_gen.get_field_value(_op_dict["cycle_method"], "name"),
            "parameter": "",
            "parameters_name": [],
            "return": _rtn,  # must be a function with a single scalar output
        }
        _op_dict["op_cycle"]["parameter"], _op_dict["op_cycle"]["parameters_name"] = (
            self._generate_cycle_parameters(
                self._code_gen.get_field_value(_op_dict["cycle_method"], "parameters"),
                _type_mapping,
            )
        )

        _, _op_dict["elaboration"] = self._find_elaboration()

        # Create *.py code file
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("Py_wrapper.py.j2")

        content = template.render(
            TOOL_WRAPPER=self._banner,
            ELABORATION=_op_dict["elaboration"],
            SENSOR=_op_dict["sensors"],
            C_INTERFACE_TYPED=_op_dict["c_interface_typed"],
            OPERATOR_NAME=_op_dict["op_name"],
            OP_CONTEXT=_op_dict["op_context"],
            OP_RESET=_op_dict["op_reset"],
            OP_CYCLE=_op_dict["op_cycle"],
            IOS_CONTEXT=_op_dict["ios_context"],
            OPERATOR_IN=_op_dict["inputs"],
            OPERATOR_OUT=_op_dict["outputs"],
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
        includes = ""
        resources = []

        # TODO: to verify this code works well with others User Stories related to Types and Imported Code
        # Get all import and  *.h header files defined for the project
        _data = self._project.data
        _path = self._project.directory
        for resource in _data["Resources"]:
            if resource["Kind"] in ("ImportedTypes", "HeaderFile"):
                new_resource = _path.parent.joinpath(resource["Path"]).resolve()
                if new_resource not in resources:
                    resources.append(new_resource)
        for resource in resources:
            includes = includes + "\n" + '#include "{}"'.format(str(resource))

        # Create swan_config.h
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent.parent / "common/templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("swan_config_template.h")

        content = template.render(HOOK_BEGIN="", HOOK_END="")

        swan_config = content.replace("#include <string.h>", "#include <string.h>" + includes)
        config_pathname.write_text(swan_config)

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
        Build wrapper using the c and def files generated by KCG swan
        and the c file wrapper.
        The builder uses the BuildSystem located in the Scade One installation.
        """
        cfg = BuildConfig()
        cfg.working_dir = str(self._target_dir())
        cfg.c_files = [str(file) for file in self._target_dir().glob("*.c")]
        cfg.o_files = [str(file) for file in self._target_dir().glob("*.def")]
        cfg.targets = [Target(self._out_name, TargetKind.SHARED_LIBRARY)]
        builder = BuildSystem(self._project.app.install_dir)
        result = builder.build(cfg)
        if not result.success:
            raise ScadeOneException(f"Error building wrapper: {result.messages}")

    def generate(self) -> None:
        """
        Generate wrapper for Scade One project.
        """

        # Initialize data
        _files = []
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
        # Generate swan_config.h file
        _conf_pathname = self._target_dir() / "swan_config.h"
        _files.append(_conf_pathname)
        self._generate_swan_config(_conf_pathname)
        # Generate py_wrapper_files.txt
        _py_wrapper_files = self._target_dir() / "py_wrapper_files.txt"
        _start_file = _py_wrapper_files.parent.absolute()
        _cnt = "\n".join(f.absolute().relative_to(_start_file).as_posix() for f in _files)
        _py_wrapper_files.write_text(_cnt)
        # Build wrapper (DLL)
        self._build_wrapper()
