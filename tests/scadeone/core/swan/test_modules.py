from typing import cast

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

import pytest

from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as swan
from ansys.scadeone.core.swan import Module, PathIdentifier


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(gen_swan_version() + "\n" + swan, module)


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
        ops = list(body.signatures)
        assert len(ops) == 2
        assert isinstance(ops[0], swan.Signature)
        assert ops[0].id.value == "operator0"
        assert isinstance(ops[1], swan.Signature)
        assert ops[1].id.value == "operator1"

    def test_add_use_directive(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        path_id = PathIdentifier.from_string("module1")
        module = Module(path_id)
        use_directive = body.use(module)
        assert use_directive is not None
        assert isinstance(use_directive, swan.UseDirective)
        assert swan.swan_to_str(use_directive) == "use module1;\n"
        assert body.use_directives[0] == use_directive

    def test_add_declaration(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        const = body.add_declaration("const const0: int32 = 0")
        assert const is not None
        assert isinstance(const, swan.ConstDecl)
        assert swan.swan_to_str(const.id) == "const0"
        assert swan.swan_to_str(const.type) == "int32"
        assert swan.swan_to_str(const.value) == "0"

    def test_add_constant(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        const = body.add_constant("const0", "int32", "0")
        assert const is not None
        assert isinstance(const, swan.ConstDecl)
        assert swan.swan_to_str(const.id) == "const0"
        assert swan.swan_to_str(const.type) == "int32"
        assert swan.swan_to_str(const.value) == "0"
        assert body.constants[0] == const
        assert isinstance(body.declarations[1], swan.ConstDeclarations)
        assert len(cast(swan.ConstDeclarations, body.declarations[1]).constants) == 1
        assert cast(swan.ConstDeclarations, body.declarations[1]).constants[0] == const

    def test_add_type(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        type = body.add_type("type0", "int32")  # noqa
        assert type is not None
        assert isinstance(type, swan.TypeDecl)
        assert swan.swan_to_str(type.id) == "type0"
        assert swan.swan_to_str(type.definition) == "int32"  # noqa
        assert body.types[0] == type
        assert isinstance(body.declarations[1], swan.TypeDeclarations)
        assert len(cast(swan.TypeDeclarations, body.declarations[1]).types) == 1
        assert cast(swan.TypeDeclarations, body.declarations[1]).types[0] == type

    def test_add_enum(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        enum = body.add_enum("enum0", ["HIGH", "MEDIUM", "LOW"])
        assert enum is not None
        assert isinstance(enum, swan.TypeDecl)
        assert swan.swan_to_str(enum) == "enum0 = enum {HIGH, MEDIUM, LOW}"

    def test_add_struct(self, parser: SwanParser):
        code = gen_code(
            """
                type type0 = int32;
                """,
            "module0",
        )
        body = parser.module_body(code)
        struct = body.add_struct("struct0", {"a": "int32", "b": "int32"})
        assert struct is not None
        assert isinstance(struct, swan.TypeDecl)
        assert swan.swan_to_str(struct) == "struct0 = struct {a: int32, b: int32}"

    def test_add_sensor(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        sensor = body.add_sensor("sensor0", "int32")
        assert sensor is not None
        assert isinstance(sensor, swan.SensorDecl)
        assert swan.swan_to_str(sensor.id) == "sensor0"
        assert swan.swan_to_str(sensor.type) == "int32"
        assert body.sensors[0] == sensor
        assert isinstance(body.declarations[1], swan.SensorDeclarations)
        assert len(cast(swan.SensorDeclarations, body.declarations[1]).sensors) == 1
        assert cast(swan.SensorDeclarations, body.declarations[1]).sensors[0] == sensor

    def test_add_group(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        group = body.add_group("group0", "int32")
        assert group is not None
        assert isinstance(group, swan.GroupDecl)
        assert swan.swan_to_str(group) == "group0 = (int32)"
        assert body.groups[0] == group

    def test_add_group_type_list(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        group = body.add_group("group0", ["int32", "int32", "int32"])
        assert group is not None
        assert isinstance(group, swan.GroupDecl)
        assert swan.swan_to_str(group) == "group0 = (int32, int32, int32)"
        assert body.groups[0] == group

    def test_add_group_type_dict(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        group = body.add_group("group0", {"a": "int32", "b": "int32", "c": "int32"})
        assert group is not None
        assert isinstance(group, swan.GroupDecl)
        assert swan.swan_to_str(group) == "group0 = (a: int32, b: int32, c: int32)"
        assert body.groups[0] == group

    def test_add_operator(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;
                """,
            "module0",
        )
        body = parser.module_body(code)
        operator = body.add_operator("operator1")
        operator.add_input("i0", "int32")
        operator.add_output("o0", "int32")
        assert operator is not None
        assert isinstance(operator, swan.Operator)
        assert swan.swan_to_str(operator.id) == "operator1"
        assert operator.is_node
        assert not operator.is_inlined
        assert len(operator.inputs) == 1
        input = cast(swan.VarDecl, operator.inputs[0])  # noqa
        assert swan.swan_to_str(input.id) == "i0"
        assert swan.swan_to_str(input.type) == "int32"
        assert len(operator.outputs) == 1
        output = cast(swan.VarDecl, operator.outputs[0])
        assert swan.swan_to_str(output.id) == "o0"
        assert swan.swan_to_str(output.type) == "int32"
        assert operator.body is not None
        assert isinstance(operator.body, swan.Scope)
        assert not operator.body.sections
        assert len(body.operators) == 1
        assert body.operators[0] == operator

    def test_add_signature(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;
                """,
            "module0",
        )
        body = parser.module_body(code)
        sign = body.add_signature("operator1")
        sign.add_input("i0", "int32")
        sign.add_output("o0", "int32")
        assert sign is not None
        assert isinstance(sign, swan.Signature)
        assert swan.swan_to_str(sign.id) == "operator1"
        assert sign.is_node
        assert not sign.is_inlined
        assert len(sign.inputs) == 1
        input = cast(swan.VarDecl, sign.inputs[0])
        assert swan.swan_to_str(input.id) == "i0"
        assert swan.swan_to_str(input.type) == "int32"
        assert len(sign.outputs) == 1
        output = cast(swan.VarDecl, sign.outputs[0])
        assert swan.swan_to_str(output.id) == "o0"
        assert swan.swan_to_str(output.type) == "int32"
        assert body.signatures[0] == sign


class TestModuleInterface:
    def test_get_types(self, parser: SwanParser):
        code = gen_code(
            """
                type type0 = int32;
                type type1 = float32;
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        types = list(interface.types)
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
        interface = parser.module_interface(code)
        sensors = list(interface.sensors)
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
        interface = parser.module_interface(code)
        consts = list(interface.constants)
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
        interface = parser.module_interface(code)
        groups = list(interface.groups)
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
        interface = parser.module_interface(code)
        signs = list(interface.signatures)
        assert len(signs) == 2
        assert isinstance(signs[0], swan.Signature)
        assert signs[0].id.value == "operator0"
        assert isinstance(signs[1], swan.Signature)
        assert signs[1].id.value == "operator1"

    def test_add_declaration(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        const = interface.add_declaration("const const0: int32 = 0")
        assert const is not None
        assert isinstance(const, swan.ConstDecl)
        assert swan.swan_to_str(const.id) == "const0"
        assert swan.swan_to_str(const.type) == "int32"
        assert swan.swan_to_str(const.value) == "0"

    def test_add_constant(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        const = interface.add_constant("const0", "int32", "0")
        assert const is not None
        assert isinstance(const, swan.ConstDecl)
        assert swan.swan_to_str(const.id) == "const0"
        assert swan.swan_to_str(const.type) == "int32"
        assert swan.swan_to_str(const.value) == "0"
        assert interface.constants[0] == const
        assert isinstance(interface.declarations[1], swan.ConstDeclarations)
        assert len(cast(swan.ConstDeclarations, interface.declarations[1]).constants) == 1
        assert cast(swan.ConstDeclarations, interface.declarations[1]).constants[0] == const

    def test_add_type(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        type = interface.add_type("type0", "int32")  # noqa
        assert type is not None
        assert isinstance(type, swan.TypeDecl)
        assert swan.swan_to_str(type.id) == "type0"
        assert swan.swan_to_str(type.definition) == "int32"  # noqa
        assert interface.types[0] == type
        assert isinstance(interface.declarations[1], swan.TypeDeclarations)
        assert len(cast(swan.TypeDeclarations, interface.declarations[1]).types) == 1
        assert cast(swan.TypeDeclarations, interface.declarations[1]).types[0] == type

    def test_add_sensor(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        sensor = interface.add_sensor("sensor0", "int32")
        assert sensor is not None
        assert isinstance(sensor, swan.SensorDecl)
        assert swan.swan_to_str(sensor.id) == "sensor0"
        assert swan.swan_to_str(sensor.type) == "int32"
        assert interface.sensors[0] == sensor
        assert isinstance(interface.declarations[1], swan.SensorDeclarations)
        assert len(cast(swan.SensorDeclarations, interface.declarations[1]).sensors) == 1
        assert cast(swan.SensorDeclarations, interface.declarations[1]).sensors[0] == sensor

    def test_add_group(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        group = interface.add_group("group0", ["int32", "int32", "int32"])
        assert group is not None
        assert isinstance(group, swan.GroupDecl)
        assert swan.swan_to_str(group.id) == "group0"
        assert isinstance(group.type, swan.GroupTypeExpressionList)
        group_type = cast(swan.GroupTypeExpressionList, group.type)
        assert len(group_type.items) == 3
        assert swan.swan_to_str(group_type.items[0]) == "int32"
        assert swan.swan_to_str(group_type.items[1]) == "int32"
        assert swan.swan_to_str(group_type.items[2]) == "int32"
        assert len(interface.groups) == 1
        assert interface.groups[0] == group

    def test_add_signature(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;
                """,
            "module0",
        )
        interface = parser.module_interface(code)
        sign = interface.add_signature("operator1")
        sign.add_input("i0", "int32")
        sign.add_output("o0", "int32")
        assert sign is not None
        assert isinstance(sign, swan.Signature)
        assert swan.swan_to_str(sign.id) == "operator1"
        assert sign.is_node
        assert not sign.is_inlined
        assert len(sign.inputs) == 1
