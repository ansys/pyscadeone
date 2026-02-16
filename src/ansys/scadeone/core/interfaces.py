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

# for reference in Model
# IProject: app return type is 'scadeone.IScadeOne'
# see https://softwareengineering.stackexchange.com/questions/369146/how-to-avoid-bidirectional-class-and-module-dependencies  # noqa: E501
# The point is that ScadeOne and Project uses each other
# Alternative is to create an intermediate interfaces.py.
from pathlib import Path
from typing import List, Optional
from abc import ABC, abstractmethod

from ansys.scadeone.core.common.logger import ScadeOneLogger
from ansys.scadeone.core.common.storage import ProjectStorage, SwanFile


class IProject(ABC):
    """Interface class"""

    @property
    @abstractmethod
    def app(self) -> Optional["IScadeOne"]:
        pass

    @property
    @abstractmethod
    def storage(self) -> Optional["ProjectStorage"]:
        pass

    @property
    @abstractmethod
    def directory(self) -> Optional[Path]:
        pass

    @abstractmethod
    def swan_sources(self, all: bool = False) -> List[SwanFile]:
        return []


class IScadeOne(ABC):
    """Interface class"""

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


class IModel(ABC):
    """Interface class for model objects."""

    @abstractmethod
    def get_module_body(self, name: str) -> Optional["ModuleBody"]:  # type: ignore # noqa: F821
        pass

    @abstractmethod
    def get_module_interface(self, name: str) -> Optional["ModuleInterface"]:  # type: ignore # noqa: F821
        pass
