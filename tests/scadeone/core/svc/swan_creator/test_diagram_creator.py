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
from ansys.scadeone.core.svc.swan_creator import ScadeOneFactory


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


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(gen_swan_version() + "\n" + swan, module)


class TestDiagramCreator:
    def test_singleton(self, diagram_factory):
        factory1 = ScadeOneFactory().diagram
        factory2 = ScadeOneFactory().diagram
        assert diagram_factory is factory1
        assert diagram_factory is factory2

    def test_create_block(self, module_factory, operator_factory, diagram_factory):
        module = module_factory.create_module("m0")
        op0 = module.add_operator("op0")
        op1 = module.add_operator("op1")
        block = diagram_factory.create_block(op0, op1)
        assert block is not None
        assert isinstance(block, swan.Block)
        assert isinstance(block.instance, swan.PathIdOpCall)
        assert swan.swan_to_str(block.instance) == "op1"

    def test_create_block_from_imported_operator(
        self, module_factory, operator_factory, diagram_factory
    ):
        m0 = module_factory.create_module("m0")
        m0_op0 = m0.add_operator("op0")
        m1 = module_factory.create_module("m1")
        m1_op0 = m1.add_operator("op0")
        block = diagram_factory.create_block(m1_op0, m0_op0)
        assert block is not None
        assert isinstance(block, swan.Block)
        assert isinstance(block.instance, swan.PathIdOpCall)
        assert swan.swan_to_str(block.instance) == "m0::op0"

    def test_create_def_block(self, operator_factory, diagram_factory):
        operator = operator_factory.create_operator("op2")
        output = operator.add_output("var1", "int32")
        def_block = diagram_factory.create_def_block(output)
        assert def_block is not None
        assert isinstance(def_block, swan.DefBlock)
        assert len(def_block.lhs.lhs_items) == 1
        assert swan.swan_to_str(def_block.lhs.lhs_items[0]) == "var1"

    def test_create_expr_block(self, operator_factory, diagram_factory):
        operator = operator_factory.create_operator("op2")
        input = operator.add_input("var1", "int32")
        expr_block = diagram_factory.create_expr_block(input)
        assert expr_block is not None
        assert isinstance(expr_block, swan.ExprBlock)
        assert isinstance(expr_block.expr, swan.PathIdExpr)
        assert swan.swan_to_str(expr_block.expr) == "var1"

    def test_create_simple_wire(self, module_factory, operator_factory):
        module = module_factory.create_module("m0")
        op0 = module.add_operator("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator("op1")
        diag = op0.add_diagram()
        op0_op1_block = diag.add_block(op1)
        op0_in0_block = diag.add_expr_block(op0_in0)
        wire = diag.connect(op0_in0_block, op0_op1_block)
        assert op0_in0_block.owner == diag
        assert op0_op1_block.owner == diag
        assert wire is not None
        assert isinstance(wire, swan.Wire)
        assert swan.swan_to_str(wire) == "(#2 wire #1 => #0)"

    def test_create_wire_with_multiple_destinations(self, module_factory, operator_factory):
        module = module_factory.create_module("m0")
        op0 = module.add_operator("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator("op1")
        op2 = module.add_operator("op2")
        diag = op0.add_diagram()
        op0_in0_block = diag.add_expr_block(op0_in0)
        op0_op1_block = diag.add_block(op1)
        op0_op2_block = diag.add_block(op2)
        wire = diag.connect(op0_in0_block, [op0_op1_block, op0_op2_block])
        assert op0_in0_block.owner == diag
        assert op0_op1_block.owner == diag
        assert op0_op2_block.owner == diag
        assert wire is not None
        assert isinstance(wire, swan.Wire)
        assert swan.swan_to_str(wire) == "(#3 wire #0 => #1, #2)"

    def test_create_wire_with_source_adaptation(self, module_factory, operator_factory):
        module = module_factory.create_module("m0")
        op0 = module.add_operator("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator("op1")
        diag = op0.add_diagram()
        op0_op1_block = diag.add_block(op1)
        op0_in0_block = diag.add_expr_block(op0_in0)
        wire = diag.connect((op0_in0_block, "1"), op0_op1_block)
        assert op0_in0_block.owner == diag
        assert op0_op1_block.owner == diag
        assert wire is not None
        assert isinstance(wire, swan.Wire)
        assert swan.swan_to_str(wire) == "(#2 wire #1 .(1) => #0)"

    def test_create_wire_with_single_target_adaptation(self, module_factory, operator_factory):
        module = module_factory.create_module("m0")
        op0 = module.add_operator("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator("op1")
        diag = op0.add_diagram()
        op0_op1_block = diag.add_block(op1)
        op0_in0_block = diag.add_expr_block(op0_in0)
        wire = diag.connect(op0_in0_block, [(op0_op1_block, "1")])
        assert op0_op1_block.owner == diag
        assert op0_in0_block.owner == diag
        assert wire is not None
        assert isinstance(wire, swan.Wire)
        assert swan.swan_to_str(wire) == "(#2 wire #1 => #0 .(1))"

    def test_create_wire_with_variable_adaptation(self):
        m0 = ScadeOneFactory().module.create_module("m0")
        op0 = m0.add_operator("op0")
        group0 = m0.add_group("group0", "(in1:int32, in2:int32)")
        op0_in0 = op0.add_input("in0", group0)
        op1 = m0.add_operator("op1")
        op1.add_input("in0", "int32")
        diag = op0.add_diagram()
        op0_op1_block = diag.add_block(op1)
        op0_in0_block = diag.add_expr_block(op0_in0)
        bar0 = diag.add_bar()
        wire0 = diag.connect(op0_in0_block, bar0)
        assert wire0 is not None
        assert isinstance(wire0, swan.Wire)
        assert swan.swan_to_str(wire0) == "(#3 wire #1 => #2)"
        wire1 = diag.connect((bar0, "in1"), op0_op1_block)
        assert wire1 is not None
        assert isinstance(wire1, swan.Wire)
        assert swan.swan_to_str(wire1) == "(#4 wire #2 .(in1) => #0)"

    def test_create_block_in_existing_diagram(self, parser, operator_factory):
        code = gen_code(
            """
                node operator0 (i0: int32)
                  returns (o0: int32)
                  {
                    diagram
                      (#0 expr i0)
                      (#20 def o0)
                      (#10 expr i1)
                  }
                node operator1 (i0: int32)
                  returns (o0: int32);
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.operators[0]
        op1 = body.signatures[0]
        diag = op0.diagrams[0]
        diag.add_block(op1)
        assert len(diag.objects) == 4
        assert isinstance(diag.objects[3], swan.Block)
        assert swan.swan_to_str(diag.objects[3]) == "(#21 block operator1)"
