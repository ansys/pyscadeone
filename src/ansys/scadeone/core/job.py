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

from abc import ABC, abstractmethod
from enum import Enum, auto
import subprocess
from pathlib import Path
from typing import Optional, Union, TypedDict
import uuid

from ansys.scadeone.core.common.storage import JobFile, JobStorage

from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.interfaces import IProject


class _PropertiesData(TypedDict, total=False):
    """Job properties data structure."""

    # Common fields
    RootDeclarations: list[str]
    Name: str
    CustomArguments: str

    # Code generation fields
    Expansion: str
    ExpansionExp: str
    ExpansionNoExp: str
    ShortCircuitOperators: str
    NameLength: str
    SignificanceLength: str
    KeepAssume: str
    GlobalsPrefix: str
    UseMacros: str
    StaticLocals: str

    # Test execution fields
    TestHarness: str
    TestResultFile: str

    # Simulation fields
    FileScenario: str
    SimulationInputType: str
    UseCycleTime: str
    CycleTime: str


class _JobData(TypedDict):
    """Job data structure."""

    Version: str
    Kind: str
    Properties: _PropertiesData
    InputPaths: list[str]


class JobStatus(Enum):
    """Exit codes for a job execution"""

    #: Success
    Success = 0
    #: Missing parameters
    MissingParameters = 1
    #: Load issue
    LoadIssue = 2
    #: Not existing project
    NotExistingProject = 3
    #: Job not found
    JobNotFound = 4
    #: Job failure
    JobFailure = 5
    #: Job name duplicate
    JobNameDuplicate = 6
    #: Internal error
    InternalError = 7
    #: Not executed yet
    NotExecutedYet = 8

    @staticmethod
    def get_message(status_code: int) -> str:
        """Get the message corresponding to a status number

        Parameters
        ----------
        code : int
            Status number

        Returns
        -------
        str
            Status message
        """
        if status_code == JobStatus.Success.value:
            return "Job execution successful"
        if status_code == JobStatus.MissingParameters.value:
            return "The arguments are not filled in"
        if status_code == JobStatus.LoadIssue.value:
            return "The project or one of their dependencies cannot be loaded"
        if status_code == JobStatus.NotExistingProject.value:
            return "The project was not found"
        if status_code == JobStatus.JobNotFound.value:
            return (
                "The project has been loaded as expected "
                "but there is no job that matches the specified name"
            )
        if status_code == JobStatus.JobFailure.value:
            return "The job execution has failed"
        if status_code == JobStatus.JobNameDuplicate.value:
            return "There is more than one job matching the requested name"
        if status_code == JobStatus.InternalError.value:
            return "Undefined error"
        if status_code == JobStatus.NotExecutedYet.value:
            return "No job was executed yet"
        return "Unknown error code"

    def __str__(self) -> str:
        return self.get_message(self.value)


class JobResult:
    """Results from the execution of a job"""

    def __init__(self, code: int, message: Optional[str] = None):
        self._code = code
        self._message = message if message else JobStatus.get_message(code)

    @property
    def code(self) -> int:
        """Get execution return code"""
        return self._code

    @property
    def message(self) -> str:
        """Get execution return message"""
        return self._message

    def __str__(self) -> str:
        return f"Code {str(self._code)}: {self._message}"


class ExpansionMode(Enum):
    """Possible values for Expansion field in code generation job properties"""

    #: None
    NONE = auto()
    #: All
    ALL = auto()
    #: Expand
    EXPAND = auto()
    #: NoExpand
    NOEXPAND = auto()

    @staticmethod
    def str_to_expansion(str_exp: Union[str, None]) -> "ExpansionMode":
        """Get Expansion value from sjob file content"""
        if str_exp:
            if str_exp == "All":
                return ExpansionMode.ALL
            if str_exp == "Expand":
                return ExpansionMode.EXPAND
            if str_exp == "NoExpand":
                return ExpansionMode.NOEXPAND
        return ExpansionMode.NONE

    def __str__(self) -> str:
        if self == ExpansionMode.ALL:
            return "All"
        if self == ExpansionMode.EXPAND:
            return "Expand"
        if self == ExpansionMode.NOEXPAND:
            return "NoExpand"
        if self == ExpansionMode.NONE:
            return "None"
        return ""


