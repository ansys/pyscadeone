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
from typing import List, Optional, Union

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.storage import ProjectFile, ProjectStorage
from ansys.scadeone.core.interfaces import IScadeOne as IScadeOne
from ansys.scadeone.core.project import Project


class ScadeOne(IScadeOne):
    """Scade One application API."""

    def __init__(self, install_dir: Optional[Union[str, Path]] = None):
        self._logger = LOGGER
        self._projects = []
        self._install_dir = Path(install_dir) if isinstance(install_dir, str) else install_dir

    @property
    def install_dir(self) -> Union[Path, None]:
        """Installation directory as given when creating the ScadeOne instance."""
        return self._install_dir

    @property
    def version(self) -> str:
        "API version."
        from ansys.scadeone.core import __version__

        return __version__

    @property
    def logger(self):
        return self._logger

    # For context management
    def __enter__(self):
        self.logger.info("Entering context")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type and not isinstance(exc_type, Union[ScadeOneException, SystemExit]):
            msg = f"Exiting on exception {exc_type}"
            if exc_value:
                msg += f" with value {exc_value}"
            self.logger.exception(msg)
        self.close()
        # propagate exception
        return False

    # end context management

    def close(self):
        """Close application, releasing any connection."""
        pass

    def __del__(self):
        self.close()

    def load_project(self, storage: Union[ProjectStorage, str, Path]) -> Union[Project, None]:
        """Load a Scade One project.

        Parameters
        ----------
        storage : Union[ProjectAsset, Path, str]
            Storage containing project data.

        Returns
        -------
        Project|None
            Project object, or None if file does not exist.
        """
        if not isinstance(storage, ProjectStorage):
            storage = ProjectFile(storage)
        if not storage.exists():
            self.logger.error(f"Project does not exist {storage.source}")
            return None
        project = Project(self, storage)
        self._projects.append(project)
        return project

    @property
    def projects(self) -> List[Project]:
        """Return the loaded projects.

        Returns
        -------
        List[Project]
           Loaded projects.
        """
        return self._projects

    def subst_in_path(self, path: str) -> str:
        """Substitute $(SCADE_ONE_LIBRARIES_DIR) in path.

        if :py:attr:`ScadeOne.install_dir` is None, no change is made.
        """
        if self.install_dir:
            return path.replace("$(SCADE_ONE_LIBRARIES_DIR)", str(self.install_dir / "libraries"))

        return path
