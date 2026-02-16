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

# This module is used to create an FMI 2.0 co-simulation or model-exchange FMU
# from a Scade One model.
# The discrete operator is executed periodically.
#
# It generates C file needed by the runtime
# and the XML description of the FMU (modelDescription.xml).
# The FMU can then be created by compiling all source files with the corresponding runtime
# into a DLL and then packing it with the generated modelDescription.xml file.

# cSpell: ignore elems oper codegen mvars outdir newl addindent lshlwapi

import platform
from abc import ABC, abstractmethod
import os
from pathlib import Path
import re
import shutil
from typing import List, Optional, Tuple, Union
import uuid
import xml.dom.minidom as D
import zipfile

import jinja2

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER

from ansys.scadeone.core.project import Project
import ansys.scadeone.core.svc.generated_code as GC

from ansys.scadeone.core.svc.build_system import (
    BuildConfig,
    BuildSystem,
    Target,
    TargetKind,
)

script_dir = Path(__file__).parent

CYCLE_FUNCTION_RETURN = "cycle_function_return"


class ModelVar:
    """
    Class representing a scalar component of a variable appearing
    in the interface of the FMU.

    Parameters
    ----------
    fmu : FMU_Export
        The FMU export object.
    sc_path : str
        The Scade One path.
    c_path : str
        The generated C code path.
    type_elem : dict
        The type of the variable.
    var_kind : str
        The kind of variable: 'input', 'output' or 'sensor'.
    """

    def __init__(
        self, fmu: "FMU_Export", sc_path: str, c_path: str, type_elem: dict, var_kind: str
    ) -> None:
        self._fmu = fmu
        self._c_path = c_path
        self._sc_path = sc_path
        self._type_elem = type_elem
        self._var_kind = var_kind
        self._type_kind = None
        self._xml_description = None
        self._xml_name = None
        self._direction = None

    @property
    def direction(self) -> str:
        """Return the direction ('input' or 'output') of the variable"""
        if self._direction is None:
            self._direction = "output" if self._var_kind == "output" else "input"
        return self._direction

    @property
    def type_name(self) -> str:
        """Return the generated type name of the variable"""
        return self._type_elem["name"]

    @property
    def type_kind(self) -> str:
        """Return the name of the FMU type corresponding to generated type of a given variable."""

        def fmu_ty_of_scade_ty(ty: dict) -> str:
            type_name = ty["name"]
            category = ty["category"]

            if category == "predefined_type":
                if type_name in ("swan_float32", "swan_float64"):
                    fmu_ty = "Real"
                elif type_name in (
                    "swan_int8",
                    "swan_int16",
                    "swan_int32",
                    "swan_int64",
                    "swan_uint8",
                    "swan_uint16",
                    "swan_uint32",
                    "swan_uint64",
                    "swan_char",
                    "swan_size",
                ):
                    fmu_ty = "Integer"
                elif type_name == "swan_bool":
                    fmu_ty = "Boolean"
                else:
                    raise ScadeOneException(
                        f"FMU_Export: Variable {self._sc_path} of type {type_name}: "
                        f"type not supported"
                    )
            elif category == "enum":
                fmu_ty = "Integer"
            elif category == "imported_type":
                raise ScadeOneException(
                    f"FMU_Export: Variable {self._sc_path} of type {type_name}: "
                    f"imported types are not supported"
                )
            else:
                raise ScadeOneException(
                    f"FMU_Export: Variable {self._sc_path} of type {type_name}: "
                    f"category {category} is not supported"  # noqa
                )
            return fmu_ty

        if self._type_kind is None:
            self._type_kind = fmu_ty_of_scade_ty(self._type_elem)
        return self._type_kind

    @property
    def oper_path(self) -> str:
        """Return the Scade One path for the exported operator owning the variable."""
        return self._fmu.oper_path + "/"

    @property
    def xml_description(self) -> str:
        """Return the description of the variable used by the FMI model description"""
        if self._xml_description is None:
            if self._var_kind == "sensor":
                self._xml_description = self._sc_path
            else:
                self._xml_description = self.oper_path + self._sc_path
        return self._xml_description

    @property
    def xml_name(self) -> str:
        """Return the name of the variable used by the FMI model description"""

        def _replace_brackets(match):
            # Find all digits in the match and join them with commas
            numbers = re.findall(r"\d+", match.group(0))
            return f"[{','.join(numbers)}]"

        if self._xml_name is None:
            if self._var_kind == "sensor":
                self._xml_name = self._c_path
            else:
                self._xml_name = self._sc_path
            # update multidimensional arrays representation: [i][j] => [i,j]
            self._xml_name = re.sub(r"(\[\d+]){2,}", _replace_brackets, self._xml_name)
        return self._xml_name

    def get_default_value(self, xml=True) -> str:
        """
        Return the default value corresponding to FMU type of a given variable.
        Expected types are 'Real', 'Integer' and 'Boolean'.

        Parameters
        ----------
        xml : bool, optional
            If True (default) the returned value is adapted to be used in the XML
            description of the FMU, otherwise it is adapted to be used in C code.

        Returns
        -------
        str
            The default value as a string.
        """
        if self.type_kind == "Real":
            return "0.0"
        elif self.type_kind == "Integer":
            return "0"
        elif xml:
            return "false"
        else:
            return "fmi2False"

    @staticmethod
    def paths_of_param(sc_path: str, c_path: str, code_type: dict) -> List[Tuple[str, str, dict]]:
        """
        Return the list of paths of scalar variables corresponding
        to the variable named `name` of type `ty` (of type `mapping.C.Type`).

        Parameters
        ----------
        sc_path : str
            The Scade One path.
        c_path : str
            The generated C code path.
        code_type : dict
            The type of the variable.

        Returns
        -------
        List[Tuple[str, str, dict]]
            The list of tuples (scade_path, code_path, type) for each scalar variable.
        """
        var_list = []

        if not code_type or "category" not in code_type:
            pass
        elif code_type["category"] == "array":
            base_type = code_type["elements"]["base_type"]
            for i in range(0, code_type["elements"]["size"]):
                var_list.extend(
                    ModelVar.paths_of_param(f"{sc_path}[{i}]", f"{c_path}[{i}]", base_type)
                )
        elif code_type["category"] == "struct":
            for f in code_type["elements"]:
                var_list.extend(
                    ModelVar.paths_of_param(
                        f"{sc_path}.{f['name']}", f"{c_path}.{f['name']}", f["type"]
                    )
                )
        elif code_type["category"] == "union":
            for f in code_type["elements"]:
                var_list.extend(
                    ModelVar.paths_of_param(
                        f"{sc_path}.{f['name']}", f"{c_path}.{f['name']}", f["type"]
                    )
                )
        else:
            var_list.append((sc_path, c_path, code_type))
        return var_list

    @staticmethod
    def model_vars_of_param(
        fmu: "FMU_Export", v: Union[GC.ModelVariable, GC.ModelSensor], var_kind: str
    ) -> List["ModelVar"]:
        """
        Return the list of variables corresponding
        to the given model variable (input or output) or sensor.

        Parameters
        ----------
        fmu : FMU_Export
            The FMU export object.
        v : Union[GC.ModelVariable, GC.ModelSensor]
            The model variable or sensor.
        var_kind : str
            The kind of variable: 'input', 'output' or 'sensor'.

        Returns
        -------
        List["ModelVar"]
            The list of model variables corresponding to the input variable.
        """
        if isinstance(v, GC.ModelVariable):
            sc_path = v.full_name(".")
        else:
            sc_path = v.path
        c_path = v.code_name
        if c_path == "__no_name__":
            # output of cycle function
            c_path = CYCLE_FUNCTION_RETURN
        code_type = v.code_type
        paths = ModelVar.paths_of_param(sc_path, c_path, code_type)
        return [ModelVar(fmu, sc_path, c_path, ty, var_kind) for sc_path, c_path, ty in paths]

    def append_xml(self, parent: D.Element) -> None:
        """
        Adds the XML element describing this model variable in FMI 2.0
        as a child of `parent`.

        Parameters
        ----------
        parent : D.Element
            The parent XML element.
        """
        d = self._fmu.create_xml_child("ScalarVariable", parent)
        d.setAttribute("causality", self.direction)
        d.setAttribute("description", self.xml_description)
        d.setAttribute("name", self.xml_name)
        fmu_ty = self.type_kind
        d.setAttribute("valueReference", self._fmu.get_next_value_reference(fmu_ty))
        if fmu_ty == "Real":
            d.setAttribute("variability", "continuous")
        else:
            d.setAttribute("variability", "discrete")
        if self.direction == "output":
            d.setAttribute("initial", "calculated")
        ty = self._fmu.create_xml_child(fmu_ty, d)
        if self.direction == "input":
            ty.setAttribute("start", self.get_default_value())

    def get_context_path(self, fmu_type: str = "") -> str:
        """
        Returns the C expression computing the offset of this model variable
        in the runtime state.

        Parameters
        ----------
        fmu_type : str, optional
            The FMU type of the variable.
            If provided the expression is casted to this type (default is no cast).

        Returns
        -------
        str
            A C expression string.
        """
        cast = "" if fmu_type == "" else f"(fmi2{fmu_type})"
        path = "" if self._var_kind == "sensor" else "comp->context->"
        return f"{cast}{path}{self._c_path}"