class JobType(Enum):
    """Job types"""

    #: Code Generation type job
    CODEGEN = auto()
    #: Simulation type job
    SIMU = auto()
    #: Test Execution type job
    TESTEXEC = auto()

    def __str__(self) -> str:
        """String representation of type.
        Used for field `kind` in sjob files"""

        if self == JobType.CODEGEN:
            return "CodeGeneration"
        if self == JobType.SIMU:
            return "Simulation"
        if self == JobType.TESTEXEC:
            return "TestExecution"
        return ""


class Job(ABC):
    """Abstract class for jobs. Must be instantiated from one of its 3 derivated classes.
    Each of them uses its corresponding `Properties` parameters and kind."""

    def __init__(
        self,
        name: str,
        kind: JobType,
        sproj: IProject,
        input_paths: Optional[list[str]] = None,
        storage: JobStorage = None,
    ) -> None:
        self._name = name
        self._kind = kind
        self._version = FormatVersions.version("sjob")
        self._input_paths = input_paths if input_paths else []
        self._storage = storage
        self._sproj = sproj

    def __eq__(self, value: "Job") -> bool:
        """Two jobs are equal if their json content is equal"""
        self.storage.load()
        value.storage.load()
        return self.storage.json == value.storage.json

    @property
    def name(self) -> str:
        """Job name"""
        return self._name

    @property
    def version(self) -> str:
        """.sjob version"""
        return self._version

    @property
    def input_paths(self) -> list[str]:
        """InputPaths parameter"""
        return self._input_paths

    @property
    def sproj(self) -> IProject:
        """Corresponding project"""
        return self._sproj

    @property
    def is_simu(self) -> bool:
        """True if job is a simulation"""
        return self._kind == JobType.SIMU

    @property
    def is_codegen(self) -> bool:
        """True if job is a code generation"""
        return self._kind == JobType.CODEGEN

    @property
    def is_testexec(self) -> bool:
        """True if job is a test execution"""
        return self._kind == JobType.TESTEXEC

    @property
    def storage(self) -> JobStorage:
        """Job storage"""
        return self._storage

    @property
    def root_declarations(self) -> str:
        return self.properties.root_declarations

    @property
    def custom_arguments(self) -> str:
        return self.properties.custom_arguments

    @root_declarations.setter
    def root_declarations(self, value: list[str]) -> None:
        self.properties.root_declarations = value

    @custom_arguments.setter
    def custom_arguments(self, value: str) -> None:
        self.properties.custom_arguments = value

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self.properties.name = value

    @property
    @abstractmethod
    def properties(self) -> "JobProperties":
        """Properties parameter.
        Its subtype depends on the Job kind,
        JobProperties is an abstract class."""
        pass

    @input_paths.setter
    def input_paths(self, value: Union[str, list[str]]) -> None:
        """Set InputPaths"""
        if isinstance(value, str):
            self._input_paths = [value]
        else:
            self._input_paths = value

    def folder_name(self) -> str:
        """Generate name of the folder containing the sjob file"""

        if self.is_simu:
            prefix = "simu_"
        elif self.is_codegen:
            prefix = "codegen_"
        elif self.is_testexec:
            prefix = "testexec_"
        else:
            prefix = "unknown_"
        guid_short = str(uuid.uuid4())[:7]
        return prefix + guid_short

    def save(self) -> _JobData:
        """Save the Job parameters into .sjob file.
        Create a new folder for a new Job."""

        data = {}
        data["Version"] = self._version
        data["Kind"] = str(self._kind)
        data["Properties"] = self.properties._to_dict()
        data["InputPaths"] = self._input_paths
        if not self._storage:
            job_folder = self.folder_name()
            sjob_path = Path(self._sproj._storage.source).parent / "jobs" / job_folder / ".sjob"
            self._storage = JobFile(sjob_path)
        parent = Path(self._storage.source).parent
        if not parent.exists():
            import os

            os.makedirs(parent)
        self._storage.json = data
        self._storage.dump()
        return data

    def run(self) -> JobResult:
        job_launcher = JobLauncher()
        job_launcher.job = self
        job_launcher.sproj = self._sproj
        job_launcher.execute()
        return job_launcher.result


