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

from ansys.scadeone.core import swan
from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(gen_swan_version() + "\n" + swan, module)


class TestOperator:
    def test_add_interfaces(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operator_declarations[0]
        op0_in1 = op0.add_input("in1", "int32")
        op0_out1 = op0.add_output("out1", "int32")
        assert len(op0.inputs) == 2
        in1 = op0.inputs[1]
        assert in1 == op0_in1
        assert isinstance(in1, swan.VarDecl)
        assert swan.swan_to_str(in1.id) == "in1"
        assert swan.swan_to_str(in1.type) == "int32"
        assert len(op0.outputs) == 2
        out1 = op0.outputs[1]
        assert out1 == op0_out1
        assert isinstance(out1, swan.VarDecl)
        assert swan.swan_to_str(out1.id) == "out1"
        assert swan.swan_to_str(out1.type) == "int32"

    def test_add_block(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32)
                {}
                node operator1 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operator_definitions[0]
        op1 = body.operator_declarations[0]
        diag = op0.add_diagram()
        diag.add_block(op1)
        assert len(op0.diagrams[0].objects) == 1
        block = op0.diagrams[0].objects[0]
        assert isinstance(block, swan.Block)
        assert swan.swan_to_str(block.lunum) == "#0"
        assert swan.swan_to_str(block.instance) == swan.swan_to_str(op1.id)

    def test_add_def_block(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32)
                {}
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operator_definitions[0]
        out0 = op0.outputs[0]
        assert isinstance(out0, swan.VarDecl)
        diag = op0.add_diagram()
        diag.add_def_block(out0)
        assert len(op0.diagrams[0].objects) == 1
        block = op0.diagrams[0].objects[0]
        assert isinstance(block, swan.DefBlock)
        assert swan.swan_to_str(block.lunum) == "#0"
        assert swan.swan_to_str(block.lhs.lhs_items[0]) == swan.swan_to_str(out0.id)

    def test_add_expr_block(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32)
                {}
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operator_definitions[0]
        in0 = op0.inputs[0]
        assert isinstance(in0, swan.VarDecl)
        diag = op0.add_diagram()
        diag.add_expr_block(in0)
        assert len(op0.diagrams[0].objects) == 1
        block = op0.diagrams[0].objects[0]
        assert isinstance(block, swan.ExprBlock)
        assert swan.swan_to_str(block.lunum) == "#0"
        assert swan.swan_to_str(block.expr) == swan.swan_to_str(in0.id)

    def test_add_two_blocks(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32)
                {}
                node operator1 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operator_definitions[0]
        in0 = op0.inputs[0]
        assert isinstance(in0, swan.VarDecl)
        op1 = body.operator_declarations[0]
        diag = op0.add_diagram()
        diag.add_block(op1)
        diag.add_expr_block(in0)
        assert len(op0.diagrams[0].objects) == 2
        block = op0.diagrams[0].objects[0]
        assert isinstance(block, swan.Block)
        assert swan.swan_to_str(block.lunum) == "#0"
        assert swan.swan_to_str(block.instance) == swan.swan_to_str(op1.id)
        expr_block = op0.diagrams[0].objects[1]
        assert isinstance(expr_block, swan.ExprBlock)
        assert swan.swan_to_str(expr_block.lunum) == "#1"
        assert swan.swan_to_str(expr_block.expr) == swan.swan_to_str(in0.id)

    def test_connect(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32)
                {}
                node operator1 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operator_definitions[0]
        in0 = op0.inputs[0]
        assert isinstance(in0, swan.VarDecl)
        op1 = body.operator_declarations[0]
        diag = op0.add_diagram()
        diag.add_block(op1)
        diag.add_expr_block(in0)
        block = op0.diagrams[0].objects[0]
        expr_block = op0.diagrams[0].objects[1]
        diag.connect(expr_block, [block])
        assert len(op0.diagrams[0].objects) == 3
        wire = op0.diagrams[0].objects[2]
        assert isinstance(wire, swan.Wire)
        assert swan.swan_to_str(wire) == "(#2 wire #1 => #0)"
