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

from typing import TYPE_CHECKING

from .diagram_creator import DiagramFactory
from .module_creator import DeclarationFactory, ModuleFactory
from .operator_creator import OperatorFactory
from .project_creator import ProjectFactory

if TYPE_CHECKING:
    pass


class ScadeOneFactory:
    """Factory for creating ScadeOne objects."""

    _instance = None

    def __init__(self) -> None:
        self.project = ProjectFactory()
        self.module = ModuleFactory()
        self.decl = DeclarationFactory()
        self.operator = OperatorFactory()
        self.diagram = DiagramFactory()

    def __new__(cls, *args, **kwargs) -> "ScadeOneFactory":
        if not cls._instance:
            cls._instance = super(ScadeOneFactory, cls).__new__(cls)
        return cls._instance
