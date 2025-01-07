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

# This module contains the classes and functions that are necessary to
# manipulate Scade One model elements retrieved from the mapping file.

from abc import ABC, abstractmethod
import functools

# cSpell: ignore oper, elems, ename
import json
from pathlib import Path
from typing import Generator, List, Optional, Tuple, Union

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.project import Project

MapElem = List[Union[str, dict]]
CodeElem = Tuple[str, dict, int]


class MappingObject(ABC):
    """
    Base class for all mapping file elements.

    - gen_code: *GeneratedCode* object
    - mapping_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", mapping_elem: dict) -> None:
        self._id = mapping_elem["id"]
        self._gen_code = gen_code
        self._mapping_elem = mapping_elem


class CDeclaration(MappingObject):
    """
    Base class for C declaration
    (function, global, macro, predefined_type, struct, array, enum, union, typedef, imported_type).

    - gen_code: *GeneratedCode* object
    - decl_elem: mapping file element
    - code_container_index: position in the list of code container elements
    """

    def __init__(
        self, gen_code: "GeneratedCode", decl_elem: dict, code_container_index: int
    ) -> None:
        super().__init__(gen_code, decl_elem)
        self._code_container_index = code_container_index

    def get_interface_file(self) -> str:
        """Returns the name of the enclosed interface C header file."""
        try:
            return self._gen_code.code[self._code_container_index]["interface_file"]
        except Exception:
            raise ScadeOneException(
                f"Generated code: no interface_file for CodeContainer at index #{self._code_container_index}"  # noqa
            )

    def get_implementation_file(self) -> str:
        """Returns the name of the enclosed implementation C file."""
        try:
            return self._gen_code.code[self._code_container_index]["implementation_file"]
        except Exception:
            raise ScadeOneException(
                f"Generated code: no implementation_file for CodeContainer at index #{self._code_container_index}"  # noqa
            )


class CParameter(MappingObject):
    """
    Class for a parameter of a generated C function.

    - gen_code: *GeneratedCode* object
    - param_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", param_elem: dict) -> None:
        super().__init__(gen_code, param_elem)
        self._name = param_elem["name"]
        self._type_id = param_elem["type"]
        self._pointer = param_elem.get("pointer", False)
        self._const = param_elem.get("const", False)
        self._type_name = None

    @property
    def param_type_id(self) -> int:
        """Returns the type id of the parameter"""
        return self._type_id

    @property
    def name(self) -> str:
        """Returns the parameter name"""
        return self._name

    @property
    def type_name(self) -> str:
        """Returns the parameter type name"""
        if self._type_name is None:
            type_elem = self._gen_code.get_code_elem(self._type_id)
            self._type_name = type_elem.get("content", {}).get("name", "__unknown__")
        return self._type_name

    @property
    def pointer(self) -> bool:
        """Indicates if the parameter is a pointer"""
        return self._pointer

    @property
    def const(self) -> bool:
        """Indicates if the parameter is a const type"""
        return self._const

    @property
    def signature(self) -> str:
        """Returns the parameter type signature (taking into account pointer and const)."""
        const = "const " if self.const else ""
        pointer = " *" if self.pointer else ""
        return f"{const}{self.type_name}{pointer}"


class CFunction(CDeclaration):
    """
    Class for a generated C function.

    - gen_code: *GeneratedCode* object
    - function_elem: mapping file element
    - code_container_index: position in the list of code container elements
    """

    def __init__(self, gen_code: "GeneratedCode", function_elem: dict, code_container_index: int):
        super().__init__(gen_code, function_elem, code_container_index)
        self._name = None
        self._parameters = None
        self._return_type = None

    @property
    def name(self) -> str:
        """Returns the function name"""
        if self._name is None:
            self._name = self._mapping_elem["name"]
        return self._name

    @property
    def parameters(self) -> List[CParameter]:
        """Returns the function parameters as a list of CParameter objects."""
        if self._parameters is None:
            self._parameters = [
                CParameter(self._gen_code, x) for x in self._mapping_elem.get("parameters", [])
            ]
        return self._parameters

    @property
    def return_type(self) -> Optional[dict]:
        """Returns the function return type as raw mapping file dictionary data, if any."""
        if self._return_type is None:
            code_id = self._mapping_elem.get("return_type", -1)
            if code_id != -1:
                self._return_type = self._gen_code.decompose_code_type(
                    self._gen_code.get_code_elem(code_id)
                )
        return self._return_type


