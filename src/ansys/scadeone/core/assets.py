# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
import os
from pathlib import Path
from typing import TYPE_CHECKING, Union, List, Optional
from abc import ABC, abstractmethod
from ansys.scadeone.core.common.storage import JobFile
import ansys.scadeone.core.swan as swan

if TYPE_CHECKING:
    from ansys.scadeone.core.job import Job
    from ansys.scadeone.core.project import Project
    from ansys.scadeone.core.svc.simdata import FileBase
    from ansys.scadeone.core.svc.test import TestResults
    from ansys.scadeone.core.swan import ModuleBody, ModuleInterface, TestModule
    from ansys.scadeone.core.svc.cgmapping import CGMapping
AssetOpenReturnType = Union[
    "ModuleBody",
    "ModuleInterface",
    "TestModule",
    "FileBase",
    Path,
    "TestResults",
    "CGMapping",
]


class Asset(ABC):
    """Base class for project assets.

    Parameters
    ----------
    path : Path | str
        Asset path relative to the project directory.
    project : Project
        Project owning the asset.
    job_name : str, optional
        Name of the job associated with the asset.
    """

    def __init__(
        self,
        path: Union[str, Path],
        project: "Project",
        job_name: Optional[str] = None,
    ) -> None:
        self._path = path
        self._project = project
        self._job_name = job_name

    @property
    def path(self) -> Optional[Path]:
        """Get the asset path.

        Returns
        -------
        Optional[Path]
            The asset path relative to the project directory.
        """
        _rel_path = Path(self._path) if isinstance(self._path, str) else self._path
        if _rel_path.is_absolute():
            try:
                return _rel_path.relative_to(self._project.directory)
            except ValueError:
                rel_path = os.path.relpath(_rel_path, start=self._project.directory)
                return Path(rel_path)
        return _rel_path

    def _relative_to_project(self, path: Path) -> Path:
        """Return *path* relative to the project directory when possible."""
        try:
            return path.relative_to(self._project.directory)
        except ValueError:
            rel_path = os.path.relpath(path, start=self._project.directory)
            return Path(rel_path)

    def _absolute_from_project(self, path: Path) -> Path:
        """Return an absolute path for a project-relative asset path."""
        if path.is_absolute():
            return path
        return Path(self._project.directory) / path

    @property
    def job_name(self) -> Optional[str]:
        """Get the name of the job associated with the asset.

        Returns
        -------
        Optional[str]
            The name of the associated job, or None if not associated with any job.
        """
        return self._job_name

    @property
    def producer_job(self) -> Optional["Job"]:
        """Give the job produced by the asset.

        Returns
        -------
        Job | None
            The job produced by the asset, or None if not associated with a job.
        """
        return self._project.get_job(self._job_name) if self._job_name else None

    @property
    def consumer_jobs(self) -> List["Job"]:
        """Jobs consumed by the asset, if available in the project.

        Returns
        -------
        List[Job]
            List of job consumed by the asset. Empty if not available or not applicable.
        """
        if isinstance(self, (ModuleBodyAsset, TestModuleAsset)):
            if not self.path:
                return []
            consumers = []
            for job in self._project.jobs:
                for ipt in job.input_paths:
                    if Path(ipt).name == self.path.name:
                        consumers.append(job)
            return consumers
        else:
            return []

    @abstractmethod
    def open(self, **kwargs) -> AssetOpenReturnType:
        """Open asset

        Returns
        -------
        AssetOpenReturnType
            Asset instance depends on its kind.
        """
        raise NotImplementedError("Asset.open must be implemented by child classes.")


class ModuleBodyAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)

    def open(self, **kwargs) -> "ModuleBody":
        """Open asset

        Returns
        -------
        ModuleBody
            The module body instance corresponding to the asset.
        """
        if not self.path:
            raise ValueError("Asset path is not set; cannot open module body.")
        module_name = swan.Module.module_name_from_path(self.path)
        module_body = self._project.model.get_module_body(module_name)
        if not module_body:
            raise ValueError(f"Module body not found for path: {self.path}")
        return module_body


class ModuleInterfaceAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)

    def open(self, **kwargs) -> "ModuleInterface":
        """Open asset

        Returns
        -------
        ModuleInterface
            The module interface instance corresponding to the asset.
        """
        if not self.path:
            raise ValueError("Asset path is not set; cannot open module interface.")
        module_name = swan.Module.module_name_from_path(self.path)
        module_interface = self._project.model.get_module_interface(module_name)
        if not module_interface:
            raise ValueError(f"Module interface not found for path: {self.path}")
        return module_interface


class TestModuleAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)

    def open(self, **kwargs) -> "TestModule":
        """Open asset

        Returns
        -------
        TestModule
            The test module instance corresponding to the asset.
        """
        if not self.path:
            raise ValueError("Asset path is not set; cannot open test module.")
        module_name = swan.Module.module_name_from_path(self.path)
        module_test = self._project.model.get_test_module(module_name)
        if not module_test:
            raise ValueError(f"Test module not found for path: {self.path}")
        return module_test


class SimulationDataAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)
        self._file: Optional["FileBase"] = None

    @property
    def path(self) -> Optional[Path]:
        """Get the simulation data trace file path.

        Returns
        -------
        Optional[Path]
            The simulation trace file path, or None if unavailable.
        """
        from ansys.scadeone.core.job import SimulationJob

        if (
            not self._job_name
            or not isinstance(job := self._project.get_job(self._job_name), SimulationJob)
            or not isinstance(job.storage, JobFile)
        ):
            return None

        trace_file = Path(job.storage.source).parent / "out" / "trace.sd"
        if not trace_file.exists():
            return None

        return self._relative_to_project(trace_file)

    def _delete(self) -> None:
        """Delete associated physical items.

        Returns
        -------
            None
        """
        if not self.path:
            return  # If path is not available, there's no physical file to delete
        trace_file = self._absolute_from_project(self.path)
        if self._file:
            self._file.close()
        trace_file.unlink()

    def open(self, mode: str = "r", **kwargs) -> "FileBase":
        """Open the simulation data for reading or editing.

        Parameters
        ----------
        mode : str, optional
            Opening mode for the file: 'r' - reading or 'w' - writing to edit the file,
            by default "r".

        Returns
        -------
        FileBase
            The simulation data file instance.
        """
        import ansys.scadeone.core.svc.simdata as sd

        if not self.path:
            raise ValueError(
                f"Cannot open simulation data asset: No trace file for job: {self._job_name}"
            )
        trace_file = self._absolute_from_project(self.path)
        if mode == "r":
            self._file = sd.open_file(str(trace_file))
        else:
            self._file = sd.edit_file(str(trace_file))
        return self._file


class GeneratedCodeAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)

    @property
    def path(self) -> Optional[Path]:
        """Get the code generation output directory path.

        Returns
        -------
        Optional[Path]
            The code generation output directory path, or None if unavailable.
        """
        from ansys.scadeone.core.job import CodeGenerationJob

        if (
            not self._job_name
            or not isinstance(job := self._project.get_job(self._job_name), CodeGenerationJob)
            or not isinstance(job.storage, JobFile)
        ):
            return None

        code_dir = Path(job.storage.source).parent / "out" / "code"

        if not code_dir.exists():
            return None

        return self._relative_to_project(code_dir)

    def _delete(self) -> None:
        """Delete associated physical items.

        Returns
        -------
            None
        """
        code_dir = self._absolute_from_project(self.path) if self.path else None
        if not code_dir:
            return  # If path is not available, there's no physical directory to delete
        shutil.rmtree(code_dir)

    def open(self, **kwargs) -> Path:
        """Open asset

        Returns
        -------
        Path
            The path to the generated code file corresponding to the asset.
        """
        code_dir = self._absolute_from_project(self.path) if self.path else None
        if not code_dir:
            raise ValueError(
                f"Cannot open generated code asset: No code directory for job: {self._job_name}"
            )
        return code_dir


class TestResultsAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)

    @property
    def path(self) -> Optional[Path]:
        """Get the test result file path.

        Returns
        -------
        Optional[Path]
            The path to the test result file, or None if unavailable.
        """
        from ansys.scadeone.core.job import TestExecutionJob

        if (
            not self._job_name
            or not isinstance(job := self._project.get_job(self._job_name), TestExecutionJob)
            or not isinstance(job.storage, JobFile)
        ):
            return None

        result_file = Path(job.storage.source).parent / "out" / job.test_result_file
        if not result_file.exists():
            return None

        return self._relative_to_project(result_file)

    def _delete(self) -> None:
        """Delete associated physical items.

        Returns
        -------
            None
        """
        if not self.path:
            return  # If path is not available, there's no physical file to delete
        self._absolute_from_project(self.path).unlink()

    def open(self, **kwargs) -> "TestResults":
        """Open asset

        Returns
        -------
        TestResults
            The test results instance corresponding to the asset.
        """
        from ansys.scadeone.core.svc.test import TestResultsParser

        trace_file = self._absolute_from_project(self.path) if self.path else None
        if not trace_file or not (test_result := TestResultsParser.load(trace_file)):
            raise ValueError(
                f"Cannot open test results asset: No file generated for job: {self._job_name}"
            )
        return test_result


class CGMappingAsset(Asset):
    def __init__(
        self, path: Union[str, Path], project: "Project", job_name: Optional[str] = None
    ) -> None:
        super().__init__(path, project, job_name)

    @property
    def path(self) -> Optional[Path]:
        """Get the CG mapping file path.

        Returns
        -------
        Optional[Path]
            The path to the CG mapping file, or None if unavailable.
        """
        from ansys.scadeone.core.job import CodeGenerationJob

        if (
            not self._job_name
            or not isinstance(job := self._project.get_job(self._job_name), CodeGenerationJob)
            or not isinstance(job.storage, JobFile)
        ):
            return None

        mapping_file = Path(job.storage.source).parent / "out" / "cg_map.json"
        if not mapping_file.exists():
            return None

        return self._relative_to_project(mapping_file)

    def _delete(self) -> None:
        """Delete physical item.

        Returns
        -------
            None
        """
        if not self.path:
            return  # If path is not available, there's no physical file to delete
        self._absolute_from_project(self.path).unlink()

    def open(self, **kwargs) -> "CGMapping":
        """Open asset

        Returns
        -------
        CGMapping
            The CGMapping corresponding to the asset.
        """
        from ansys.scadeone.core.svc.cgmapping import CGMapping

        if not self.path:
            raise ValueError(
                f"Cannot open CG mapping asset: No mapping file for job: {self._job_name}"
            )
        mapping_file = self._absolute_from_project(self.path)
        return CGMapping.from_file(mapping_file)