class CodeGenerationJob(Job):
    """Job of Code Generation kind"""

    def __init__(
        self, name: str, sproj: IProject, data: dict = None, storage: JobStorage = None
    ) -> None:
        if data:
            super().__init__(name, JobType.CODEGEN, sproj, data.get("InputPaths"), storage)
            self._properties = CodeGenerationJobProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.CODEGEN, sproj)
            self._properties = CodeGenerationJobProperties(name)

    @property
    def properties(self) -> "CodeGenerationJobProperties":
        "Code generation job properties"
        return self._properties

    @property
    def expansion(self) -> ExpansionMode:
        return self.properties.expansion

    @property
    def expansion_exp(self) -> str:
        return self.properties.expansion_exp

    @property
    def expansion_no_exp(self) -> str:
        return self.properties.expansion_no_exp

    @property
    def short_circuit_operators(self) -> bool:
        return self.properties.short_circuit_operators

    @property
    def name_length(self) -> int:
        return self.properties.name_length

    @property
    def significance_length(self) -> int:
        return self.properties.significance_length

    @property
    def keep_assume(self) -> str:
        return self.properties.keep_assume

    @property
    def globals_prefix(self) -> str:
        return self.properties.globals_prefix

    @property
    def use_macros(self) -> bool:
        return self.properties.use_macros

    @property
    def static_locals(self) -> bool:
        return self.properties.static_locals

    @expansion.setter
    def expansion(self, value: Union[ExpansionMode, str, None]) -> None:
        self.properties.expansion = value

    @expansion_exp.setter
    def expansion_exp(self, value: str) -> None:
        self.properties.expansion_exp = value

    @expansion_no_exp.setter
    def expansion_no_exp(self, value: str) -> None:
        self.properties.expansion_no_exp = value

    @short_circuit_operators.setter
    def short_circuit_operators(self, value: bool) -> None:
        self.properties.short_circuit_operators = value

    @name_length.setter
    def name_length(self, value: int) -> None:
        self.properties.name_length = value

    @significance_length.setter
    def significance_length(self, value: int) -> None:
        self.properties.significance_length = value

    @keep_assume.setter
    def keep_assume(self, value: str) -> None:
        self.properties.keep_assume = value

    @globals_prefix.setter
    def globals_prefix(self, value: str) -> None:
        self.properties.globals_prefix = value

    @use_macros.setter
    def use_macros(self, value: bool) -> None:
        self.properties.use_macros = value

    @static_locals.setter
    def static_locals(self, value: bool) -> None:
        self.properties.static_locals = value


class SimulationJob(Job):
    """Job of Simulation kind"""

    def __init__(
        self, name: str, sproj: IProject, data: dict = None, storage: JobStorage = None
    ) -> None:
        if data:
            super().__init__(name, JobType.SIMU, sproj, data.get("InputPaths"), storage)
            self._properties = SimulationJobProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.SIMU, sproj)
            self._properties = SimulationJobProperties(name)

    @property
    def properties(self) -> "SimulationJobProperties":
        """Simulation job properties"""
        return self._properties

    @property
    def file_scenario(self) -> str:
        return self.properties.file_scenario

    @property
    def simulation_input_type(self) -> str:
        return self.properties.simulation_input_type

    @property
    def test_harness(self) -> str:
        return self.properties.test_harness

    @property
    def use_cycle_time(self) -> bool:
        return self.properties.use_cycle_time

    @property
    def cycle_time(self) -> int:
        return self.properties.cycle_time

    @file_scenario.setter
    def file_scenario(self, value: str) -> None:
        self.properties.file_scenario = value

    @simulation_input_type.setter
    def simulation_input_type(self, value: str) -> None:
        self.properties.simulation_input_type = value

    @test_harness.setter
    def test_harness(self, value: str) -> None:
        self.properties.test_harness = value

    @use_cycle_time.setter
    def use_cycle_time(self, value: bool) -> None:
        self.properties.use_cycle_time = value

    @cycle_time.setter
    def cycle_time(self, value: int) -> None:
        self.properties.cycle_time = value


