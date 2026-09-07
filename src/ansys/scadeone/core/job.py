# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
import subprocess
from pathlib import Path
from typing import Optional, Union, TypedDict
import uuid
import shutil

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import JobFile, JobStorage, ProjectFile

from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.interfaces import IProject, IScadeOne
import ansys.scadeone.core.assets as assets
import ansys.scadeone.core.swan as swn


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
    NameLength: str
    KeepAssume: str
    GlobalsPrefix: str
    UseMacros: str
    StaticLocals: str
    MaxFunctionParameters: str
    Probes: str

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
    SUCCESS = 0
    #: Missing parameters
    MISSING_PARAMETERS = 1
    #: Load issue
    LOAD_ISSUE = 2
    #: Not existing project
    NOT_EXISTING_PROJECT = 3
    #: Job not found
    JOB_NOT_FOUND = 4
    #: Job failure
    JOB_FAILURE = 5
    #: Job name duplicate
    JOB_NAME_DUPLICATE = 6
    #: Internal error
    INTERNAL_ERROR = 7
    #: Not executed yet
    NOT_EXECUTED_YET = 8

    @staticmethod
    def get_message(status_code: int) -> str:
        """Gets the message corresponding to a status number

        Parameters
        ----------
        code : int
            Status number

        Returns
        -------
        str
            Status message
        """
        if status_code == JobStatus.SUCCESS.value:
            return "Job execution successful"
        if status_code == JobStatus.MISSING_PARAMETERS.value:
            return "The arguments are not filled in"
        if status_code == JobStatus.LOAD_ISSUE.value:
            return "The project or one of their dependencies cannot be loaded"
        if status_code == JobStatus.NOT_EXISTING_PROJECT.value:
            return "The project was not found"
        if status_code == JobStatus.JOB_NOT_FOUND.value:
            return (
                "The project has been loaded as expected "
                "but there is no job that matches the specified name"
            )
        if status_code == JobStatus.JOB_FAILURE.value:
            return "The job execution has failed"
        if status_code == JobStatus.JOB_NAME_DUPLICATE.value:
            return "There is more than one job matching the requested name"
        if status_code == JobStatus.INTERNAL_ERROR.value:
            return "Undefined error"
        if status_code == JobStatus.NOT_EXECUTED_YET.value:
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
        """Gets execution return code"""
        return self._code

    @property
    def message(self) -> str:
        """Gets execution return message"""
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
    NO_EXPAND = auto()

    @staticmethod
    def str_to_expansion(str_exp: Union[str, None]) -> "ExpansionMode":
        """Gets Expansion value from sjob file content"""
        if str_exp:
            if str_exp == "All":
                return ExpansionMode.ALL
            if str_exp == "Expand":
                return ExpansionMode.EXPAND
            if str_exp == "NoExpand":
                return ExpansionMode.NO_EXPAND
        return ExpansionMode.NONE

    def __str__(self) -> str:
        if self == ExpansionMode.ALL:
            return "All"
        if self == ExpansionMode.EXPAND:
            return "Expand"
        if self == ExpansionMode.NO_EXPAND:
            return "NoExpand"
        if self == ExpansionMode.NONE:
            return "None"
        return ""


class JobType(Enum):
    """Job types"""

    #: Code Generation type job
    CODE_GENERATION = auto()
    #: Simulation type job
    SIMULATION = auto()
    #: Test Execution type job
    TEST_EXECUTION = auto()
    #: Model Check type job
    MODEL_CHECK = auto()

    def __str__(self) -> str:
        """String representation of type.
        Used for field `kind` in sjob files"""

        if self == JobType.CODE_GENERATION:
            return "CodeGeneration"
        if self == JobType.SIMULATION:
            return "Simulation"
        if self == JobType.TEST_EXECUTION:
            return "TestExecution"
        if self == JobType.MODEL_CHECK:
            return "ModelCheck"
        return ""


