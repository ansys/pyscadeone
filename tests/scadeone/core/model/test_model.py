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

from pathlib import Path  # noqa
from typing import cast

import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model import Model
import ansys.scadeone.core.swan as Swan
from ansys.scadeone.core.interfaces import IProject
from ansys.scadeone.core.common.storage import SwanFile


@pytest.fixture
def model(cc_project):
    app = ScadeOne()
    project = app.load_project(cc_project)
    return project.model


# Mockups for internal TU of model.load_project.
class MockySwanFile(SwanFile):
    def __init__(self):
        super().__init__("mocky.swan")

    @property
    def is_module(self) -> bool:
        return False

    @property
    def is_interface(self) -> bool:
        return False

    @property
    def is_test(self) -> bool:
        return False


class MockyStorage:
    def exists(self) -> bool:
        return True


class MockyProject(IProject):
    def __init__(self):
        self._storage = MockyStorage()

    @property
    def storage(self):
        return self._storage

    @property
    def app(self):
        # unused, but required by interface
        ...

    @property
    def directory(self) -> Path:
        # unused, but required by interface
        ...

    @property
    def model(self):
        # unused, but required by interface
        ...

    def dependencies(self, all=False) -> list[IProject]:
        # unused, but required by interface
        return []

    def swan_sources(self) -> list[SwanFile]:
        return [MockySwanFile()]


class TestModel:
    def test_model_creation(self, model: Model):
        assert not model.is_all_modules_loaded

    # @pytest.skip(reason="This test is not working need to migrate to swan version 2027")
    def test_type_count(self, model: Model):
        def filter(obj: Swan.GlobalDeclaration):
            return isinstance(obj, Swan.TypeDeclarations)

        types = model.filter_declarations(filter)
        assert len(list(types)) == 5
        assert model.is_all_modules_loaded

    def test_find_regulation(self, model: Model):
        def filter(obj: Swan.GlobalDeclaration):
            if isinstance(obj, Swan.OperatorDefinition):
                return str(obj.id) == "Regulation"
            return False

        decl = model.find_declaration(filter)
        assert decl is not None
        # DOES NOTHING AT RUNTIME, BUT TYPING KNOWS
        op = cast(Swan.OperatorDefinition, decl)
        first = cast(Swan.VarDecl, op.inputs[0])
        assert str(first.id) == "CruiseSpeed"
        assert model.is_all_modules_loaded

    def test_path(self, model: Model):
        types = list(model.types)
        assert len(types) == 5
        assert types[0].get_full_path() == "CarTypes::tPercent"
        assert types[1].get_full_path() == "CarTypes::tRpm"
        assert types[2].get_full_path() == "CarTypes::tSpeed"
        assert types[3].get_full_path() == "CarTypes::tTorq"
        assert types[4].get_full_path() == "CC::tCruiseState"

    def test_model_load_project_bad_swan(self):
        mocky = MockyProject()
        model = Model(mocky)
        with pytest.raises(Exception, match="Unexpected Swan file kind"):
            model.load_project(mocky)

    def test_module_exists(self, model: Model):
        # CC project's own modules
        for f in ["CC.swan", "CarTypes.swani"]:
            swan_file = SwanFile(f)
            assert model.module_exists(swan_file)
        # Utils.swan belongs to a dependency project, not to CC's own model
        assert not model.module_exists(SwanFile("Utils.swan"))
        assert not model.module_exists(SwanFile("NonExistingModule.swan"))