class TestExecutionJob(Job):
    """Job of Test Execution kind"""

    def __init__(
        self, name: str, sproj: IProject, data: dict = None, storage: JobStorage = None
    ) -> None:
        if data:
            super().__init__(name, JobType.TESTEXEC, sproj, data.get("InputPaths"), storage)
            self._properties = TextExecutionJobProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.TESTEXEC, sproj)
            self._properties = TextExecutionJobProperties(name)

    @property
    def properties(self) -> "TextExecutionJobProperties":
        """Test execution job properties"""
        return self._properties

    @property
    def test_harness(self) -> str:
        return self.properties.test_harness

    @property
    def test_result_file(self) -> str:
        return self.properties.test_result_file

    @test_harness.setter
    def test_harness(self, value: str) -> None:
        self.properties.test_harness = value

    @test_result_file.setter
    def test_result_file(self, value: str) -> None:
        self.properties.test_result_file = value


class JobProperties(ABC):
    """Abstract class for job properties, cannot be instantiated.
    Its derived class depends on the kind of Job.
    The parameters presented here can be found in all 3 kinds of Jobs properties.
    """

    def __init__(self, name: str, prop: dict) -> None:
        self._name = name
        self._root_declarations = prop.get("RootDeclarations", [""])
        self._custom_arguments = prop.get("CustomArguments", "")

    @property
    def root_declarations(self) -> list[str]:
        """RootDeclarations common property"""
        return self._root_declarations

    @property
    def custom_arguments(self) -> str:
        """CustomArguments common property"""
        return self._custom_arguments

    @property
    def name(self) -> str:
        """Name common property"""
        return self._name

    @root_declarations.setter
    def root_declarations(self, value: Union[str, list[str]]) -> None:
        """Set RootDeclarations. String can be passed instead of a single element list."""
        if isinstance(value, str):
            self._root_declarations = [value]
        else:
            self._root_declarations = value

    @custom_arguments.setter
    def custom_arguments(self, value: str) -> None:
        """Set CustomArguments"""
        self._custom_arguments = value

    @name.setter
    def name(self, value: str) -> None:
        """Set Name"""
        self._name = value

    def _to_dict(self, data: _PropertiesData) -> _PropertiesData:
        """Return the Properties dictionary that was prefilled
        by one of derivated Properties method"""

        data["RootDeclarations"] = self._root_declarations
        data["CustomArguments"] = self._custom_arguments
        data["Name"] = self._name
        return data


