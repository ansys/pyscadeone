# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2024 ANSYS, Inc.
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

from abc import ABC
from typing import TYPE_CHECKING, cast

from ansys.scadeone.core.common.storage import ProjectStorage
from ansys.scadeone.core.interfaces import IScadeOne
from ansys.scadeone.core.common.exception import ScadeOneException

if TYPE_CHECKING:
    from ansys.scadeone.core.project import Project
    from ansys.scadeone.core.scadeone import ScadeOne
    from ansys.scadeone.core.swan.modules import Module, ModuleInterface


class ProjectFactory:
    @staticmethod
    def create_project(app: "IScadeOne", storage: ProjectStorage) -> "Project":
        """Create a project."""
        from ansys.scadeone.core.project import Project

        project = Project(app, storage)
        project.is_new = True
        return project


class ProjectAdder:
    @staticmethod
    def add_project(app: "ScadeOne", project: "Project") -> None:
        """Add a project to the application."""
        app.projects.append(project)


class ProjectCreator(ABC):
    @staticmethod
    def _set_module_source(project: "Project", module: "Module") -> None:
        project_dir = project.directory
        if not project_dir:
            raise ScadeOneException("Cannot add module to project without directory.")
        swan_file_name = module.file_name
        module_path = project_dir / "assets" / swan_file_name
        module.source = str(module_path)

    def add_module(self, name: str) -> "Module":
        """Add a module to the project.

        Parameters
        ----------
        name: str
            Module name.

        Returns
        -------
        Module
            Module object.
        """
        from ansys.scadeone.core.svc.swan_creator.module_creator import ModuleAdder, ModuleFactory

        module = ModuleFactory.create_module(name)
        ModuleAdder.add_module(self.model, module)
        ProjectCreator._set_module_source(cast("Project", self), module)
        return module

    def add_module_interface(self, name: str) -> "ModuleInterface":
        """Add a module interface to the model.

        Parameters
        ----------
        name: str
            Module name.

        Returns
        -------
        ModuleInterface
            ModuleInterface object.
        """
        from ansys.scadeone.core.svc.swan_creator.module_creator import ModuleAdder, ModuleFactory

        module = ModuleFactory.create_module_interface(name)
        ModuleAdder.add_module(self.model, module)
        ProjectCreator._set_module_source(cast("Project", self), module)
        return module
