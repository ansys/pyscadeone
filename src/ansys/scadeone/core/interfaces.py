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
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import Enum, auto

from ansys.scadeone.core.common.logger import ScadeOneLogger
from ansys.scadeone.core.common.storage import ProjectFile, SwanFile

if TYPE_CHECKING:
    from ansys.scadeone.core.model.loader import SwanParser


class IProject(ABC):
    """Interface class"""

    @property
    @abstractmethod
    def app(self) -> IScadeOne:
        pass

    @property
    @abstractmethod
    def storage(self) -> ProjectFile:
        pass

    @property
    @abstractmethod
    def directory(self) -> Path:
        pass

    @abstractmethod
    def dependencies(self, all=False) -> List[IProject]:
        pass

    @property
    @abstractmethod
    def model(self) -> IModel:
        pass

    @abstractmethod
    def swan_sources(self, all: bool = False) -> List[SwanFile]:
        return []


class IScadeOne(ABC):
    """Interface class"""

    class Tool(Enum):
        """Enum for Scade One tools, used in get_tool_path method."""

        #: Job launcher tool for running Scade One jobs.
        JOB_LAUNCHER = auto()
        #: LIBRARIES for Scade One libraries.
        LIBRARIES = auto()
        #: MINGW tool for C code generation.
        MINGW = auto()
        #: Scade One installation directory.
        SCADE_ONE_LOCATION = auto()
        #: Simulator tool for running Scade One simulations.
        SIMULATOR = auto()

        def __str__(self) -> str:
            # To be completed when more tools are added
            # The returned value must correspond to the XML tag used
            # in the Configuration/modulesLocation.config file
            if self == IScadeOne.Tool.JOB_LAUNCHER:
                return "JobLauncherBinLocation"
            elif self == IScadeOne.Tool.LIBRARIES:
                return "ScadeOneLibrariesLocation"
            elif self == IScadeOne.Tool.MINGW:
                return "MingwLocation"
            elif self == IScadeOne.Tool.SIMULATOR:
                return "SimulatorLocation"
            elif self == IScadeOne.Tool.SCADE_ONE_LOCATION:
                return "ScadeOneLocation"
            return ""

    @property
    @abstractmethod
    def logger(self) -> ScadeOneLogger:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        return ""

    @property
    @abstractmethod
    def install_dir(self) -> Optional[Path]:
        """Installation directory as given when creating the ScadeOne instance."""
        pass

    @abstractmethod
    def subst_in_path(self, path: str) -> str:
        pass

    @property
    @abstractmethod
    def parser(self) -> SwanParser:
        """Shared Swan parser used by all per-project models."""
        pass

    @abstractmethod
    def find_project(self, path: Path) -> Optional[IProject]:
        """Return the loaded :py:class:`IProject` for the given sproj path, or None."""
        pass

    @abstractmethod
    def get_tool_path(self, tool: Tool) -> Path | None:
        """Get the path of a Scade One tool.

        Parameters
        ----------
        tool : IScadeOne.Tool
            Enum value representing the tool. Currently supported value is IScadeOne.Tool.JOB_LAUNCHER.
        Returns
        -------
        Path|None
            Path to the tool executable, or None if not found.
        """


class IModel(ABC):
    """Interface class for model objects."""

    @property
    @abstractmethod
    def project(self) -> IProject:
        """Project the model belongs to."""
        pass

    @abstractmethod
    def get_module_body(self, name: str) -> Optional["ModuleBody"]:  # type: ignore # noqa: F821
        pass

    @abstractmethod
    def get_module_interface(self, name: str) -> Optional["ModuleInterface"]:  # type: ignore # noqa: F821
        pass

    @abstractmethod
    def load_all_modules(
        self,
        *,
        bodies: bool = True,
        interfaces: bool = True,
        test_modules: bool = True,
        dependencies: bool = True,
    ) -> None:
        pass
