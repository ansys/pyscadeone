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


# THIS MODULE CONTAINS THE CLASSES FOR TEST HARNESS AND TEST MODULE
# THIS IS NOT YET FULLY IMPLEMENTED

from typing import Union, List, Optional, Callable
from pathlib import Path

from ansys.scadeone.core.common.storage import SwanFile
from ansys.scadeone.core.swan.variable import VarDecl
from ansys.scadeone.core.swan.typedecl import Uint64Type, BoolType
from ansys.scadeone.core.swan.modules import ModuleBody, UseDirective, GlobalDeclaration
from ansys.scadeone.core.swan.scopes import Scope
import ansys.scadeone.core.swan.common as common


class Source(common.SwanItem):  # numpydoc ignore=PR01
    """Class representing a source in the harness."""

    def __init__(self, id: common.Identifier) -> None:
        super().__init__()
        self._id = id

    @property
    def id(self) -> common.Identifier:
        """Source identifier."""
        return self._id


class Oracle(common.SwanItem):  # numpydoc ignore=PR01
    """Class representing an oracle in the harness."""

    def __init__(self, id: common.Identifier) -> None:
        super().__init__()
        self._id = id

    @property
    def id(self) -> common.Identifier:
        """Oracle identifier."""
        return self._id


class SetSensorEquation(common.Equation):  # numpydoc ignore=PR01
    """Class representing a set sensor equation in the harness."""

    def __init__(self, sensor: common.PathIdentifier, value: common.Expression) -> None:
        super().__init__()
        self._sensor = sensor
        self._value = value

    @property
    def sensor(self) -> common.PathIdentifier:
        """Sensor identifier."""
        return self._sensor

    @property
    def value(self) -> common.Expression:
        """Value to set."""
        return self._value


class TestHarness(common.Declaration, common.PragmaBase, common.ModuleItem):  # numpydoc ignore=PR01
    """Test harness definition."""

    def __init__(
        self,
        id: common.Identifier,
        body: Union[Scope, common.Equation, None, Callable],
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        common.Declaration.__init__(self, id)
        common.PragmaBase.__init__(self, pragmas)
        self._body = body
        self._inputs = [VarDecl(common.Identifier("_current_cycle"), type=Uint64Type())]
        self._outputs = [VarDecl(common.Identifier("_stop_condition"), type=BoolType())]

    @property
    def body(self) -> Union[Scope, common.Equation, None]:
        """Harness body: a scope, an equation, or None."""
        if isinstance(self._body, Callable):
            body = self._body(self)
            self._body = body
            self.set_owner(self, self._body)
        return self._body

    def __str__(self) -> str:
        buffer = f"_harness {self.id}\n{self.body}\n"
        return buffer


class TestModule(ModuleBody):  # numpydoc ignore=PR01
    """Test module definition."""

    def __init__(
        self,
        name: common.PathIdentifier,
        use_directives: Optional[List[UseDirective]] = None,
        declarations: Optional[List[GlobalDeclaration]] = None,
    ) -> None:
        super().__init__(name, use_directives, declarations)

    @property
    def extension(self) -> str:
        """Returns module extension, with '.' included."""
        return ".swant"


def load_test_module(module: Path):
    """Load a test module from a file."""
    from ansys.scadeone.core.common.logger import LOGGER
    from ansys.scadeone.core.model.loader import SwanParser
    from ansys.scadeone.core.common.exception import ScadeOneException

    test = SwanFile(module)
    if not test.is_test:
        raise ScadeOneException("Model.load_source: unexpected file kind {swan.path}.")
    ast = SwanParser(LOGGER).module_body(test)
    ast.source = str(test.path)
    return ast


if __name__ == "__main__":
    # Test the module
    test = load_test_module(
        Path(r"C:\Scade One\examples\QuadFlightControl\QuadFlightControl\assets\QuadTest.swant")
    )
    print(test)
