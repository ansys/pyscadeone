# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.scadeone.core import swan
from ansys.scadeone.core.svc.swan_creator import ScadeOneFactory


class TestModelCreator:
    def test_create_invalid_module_by_name(self):
        with pytest.raises(swan.ScadeOneException):
            ScadeOneFactory().module.create_module_body("module$")

    def test_create_invalid_module_by_path(self):
        with pytest.raises(swan.ScadeOneException):
            ScadeOneFactory().module.create_module_body("module::$")

    def test_create_module_body(self):
        module = ScadeOneFactory().module.create_module_body("module")
        assert module is not None
        assert swan.swan_to_str(module.name) == "module"

    def test_create_module_interface(self):
        module = ScadeOneFactory().module.create_module_interface("module")
        assert module is not None
        assert swan.swan_to_str(module.name) == "module"

    def test_create_module_namespace(self):
        module = ScadeOneFactory().module.create_module_body("lib::submodule::module")
        assert module is not None
        assert swan.swan_to_str(module.name) == "lib::submodule::module"

    def test_create_test_module(self):
        test_module = ScadeOneFactory().module.create_test_module("test_module")
        assert test_module is not None
        assert swan.swan_to_str(test_module.name) == "test_module"