class CodeGenerationJobProperties(JobProperties):
    """Properties of Code Generation kind Jobs.
    Parameters presented here are unique to Code Generation."""

    def __init__(self, name: str, prop: dict = None) -> None:
        if not prop:
            prop = {}
        super().__init__(name, prop)
        self._expansion = ExpansionMode.str_to_expansion(prop.get("Expansion"))
        self._expansion_exp = prop.get("ExpansionExp", "")
        self._expansion_no_exp = prop.get("ExpansionNoExp", "")
        self._short_circuit_operators = prop.get("ShortCircuitOperators") == "True"
        self._name_length = int(prop.get("NameLength", 200))
        self._significance_length = int(prop.get("SignificanceLength", 31))
        self._keep_assume = prop.get("KeepAssume") == "True"
        self._globals_prefix = prop.get("GlobalsPrefix", "")
        self._use_macros = prop.get("UseMacros") == "True"
        self._static_locals = prop.get("StaticLocals") == "True"

    @property
    def expansion(self) -> ExpansionMode:
        """Expansion property"""
        return self._expansion

    @property
    def expansion_exp(self) -> str:
        """ExpansionExp property"""
        return self._expansion_exp

    @property
    def expansion_no_exp(self) -> str:
        """ExpansionNoExp property"""
        return self._expansion_no_exp

    @property
    def short_circuit_operators(self) -> bool:
        """ShortCircuitOperators property"""
        return self._short_circuit_operators

    @property
    def name_length(self) -> int:
        """NameLength property"""
        return self._name_length

    @property
    def significance_length(self) -> int:
        """SignificanceLength property"""
        return self._significance_length

    @property
    def keep_assume(self) -> bool:
        """KeepAssume property"""
        return self._keep_assume

    @property
    def globals_prefix(self) -> str:
        """GlobalsPrefix property"""
        return self._globals_prefix

    @property
    def use_macros(self) -> bool:
        """UseMacros property"""
        return self._use_macros

    @property
    def static_locals(self) -> bool:
        """StaticLocals property"""
        return self._static_locals

    @expansion.setter
    def expansion(self, value: Union[ExpansionMode, str, None]) -> None:
        """Set Expansion"""
        if isinstance(value, ExpansionMode):
            self._expansion = value
        elif isinstance(value, str):
            self._expansion = ExpansionMode.str_to_expansion(value)
        else:
            self._expansion = ExpansionMode.NONE

    @expansion_exp.setter
    def expansion_exp(self, value: str) -> None:
        """Set ExpansionExp"""
        self._expansion_exp = value

    @expansion_no_exp.setter
    def expansion_no_exp(self, value: str) -> None:
        """Set ExpansionNoExp"""
        self._expansion_no_exp = value

    @short_circuit_operators.setter
    def short_circuit_operators(self, value: bool) -> None:
        """Set ShortCircuitOperators"""
        self._short_circuit_operators = value

    @name_length.setter
    def name_length(self, value: int) -> None:
        """Set NameLength"""
        self._name_length = value

    @significance_length.setter
    def significance_length(self, value: int) -> None:
        """Set SignificanceLength"""
        self._significance_length = value

    @keep_assume.setter
    def keep_assume(self, value: bool) -> None:
        """Set KeepAssume"""
        self._keep_assume = value

    @globals_prefix.setter
    def globals_prefix(self, value: str) -> None:
        """Set GlobalsPrefix"""
        self._globals_prefix = value

    @use_macros.setter
    def use_macros(self, value: bool) -> None:
        """Set UseMacros"""
        self._use_macros = value

    @static_locals.setter
    def static_locals(self, value: bool) -> None:
        """Set StaticLocals"""
        self._static_locals = value

    def _to_dict(self) -> _PropertiesData:
        data = {}
        data["Expansion"] = str(self._expansion)
        data["ExpansionExp"] = self._expansion_exp
        data["ExpansionNoExp"] = self._expansion_no_exp
        data["ShortCircuitOperators"] = str(self._short_circuit_operators)
        data["NameLength"] = str(self._name_length)
        data["SignificanceLength"] = str(self._significance_length)
        data["KeepAssume"] = str(self._keep_assume)
        data["GlobalsPrefix"] = self._globals_prefix
        data["UseMacros"] = str(self._use_macros)
        data["StaticLocals"] = str(self._static_locals)
        return super()._to_dict(data)