class ModelObject(MappingObject):
    """
    Base Class for mapping file model elements.

    - gen_code: *GeneratedCode* object
    - model_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", model_elem: dict) -> None:
        super().__init__(gen_code, model_elem)

    def get_code_elem(self, role: str = "", silent: bool = False) -> Optional[dict]:
        """Returns the data associated to the model element, if any."""
        code_id = self._gen_code.get_code_id(self._id, role, silent)
        if code_id != -1:
            return self._gen_code.get_code_elem(code_id)
        else:
            return None


class ModelSensor(ModelObject):
    """
    Class for model sensors.

    - gen_code: *GeneratedCode* object
    - var_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", sensor_elem: dict) -> None:
        super().__init__(gen_code, sensor_elem)
        self._path = None
        self._type_id = sensor_elem.get("type", -1)
        self._code_name = None
        self._code_type = None
        self._code_type_name = None

    @property
    def path(self) -> str:
        """Returns the Scade One sensor path"""
        if self._path is None:
            self._path = self._mapping_elem["path"]
        return self._path

    @property
    def code_name(self) -> str:
        """Returns the name of the variable as defined in the generated C function."""
        if self._code_name is None:
            code_elem = self.get_code_elem(silent=True)
            if code_elem is None:
                self._code_name = "__no_name__"
            else:
                self._code_name = code_elem["content"]["name"]
        return self._code_name

    @property
    def code_type(self) -> dict:
        """
        Returns the generated C code data corresponding to the sensor type.
        ('name': C type name, 'category': type category and 'elements': sub elements of the type)
        """
        if self._code_type is None:
            code_elem = self.get_code_elem(silent=True)
            self._code_type = self._gen_code.decompose_code_type(
                self._gen_code.get_code_elem(code_elem["content"]["type"])
            )
        return self._code_type

    @property
    def code_type_name(self) -> str:
        """Returns the sensor C type name"""
        if self._code_type_name is None:
            self._code_type_name = self.code_type.get("name", "__unknown__")
        return self._code_type_name

    def get_code_elem(self, role: str = "", silent: bool = False) -> Optional[dict]:
        """Returns the data associated to the model element, if any."""
        code_elem = super().get_code_elem(role, True)
        if code_elem is None:
            # no correspondence in mapping section => use the model id as the code id
            code_elem = self._gen_code.get_code_elem(self._id)
        return code_elem