class FMU_Export(ABC):
    """
    FMU export main base class.

    Parameters
    ----------
    prj : Project
        The Scade One project.
    job_name : str
        The name of the code generation job for the operator to be exported as an FMU.
    oper_name : str, optional
        Optional operator name (by default it is the root operator of the job if it is
    unique, if provided it has to be a root operator for the job).
    """

    def __init__(self, prj: Project, job_name: str, oper_name: str = "") -> None:
        if prj is None:
            raise ScadeOneException("FMU_Export: Valid Scade One project is expected.")
        self._project = prj
        self.root_operator = oper_name
        # get generated code data
        self.codegen = GC.GeneratedCode(
            prj, job_name
        )  #: Associated :py:class:`GeneratedCode` object.

        if oper_name != "":
            if oper_name not in self.codegen.root_operators:
                raise ScadeOneException(
                    f"FMU_Export: No root operator named {oper_name} for selected job {job_name}."
                )
        elif len(self.codegen.root_operators) != 1:
            raise ScadeOneException(
                f"FMU_Export: The job {job_name} has several root operators."
                " Use parameter 'oper_name' to select one."
            )
        else:
            self.root_operator = self.codegen.root_operators[0]

        # initialize generator state
        self.out_dir = Path("")
        self.uuid = None
        self.default_period = 0.0
        self.fmu_xml_file = Path("")
        self.fmu_c_file = Path("")
        self._value_ref_counter = {}
        self._kind_cs = False
        self._source_dir = Path("")
        self._start_dir = Path.cwd()
        self._generate_ok = False
        self._job_name = job_name
        self._doc = None
        self._oper = None
        self._sensors = None
        # populate model variables
        self._mvars = []

    @property
    def oper(self) -> GC.ModelOperator:
        """Return the *ModelOperator* object."""
        if self._oper is None:
            self._oper = self.codegen.get_model_operator(self.root_operator)
            if not isinstance(self._oper, GC.ModelOperator):
                raise ScadeOneException(
                    f"FMU_Export: Operator {self.root_operator} cannot be monomorphic."
                )

        return self._oper

    @property
    def oper_path(self) -> str:
        """Returns the Scade One path for the operator exported as FMU."""
        return self.oper.path

    @property
    def model_id(self) -> str:
        """Returns the name identifier of the operator exported as FMU."""
        return self.root_operator.replace("::", "_")

    @property
    def sensors(self) -> List[GC.ModelSensor]:
        """Return the *ModelSensor* objects."""
        if self._sensors is None:
            self._sensors = self.codegen.get_model_sensors()
        return self._sensors

    @property
    def elaboration_function(self) -> Optional[GC.CFunction]:
        """Return the elaboration function of the operator."""
        return self.codegen.get_elaboration_function()

    def create_xml_child(self, name: str, parent: D.Node) -> D.Element:
        """Create an XML child element."""
        d = self._doc.createElement(name)
        parent.appendChild(d)
        return d

    def get_next_value_reference(self, fmu_ty: str) -> str:
        """Get the next value reference for a given fmu type.

        Parameters
        ----------
        fmu_ty : str
            The FMU type.

        Returns
        -------
        str
            The next value reference as a string.
        """
        if fmu_ty in self._value_ref_counter:
            self._value_ref_counter[fmu_ty] += 1
        else:
            self._value_ref_counter[fmu_ty] = 0
        return str(self._value_ref_counter[fmu_ty])

    def _add_period_var(self, parent: D.Node) -> None:
        """
        Adds the period variable to the list of variables in the XML description.

        Parameters
        ----------
        parent : D.Node
            The parent XML element.
        """
        d = self.create_xml_child("ScalarVariable", parent)
        d.setAttribute("causality", "parameter")
        d.setAttribute("description", "Period")
        d.setAttribute("name", "period")
        d.setAttribute("valueReference", self.get_next_value_reference("Real"))
        d.setAttribute("variability", "fixed")
        ty = self.create_xml_child("Real", d)
        ty.setAttribute("start", str(self.default_period))

    @abstractmethod
    def generate(self, kind: str, outdir: str, period: float = 0.02):
        """
        Generate the FMI 2.0 XML and C file according to SCADE generated code.

        Parameters
        ----------
        kind : str
            The type of generation (e.g., 'model-exchange' or 'co-simulation').
        outdir : str
            The output directory for the generated files.
        period : float, optional
            The time period for the simulation, by default 0.02

        Raises
        ------
        ScadeOneException
            If the generation process fails due to invalid parameters or execution errors.
        """
        raise ScadeOneException("abstract method call")

    @abstractmethod
    def build(self, with_sources: bool = False, args: Optional[dict] = None):
        """
        Build the FMU system from the generated files.

        Parameters
        ----------
        with_sources : bool, optional
            Whether to include source files in the build, by default False
        args : Optional[dict], optional
            Additional arguments for the build process, by default None

        Raises
        ------
        ScadeOneException
            If the build process fails due to invalid parameters or execution errors.
        """
        raise ScadeOneException("abstract method call")


