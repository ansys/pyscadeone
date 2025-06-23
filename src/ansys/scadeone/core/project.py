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

import json
from pathlib import Path
from typing import List, Optional, Union, TypedDict

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


class _ProjectResource(TypedDict):
    """Project resource structure."""

    Kind: str
    Path: str
    Key: str


class _ProjectData(TypedDict):
    """Project data structure."""

    Version: str
    Name: str
    Dependencies: list[str]
    Resources: list[_ProjectResource]


class Project(IProject, ProjectCreator):
    """This class is the entry point of a project."""

    def __init__(self, app: IScadeOne, project: ProjectStorage) -> None:
        """Initialize a project file.

        Parameters
        ----------
        app : ScadeOne
            Application object.
        """
        self._app = app
        self._storage = project
        self._dependencies = None
        self._jobs = {}
        self._data = None
        self.is_new = False

    def save(self) -> None:
        """Save the project, that is all its modules.

        Two cases:

        - new project, saving to the `.sproj` location
        - loaded project, saving and replacing old files
        """

        if not self.is_new:
            self.model.load_all_modules()

        for module in self.model.modules:
            try:
                module_src = Path(module.source)
                module_src.parent.mkdir(parents=True, exist_ok=True)

                with module_src.open("w", newline="") as fd:
                    fd.write(swan_to_str(module))

                LOGGER.info(f"Saved: {module.source}")

            except Exception as e:
                raise ScadeOneException(f"Failed to save module {module.name.as_string}: {e}")

        if self.is_new:
            # Currently, no feature involves sproj edition
            # (dependencies, resources, project renaming...)
            self.build_sproj()

    def build_sproj(self) -> None:
        """Init SPROJ starting content."""

        Path(self._storage.path).parent.mkdir(parents=True, exist_ok=True)

        json_data = {
            "Version": FormatVersions.version("sproj"),
            "Name": self._storage.path.stem,
            "Dependencies": [],
            "Resources": [],
        }

        self._storage.set_content(json.dumps(json_data, indent=2))
        LOGGER.info(f"Created: {self._storage.source}")

    def check_exists(self, parent_path: Union[Path, str]) -> bool:
        """Return true if any of the project modules or sproj already exists
        attention, dependencies may not be checked."""

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
        return self.app.model

    @property
    def modules(self) -> List[Module]:
        return self.model.modules

    @property
    def storage(self) -> ProjectStorage:
        """Project storage."""
        return self._storage

    @property
    def data(self) -> _ProjectData:
        """Project JSON data."""
        if self._data is None:
            self._data = self.storage.load().json
        return self._data

    @property
    def directory(self) -> Optional[Path]:
        """Project directory: Path if storage is a file, else None."""
        if isinstance(self.storage, ProjectFile):
            return Path(self.storage.path.parent.as_posix())
        return None

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
        if self._dependencies is not None:
            return self._dependencies
        if self.directory is None:
            return []

        def check_path(path: str) -> Path:
            s_path = self.app.subst_in_path(path).replace("\\", "/")
            p = Path(s_path)
            if not p.is_absolute():
                p = self.directory / p
            if p.exists():
                return p
            raise ScadeOneException(f"no such file: {path}")

        paths = [check_path(d) for d in self.data["Dependencies"]]
        self._dependencies = [Project(self._app, ProjectFile(p)) for p in paths]
        return self._dependencies

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

        for project in dependencies:
            source = project.storage.source
            if source in visited:
                continue

            visited[source] = project
            project_deps = project.dependencies(all=True)
            for sub_project in project_deps:
                sub_source = sub_project.storage.source
                if sub_source in visited:
                    continue
                visited[sub_source] = sub_project

        return list(visited.values())