class ModelVariableBase(ModelObject):
    """
    Base class for model variables (operators inputs or outputs).

    - gen_code: *GeneratedCode* object
    - var_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", var_elem: dict) -> None:
        super().__init__(gen_code, var_elem)
        self._code_name = None
        self._code_type = None
        self._code_elem = None

    @property
    @abstractmethod
    def parent(self) -> "ModelOperatorBase":
        """Returns the model operator object owning the variable"""
        pass

    @property
    def code_name(self) -> str:
        """Returns the name of the variable as defined in the generated C function."""
        if self._code_name is None:
            if self._code_elem is None:
                self._code_elem = self.get_code_elem(silent=True)
            if self._code_elem is None:
                self._code_name = "__no_name__"
            elif (
                self._code_elem["category"] == "fields"
                and self._code_elem["parent_category"] == "struct"
            ):
                # parameter is defined in struct => find the name of the corresponding parameter
                # in the function
                func = self.parent.cycle_method
                ctx_path = "__unknown__"
                for p in func.parameters:
                    if p.param_type_id == self._code_elem["parent_id"]:
                        ctx_path = p.name
                        break
                self._code_name = ctx_path + "." + self._code_elem["content"]["name"]
            else:
                self._code_name = self._code_elem["content"]["name"]
        return self._code_name

    @property
    def code_type(self) -> dict:
        """
        Returns the generated C code data corresponding to the variable type.
        ('name': C type name, 'category': type category and 'elements': sub elements of the type)
        """
        if self._code_type is None:
            if self._code_elem is None:
                self._code_elem = self.get_code_elem(silent=True)
            if self._code_elem is None:
                # no code associated to variable => it is the return of
                # the cycle function or a polymorphic param
                if self.parent.cycle_method is None:
                    self._code_type = {}
                else:
                    self._code_type = self.parent.cycle_method.return_type
                    if self._code_type is None:
                        raise ScadeOneException(
                            f"Generated code: return_type missing for CycleMethod of operator {self.parent.path}"  # noqa
                        )
            else:
                self._code_type = self._gen_code.decompose_code_type(
                    self._gen_code.get_code_elem(self._code_elem["content"]["type"])
                )
        return self._code_type


class ModelVariable(ModelVariableBase):
    """
    Class for model variables (inputs or outputs) of operator.

    - gen_code: *GeneratedCode* object
    - var_elem: mapping file element
    - parent: *ModelOperator* object of the parent operator
    """

    def __init__(self, gen_code: "GeneratedCode", var_elem: dict, parent: "ModelOperator") -> None:
        super().__init__(gen_code, var_elem)
        self._parent = parent
        self._name = var_elem["name"]
        self._projection = var_elem.get("projection", "")

    @property
    def parent(self) -> "ModelOperator":
        """Returns the model operator object owning the variable"""
        return self._parent

    @property
    def name(self) -> str:
        """Returns the variable name"""
        return self._name

    @property
    def group_items(self) -> List[Union[str, int]]:
        """Returns the group item(s) associated with variable (only applicable for group type)."""
        return self._projection

    def full_name(self, separator: str = "_") -> str:
        """
        Returns variable name taking into account group item(s) to suffix the name when applicable
        (main separator between the operator variable name and group item(s) name can be changed,
        default is '_')
        """
        group_suffix = "_".join("_" + str(i) if isinstance(i, int) else i for i in self.group_items)
        return self.name + (separator if len(self.group_items) > 0 else "") + group_suffix


class ModelVariableMonomorphic(ModelVariableBase):
    """
    Class for model variables (inputs or outputs) of monomorphic instance of operator.

    - gen_code: *GeneratedCode* object
    - var_elem: mapping file element
    - parent: *ModelMonomorphicInstance* object of the parent monomorphic instance
    """

    def __init__(
        self, gen_code: "GeneratedCode", var_elem: dict, parent: "ModelMonomorphicInstance"
    ) -> None:
        super().__init__(gen_code, var_elem)
        self._parent = parent
        self._source = None

    @property
    def parent(self) -> "ModelMonomorphicInstance":
        """Returns the model operator object owning the variable"""
        return self._parent

    @property
    def source(self) -> "ModelVariable":
        """Returns ModelVariable object source of the monomorphic instance variable."""
        if self._source is None:
            # get id of corresponding model variable
            id = self._mapping_elem.get("src", 0)
            # browse the inputs and outputs of the operator source of the instance
            for i in self.parent.source.inputs:
                if i._id == id:
                    self._source = i
                    break
            if self._source is None:
                for i in self.parent.source.outputs:
                    if i._id == id:
                        self._source = i
                        break
        return self._source


class ModelOperatorBase(ModelObject):
    """
    Base class for model operator or monomorphic instance of an operator.

    - gen_code: *GeneratedCode* object
    - oper_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", oper_elem: dict) -> None:
        super().__init__(gen_code, oper_elem)
        self._path = None
        self._inputs = None
        self._outputs = None
        self._watches = None
        self._instances = None
        self._cycle_method = None
        self._init_method = None
        self._reset_method = None

    @property
    def path(self) -> str:
        """Returns the Scade One operator path"""
        if self._path is None:
            self._path = self._mapping_elem["path"]
        return self._path

    @property
    def watches(self) -> List[dict]:
        """Returns the list of watches for the operator (as raw data, to be completed)."""
        if self._watches is None:
            self._watches = self._mapping_elem["watches"]
        return self._watches

    @property
    def instances(self) -> List[dict]:
        """Returns the list of instances for the operator (as raw data, to be completed)."""
        if self._instances is None:
            self._instances = self._mapping_elem["instances"]
        return self._instances

    @property
    def cycle_method(self) -> Optional["CFunction"]:
        """Returns the cycle method C function for the operator (as a CFunction object), if any."""
        if self._cycle_method is None:
            method_elem = self.get_code_elem("CycleMethod", silent=True)
            if method_elem is not None:
                self._cycle_method = CFunction(
                    self._gen_code, method_elem["content"], method_elem["code_index"]
                )
        return self._cycle_method

    @property
    def init_method(self) -> Optional["CFunction"]:
        """Returns the init method C function for the operator (as a CFunction object), if any."""
        if self._init_method is None:
            method_elem = self.get_code_elem("InitMethod", silent=True)
            if method_elem is not None:
                self._init_method = CFunction(
                    self._gen_code, method_elem["content"], method_elem["code_index"]
                )
        return self._init_method

    @property
    def reset_method(self) -> Optional["CFunction"]:
        """Returns the reset method C function for the operator (as a CFunction object), if any."""
        if self._reset_method is None:
            method_elem = self.get_code_elem("ResetMethod", silent=True)
            if method_elem is not None:
                self._reset_method = CFunction(
                    self._gen_code, method_elem["content"], method_elem["code_index"]
                )
        return self._reset_method