class Job(ABC):
    """Abstract class for jobs.
    Must be instantiated from one of its 4 derivated classes.
    Each of them uses its corresponding `Properties` parameters and kind."""

    def __init__(
        self,
        name: str,
        kind: JobType,
        sproj: IProject,
        input_paths: Optional[list[str]] = None,
        storage: JobStorage | None = None,
    ) -> None:
        self._name = name
        self._kind = kind
        self._version = FormatVersions.version("sjob")
        self._input_paths = input_paths if input_paths else []
        self._storage = storage
        self._sproj = sproj
        self._input_assets: list[assets.Asset] = []
        self._output_assets: list[assets.Asset] = []

    def __eq__(self, value: object) -> bool:
        """Two jobs are equal if their json content is equal"""
        if not isinstance(value, Job):
            return False
        if not (isinstance(self.storage, JobFile) and isinstance(value.storage, JobFile)):
            raise ScadeOneException("Cannot compare jobs that do not have file storage.")
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
    def is_simulation(self) -> bool:
        """True if job is a simulation"""
        return self._kind == JobType.SIMULATION

    @property
    def is_code_generation(self) -> bool:
        """True if job is a code generation"""
        return self._kind == JobType.CODE_GENERATION

    @property
    def is_test_execution(self) -> bool:
        """True if job is a test execution"""
        return self._kind == JobType.TEST_EXECUTION

    @property
    def is_model_check(self) -> bool:
        """True if job is a model check"""
        return self._kind == JobType.MODEL_CHECK

    @property
    def storage(self) -> JobStorage | JobFile | None:
        """Job storage"""
        return self._storage

    @property
    def root_declarations(self) -> list[str]:
        return self.properties.root_declarations

    @property
    def custom_arguments(self) -> str:
        return self.properties.custom_arguments

    @property
    def input_assets(self) -> list[assets.Asset]:
        """Input assets of the job"""
        if self._input_assets:
            return self._input_assets

        _list_modules = [str(mdl.name) for mdl in self.sproj.modules]
        for input_path_str in self.input_paths:
            input_path = Path(input_path_str)
            module_name = swn.Module.module_name_from_path(input_path)

            suffix = input_path.suffix
            if suffix == ".swan" and module_name in _list_modules:
                self._input_assets.append(assets.ModuleBodyAsset(input_path, self.sproj))
            elif suffix == ".swani" and module_name in _list_modules:
                self._input_assets.append(assets.ModuleInterfaceAsset(input_path, self.sproj))
            elif suffix == ".swant" and module_name in _list_modules:
                self._input_assets.append(assets.TestModuleAsset(input_path, self.sproj))

        return self._input_assets

    @property
    @abstractmethod
    def output_assets(self) -> list[assets.Asset]:
        """Output assets of the job.
        Must be implemented by child classes corresponding to its asset type."""
        pass

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
    def properties(self) -> JobProperties:
        """Properties parameter.
        Its subtype depends on the Job kind,
        JobProperties is an abstract class."""
        pass

    @input_paths.setter
    def input_paths(self, value: Union[str, list[str]]) -> None:
        """Sets InputPaths"""
        if isinstance(value, str):
            self._input_paths = [value]
        else:
            self._input_paths = value

    def folder_name(self) -> str:
        """Generate name of the folder containing the sjob file"""

        if self.is_simulation:
            prefix = "simu_"
        elif self.is_code_generation:
            prefix = "codegen_"
        elif self.is_test_execution:
            prefix = "testexec_"
        elif self.is_model_check:
            prefix = "check_"
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
            if not isinstance(self._sproj.storage, ProjectFile):
                raise ScadeOneException("Cannot save a job for a project without file storage.")
            job_folder = self.folder_name()
            sjob_path = Path(self._sproj.storage.source).parent / "jobs" / job_folder / ".sjob"
            self._storage = JobFile(sjob_path)
        elif not isinstance(self._storage, JobFile):
            raise ScadeOneException("Cannot save a job that does not have file storage.")
        parent = Path(self._storage.source).parent
        if not parent.exists():
            import os

            os.makedirs(parent)
        self._storage.json = data
        self._storage.dump(indent=2)
        return _JobData(**data)

    def run(self) -> JobResult:
        job_launcher = JobLauncher()
        job_launcher.job = self
        job_launcher.sproj = self._sproj
        job_launcher.execute()
        return job_launcher.result

    def delete(self) -> None:
        """Delete the job output assets and the job outputs itself."""

        if not isinstance(self._storage, JobFile):
            raise ScadeOneException("Cannot delete a job that does not have file storage.")

        # Delete output assets linked to the job
        for asset in self.output_assets:
            asset._delete()

        job_folder = self._storage.path.parent

        # Delete the job folder, which contains the .sjob file and generated other outputs.
        if job_folder.exists():
            shutil.rmtree(job_folder)

    def add_asset(self, asset: assets.Asset) -> None:
        """Add an asset to the job."""
        supported_asset_types = (
            assets.ModuleBodyAsset,
            assets.TestModuleAsset,
        )
        if not isinstance(asset, supported_asset_types):
            raise ScadeOneException("Only Swan module or test module assets are supported.")

        asset_path = asset.path
        if not asset_path:
            raise ScadeOneException("Cannot add asset: asset path is not available.")

        module_name = swn.Module.module_name_from_path(asset_path)
        project_modules = {str(mdl.name) for mdl in self.sproj.modules}
        if module_name not in project_modules:
            raise ScadeOneException(
                f"Cannot add asset: module '{module_name}' is not part of the project."
            )

        asset_path_str = asset_path.as_posix()

        if asset_path_str not in [Path(p).as_posix() for p in self.input_paths]:
            self.input_paths.append(asset_path_str)
            try:
                self.save()
            except Exception:
                self.input_paths.pop()
                raise

            self._input_assets.append(asset)

    def remove_asset(self, asset: assets.Asset) -> None:
        """Remove an asset from the job."""
        if not asset.path:
            return

        asset_path_str = Path(asset.path).as_posix()

        if asset_path_str in [Path(p).as_posix() for p in self.input_paths]:
            self._input_paths = [
                p for p in self._input_paths if Path(p).as_posix() != asset_path_str
            ]
            self.save()

        if any(Path(existing.path).as_posix() == asset_path_str for existing in self.input_assets):
            self._input_assets = [
                existing
                for existing in self.input_assets
                if Path(existing.path).as_posix() != asset_path_str
            ]