class SimulationJobProperties(JobProperties):
    """Properties of Simulation kind Jobs.
    Parameters presented here are unique to Simulation."""

    def __init__(self, name: str, prop: dict = None) -> None:
        if not prop:
            prop = {}
        super().__init__(name, prop)
        self._file_scenario = prop.get("FileScenario", "")
        self._simulation_input_type = prop.get("SimulationInputType", "Harness")
        self._test_harness = prop.get("TestHarness", "")  # Optional
        self._use_cycle_time = prop.get("UseCycleTime") == "True"  # bool
        self._cycle_time = int(prop.get("CycleTime", 200))  # Optional int (ms)

    @property
    def file_scenario(self) -> str:
        """FileScenario property"""
        return self._file_scenario

    @property
    def simulation_input_type(self) -> str:
        """SimulationInputType property"""
        return self._simulation_input_type

    @property
    def test_harness(self) -> str:
        """TestHarness property"""
        return self._test_harness

    @property
    def use_cycle_time(self) -> bool:
        """UseCycleTime property"""
        return self._use_cycle_time

    @property
    def cycle_time(self) -> int:
        """CycleTime property"""
        return self._cycle_time

    @file_scenario.setter
    def file_scenario(self, value: str) -> None:
        """Set FileScenario"""
        self._file_scenario = value

    @simulation_input_type.setter
    def simulation_input_type(self, value: str) -> None:
        """Set SimulationInputType"""
        self._simulation_input_type = value

    @test_harness.setter
    def test_harness(self, value: str) -> None:
        """Set TestHarness"""
        self._test_harness = value

    @use_cycle_time.setter
    def use_cycle_time(self, value: bool) -> None:
        """Set UseCycleTime"""
        self._use_cycle_time = value

    @cycle_time.setter
    def cycle_time(self, value: int) -> None:
        """Set CycleTime"""
        self._cycle_time = value

    def _to_dict(self) -> _PropertiesData:
        data = {}
        data["FileScenario"] = self._file_scenario
        data["SimulationInputType"] = self._simulation_input_type
        data["TestHarness"] = self._test_harness
        data["UseCycleTime"] = str(self._use_cycle_time)
        data["CycleTime"] = str(self._cycle_time)
        return super()._to_dict(data)


class TextExecutionJobProperties(JobProperties):
    """Properties of Test Execution kind Jobs.
    Parameters presented here are unique to Test Execution."""

    def __init__(self, name: str, prop: dict = None) -> None:
        if not prop:
            prop = {}
        super().__init__(name, prop)
        self._test_harness = prop.get("TestHarness", "")
        self._test_result_file = prop.get("TestResultFile", "testResults.json")

    @property
    def test_harness(self) -> str:
        """TestHarness property"""
        return self._test_harness

    @property
    def test_result_file(self) -> str:
        """TestResultFile property"""
        return self._test_result_file

    @test_harness.setter
    def test_harness(self, val: str) -> None:
        """Set TestHarness"""
        self._test_harness = val

    @test_result_file.setter
    def test_result_file(self, val: str) -> None:
        """Set TestResultFile"""
        self._test_result_file = val

    def _to_dict(self) -> _PropertiesData:
        data = {}
        data["TestHarness"] = self._test_harness
        data["TestResultFile"] = self._test_result_file
        return super()._to_dict(data)


class JobLauncher:
    """Class used to execute a Job.
    Must set a job and a project in order to execute."""

    def __init__(self) -> None:
        self._sproj = None
        self._job = None
        self._result = JobResult(8)

    @property
    def job(self) -> Union[Job, None]:
        """Job that should be executed"""
        return self._job

    @property
    def sproj(self) -> Union[IProject, None]:
        """Project of the job"""
        return self._sproj

    @property
    def result(self) -> JobResult:
        """Gets the result of the last executed job"""
        return self._result

    @job.setter
    def job(self, value: Job) -> None:
        """Set Job to execute"""
        self._job = value

    @sproj.setter
    def sproj(self, value: IProject) -> None:
        """Set Job's project"""
        self._sproj = value

    def execute(self) -> bool:
        """Execute the Job via JobLauncher executable"""
        from ansys.scadeone.core import ScadeOneException

        if not self._job:
            raise ScadeOneException("No Job was assigned for JobLauncher to execute.")
        elif not self._sproj:
            raise ScadeOneException("No Job project was assigned for the JobLauncher")
        job_launcher = self._sproj.app.tools.job_launcher

        if not job_launcher:
            raise ScadeOneException(
                "Job launcher tool was not found. It is required for Job Execution."
            )

        proc = subprocess.run(
            [str(job_launcher), "run", "-p", self._sproj._storage.source, "-j", self._job.name]
        )
        self._result = JobResult(proc.returncode)
        return self._result.code == JobStatus.Success.value
