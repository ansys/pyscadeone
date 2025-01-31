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

from pathlib import Path
from typing import Union, List
from typing_extensions import Self

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.interfaces import IScadeOne, IProject
from ansys.scadeone.core.common.storage import ProjectStorage, ProjectFile, SwanFile

from ansys.scadeone.core.model import Model


class Project(IProject):
    """This class is the entry point of a project."""

    def __init__(self, app: IScadeOne, project: ProjectStorage):
        """Initialize a project file.

        Parameters
        ----------
        app : ScadeOne
            Application object.
        """
        self._app = app
        self._storage = project
        self._model = None
        self._dependencies = None
        self._jobs = {}
        self._data = None

    @property
    def app(self) -> IScadeOne:
        """Access to current Scade One application."""
        return self._app

    @property
    def storage(self) -> ProjectStorage:
        """Project storage."""
        return self._storage

    @property
    def model(self):
        """Access to model represented by the sources."""
        if self._model is None:
            self._model = Model().configure(self)
        return self._model

    @property
    def data(self):
        """Project JSON data."""
        if self._data is None:
            self._data = self.storage.load().json
        return self._data

    @property
    def directory(self) -> Union[Path, None]:
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
            if swan.suffix in (".swan", ".swani")
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

    def _get_dependencies(self) -> List[Self]:
        """Projects directly referenced as dependencies.

        Returns
        -------
        list[Project]
            List of referenced projects.

        Raises
        ------
        ScadeOneException
            Raises exception if a project file does not exist.
        """
        if self._dependencies is not None:
            return self._dependencies
        if self.directory is None:
            return []

        def check_path(path: str):
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

    def dependencies(self, all=False) -> List[Self]:
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