class CodeGenerationJob(Job):
    """Job of Code Generation kind"""

    def __init__(
        self,
        name: str,
        sproj: IProject,
        data: dict | None = None,
        storage: JobStorage | None = None,
    ) -> None:
        if data:
            super().__init__(name, JobType.CODE_GENERATION, sproj, data.get("InputPaths"), storage)
            self._properties = CodeGenerationJobProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.CODE_GENERATION, sproj)
            self._properties = CodeGenerationJobProperties(name)

    @property
    def properties(self) -> CodeGenerationJobProperties:
        "Code generation job properties"
        return self._properties

    @property
    def output_assets(self) -> list[assets.Asset]:
        """Output assets of the job - Generated code asset"""
        if self._output_assets:
            return self._output_assets

        self._output_assets = [
            assets.GeneratedCodeAsset(self.storage.path.parent, self.sproj, self.name),
            assets.CGMappingAsset(self.storage.path.parent, self.sproj, self.name),
        ]
        return self._output_assets

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
    def name_length(self) -> int:
        return self.properties.name_length

    @property
    def max_function_parameters(self) -> int | None:
        return self.properties.max_function_parameters

    @property
    def keep_assume(self) -> bool:
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

    @property
    def with_probes(self) -> bool:
        return self.properties.with_probes

    @expansion.setter
    def expansion(self, value: Union[ExpansionMode, str, None]) -> None:
        self.properties.expansion = value

    @expansion_exp.setter
    def expansion_exp(self, value: str) -> None:
        self.properties.expansion_exp = value

    @expansion_no_exp.setter
    def expansion_no_exp(self, value: str) -> None:
        self.properties.expansion_no_exp = value

    @name_length.setter
    def name_length(self, value: int) -> None:
        self.properties.name_length = value

    @max_function_parameters.setter
    def max_function_parameters(self, value: int | None) -> None:
        self.properties.max_function_parameters = value

    @keep_assume.setter
    def keep_assume(self, value: bool) -> None:
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

    @with_probes.setter
    def with_probes(self, value: bool) -> None:
        self.properties.with_probes = value


