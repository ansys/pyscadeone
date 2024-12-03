# Copyright (c) 2024 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as swan


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(SwanString.gen_version() + "\n" + swan, module)


class TestModuleBody:

    def test_get_types(self, parser: SwanParser):
        code = gen_code(
            """
                type type0 = int32;
                type type1 = float32;
                """,
            "module0",
        )
        body = parser.module_body(code)
        types = list(body.types)
        assert len(types) == 2
        assert isinstance(types[0], swan.TypeDecl)
        assert types[0].id.value == "type0"
        assert isinstance(types[1], swan.TypeDecl)
        assert types[1].id.value == "type1"

    def test_get_sensors(self, parser: SwanParser):
        code = gen_code(
            """
                sensor sensor0: int32;
                sensor sensor1: int32;
                """,
            "module0",
        )
        body = parser.module_body(code)
        sensors = list(body.sensors)
        assert len(sensors) == 2
        assert isinstance(sensors[0], swan.SensorDecl)
        assert sensors[0].id.value == "sensor0"
        assert isinstance(sensors[1], swan.SensorDecl)
        assert sensors[1].id.value == "sensor1"

    def test_get_constants(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;
                const const1: int32 = 0;
                """,
            "module0",
        )
        body = parser.module_body(code)
        consts = list(body.constants)
        assert len(consts) == 2
        assert isinstance(consts[0], swan.ConstDecl)
        assert consts[0].id.value == "const0"
        assert isinstance(consts[1], swan.ConstDecl)
        assert consts[1].id.value == "const1"

    def test_get_groups(self, parser: SwanParser):
        code = gen_code(
            """
                group group0 = (i0: int32, i1:int32);
                group group1 = (i0: int32, i1:int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        groups = list(body.groups)
        assert len(groups) == 2
        assert isinstance(groups[0], swan.GroupDecl)
        assert groups[0].id.value == "group0"
        assert isinstance(groups[1], swan.GroupDecl)
        assert groups[1].id.value == "group1"

    def test_get_operators(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                node operator1 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        ops = list(body.operators)
        assert len(ops) == 2
        assert isinstance(ops[0], swan.Operator)
        assert ops[0].id.value == "operator0"
        assert isinstance(ops[1], swan.Operator)
        assert ops[1].id.value == "operator1"


class TestModuleInterface:

    def test_get_types(self, parser: SwanParser):
        code = gen_code(
            """
                type type0 = int32;
                type type1 = float32;
                """,
            "module0",
        )
        body = parser.module_interface(code)
        types = list(body.types)
        assert len(types) == 2
        assert isinstance(types[0], swan.TypeDecl)
        assert types[0].id.value == "type0"
        assert isinstance(types[1], swan.TypeDecl)
        assert types[1].id.value == "type1"

    def test_get_sensors(self, parser: SwanParser):
        code = gen_code(
            """
                sensor sensor0: int32;
                sensor sensor1: int32;
                """,
            "module0",
        )
        body = parser.module_interface(code)
        sensors = list(body.sensors)
        assert len(sensors) == 2
        assert isinstance(sensors[0], swan.SensorDecl)
        assert sensors[0].id.value == "sensor0"
        assert isinstance(sensors[1], swan.SensorDecl)
        assert sensors[1].id.value == "sensor1"

    def test_get_constants(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;
                const const1: int32 = 0;
                """,
            "module0",
        )
        body = parser.module_interface(code)
        consts = list(body.constants)
        assert len(consts) == 2
        assert isinstance(consts[0], swan.ConstDecl)
        assert consts[0].id.value == "const0"
        assert isinstance(consts[1], swan.ConstDecl)
        assert consts[1].id.value == "const1"

    def test_get_groups(self, parser: SwanParser):
        code = gen_code(
            """
                group group0 = (i0: int32, i1:int32);
                group group1 = (i0: int32, i1:int32);
                """,
            "module0",
        )
        body = parser.module_interface(code)
        groups = list(body.groups)
        assert len(groups) == 2
        assert isinstance(groups[0], swan.GroupDecl)
        assert groups[0].id.value == "group0"
        assert isinstance(groups[1], swan.GroupDecl)
        assert groups[1].id.value == "group1"

    def test_get_signatures(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                node operator1 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_interface(code)
        signs = list(body.signatures)
        assert len(signs) == 2
        assert isinstance(signs[0], swan.Signature)
        assert signs[0].id.value == "operator0"
        assert isinstance(signs[1], swan.Signature)
        assert signs[1].id.value == "operator1"
