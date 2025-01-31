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

# This module is used to create an FMI 2.0 co-simulation or model-exchange FMU
# from a Scade One model.
# The discrete operator is executed periodically.
#
# It generates C file needed by the runtime
# and the XML description of the FMU (modelDescription.xml).
# The FMU can then be created by compiling all source files with the corresponding runtime
# into a DLL and then packing it with the generated modelDescription.xml file.

# cSpell: ignore elems oper codegen mvars outdir newl addindent lshlwapi

from abc import ABC, abstractmethod
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import List, Optional, Tuple, Union
import uuid
import xml.dom.minidom as D
import zipfile

import jinja2

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
import ansys.scadeone.core.project as project
import ansys.scadeone.core.svc.generated_code as GC

script_dir = Path(__file__).parent

CYCLE_FUNCTION_RETURN = "cycle_function_return"

# Model variables


class ModelVar:
    """
    Class representing a scalar component of a variable appearing
    in the interface of the FMU.
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
                if type_name == "swan_float32" or type_name == "swan_float64":
                    fmu_ty = "Real"
                elif (
                    type_name == "swan_int8"
                    or type_name == "swan_int16"
                    or type_name == "swan_int32"
                    or type_name == "swan_int64"
                    or type_name == "swan_uint8"
                    or type_name == "swan_uint16"
                    or type_name == "swan_uint32"
                    or type_name == "swan_uint64"
                    or type_name == "swan_char"
                    or type_name == "swan_size"
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
            elif category == "typedef":
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
        """
        var_list = []

        if code_type["category"] == "array":
            base_type = code_type["elements"]["base_type"]
            for i in range(0, code_type["elements"]["size"]):
                var_list.extend(
                    ModelVar.paths_of_param(
                        "%s[%d]" % (sc_path, i), "%s[%d]" % (c_path, i), base_type
                    )
                )
        elif code_type["category"] == "struct":
            for f in code_type["elements"]:
                var_list.extend(
                    ModelVar.paths_of_param(
                        "%s.%s" % (sc_path, f["name"]), "%s.%s" % (c_path, f["name"]), f["type"]
                    )
                )
        elif code_type["category"] == "union":
            for f in code_type["elements"]:
                var_list.extend(
                    ModelVar.paths_of_param(
                        "%s.%s" % (sc_path, f["name"]), "%s.%s" % (c_path, f["name"]), f["type"]
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
        # Returns the C expression computing the offset of this model variable
        # in the runtime state.
        cast = "" if fmu_type == "" else f"(fmi2{fmu_type})"
        path = "" if self._var_kind == "sensor" else "comp->context->"
        return f"{cast}{path}{self._c_path}"


class FMU_Export(ABC):
    """
    FMU export main base class.

    - project: *Project* object.
    - job_name: name of the code generation job for the operator to be exported as an FMU.
    - oper_name: optional operator name (by default it is the root operator of the job if it is
    unique, if provided it has to be a root operator for the job).
    """

    def __init__(self, prj: project.Project, job_name: str, oper_name: str = "") -> None:
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

    @staticmethod
    def call(cmd: List[str], env=None) -> Tuple[int, str]:
        # Executes `cmd` and outputs its return code.
        # `cmd` is a list of strings (one for each word in the command line)
        # `env` is a dictionary of environment variables to be set for the command
        LOGGER.debug(f"Executing command: {cmd}")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, env=env)
            return p.returncode, p.stdout + p.stderr
        except FileNotFoundError:
            raise ScadeOneException(
                f"FMU Export: the compiler command '{cmd[0]}' cannot be found."
                f" Use the 'args' parameter to provide proper path."
            )

    @property
    def oper(self) -> GC.ModelOperator:
        if self._oper is None:
            self._oper = self.codegen.get_model_operator(self.root_operator)
            if not isinstance(self._oper, GC.ModelOperator):
                raise ScadeOneException(
                    f"FMU_Export: Operator {self.root_operator} cannot be monomorphic."
                )

        return self._oper

    @property
    def oper_path(self) -> str:
        # Returns the Scade One path for the operator exported as FMU.
        return self.oper.path

    @property
    def model_id(self) -> str:
        # Returns the name identifier of the operator exported as FMU.
        return self.root_operator.replace("::", "_")

    @property
    def sensors(self) -> List[GC.ModelSensor]:
        if self._sensors is None:
            self._sensors = self.codegen.get_model_sensors()
        return self._sensors

    def create_xml_child(self, name: str, parent: D.Node) -> D.Element:
        # Creates an XML child element
        d = self._doc.createElement(name)
        parent.appendChild(d)
        return d

    def get_next_value_reference(self, fmu_ty: str) -> str:
        if fmu_ty in self._value_ref_counter:
            self._value_ref_counter[fmu_ty] += 1
        else:
            self._value_ref_counter[fmu_ty] = 0
        return str(self._value_ref_counter[fmu_ty])

    def _add_period_var(self, parent: D.Node) -> None:
        # Adds the period variable to the list of variables in the XML description.
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
        raise ScadeOneException("abstract method call")

    @abstractmethod
    def build(self, with_sources: bool = False, args: Optional[dict] = None):
        raise ScadeOneException("abstract method call")


class FMU_2_Export(FMU_Export):
    """
    FMU 2.0 export main class.

    - project: *Project* object.
    - job_name: name of the code generation job for the operator to be exported as an FMU.
    - oper_name: optional operator name (by default it is the root operator of the job,\
     if provided it has to be a root operator for the job).
    - max_variables: maximum number on FMI variables (flattened sensors, inputs and outputs) \
     supported by the export (1000 by default).
    """

    def __init__(
        self, prj: project.Project, job_name: str, oper_name: str = "", max_variables: int = 1000
    ) -> None:
        super().__init__(prj, job_name, oper_name)
        self.max_variables = max_variables

    def _generate_xml(self) -> None:
        # Generates the modelDescription.xml file describing the FMU.
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
        # Adds as a child of root the XML element describing
        # the FMU kind (model-exchange or co-simulation).
        if self._kind_cs:
            d = self.create_xml_child("CoSimulation", root)
            d.setAttribute("modelIdentifier", self.model_id)
            d.setAttribute("canHandleVariableCommunicationStepSize", "true")
        else:
            d = self.create_xml_child("ModelExchange", root)
            d.setAttribute("modelIdentifier", self.model_id)

    def _generate_var_infos(self, var_type: str) -> Tuple[str, str]:
        # Generate variable access for FMI getter/setter C functions.
        idx = 0
        stmts_set = []
        stmts_get = []
        for mv in self._mvars:
            fmu_ty = mv.type_kind
            if fmu_ty == var_type:
                stmts_set.append(
                    "case %d: %s = (%s) value[i]; break;"
                    % (idx, mv.get_context_path(), mv.type_name)
                )
                stmts_get.append(
                    "case %d: value[i] = %s; break;" % (idx, mv.get_context_path(fmu_ty))
                )
                idx = idx + 1

        if var_type == "Real":
            stmts_set.append("case %d: comp->period = value[i]; break;" % idx)
            stmts_get.append("case %d: value[i] = comp->period; break;" % idx)

        return "\n".join(stmts_set), "\n".join(stmts_get)

    def _generate_var_init(self) -> str:
        # Generates variable initialization C statements.
        stmts_init = []
        for mv in self._mvars:
            stmts_init.append(
                "%s = (%s)%s;"
                % (mv.get_context_path(), mv.type_name, mv.get_default_value(xml=False))
            )

        stmts_init.append("comp->period = %s;" % self.default_period)

        return "\n".join(stmts_init)

    def _generate_fmu_wrapper(self) -> None:
        # Generates the FMU wrapper C file from template.
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
        template = environment.get_template("FMI_v2.0_template.c")

        cycle_function = self.oper.cycle_method
        init_function = self.oper.init_method
        reset_function = self.oper.reset_method

        includes = (
            """
#include "%s"
"""
            % (cycle_function.get_interface_file())
        ).strip()

        fmi_set_real, fmi_get_real = self._generate_var_infos("Real")
        fmi_set_integer, fmi_get_integer = self._generate_var_infos("Integer")
        fmi_set_boolean, fmi_get_boolean = self._generate_var_infos("Boolean")

        scade_context = "SCADE_%s" % self.model_id

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
        define_scade_context = (
            """
typedef struct {
    %s
} %s;%s
"""
            % ("\n    ".join(ctx_params), scade_context, sensors)
        ).strip()

        define_state_vector = "#define STATE_VECTOR_SIZE 0"

        if init_function is not None or reset_function is not None:
            if init_function is not None:
                call_params = []
                for param in init_function.parameters:
                    access = "&" if param.pointer else ""
                    call_params.append(f"{access}comp->context->{param.name}")
                call_init = "%s(%s);" % (init_function.name, ", ".join(call_params))
            else:
                call_init = ""
            if reset_function is not None:
                call_params = []
                for param in reset_function.parameters:
                    access = "&" if param.pointer else ""
                    call_params.append(f"{access}comp->context->{param.name}")
                call_reset = "%s(%s);" % (reset_function.name, ", ".join(call_params))
            else:
                call_reset = ""

            init_context = (
                """
#ifndef SWAN_USER_DEFINED_INIT
        %s
#else
#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
        %s
#endif
#endif
"""
                % (call_init, call_reset)
            ).strip()
        else:
            init_context = ""

        call_params = []
        for param in cycle_function.parameters:
            access = "&" if param.pointer else ""
            cast = f"({param.signature})" if param.const else ""
            call_params.append(f"{cast}{access}comp->context->{param.name}")

        if return_type is not None:
            # the output is returned by the function
            call_cycle_return = f"comp->context->{CYCLE_FUNCTION_RETURN} = "
        else:
            call_cycle_return = ""

        call_cycle = "%s%s(%s);" % (call_cycle_return, cycle_function.name, ", ".join(call_params))

        content = template.render(
            FMI_KIND_CS=self._kind_cs,
            FMI_USE_DBG_LOGS=0,
            FMI_FILE_NAME=out_c_file,
            FMI_INCLUDES=includes,
            FMI_DEFINE_SCADE_CONTEXT=define_scade_context,
            FMI_SCADE_CONTEXT=scade_context,
            FMI_SCADE_CONTEXT_SIZE=f"sizeof({scade_context})",
            FMI_DEFINE_STATE_VECTOR=define_state_vector,
            FMI_MODEL_IDENTIFIER=self.model_id + "_FMU",
            FMI_MODEL_GUID=self.uuid,
            FMI_TASK_PERIOD=self.default_period,
            FMI_NB_REALS=self._value_ref_counter.get("Real", -1) + 1,
            FMI_NB_INTEGERS=self._value_ref_counter.get("Integer", -1) + 1,
            FMI_NB_BOOLEANS=self._value_ref_counter.get("Boolean", -1) + 1,
            FMI_GET_REAL=fmi_get_real,
            FMI_GET_INTEGER=fmi_get_integer,
            FMI_GET_BOOLEAN=fmi_get_boolean,
            FMI_GET_STATES_FUNC_DECL="/* get state decl: N/A */",
            FMI_SET_REAL=fmi_set_real,
            FMI_SET_INTEGER=fmi_set_integer,
            FMI_SET_BOOLEAN=fmi_set_boolean,
            FMI_SET_STATES_FUNC_DECL="/* set state decl: N/A */",
            FMI_INIT_VALUES=self._generate_var_init(),
            FMI_INIT_CONTEXT=init_context,
            FMI_CALL_CYCLE=call_cycle,
            FMI_GET_FMU_STATE_FUNC="/* get state not implemented */",
            FMI_SET_FMU_STATE_FUNC="/* set state not implemented */",
            FMI_ROOT_OP_NAME=self.model_id,
        )

        with open(self.fmu_c_file, mode="w", encoding="utf-8") as out:
            out.write(content)

    def _build_dll(self, args: dict) -> None:
        # Creates the FMU dll from Scade One and FMU generated files.

        compiler = args.get("cc", "gcc")
        arch = args.get("arch", "win64")

        user_sources = args.get("user_sources", [])

        gen_dir = Path(self.codegen.generated_code_dir)

        # check that gen_dir exists and is not empty
        if not gen_dir.exists() or not any(gen_dir.iterdir()):
            raise ScadeOneException(
                f"FMU Export: job {self._job_name}:"
                f" generated code is missing under '{gen_dir.name}' sub-directory."
            )

        dll_dir = Path("..") / "binaries" / arch

        LOGGER.info(f"- Compile and create FMU DLL {Path(dll_dir) / self.model_id}.dll")

        # copy generated files in the source directory
        LOGGER.debug(f"  copy Scade One CG generated files from {gen_dir} to {self._source_dir}")
        for f in gen_dir.iterdir():
            if f.suffix in {".c", ".h"}:
                shutil.copy(Path(gen_dir) / f.name, self._source_dir)

        # copy user source files in the source directory
        for src in user_sources:
            src_path = Path(src)
            if src_path.is_dir():
                LOGGER.debug(f"  copy user source files from {src_path} to {self._source_dir}")
                for f in src_path.iterdir():
                    if f.is_dir():
                        shutil.copytree(f, self._source_dir / f.name, dirs_exist_ok=True)
                    else:
                        shutil.copy(f, self._source_dir)
            elif src_path.is_file():
                LOGGER.debug(
                    f"  copy user source file {src_path.name} from {src_path.parent}'"
                    f" to {self._source_dir}"
                )
                shutil.copy(src_path, self._source_dir)
            else:
                LOGGER.debug(f"  user source {src} not a file or a directory: ignored")

        # copy include files in the source directory
        LOGGER.debug(
            f"  copy FMU export includes from {Path(script_dir) / 'includes'} to {self._source_dir}"
        )
        shutil.copytree(
            Path(script_dir) / "includes" / "FMI", self._source_dir / "FMI", dirs_exist_ok=True
        )

        # create swan_config.h from template
        swan_config = self._source_dir / "swan_config.h"
        LOGGER.debug("  create swan_config.h from template")

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

        # memorize all C files for compilation
        c_files = []
        for fs in self._source_dir.iterdir():
            if fs.suffix == ".c":
                c_files.append(fs.name)

        binaries_dir = Path(self.out_dir) / "binaries"
        if binaries_dir.exists():
            shutil.rmtree(binaries_dir)
        binaries_dir.mkdir()

        if compiler == "gcc":
            # call GCC compiler
            if arch == "win32" or arch == "linux32":
                gcc_arch = "-m32"
            else:
                gcc_arch = "-m64"
            gcc = "gcc"
            gcc_path = args.get("gcc_path", "")
            env = None
            path_sav = os.environ["PATH"]
            if (
                gcc_path == ""
                and self._project.app.install_dir is not None
                and shutil.which("gcc") is None
            ):
                # set gcc_path on version installed with Scade One
                gcc_path = str(self._project.app.install_dir / "contrib" / "mingw64" / "bin")
            if gcc_path != "":
                os.environ["PATH"] = gcc_path + os.pathsep + path_sav
            cmd_comp = [gcc, "-c", gcc_arch, "-I" + str(Path("..") / "sources")]
            cmd_comp.extend(args.get("cc_opts", []))

            # create obj directory and compile from it
            obj_dir = self.out_dir / "objects"
            if obj_dir.exists():
                shutil.rmtree(obj_dir)
            obj_dir.mkdir()
            os.chdir(obj_dir)

            try:
                for fc in c_files:
                    cmd = cmd_comp.copy()
                    if fc == self.fmu_c_file.name:
                        cmd.append("-Wall")
                    cmd.append(str(Path("..") / "sources" / fc))
                    rc, traceback = FMU_Export.call(cmd, env)
                    if rc != 0:
                        msg = f"FMU_Export: Compilation failed for {fc}.\n"
                        msg += f"command: {cmd}\n"
                        msg += f"error {rc}:\n{traceback}"
                        os.chdir(self._start_dir)
                        raise ScadeOneException(msg)

                cmd_link = [
                    gcc,
                    gcc_arch,
                    "-lshlwapi",
                    "-Wl,--export-all-symbols",
                    "-shared",
                    "-static-libgcc",
                    "-g",
                ]
                cmd_link.extend(args.get("link_opts", []))
                cmd_link.extend(["-o", str(Path(dll_dir) / (self.model_id + ".dll"))])
                cmd_link.append("*")

                if not dll_dir.exists():
                    dll_dir.mkdir()

                rc, traceback = FMU_Export.call(cmd_link, env)
                if rc != 0:
                    msg = f"FMU_Export: dll creation failed for {self.model_id}.\n"
                    msg += f"command: {cmd_link}\n"
                    msg += f"error {rc}:\n{traceback}"
                    os.chdir(self._start_dir)
                    raise ScadeOneException(msg)

            finally:
                if gcc_path != "":
                    os.environ["PATH"] = path_sav

                os.chdir(self._start_dir)
        else:
            raise ScadeOneException(
                f"FMU_Export: '{compiler}' compiler not supported for this version (only gcc "
                f"is supported)"
            )

    def _build_zip(self, with_sources: bool):
        # Creates the FMU zip archive
        os.chdir(self.out_dir)
        fmu_filename = Path(self.model_id + ".fmu")

        LOGGER.info(f"- Creating FMU zip archive {fmu_filename} under directory {self.out_dir}")

        try:
            if fmu_filename.exists():
                fmu_filename.unlink()

            with zipfile.ZipFile(fmu_filename, "w") as fmu:
                for arch_dir in Path("binaries").iterdir():
                    fmu.write(Path("binaries") / arch_dir.name / (self.model_id + ".dll"))
                if with_sources:
                    for root, _, files in os.walk("sources"):
                        fmu.write(root)
                        for f in files:
                            fmu.write(Path(root) / f)
                fmu.write("modelDescription.xml")
                fmu.write(Path(script_dir) / "model.png", "model.png")

        finally:
            os.chdir(self._start_dir)

    def generate(self, kind: str, outdir: Union[str, os.PathLike], period: float = 0.02) -> None:
        """
        Generate the FMI 2.0 XML and C file according to SCADE generated code.

        - kind: FMI kind ('ME' for Model Exchange, 'CS' for Co-Simulation).
        - outdir: directory where the files are generated.
        - period: execution period in seconds.
        """

        def _add_variable(entry: Union[GC.ModelVariable, GC.ModelSensor], var_kind: str) -> None:
            mv = ModelVar.model_vars_of_param(self, entry, var_kind)
            if len(mv) + len(self._mvars) > self.max_variables:
                raise ScadeOneException(
                    f"FMU Export: The maximum number of supported model variables "
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
        self.out_dir = Path(outdir)
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

        - *with_sources*: True to keep the sources in the FMU package
        - *args*: build arguments, provided as a dictionary:

          - *cc*: compiler name (only gcc supported)
          - *arch*: compiler architecture (only win64 supported)
          - *gcc_path*: path on the bin directory where gcc is located
          - *user_sources*: list of user source files or directories (code, includes)
          - *cc_opts*: list of extra compiler options
          - *link_opts*: list of extra link (DLL creation) options
          - *swan_config_begin*: data to insert at the beginning of ``swan_config.h``
          - *swan_config_end*: data to insert at the end of ``swan_config.h``

        Note for gcc compiler:
            If the Scade One installation directory is provided when *ScadeOne* class is
            instantiated, and gcc is not already in the PATH, the gcc from the Scade One
            installation is used.
        """

        LOGGER.info(f"Build the FMU under directory {self.out_dir}")

        if not self._generate_ok:
            raise ScadeOneException("FMU Export: 'generate' method must be called first.")

        if args is None:
            args = {}
        self._build_dll(args)
        self._build_zip(with_sources)

        LOGGER.info("Build of the FMU done.")
