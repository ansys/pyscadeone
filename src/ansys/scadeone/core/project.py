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

from enum import Enum, auto
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import (
    JobFile,
    ProjectFile,
    ProjectStorage,
    SwanFile,
)
from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.interfaces import IProject, IScadeOne
from ansys.scadeone.core.job import Job
from ansys.scadeone.core.svc.swan_creator.job_creator import JobFactory
from ansys.scadeone.core.model.model import Model
from ansys.scadeone.core.svc.swan_creator.project_creator import ProjectCreator
from ansys.scadeone.core.svc.swan_printer import swan_to_str
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.swan.modules import Module


class ResourceKind(Enum):
    """Project resource kind."""

    #: Header file
    HEADER_FILE = auto()
    #: Source file
    SOURCE_FILE = auto()
    #: Simulation data file
    SIMULATION_DATA = auto()

    def file_extension(self) -> str:
        """Returns expected file extension for the resource kind."""

        if self is ResourceKind.HEADER_FILE:
            return ".h"
        if self is ResourceKind.SOURCE_FILE:
            return ".c"
        if self is ResourceKind.SIMULATION_DATA:
            return ".sd"
        return ""

    @staticmethod
    def str_to_kind(kind_str: str) -> "ResourceKind":
        """Converts sproj kind string to a ResourceKind enum."""

        if kind_str == "HeaderFile":
            return ResourceKind.HEADER_FILE
        if kind_str == "SourceFile":
            return ResourceKind.SOURCE_FILE
        if kind_str == "SimulationData":
            return ResourceKind.SIMULATION_DATA
        raise ScadeOneException(f"Unknown resource kind: {kind_str}")

    def __str__(self) -> str:
        if self is ResourceKind.HEADER_FILE:
            return "HeaderFile"
        if self is ResourceKind.SOURCE_FILE:
            return "SourceFile"
        if self is ResourceKind.SIMULATION_DATA:
            return "SimulationData"
        return "Unknown"


class Resource:
    """Project resource.

    Parameters
    ----------
    kind : ResourceKind
        Kind of the resource (header, source, simulation data).
    path : Path
        Path to the resource.
    key : str, optional
        Key of the resource (simulation data only).
    """

    def __init__(self, kind: ResourceKind, path: Path, key: Optional[str] = None) -> None:
        if kind is not ResourceKind.SIMULATION_DATA and key:
            raise ScadeOneException("Only simulation data resources use a key.")
        if kind is ResourceKind.SIMULATION_DATA and not key:
            raise ScadeOneException("Simulation data resources must have a key.")
        if isinstance(path, str):
            path = Path(path)
        if path.suffix != kind.file_extension():
            raise ScadeOneException(
                (
                    f"{path.suffix if path.suffix else 'No extension'} file was used for "
                    f"{kind} resource. Expected file: {kind.file_extension()}."
                )
            )
        self._kind = kind
        self._path = path
        self._key = key if key else None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return False
        return self._kind == other._kind and self._path == other._path and self._key == other._key

    @property
    def path(self) -> Path:
        """Path to the resource."""
        return self._path

    @path.setter
    def path(self, value: Union[str, Path]) -> None:
        """Set the path to the resource."""
        if isinstance(value, str):
            value = Path(value)
        if value.suffix != self._kind.file_extension():
            raise ScadeOneException(
                f"File extension was changed from {self._path.suffix} to {value.suffix}."
            )
        self._path = value

    @property
    def key(self) -> Optional[str]:
        """Key of the resource (simulation data only)."""
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        """Set the key of the resource."""
        if self._kind is not ResourceKind.SIMULATION_DATA:
            raise ScadeOneException("Only simulation data resources use a key.")
        if not value:
            raise ScadeOneException("Key can't be empty.")
        self._key = value

    @property
    def kind(self) -> ResourceKind:
        """Kind of the resource."""
        return self._kind

    def _to_json_dict(self) -> Dict[str, str]:
        """Return the resource as a dictionary."""

        project_dict = {
            "Kind": str(self._kind),
            "Path": str(self._path),
            "Key": self._key if self._key else "",
        }
        return project_dict

    def __repr__(self) -> str:
        return f"Resource(kind={self._kind}, path={self._path}, key={self._key})"


