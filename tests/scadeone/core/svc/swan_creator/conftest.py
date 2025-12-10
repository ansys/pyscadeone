# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model.model import Model
from ansys.scadeone.core.model.loader import SwanParser
from ansys.scadeone.core.svc.swan_creator import ScadeOneFactory


@pytest.fixture(scope="session")
def app():
    return ScadeOne()


@pytest.fixture
def module_factory():
    return ScadeOneFactory().module


@pytest.fixture
def diagram_factory():
    return ScadeOneFactory().diagram


@pytest.fixture
def operator_factory():
    return ScadeOneFactory().operator


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


@pytest.fixture
def model(app):
    return Model(app)