class FMU_2_Export(FMU_Export):
    """
    FMU 2.0 export main class.

    Parameters
    ----------
    prj : Project
        The Scade One project.
    job_name : str
        The name of the code generation job for the operator to be exported as an FMU.
    oper_name : str, optional
        Optional operator name (by default it is the root operator of the job,\
     if provided it has to be a root operator for the job).
    max_variables : int, optional
        Maximum number on FMI variables (flattened sensors, inputs and outputs) \
     supported by the export (1000 by default).
    """

    def __init__(
        self, prj: Project, job_name: str, oper_name: str = "", max_variables: int = 1000
    ) -> None:
        super().__init__(prj, job_name, oper_name)
        self.max_variables = max_variables

    def _generate_xml(self) -> None:
        """Generates the modelDescription.xml file describing the FMU."""
        self.fmu_xml_file = self.out_dir / "modelDescription.xml"
        LOGGER.info(f" - FMI XML description: {self.fmu_xml_file}")
        self._doc = D.Document()
        # generate root element
        root = self.create_xml_child("fmiModelDescription", self._doc)
        root.setAttribute("fmiVersion", "2.0")
        root.setAttribute("generationTool", "ScadeOne")
        self.uuid = str(uuid.uuid1())
        root.setAttribute("guid", self.uuid)
        root.setAttribute("modelName", self.model_id)
        root.setAttribute("numberOfEventIndicators", "0")
        root.setAttribute("variableNamingConvention", "structured")

        # add part specific to FMU kind
        self._add_fmu_element(root)
        # print model variables
        model_vars = self.create_xml_child("ModelVariables", root)
        for mv in self._mvars:
            mv.append_xml(model_vars)
        self._add_period_var(model_vars)
        # print model structure
        struct = self.create_xml_child("ModelStructure", root)
        # Outputs and InitialUnknowns
        outs = None
        init = None
        var_index = 0
        for mv in self._mvars:
            var_index += 1
            if mv.direction == "output":
                # Outputs
                if outs is None:
                    outs = self.create_xml_child("Outputs", struct)
                do = self.create_xml_child("Unknown", outs)
                do.setAttribute("index", str(var_index))
                outs.appendChild(do)
                # InitialUnknowns
                if init is None:
                    init = self.create_xml_child("InitialUnknowns", struct)
                di = self.create_xml_child("Unknown", init)
                di.setAttribute("index", str(var_index))
                init.appendChild(di)
        # write to file
        with self.fmu_xml_file.open("w") as fd:
            self._doc.writexml(fd, encoding="UTF-8", indent="", addindent="  ", newl="\n")

    def _add_fmu_element(self, root: D.Node) -> None:
        """
        Adds as a child of root the XML element describing
        the FMU kind (model-exchange or co-simulation).

        Parameters
        ----------
        root : D.Node
            The root XML element.
        """
        if self._kind_cs:
            d = self.create_xml_child("CoSimulation", root)
            d.setAttribute("modelIdentifier", self.model_id)
            d.setAttribute("canHandleVariableCommunicationStepSize", "true")
        else:
            d = self.create_xml_child("ModelExchange", root)
            d.setAttribute("modelIdentifier", self.model_id)

    def _generate_var_infos(self, var_type: str) -> Tuple[str, str]:
        """
        Generate variable access for FMI getter/setter C functions.

        Parameters
        ----------
        var_type : str
            A variable type.

        Returns
        -------
        Tuple[str, str]
            A tuple containing the C statements for the setter and getter functions.
        """
        idx = 0
        stmts_set = []
        stmts_get = []
        for mv in self._mvars:
            fmu_ty = mv.type_kind
            if fmu_ty == var_type:
                stmts_set.append(
                    "case {tag}: {var} = ({type}) value[i]; break;".format(
                        tag=idx, var=mv.get_context_path(), type=mv.type_name
                    )
                )
                stmts_get.append(
                    "case {tag}: value[i] = {expr}; break;".format(
                        tag=idx, expr=mv.get_context_path(fmu_ty)
                    )
                )
                idx = idx + 1

        if var_type == "Real":
            stmts_set.append(f"case {idx}: comp->period = value[i]; break;")
            stmts_get.append(f"case {idx}: value[i] = comp->period; break;")

        return "\n".join(stmts_set), "\n".join(stmts_get)

    def _generate_var_init(self) -> str:
        """
        Generates variable initialization C statements.

        Returns
        -------
        str
            The C statements as a string.
        """
        stmts_init = []
        for mv in self._mvars:
            stmts_init.append(
                "{var} = ({type}){expr};".format(
                    var=mv.get_context_path(),
                    type=mv.type_name,
                    expr=mv.get_default_value(xml=False),
                )
            )

        stmts_init.append(f"comp->period = {self.default_period};")

        return "\n".join(stmts_init)

    def _generate_fmu_wrapper(self) -> None:
        """Generates the FMU wrapper C file from template."""
        self._source_dir = self.out_dir / "sources"

        if self._source_dir.exists():
            shutil.rmtree(self._source_dir)
        self._source_dir.mkdir()

        out_c_file = self.model_id + "_FMU.c"
        self.fmu_c_file = self._source_dir / out_c_file
        LOGGER.info(f" - FMI C wrapper: {self.fmu_c_file}")

        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(script_dir / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("FMI_v2.0_template.j2")

        cycle_function = self.oper.cycle_method
        init_function = self.oper.init_method
        reset_function = self.oper.reset_method

        include_files = [cycle_function.get_interface_file(), "swan_consts.h", "swan_sensors.h"]

        if self.elaboration_function:
            include_files.append(self.elaboration_function.get_interface_file())

        includes = "\n".join(f'#include "{f}"' for f in include_files)

        fmi_set_real, fmi_get_real = self._generate_var_infos("Real")
        fmi_set_integer, fmi_get_integer = self._generate_var_infos("Integer")
        fmi_set_boolean, fmi_get_boolean = self._generate_var_infos("Boolean")

        scade_context = f"SCADE_{self.model_id}"

        return_type = cycle_function.return_type

        ctx_params = []
        for param in cycle_function.parameters:
            ctx_params.append(f"{param.type_name} {param.name};")
        if return_type is not None:
            ctx_params.append(f"{return_type['name']} {CYCLE_FUNCTION_RETURN};")

        # add sensors as global variables if any
        if len(self.sensors):
            sensors = "\n\n/* Sensors */"
            for s in self.sensors:
                sensors += f"\n{s.code_type_name} {s.code_name};"
        else:
            sensors = ""

        define_scade_context = """
typedef struct {{
    {fields}
}} {context};{sensors}
""".format(fields="\n    ".join(ctx_params), context=scade_context, sensors=sensors).strip()

        define_state_vector = "#define STATE_VECTOR_SIZE 0"

        if init_function is not None or reset_function is not None:
            if init_function is not None:
                call_params = []
                for param in init_function.parameters:
                    access = "&" if param.is_pointer else ""
                    call_params.append(f"{access}comp->context->{param.name}")
                call_init = f"{init_function.name}({', '.join(call_params)});"
            else:
                call_init = ""
            if reset_function is not None:
                call_params = []
                for param in reset_function.parameters:
                    access = "&" if param.is_pointer else ""
                    call_params.append(f"{access}comp->context->{param.name}")
                call_reset = f"{reset_function.name}({', '.join(call_params)});"
            else:
                call_reset = ""

            init_context = (
                f"""
#ifndef SWAN_USER_DEFINED_INIT
        {call_init}
#else
#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
        {call_reset}
#endif
#endif
"""
            ).strip()
        else:
            init_context = "/* no context to initialize */"

        call_params = []
        for param in cycle_function.parameters:
            access = "&" if param.is_pointer else ""
            cast = f"({param.signature})" if param.is_const else ""
            call_params.append(f"{cast}{access}comp->context->{param.name}")

        if return_type is not None:
            # the output is returned by the function
            call_cycle_return = f"comp->context->{CYCLE_FUNCTION_RETURN} = "
        else:
            call_cycle_return = ""

        call_cycle = "{assign}{function}({args});".format(
            assign=call_cycle_return,
            function=cycle_function.name,
            args=", ".join(call_params),
        )

        if self.elaboration_function:
            call_elaborate = f"{self.elaboration_function.name}();"
        else:
            call_elaborate = ""

        rendering_context = {
            "FMI_KIND_CS": self._kind_cs,
            "FMI_USE_DBG_LOGS": 0,
            "FMI_FILE_NAME": out_c_file,
            "FMI_INCLUDES": includes,
            "FMI_DEFINE_SCADE_CONTEXT": define_scade_context,
            "FMI_SCADE_CONTEXT": scade_context,
            "FMI_SCADE_CONTEXT_SIZE": f"sizeof({scade_context})",
            "FMI_DEFINE_STATE_VECTOR": define_state_vector,
            "FMI_MODEL_IDENTIFIER": self.model_id + "_FMU",
            "FMI_MODEL_GUID": self.uuid,
            "FMI_TASK_PERIOD": self.default_period,
            "FMI_NB_REALS": self._value_ref_counter.get("Real", -1) + 1,
            "FMI_NB_INTEGERS": self._value_ref_counter.get("Integer", -1) + 1,
            "FMI_NB_BOOLEANS": self._value_ref_counter.get("Boolean", -1) + 1,
            "FMI_GET_REAL": fmi_get_real,
            "FMI_GET_INTEGER": fmi_get_integer,
            "FMI_GET_BOOLEAN": fmi_get_boolean,
            "FMI_GET_STATES_FUNC_DECL": "/* get state decl: N/A */",
            "FMI_SET_REAL": fmi_set_real,
            "FMI_SET_INTEGER": fmi_set_integer,
            "FMI_SET_BOOLEAN": fmi_set_boolean,
            "FMI_SET_STATES_FUNC_DECL": "/* set state decl: N/A */",
            "FMI_INIT_VALUES": self._generate_var_init(),
            "FMI_INIT_CONTEXT": init_context,
            "FMI_CALL_ELABORATE": call_elaborate,
            "FMI_CALL_CYCLE": call_cycle,
            "FMI_GET_FMU_STATE_FUNC": "/* get state not implemented */",
            "FMI_SET_FMU_STATE_FUNC": "/* set state not implemented */",
            "FMI_ROOT_OP_NAME": self.model_id,
        }
        content = template.render(rendering_context)

        with open(self.fmu_c_file, mode="w", encoding="utf-8") as out:
            out.write(content)

    def _collect_source_files(self) -> None:
        """
        Collect the source files (.c and .h) from the generated code directory
        and copy them in source directory.
        """

        gen_dir = Path(self.codegen.generated_code_dir)
        if not gen_dir.exists() or not any(gen_dir.iterdir()):
            raise ScadeOneException(
                f"FMU export: job {self._job_name}:"
                f" generated code is missing under '{gen_dir.name}' sub-directory."
            )

        generated_files = [f for f in gen_dir.iterdir() if f.suffix in {".c", ".h"}]
        if not generated_files:
            raise ScadeOneException(
                f"FMU Export: No .c or .h files found in the generated code directory '{gen_dir}'."
            )

        for f in generated_files:
            shutil.copy(Path(gen_dir) / f.name, self._source_dir)

        LOGGER.debug(f"Collected generated files: {[str(f) for f in generated_files]}")

    @staticmethod
    def _collect_user_source_files(user_sources: List[Union[str, Path]]) -> List[Path]:
        """
        Collect user source files (.c and .h) from the provided directories or files.

        Parameters
        ----------
        user_sources : List[Union[str, Path]]
            A list of user source directories or files.

        Returns
        -------
        List[Path]
            A list of paths to the collected user source files.
        """

        collected_files = []

        for src in user_sources:
            src_path = Path(src)
            if src_path.is_dir():
                LOGGER.debug(f"Collecting user source files from directory: {src_path}")
                collected_files.extend(
                    [f.resolve(strict=True) for f in src_path.iterdir() if f.suffix in {".c", ".h"}]
                )
            elif src_path.is_file() and src_path.suffix in {".c", ".h"}:
                LOGGER.debug(f"Collecting user source file: {src_path}")
                collected_files.append(src_path.resolve(strict=True))
            else:
                LOGGER.debug(f"User source {src} is not a valid file or directory.")

        if not collected_files:
            LOGGER.debug("No valid user source files (.c or .h) were found.")
        else:
            LOGGER.debug(f"Collected user source files: {[str(f) for f in collected_files]}")
        return collected_files

    @staticmethod
    def _copy_fmi_folder(dest_dir: Path) -> None:
        """
        Copy the FMI folder to the specified destination directory.

        Parameters
        ----------
        dest_dir : Path
            The destination directory where the FMI folder will be copied.
        """

        fmi_dir = Path(script_dir) / "includes" / "FMI"
        if not fmi_dir.exists():
            raise ScadeOneException(f"FMI folder not found at expected location: {fmi_dir}")
        target_dir = dest_dir / "FMI"
        LOGGER.debug(f"Copying FMI folder from {fmi_dir} to {target_dir}")
        shutil.copytree(fmi_dir, target_dir, dirs_exist_ok=True)

    @staticmethod
    def _collect_include_dirs(cc_opts: List[str]) -> List[Path]:
        """
        Collect include directories from compiler options.

        Parameters
        ----------
        cc_opts : List[str]
            List of compiler options.

        Returns
        -------
        List[Path]
            A list of paths to the collected include directories.
        """

        include_dirs = []
        for opt in cc_opts:
            if opt.startswith("-I"):
                dir_path = opt[2:].strip()
                if dir_path:
                    include_dirs.append(Path(dir_path))
                else:
                    raise ScadeOneException(f"Invalid include directory specified: {opt}")
        LOGGER.debug(f"Collected include directories: {[str(d) for d in include_dirs]}")
        return include_dirs

    @staticmethod
    def _collect_link_opts(link_opts: List[Union[str, Path]]) -> Tuple[List[Path], List[Path]]:
        """
        Collect linker files from link options.

        Parameters
        ----------
        link_opts : List[Union[str, Path]]
            List of linker options or paths (files or directories).

        Returns
        -------
        List[Path]
            A list of paths to the collected linker options, including *.o files.
        """

        o_files = []
        link_files = []

        for opt in link_opts:
            opt_path = Path(opt)
            if opt_path.is_dir():
                LOGGER.debug(f"Collecting link files from directory: {opt_path}")
                # Collect *.o and other link files in the directory
                for f in opt_path.rglob("*"):
                    if f.suffix == ".o":
                        o_files.append(f)
                    else:
                        link_files.append(f)
            elif opt_path.is_file():
                if opt_path.suffix == ".o":
                    LOGGER.debug(f"Collecting link option file: {opt_path}")
                    o_files.append(opt_path)
                else:
                    link_files.append(opt_path)
            else:
                LOGGER.warning(
                    f"Link option {opt} is not a valid link file or directory, skipping."
                )
        if o_files:
            LOGGER.debug(f"Collected *.o files: {[str(opt) for opt in o_files]}")
        if link_files:
            LOGGER.debug(f"Collected link files: {[str(opt) for opt in link_files]}")

        return o_files, link_files

    @staticmethod
    def _generate_swan_config(args: dict, dest_dir: Path) -> Path:
        """
        Generate the `swan_config.h` file from a template.

        Parameters
        ----------
        args : dict
            Arguments containing `swan_config_begin` and `swan_config_end`.
        dest_dir : Path
            The directory where the `swan_config.h` file will be created.

        Returns
        -------
        Path
            The path to the generated `swan_config.h` file.
        """
        swan_config = dest_dir / "swan_config.h"
        LOGGER.debug(f"Creating swan_config.h in {swan_config}")
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(script_dir) / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = environment.get_template("swan_config_template.h")
        content = template.render(
            FMI_HOOK_BEGIN=args.get("swan_config_begin", ""),
            FMI_HOOK_END=args.get("swan_config_end", ""),
        )
        with open(swan_config, mode="w", encoding="utf-8") as out:
            out.write(content)
        return swan_config

    def _build_fmu(self, args: dict) -> None:
        """
        Creates the FMU dll or *.so from Scade One and FMU generated files.

        Parameters
        ----------
        args : dict
            A dictionary of arguments for the build process.
        """

        # Prepare build configuration
        cfg = BuildConfig()
        arch = ""
        if platform.system() == "Windows":
            arch = "win64" if platform.architecture()[0] == "64bit" else "win32"
        elif platform.system() == "Linux":
            arch = "linux64" if platform.architecture()[0] == "64bit" else "linux32"
        else:
            raise ScadeOneException(f"Unsupported platform: {platform.system()}")

        build_dir = Path(self.out_dir) / "binaries" / arch
        build_dir.mkdir(parents=True, exist_ok=True)
        cfg.working_dir = str(build_dir)

        # Collect source files
        self._collect_source_files()
        user_sources = args.get("user_sources", [])
        all_source_files = (
            list(self._source_dir.iterdir()) + self._collect_user_source_files(user_sources)
            if user_sources
            else list(self._source_dir.iterdir())
        )
        for f in all_source_files:
            if f.suffix == ".c":
                cfg.c_files.append(str(f))
            elif f.suffix == ".h":
                cfg.h_files.append(str(f))
                if str(f.parent) not in cfg.include_dirs:
                    cfg.include_dirs.append(str(f.parent))

        # Collect FMI files
        cfg.include_dirs.append(str(Path(script_dir) / "includes" / "FMI"))

        # Generate swan_config.h
        self._generate_swan_config(args, self._source_dir)
        cfg.include_dirs.append(str(self._source_dir))

        cfg.targets = [Target(self.model_id, TargetKind.SHARED_LIBRARY)]

        # Collect link files
        link_opts = args.get("link_opts", [])
        o_files, link_files = self._collect_link_opts(link_opts)
        cfg.o_files.extend([str(p) for p in o_files])
        if link_files:
            cfg.lib_files.extend([p.name for p in link_files])
            for link_file in link_files:
                if link_file.is_dir():
                    shutil.copytree(link_file, build_dir / link_file.name)
                elif link_file.is_file():
                    shutil.copy(link_file, build_dir / link_file.name)

        # Collect include directories from compiler options
        cc_opts = args.get("cc_opts", [])
        if cc_opts:
            if any(opt.startswith("-I") for opt in cc_opts):
                include_dirs = self._collect_include_dirs(cc_opts)
                cfg.include_dirs.extend([str(d) for d in include_dirs])
            else:
                # To-do: handle other compiler options
                pass

        # Build system
        builder = BuildSystem(self._project.app.install_dir)
        result = builder.build(cfg)

        # Handle build result
        if not result.is_succeeded:
            raise ScadeOneException(
                f"Error building {'*.dll' if 'win' in arch else '*.so'} file: {result.messages}"
            )

        if platform.system() == "Linux":
            # rename the generated .so to have the expected name
            so_name = build_dir / f"lib{self.model_id}.so"
            target_name = build_dir / f"{self.model_id}.so"
            if so_name.exists():
                shutil.move(so_name, target_name)
            else:
                LOGGER.warning(f"File not found: {so_name}, skipping rename.")

    def _build_zip(self, with_sources: bool, args: dict) -> None:
        """
        Creates the FMU zip archive

        Parameters
        ----------
        with_sources : bool
            True to include the sources in the FMU package.
        """

        fmu_filename = Path(self.out_dir) / f"{self.model_id}.fmu"
        if fmu_filename.exists():
            shutil.rmtree(fmu_filename, ignore_errors=True)

        # Copy user source files
        user_sources = args.get("user_sources", [])
        user_files = self._collect_user_source_files(user_sources)
        for f in user_files:
            shutil.copy(f, self._source_dir)

        # Copy swan_config.h to source_dir
        swan_config = self._source_dir / "swan_config.h"
        if not swan_config.exists():
            self._generate_swan_config(args, self._source_dir)

        # Copy FMI folder
        self._copy_fmi_folder(self._source_dir)

        # Copy include directories
        cc_opts = args.get("cc_opts", [])
        include_dirs = self._collect_include_dirs(cc_opts)
        for include_dir in include_dirs:
            target_dir = self._source_dir / include_dir.name
            shutil.copytree(include_dir, target_dir, dirs_exist_ok=True)

        # Copy link *.o files to source_dir
        link_opts = args.get("link_opts", [])
        o_paths, link_paths = self._collect_link_opts(link_opts)
        for link_path in link_paths:
            shutil.copy(link_path, self._source_dir)
        for o_path in o_paths:
            shutil.copy(o_path, self._source_dir)

        # Create FMU zip archive
        fmu_filename = Path(self.out_dir) / f"{self.model_id}.fmu"
        if fmu_filename.exists():
            shutil.rmtree(fmu_filename, ignore_errors=True)

        LOGGER.info(f"- Creating FMU zip archive {fmu_filename}")

        binaries_dir = Path(self.out_dir) / "binaries"
        sources_dir = self._source_dir

        try:
            with zipfile.ZipFile(fmu_filename, "w") as fmu:
                # Add *.dll/*.so files from binaries directory
                for arch_dir in binaries_dir.iterdir():
                    fmu_path = (
                        binaries_dir / arch_dir.name / f"{self.model_id}.dll"
                        if platform.system() == "Windows"
                        else binaries_dir / arch_dir.name / f"{self.model_id}.so"
                    )
                    if fmu_path.exists():
                        LOGGER.info(
                            f"- Adding {'*.dll file' if platform.system() == 'Windows' else '*.so file'}: {fmu_path}"
                        )
                        fmu.write(fmu_path, arcname=f"binaries/{arch_dir.name}/{fmu_path.name}")
                    else:
                        LOGGER.debug(f"File not found: {fmu_path}, skipping.")

                # Add source files if requested
                if with_sources:
                    for root, _, files in os.walk(sources_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = f"sources/{file_path.relative_to(sources_dir)}"
                            LOGGER.debug(f"Adding source file: {file_path} as {arcname}")
                            fmu.write(file_path, arcname=arcname)

                # Add the model description XML file
                model_description_path = self.fmu_xml_file
                if model_description_path.exists():
                    LOGGER.debug(f"- Adding model description file: {model_description_path}")
                    fmu.write(model_description_path, arcname="modelDescription.xml")

                # Add optional model image
                model_image_path = Path(script_dir) / "model.png"
                if model_image_path.exists():
                    LOGGER.debug(f"- Adding model image file: {model_image_path}")
                    fmu.write(model_image_path, arcname="model.png")

        except Exception as e:
            LOGGER.error(f"Error while creating FMU zip archive: {e}")
            raise ScadeOneException(f"Failed to create FMU zip archive: {e}")

    def generate(self, kind: str, outdir: Union[str, os.PathLike], period: float = 0.02) -> None:
        """
        Generate the FMI 2.0 XML and C file according to SCADE generated code.

        Parameters
        ----------
        kind : str
            The FMI kind ('ME' for Model Exchange, 'CS' for Co-Simulation).
        outdir : Union[str, os.PathLike]
            The output directory where the files are generated.
        period : float, optional
            The execution period in seconds (default is 0.02).
        """

        def _add_variable(entry: Union[GC.ModelVariable, GC.ModelSensor], var_kind: str) -> None:
            """
            Add a variable to the list of model variables.

            Parameters
            ----------
            entry : Union[GC.ModelVariable, GC.ModelSensor]
                The model variable or sensor to add.
            var_kind : str
                The kind of variable: 'input', 'output' or 'sensor'.
            """
            mv = ModelVar.model_vars_of_param(self, entry, var_kind)
            if len(mv) + len(self._mvars) > self.max_variables:
                raise ScadeOneException(
                    f"FMU export: The maximum number of supported model variables "
                    f"({self.max_variables}) is reached. Use max_variables parameter of "
                    f"FMU_2_Export class to increase it."
                )
            else:
                self._mvars.extend(mv)

        LOGGER.info(f"Generate the FMI related files under directory {outdir} (FMI kind {kind})")

        if not self.codegen.is_code_generated:
            raise ScadeOneException(f"FMU_Export: Code is not generated for job {self._job_name}")

        self._generate_ok = False

        if kind == "CS":
            self._kind_cs = True
        elif kind == "ME":
            self._kind_cs = False
        else:
            raise ScadeOneException('FMU_Export: Unknown FMU kind (expected "CS" or "ME")')

        # Fills `self._mvars` with the `:py:class:ModelVar` representing
        # the sensors and the input/outputs of the root operator.
        self._mvars = []
        # sensors
        for s in self.sensors:
            _add_variable(s, "sensor")
        for v in self.oper.inputs:
            _add_variable(v, "input")
        for v in self.oper.outputs:
            _add_variable(v, "output")

        # initialize generator state
        self.out_dir = Path(outdir).absolute()
        if not self.out_dir.exists():
            self.out_dir.mkdir()
        self.default_period = period
        self._value_ref_counter = {}

        self._generate_xml()
        self._generate_fmu_wrapper()

        LOGGER.info("Generation of FMI related files done")
        self._generate_ok = True

    def build(self, with_sources: bool = False, args: Optional[dict] = None) -> None:
        """
        Build the FMU package from generated files.

        The .FMU is built in the *outdir* directory provided
        when code was generated (see method :py:attr:`generate`),
        and its name is the name of the selected operator.

        Parameters
        ----------
        with_sources : bool, optional
            True to keep the sources in the FMU package.
        args : Optional[dict], optional
            Build arguments, provided as a dictionary (default is None):
            - *user_sources*: list of user source files or directories (code, includes)
            - *cc_opts*: list of extra compiler options
            - *link_opts*: list of extra link options
            - *swan_config_begin*: data to insert at the beginning of ``swan_config.h``
            - *swan_config_end*: data to insert at the end of ``swan_config.h``
        """

        LOGGER.info(f"Build the FMU under directory {self.out_dir}")

        if not self._generate_ok:
            raise ScadeOneException("FMU export: 'generate' method must be called first.")

        if args is None:
            args = {}
        self._build_fmu(args)
        self._build_zip(with_sources, args)

        LOGGER.info("Build of the FMU done.")