class ModelOperator(ModelOperatorBase):
    """
    Class for model operator.

    - gen_code: *GeneratedCode* object
    - oper_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", oper_elem: dict) -> None:
        super().__init__(gen_code, oper_elem)
        self._root = oper_elem.get("root", False)
        self._imported = oper_elem.get("imported", False)
        self._expanded = oper_elem.get("expanded", False)
        self._specialize = oper_elem.get("specialize", 0)

    @property
    def root(self) -> bool:
        """Returns True if the operator is a root operator"""
        return self._root

    @property
    def imported(self) -> bool:
        """Returns True if the operator is an imported operator"""
        return self._imported

    @property
    def expanded(self) -> bool:
        """Returns True if the operator is expanded (inlined)"""
        return self._expanded

    @property
    def specialize(self) -> bool:
        """Returns True if the operator is specialized"""
        return self._specialize

    @property
    def inputs(self) -> List[ModelVariable]:
        """Returns the list of inputs for the operator (as ModelVariable objects)."""
        if self._inputs is None:
            self._inputs = [
                ModelVariable(self._gen_code, x, self) for x in self._mapping_elem.get("inputs", [])
            ]
        return self._inputs

    @property
    def outputs(self) -> List[ModelVariable]:
        """Returns the list of outputs for the operator (as ModelVariable objects)."""
        if self._outputs is None:
            self._outputs = [
                ModelVariable(self._gen_code, x, self)
                for x in self._mapping_elem.get("outputs", [])
            ]
        return self._outputs


class ModelMonomorphicInstance(ModelOperatorBase):
    """
    Class for monomorphic instance of polymorphic model operator.

    - gen_code: *GeneratedCode* object
    - oper_elem: mapping file element
    """

    def __init__(self, gen_code: "GeneratedCode", oper_elem: dict) -> None:
        super().__init__(gen_code, oper_elem)
        self._source = None
        self._type_parameters = oper_elem.get("type_parameters", [])
        self._size_parameters = oper_elem.get("size_parameters", [])

    @property
    def source(self) -> "ModelOperator":
        """Returns ModelOperator object source of the monomorphic instance."""
        if self._source is None:
            id = self._mapping_elem.get("src", 0)
            try:
                _, op_elem = next(
                    i for i in self._gen_code.get_model_elements("operator") if i[1]["id"] == id
                )
                self._source = ModelOperator(self._gen_code, op_elem)
            except StopIteration:
                raise ScadeOneException(
                    f"Generated code: can't find source operator (id: {id}) for {self.path}"
                )
        return self._source

    @property
    def inputs(self) -> List[ModelVariableMonomorphic]:
        """Returns the list of inputs for the operator (as ModelVariableMonomorphic objects)."""
        if self._inputs is None:
            self._inputs = [
                ModelVariableMonomorphic(self._gen_code, x, self)
                for x in self._mapping_elem.get("inputs", [])
            ]
        return self._inputs

    @property
    def outputs(self) -> List[ModelVariableMonomorphic]:
        """Returns the list of outputs for the operator (as ModelVariableMonomorphic objects)."""
        if self._outputs is None:
            self._outputs = [
                ModelVariableMonomorphic(self._gen_code, x, self)
                for x in self._mapping_elem.get("outputs", [])
            ]
        return self._outputs


class GeneratedCode(object):
    """
    Generated code main class.

    Parameters
    ----------
    project: Project
        Current project.

    job_name: str
        Code generation name.
    """

    def __init__(self, project: Project, job_name: str) -> None:
        self._project = project
        self._job_name = job_name
        self._mapping = None
        self._generated_code_dir = None
        self._root_operators = []
        self._job_path = Path("")
        self._mapping_path = Path("")
        self._parse_job()

    def _parse_job(self) -> None:
        # Check and retrieve job path.
        found_job = None
        for job in self._project.directory.glob("jobs/*/.sjob"):
            with open(job) as f:
                jj = json.load(f)
                if (
                    "Properties" in jj
                    and jj.get("Kind", "") == "CodeGeneration"
                    and self._job_name == jj["Properties"].get("Name", "__not_found__")
                ):
                    self._root_operators = jj["Properties"].get("RootDeclarations", [])
                    found_job = job
                    break
        if found_job is None:
            raise ScadeOneException(
                f'Generated code: no CodeGeneration kind job named "{self._job_name}"'
            )
        self._job_path = found_job
        self._mapping_path = self._job_path.parent / "out" / "cg_map.json"

    def _load_mapping(self) -> None:
        # According to job, loads the mapping file as a dictionary.
        if self.job_path is not None:
            if not self.is_code_generated:
                raise ScadeOneException(
                    f"Generated code: code is not generated for job {self._job_name}"
                )
            try:
                with open(self._mapping_path) as f:
                    self._mapping = json.load(f)
                    self._generated_code_dir = self._mapping_path.parent / "code"
            except Exception:
                raise ScadeOneException(
                    "Generated code: cannot open mapping file"
                    + f" ({self._mapping_path.name}) for job {self._job_name}"
                )

    @property
    def job_path(self) -> Path:
        # Returns job path.
        return self._job_path

    @property
    def mapping(self) -> dict:
        """Returns the mapping file as a dictionary."""
        if self._mapping is None:
            self._load_mapping()
        return self._mapping

    @property
    def generated_code_dir(self) -> str:
        """Returns the generated code directory path name."""
        if self._generated_code_dir is None:
            self._load_mapping()
        return self._generated_code_dir

    @property
    def root_operators(self) -> List[str]:
        """Returns the list of root operators names."""
        return self._root_operators

    @property
    def code(self) -> List[dict]:
        """Returns the 'code' data section."""
        return self.mapping["code"]

    @property
    def is_code_generated(self) -> bool:
        """Returns True if the code is generated for the job."""
        return self._mapping_path.exists()

    def decompose_code_type(self, ctype: dict) -> dict:
        """
        Returns (as a dictionary) the C type name, category (array, struct, enum, union, typedef,
        predefined_type) and sub elements of a given type element.

        The sub elements depends on the category:

        - For an array, it is a dictionary with base_type giving the type data of the element
          (same format as this method) and size giving the size of the array.
        - For a struct, it is a list of dictionaries, with name giving the field name,
          type giving the field type data (same format as this method), pointer indicating if field
          is a pointer type and size giving optional list of integer or constant names.
        - For an enum, it is a dictionary with tag_name giving internal tag name for the enum,
          and values giving the list of names corresponding to the enum values.
        - For a union, it is a list of dictionaries, with name giving the variant field name,
          type giving the variant field type data (same format as this method)
          and enum_value giving optional integer value.
        - For a typedef (imported type), it is the function names used to manipulate
          the imported type.
        - For a predefined_type, it is None.

        """
        category = ctype.get("category", "")
        content = ctype.get("content", {})
        if category == "array":
            type_elem = self.decompose_code_type(self.get_code_elem(content.get("base_type", -1)))
            type_content = {"base_type": type_elem, "size": content.get("size", 0)}
        elif category == "struct":
            type_content = []
            for e in content.get("fields", []):
                type_content.append(
                    {
                        "name": e["name"],
                        "type": self.decompose_code_type(self.get_code_elem(e["type"])),
                        "pointer": e["pointer"],
                        "size": e.get("size", []),
                    }
                )
        elif category == "enum":
            elems = []
            for e in content.get("values", []):
                elems.append(e["name"])
            type_content = {"tag_name": content.get("tag_name", ""), "values": elems}
        elif category == "union":
            type_content = []
            for e in content.get("variants", []):
                type_content.append(
                    {
                        "name": e["name"],
                        "type": self.decompose_code_type(self.get_code_elem(e["type"])),
                        "enum_value": e["enum_value"],
                    }
                )
        elif category == "typedef":
            # typedef is used for imported types
            # check that the 3 functions/macros are present: init, cp, eq
            type_content = []
        elif category == "predefined_type":
            type_content = None
        else:
            type_content = content

        return {"name": content.get("name", ""), "category": category, "elements": type_content}

    def get_code_elem(self, code_id: int) -> dict:
        """
        Returns (as a dictionary) the code data corresponding to given code identifier.

        - code_index: position of the element in the code section list
        - parent_category: category (declarations, function, struct, enum, union) of the parent
          code element
        - parent_name: name of the parent code element
        - parent_id: code identifier of the parent code element
        - category: category (declarations, function, struct, enum, union) of the code element
        - content: data content (the element itself)
        - index: position of the element in the declaration
        """

        def _parse_sub_elem(parent: CodeElem, ename: str) -> dict:
            for e in parent[1].get(ename, []):
                if e["id"] == code_id:
                    return {
                        "code_index": code_idx,
                        "parent_category": parent[0],
                        "parent_name": d[1]["name"],
                        "parent_id": d[1]["id"],
                        "category": ename,
                        "content": e,
                        "index": idx,
                    }
            return {}

        for code_idx, cont in enumerate(self.code):
            for idx, d in enumerate(cont.get("declarations", [])):
                if d[1]["id"] == code_id:
                    return {
                        "code_index": code_idx,
                        "parent_category": "declarations",
                        "parent_name": "",
                        "parent_id": -1,
                        "category": d[0],
                        "content": d[1],
                        "index": idx,
                    }
                sub = {}
                if d[0] == "function":
                    sub = _parse_sub_elem(d, "parameters")
                elif d[0] == "struct":
                    sub = _parse_sub_elem(d, "fields")
                elif d[0] == "enum":
                    sub = _parse_sub_elem(d, "values")
                elif d[0] == "union":
                    sub = _parse_sub_elem(d, "variants")
                if len(sub):
                    return sub
        return {}

    def get_code_id(self, model_id: int, role: str = "", silent: bool = False) -> int:
        """
        Returns the code identifier associated to a given model identifier for a given *role*.

        If *silent* is set to True, the functions returns -1 in case no code is found. Otherwise,
        exception is raised.
        """
        xx = (x[0] for x in self.get_code_ids(model_id) if x[1] == role)
        try:
            return next(xx)
        except StopIteration:
            if silent:
                return -1
            else:
                role_str = f"for role {role}" if role != "" else "without role"
                raise ScadeOneException(
                    f"Generated code: no code id associated to model id #{model_id} {role_str}"
                )

    def get_code_ids(self, model_id: int) -> Generator[Tuple[int, str], None, None]:
        """
        Returns the list of code identifiers associated to a given model identifier
        (as a Generator of code, role tuples).
        """
        return (
            (x["code_id"], x.get("role", ""))
            for x in self.mapping["mapping"]
            if x["model_id"] == model_id
        )

    def get_model_elements(self, filter: str = "") -> Generator[MapElem, None, None]:
        """
        Returns the list of model elements defined in the mapping file
        (as a Generator of MapElem objects).

        If *filter* is set, returns only the elements of the given category
        (elaboration, predefined_type, array, struct, enum, variant, named_type, sensor,
        operator, mono).
        """
        return (y for y in self.mapping["model"] if filter == "" or filter == y[0])

    @functools.cache
    def get_model_monomorphic_instance(self, name: str) -> ModelMonomorphicInstance:
        """Returns the *ModelMonomorphicInstance* object corresponding
        to given operator path name."""
        try:
            op_kind, op_elem = next(
                i for i in self.get_model_elements("mono") if i[1]["path"] == name
            )
            return ModelMonomorphicInstance(self, op_elem)
        except StopIteration:
            raise ScadeOneException(f"Generated code: no monomorphic instance named {name}")

    @functools.cache
    def get_model_monomorphic_instances(self) -> List[ModelMonomorphicInstance]:
        """Returns the list of *ModelMonomorphicInstance* objects for the mapping file."""
        oper_list = []
        for _, op_elem in self.get_model_elements("mono"):
            oper_list.append(ModelMonomorphicInstance(self, op_elem))
        return oper_list

    @functools.cache
    def get_model_operator(self, name: str) -> ModelOperator:
        """Returns the *ModelOperator* object corresponding to given operator path name."""
        try:
            _, op_elem = next(
                i for i in self.get_model_elements("operator") if i[1]["path"] == name
            )
            return ModelOperator(self, op_elem)
        except StopIteration:
            raise ScadeOneException(f"Generated code: no operator named {name}")

    @functools.cache
    def get_model_operators(self) -> List[ModelOperator]:
        """Returns the list of *ModelOperator* objects for the mapping file."""
        oper_list = []
        for op_kind, op_elem in self.get_model_elements("operator"):
            oper_list.append(ModelOperator(self, op_elem))
        return oper_list

    @functools.cache
    def get_model_sensor(self, name: str) -> ModelSensor:
        """Returns the *ModelSensor* object corresponding to given sensor path name."""
        try:
            _, sensor_elem = next(
                i for i in self.get_model_elements("sensor") if i[1]["path"] == name
            )
            return ModelSensor(self, sensor_elem)
        except StopIteration:
            raise ScadeOneException(f"Generated code: no sensor named {name}")

    @functools.cache
    def get_model_sensors(self) -> List[ModelSensor]:
        """Returns the list of *ModelSensor* objects for the mapping file."""
        sensor_list = []
        for _, sensor_elem in self.get_model_elements("sensor"):
            sensor_list.append(ModelSensor(self, sensor_elem))
        return sensor_list