class SimulationJob(Job):
    """Job of Simulation kind"""

    def __init__(
        self,
        name: str,
        sproj: IProject,
        data: dict | None = None,
        storage: JobStorage | None = None,
    ) -> None:
        if data:
            super().__init__(name, JobType.SIMULATION, sproj, data.get("InputPaths"), storage)
            self._properties = SimulationJobProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.SIMULATION, sproj)
            self._properties = SimulationJobProperties(name)

    @property
    def properties(self) -> SimulationJobProperties:
        """Simulation job properties"""
        return self._properties

    @property
    def output_assets(self) -> list[assets.Asset]:
        """Output assets of the job - Simulation data asset"""
        if self._output_assets:
            return self._output_assets
        self._output_assets = [
            assets.SimulationDataAsset(self.storage.path.parent, self.sproj, self.name)
        ]
        return self._output_assets

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
        self,
        name: str,
        sproj: IProject,
        data: dict | None = None,
        storage: JobStorage | None = None,
    ) -> None:
        if data:
            super().__init__(name, JobType.TEST_EXECUTION, sproj, data.get("InputPaths"), storage)
            self._properties = TestExecutionProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.TEST_EXECUTION, sproj)
            self._properties = TestExecutionProperties(name)

    @property
    def properties(self) -> TestExecutionProperties:
        """Test execution job properties"""
        return self._properties

    @property
    def output_assets(self) -> list[assets.Asset]:
        """Output assets of the job - Test results asset"""
        if self._output_assets:
            return self._output_assets
        self._output_assets = [
            assets.TestResultsAsset(self.storage.path.parent, self.sproj, self.name)
        ]
        return self._output_assets

    @property
    def test_result_file(self) -> str:
        return self.properties.test_result_file

    @test_result_file.setter
    def test_result_file(self, value: str) -> None:
        self.properties.test_result_file = value


class ModelCheckJob(Job):
    """Job of Model Check kind"""

    def __init__(
        self,
        name: str,
        sproj: IProject,
        data: dict | None = None,
        storage: JobStorage | None = None,
    ) -> None:
        if data:
            super().__init__(name, JobType.MODEL_CHECK, sproj, data.get("InputPaths"), storage)
            self._properties = ModelCheckJobProperties(name, data.get("Properties"))
        else:
            super().__init__(name, JobType.MODEL_CHECK, sproj)
            self._properties = ModelCheckJobProperties(name)

    @property
    def properties(self) -> ModelCheckJobProperties:
        "Model check job properties"
        return self._properties

    @property
    def output_assets(self) -> list[assets.Asset]:
        """Output assets of the job - Model check has no output assets
        TODO to implement"""
        if self._output_assets:
            return self._output_assets
        return self._output_assets


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
        """Sets RootDeclarations. String can be passed instead of a single element list."""
        if isinstance(value, str):
            self._root_declarations = [value]
        else:
            self._root_declarations = value

    @custom_arguments.setter
    def custom_arguments(self, value: str) -> None:
        """Sets CustomArguments"""
        self._custom_arguments = value

    @name.setter
    def name(self, value: str) -> None:
        """Sets Name"""
        self._name = value

    def _to_dict(self) -> _PropertiesData:
        """Always called by one of its derived methods.
        Returns the Properties dictionary prefilled with common properties,
        to be eventually completed by the derived JobProperties class"""

        data = {}
        data["RootDeclarations"] = self._root_declarations
        data["Name"] = self._name
        data["CustomArguments"] = self._custom_arguments
        return _PropertiesData(**data)