class Project(IProject, ProjectCreator):
    """This class is the entry point of a project.

    Parameters
    ----------
    app : ScadeOne
        Application object.
    project : ProjectStorage
        Project storage object.
    is_new : bool, optional
        True if the project is new, that is, it has not been loaded from a file.
    """

    def __init__(self, app: IScadeOne, project: ProjectStorage, is_new: bool = False) -> None:
        self._app = app
        self._storage = project
        self._dependencies: List[str] = []
        self._jobs = {}
        self._resources: list[Resource] = []
        self._is_new = is_new
        self._is_modified = False
        self._name = (
            self._storage.path.stem if isinstance(self._storage, ProjectFile) else "New Project"
        )
        self._version = None

        self._load_project_data()  # take of is_new for default value

    def _load_project_data(self) -> None:
        """Load project data from the storage.

        If the project is new, it will not load any data.
        """
        if not self._is_new:
            try:
                _data = self.storage.load().json
                self._name = _data["Name"]
                self._version = _data["Version"]
                for dep in _data["Dependencies"]:
                    self._dependencies.append(dep)
                for res in _data.get("Resources", []):
                    kind = ResourceKind.str_to_kind(res["Kind"])
                    resource = Resource(kind, res["Path"], res.get("Key"))
                    self._resources.append(resource)
            except Exception as e:
                raise ScadeOneException(f"Failed to load project data: {e}")
        else:
            self._version = FormatVersions.version("sproj")

    def set_modified(self) -> None:
        """Set the project as modified."""

        self._is_modified = True
        self._version = FormatVersions.version("sproj")

    def save(self) -> None:
        """Save the following:

        - Project modules
        - Project dependencies
        - Project resources
        - sproj version

        Two cases:

        - new project, saving to the `.sproj` location
        - loaded project, saving and replacing old files
        """

        if not self._is_new:
            self.model.load_all_modules()

        for module in self.model.modules:
            if not (source := module.source):
                raise ScadeOneException(f"Module {module.name.as_string} has no source to save.")
            try:
                module_src = Path(source)
                module_src.parent.mkdir(parents=True, exist_ok=True)

                with module_src.open("w", newline="") as fd:
                    fd.write(swan_to_str(module))

                LOGGER.info(f"Saved: {module.source}")

            except Exception as e:
                raise ScadeOneException(f"Failed to save module {module.name.as_string}: {e}")

        if self._is_new or self._is_modified:
            self._save_sproj()

    def _save_sproj(self) -> None:
        """Init SPROJ starting content."""

        Path(self._storage.path).parent.mkdir(parents=True, exist_ok=True)

        json_data = {
            "Version": self._version,
            "Name": self._name,
            "Dependencies": self._dependencies,
            "Resources": [resource._to_json_dict() for resource in self._resources],
        }

        self._storage.set_content(json.dumps(json_data, indent=2))
        self._is_modified = False
        LOGGER.info(f"Created: {self._storage.source}")

    def check_exists(self, parent_path: Union[Path, str]) -> bool:
        """Return true if any of the project modules or sproj already exists

        .. warning::

           Dependencies may not be checked."""

        if Path(self._storage.source).exists():
            return True
        for module in self.model.modules:
            file_path = parent_path / Path(module.source)
            if file_path.exists():
                return True
        return False

    def load_jobs(self) -> List[Job]:
        """(Re)load and return all the jobs of a project."""
        self._jobs = {}
        if self.directory:
            job_files = [
                JobFile(job) for job in self.directory.glob("jobs/**/*") if job.name == ".sjob"
            ]
            for job in job_files:
                job.load()
                job_json = job.json
                job_name = job_json["Properties"]["Name"]
                typed_job = JobFactory.create_job(job, self)
                if typed_job:
                    self._jobs[job_name] = typed_job
        return self.jobs

    def get_job(self, name: str) -> Union[Job, None]:
        """Get a job from its name."""
        return self._jobs.get(name)

    @property
    def jobs(self) -> List[Job]:
        """Return job files of the project."""
        return list(self._jobs.values())

    @property
    def app(self) -> IScadeOne:
        """Access to current Scade One application."""
        return self._app

    @property
    def model(self) -> Model:
        """Access to the project model."""
        return self.app.model

    @property
    def modules(self) -> List[Module]:
        """Loaded modules from the model"""
        return self.model.modules

    @property
    def storage(self) -> ProjectStorage:
        """Project storage."""
        return self._storage

    @property
    def directory(self) -> Optional[Path]:
        """Project directory: Path if storage is a file, else None."""
        if isinstance(self.storage, ProjectFile):
            return Path(self.storage.path.parent.as_posix())
        return None

    @property
    def resources(self) -> List[Resource]:
        """Project resources."""
        return self._resources

    def _get_swan_sources(self) -> List[SwanFile]:
        """Return Swan files of project.

        Returns
        -------
        List[SwanFile]
            List of SwanFile objects.
        """
        if self.directory is None:
            return []
        # glob uses Unix-style. Cannot have a fancy re, so need to check
        sources = [
            SwanFile(swan)
            for swan in self.directory.glob("assets/*.*")
            if swan.suffix in (".swan", ".swani", ".swant")
        ]
        return sources

    def swan_sources(self, all=False) -> List[SwanFile]:
        """Return all Swan sources from project.

        If all is True, include also sources from project dependencies.

        Returns
        -------
        list[SwanFile]
            List of all SwanFile objects.
        """
        sources = self._get_swan_sources()
        if all is False:
            return sources
        for lib in self.dependencies(all=True):
            sources.extend(lib.swan_sources())
        return sources

    def _get_dependencies(self) -> List["Project"]:
        """Projects directly referenced as dependencies.

        Returns
        -------
        list[Project]
            List of referenced projects.

        Raises
        ------
        ScadeOneException
            Raise exception if a project file does not exist.
        """
        if self.directory is None:
            # case of a project not created from a file (future use case)
            return []

        def get_path(path: str) -> Path:
            s_path = self.app.subst_in_path(path).replace("\\", "/")
            p = Path(s_path)
            if not p.is_absolute():
                p = self.directory / p
            if p.exists():
                return p
            raise ScadeOneException(f"no such file: {path}")

        paths = [get_path(d) for d in self._dependencies]
        dependencies = [Project(self._app, ProjectFile(p)) for p in paths]
        return dependencies

    def dependencies(self, all=False) -> List["Project"]:
        """Project dependencies as list of Projects.

        If all is True, include recursively dependencies of dependencies.

        A dependency occurs only once.
        """
        dependencies = self._get_dependencies()
        if not all:
            return dependencies

        # compute recursively all dependencies
        # One a project is visited, it is marked as visited
        # As returned Projects may be different objects project.dependencies() calls
        # one discriminates using the project source string.
        visited = {}

        def aux_visit(project: "Project"):
            """Auxiliary function to visit project dependencies."""
            for dep in project._get_dependencies():
                source = dep.storage.source  # type: ignore
                if source in visited:
                    continue
                visited[source] = dep
                aux_visit(dep)

        aux_visit(self)
        return list(visited.values())

    def add_resource(
        self,
        kind: ResourceKind,
        file_path: Union[Path, str],
        key_name: Optional[str] = None,
        exist_check: bool = True,
    ) -> Resource:
        """Add a new resource to the project.
        For simulation data files (:py:attr:`ResourceKind.SIMULATION_DATA`),
        `key_name` must be provided.

        Parameters
        ----------
        kind : ResourceKind
            Kind of the resource.
        file_path : Union[Path, str]
            Path to the resource file.
        key_name : Optional[str]
            Key of the resource (for simulation data only).
        exist_check : bool
            Checks if file exists, raises exception if not. Default True.
            Can be disabled for debugging or placeholder use.

        Returns
        -------
        Resource
            The created resource object.

        Raises
        ------
        ScadeOneException
            If the resource file does not exist and `exist_check` is True.
            If the key name is already used in the project.
            If the file path is already in the project resources.
        """

        if exist_check and not Path(file_path).exists():
            raise ScadeOneException(f"Resource file '{file_path}' does not exist.")
        if key_name and key_name in [r.key for r in self.resources]:
            raise ScadeOneException(f"Resource key '{key_name}' already used in project.")
        _file_path = Path(file_path) if isinstance(file_path, str) else file_path
        if _file_path in [r.path for r in self.resources]:
            raise ScadeOneException(f"Resource '{file_path}' already in project.")
        resource = Resource(kind, _file_path, key_name)
        self.set_modified()
        self._resources.append(resource)
        return resource

    def add_dependency(self, project: IProject) -> None:
        """Add a project as a dependency.

        Parameters
        ----------
        project : IProject
            Project to add as a dependency.

        Raises
        ------
        ScadeOneException
            If the project is the same as the current project.
        """
        if project.storage.source == self.storage.source:
            raise ScadeOneException("A project cannot depend on itself.")
        rel_path = os.path.relpath(project.storage.source, str(self.directory))
        if rel_path not in self._dependencies:
            self._dependencies.append(rel_path)
            self.set_modified()

    def remove_dependency(self, project: IProject) -> None:
        """Remove a project from the dependencies.

        Parameters
        ----------
        project : IProject
            Project to remove from the dependencies.

        Raises
        ------
        ScadeOneException
            If the project is not a dependency.
        """
        rel_path = os.path.relpath(project.storage.source, str(self.directory))
        if rel_path in self._dependencies:
            self._dependencies.remove(rel_path)
            self.set_modified()
        else:
            raise ScadeOneException("The project is not a dependency.")
