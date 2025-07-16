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

from pathlib import Path  # noqa
from typing import cast

import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model import Model
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as S


@pytest.fixture
def model(cc_project):
    app = ScadeOne()
    project = app.load_project(cc_project)
    return project.model


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


class TestModel:
    def test_model_creation(self, model: Model):
        assert not model.all_modules_loaded

    def test_type_count(self, model: Model):
        def filter(obj: S.GlobalDeclaration):
            return isinstance(obj, S.TypeDeclarations)

        types = model.filter_declarations(filter)
        assert len(list(types)) == 5
        assert model.all_modules_loaded

    def test_find_regulation(self, model: Model):
        def filter(obj: S.GlobalDeclaration):
            if isinstance(obj, S.Operator):
                return str(obj.id) == "Regulation"
            return False

        decl = model.find_declaration(filter)
        assert decl is not None
        # DOES NOTHING AT RUNTIME, BUT TYPING KNOWS
        op = cast(S.Operator, decl)
        first = cast(S.VarDecl, op.inputs[0])
        assert str(first.id) == "CruiseSpeed"
        assert model.all_modules_loaded

    def test_path(self, model: Model):
        types = list(model.types)
        assert len(types) == 5
        assert types[0].get_full_path() == "CarTypes::tPercent"
        assert types[1].get_full_path() == "CarTypes::tRpm"
        assert types[2].get_full_path() == "CarTypes::tSpeed"
        assert types[3].get_full_path() == "CarTypes::tTorq"
        assert types[4].get_full_path() == "CC::tCruiseState"