class CodeGenerationJobProperties(JobProperties):
    """Properties of Code Generation kind Jobs.
    Parameters presented here are unique to Code Generation."""

    def __init__(self, name: str, prop: dict | None = None) -> None:
        if not prop:
            prop = {}
        super().__init__(name, prop)
        self._expansion = ExpansionMode.str_to_expansion(prop.get("Expansion"))
        self._expansion_exp = prop.get("ExpansionExp", "")
        self._expansion_no_exp = prop.get("ExpansionNoExp", "")
        self._name_length = int(prop.get("NameLength", 200))
        self._max_function_parameters: int | None = None
        try:
            self._max_function_parameters = int(prop.get("MaxFunctionParameters", ""))
        except ValueError:
            pass
        self._keep_assume = prop.get("KeepAssume") == "True"
        self._globals_prefix = prop.get("GlobalsPrefix", "")
        self._use_macros = prop.get("UseMacros") == "True"
        self._static_locals = prop.get("StaticLocals") == "True"
        self._with_probes = prop.get("Probes") == "True"

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
    def name_length(self) -> int:
        """NameLength property"""
        return self._name_length

    @property
    def max_function_parameters(self) -> int | None:
        """MaxFunctionParameters property. None if the value is unset or invalid"""
        return self._max_function_parameters

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

    @property
    def with_probes(self) -> bool:
        """Probes property. True if probes are generated, False otherwise"""
        return self._with_probes

    @expansion.setter
    def expansion(self, value: Union[ExpansionMode, str, None]) -> None:
        """Sets Expansion"""
        if isinstance(value, ExpansionMode):
            self._expansion = value
        elif isinstance(value, str):
            self._expansion = ExpansionMode.str_to_expansion(value)
        else:
            self._expansion = ExpansionMode.NONE

    @expansion_exp.setter
    def expansion_exp(self, value: str) -> None:
        """Sets ExpansionExp"""
        self._expansion_exp = value

    @expansion_no_exp.setter
    def expansion_no_exp(self, value: str) -> None:
        """Sets ExpansionNoExp"""
        self._expansion_no_exp = value

    @name_length.setter
    def name_length(self, value: int) -> None:
        """Sets NameLength"""
        self._name_length = value

    @max_function_parameters.setter
    def max_function_parameters(self, value: int | None) -> None:
        """Sets MaxFunctionParameters"""
        self._max_function_parameters = value

    @keep_assume.setter
    def keep_assume(self, value: bool) -> None:
        """Sets KeepAssume"""
        self._keep_assume = value

    @globals_prefix.setter
    def globals_prefix(self, value: str) -> None:
        """Sets GlobalsPrefix"""
        self._globals_prefix = value

    @use_macros.setter
    def use_macros(self, value: bool) -> None:
        """Sets UseMacros"""
        self._use_macros = value

    @static_locals.setter
    def static_locals(self, value: bool) -> None:
        """Sets StaticLocals"""
        self._static_locals = value

    @with_probes.setter
    def with_probes(self, value: bool) -> None:
        """Sets Probes"""
        self._with_probes = value

    def _to_dict(self) -> _PropertiesData:
        """Returns Code Generation JobProperties as a dictionary
        for saving"""

        data = super()._to_dict()
        data["Expansion"] = str(self._expansion)
        data["ExpansionExp"] = self._expansion_exp
        data["ExpansionNoExp"] = self._expansion_no_exp
        data["NameLength"] = str(self._name_length)
        data["MaxFunctionParameters"] = (
            str(self._max_function_parameters) if self._max_function_parameters is not None else ""
        )
        data["KeepAssume"] = str(self._keep_assume)
        data["GlobalsPrefix"] = self._globals_prefix
        data["UseMacros"] = str(self._use_macros)
        data["StaticLocals"] = str(self._static_locals)
        data["Probes"] = str(self._with_probes)
        return data


class SimulationJobProperties(JobProperties):
    """Properties of Simulation kind Jobs.
    Parameters presented here are unique to Simulation."""

    def __init__(self, name: str, prop: dict | None = None) -> None:
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
        """Sets FileScenario"""
        self._file_scenario = value

    @simulation_input_type.setter
    def simulation_input_type(self, value: str) -> None:
        """Sets SimulationInputType"""
        self._simulation_input_type = value

    @test_harness.setter
    def test_harness(self, value: str) -> None:
        """Sets TestHarness"""
        self._test_harness = value

    @use_cycle_time.setter
    def use_cycle_time(self, value: bool) -> None:
        """Sets UseCycleTime"""
        self._use_cycle_time = value

    @cycle_time.setter
    def cycle_time(self, value: int) -> None:
        """Sets CycleTime"""
        self._cycle_time = value

    def _to_dict(self) -> _PropertiesData:
        """Returns Simulation JobProperties as a dictionary
        for saving"""

        data = super()._to_dict()
        data["FileScenario"] = self._file_scenario
        data["SimulationInputType"] = self._simulation_input_type
        data["TestHarness"] = self._test_harness
        data["UseCycleTime"] = str(self._use_cycle_time)
        if self._use_cycle_time:
            data["CycleTime"] = str(self._cycle_time)
        return data


class TestExecutionProperties(JobProperties):
    """Properties of Test Execution kind Jobs.
    Parameters presented here are unique to Test Execution."""

    def __init__(self, name: str, prop: dict | None = None) -> None:
        if not prop:
            prop = {}
        super().__init__(name, prop)
        self._test_harness = prop.get("TestHarness", "")
        self._test_result_file = prop.get("TestResultFile", "testResults.json")

    @property
    def test_result_file(self) -> str:
        """TestResultFile property"""
        return self._test_result_file or "testResults.json"

    @test_result_file.setter
    def test_result_file(self, val: str) -> None:
        """Sets TestResultFile"""
        self._test_result_file = val

    def _to_dict(self) -> _PropertiesData:
        """Returns Test Execution JobProperties as a dictionary
        for saving"""

        data = super()._to_dict()
        data["TestHarness"] = self._test_harness
        data["TestResultFile"] = self._test_result_file
        return data


class ModelCheckJobProperties(JobProperties):
    """Properties of Model Check kind Jobs.
    Model Check has no unique parameter."""

    def __init__(self, name: str, prop: dict | None = None) -> None:
        if not prop:
            prop = {}
        super().__init__(name, prop)

    def _to_dict(self) -> _PropertiesData:
        """Returns Model Check JobProperties as a dictionary
        for saving"""

        return super()._to_dict()


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
        """Sets Job to execute"""
        self._job = value

    @sproj.setter
    def sproj(self, value: IProject) -> None:
        """Sets Job's project"""
        self._sproj = value

    def execute(self) -> bool:
        """Execute the Job via JobLauncher executable"""
        from ansys.scadeone.core import ScadeOneException

        if not self._job:
            raise ScadeOneException("No Job was assigned for JobLauncher to execute.")
        elif not self._sproj:
            raise ScadeOneException("No Job project was assigned for the JobLauncher")
        job_launcher = self._sproj.app.get_tool_path(IScadeOne.Tool.JOB_LAUNCHER)

        if not job_launcher:
            raise ScadeOneException(
                "Job launcher tool was not found. It is required for Job Execution."
            )
        if not isinstance(self._sproj.storage, ProjectFile):
            raise ScadeOneException("Cannot execute a job for a project without file storage.")
        proc = subprocess.run(
            [str(job_launcher), "run", "-p", self._sproj.storage.source, "-j", self._job.name]
        )
        self._result = JobResult(proc.returncode)
        return self._result.code == JobStatus.SUCCESS.value
