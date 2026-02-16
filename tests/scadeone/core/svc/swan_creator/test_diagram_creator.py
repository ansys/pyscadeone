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

import tools
from ansys.scadeone.core import swan
from ansys.scadeone.core.common.versioning import ScadeOneException
from ansys.scadeone.core.model.model import Model
from ansys.scadeone.core.svc.swan_creator import ScadeOneFactory


class TestDiagramCreator:
    def test_singleton(self, diagram_factory):
        factory1 = ScadeOneFactory().diagram
        factory2 = ScadeOneFactory().diagram
        assert diagram_factory is factory1
        assert diagram_factory is factory2

    def test_create_block(self, module_factory, diagram_factory):
        module = module_factory.create_module_body("m0")
        op0 = module.add_operator_definition("op0")
        op1 = module.add_operator_definition("op1")
        diag0 = op0.add_diagram()
        block = diagram_factory.create_block(diag0, op1)
        assert block is not None
        assert isinstance(block, swan.Block)
        assert isinstance(block.instance, swan.NamedInstance)
        assert swan.swan_to_str(block.instance) == "op1"

    def test_create_block_from_imported_operators(
        self, model: Model, module_factory, diagram_factory
    ):
        # Create a 1st module and an operator in the model
        m1 = module_factory.create_module_body("ns1::m1")
        model.add_body(m1)
        m1_op = m1.add_operator_definition("op1")
        # Create a 2nd module and an operator in the model
        m2 = module_factory.create_module_body("ns1::ns2::m2")
        model.add_body(m2)
        m2_op = m2.add_operator_definition("op2")
        # Create a 3rd module and an operator in the model
        m3 = module_factory.create_module_body("m3")
        model.add_body(m3)
        m3.use("ns1::m1")
        m3.use("ns1::ns2::m2", "M")
        m3_op = m3.add_operator_definition("op3")
        diag_m3 = m3_op.add_diagram()
        # Create a block in the diagram of the 3rd module using the operator from the 1st module
        block = diagram_factory.create_block(diag_m3, m1_op)
        assert block is not None
        assert isinstance(block, swan.Block)
        assert isinstance(block.instance, swan.NamedInstance)
        assert swan.swan_to_str(block.instance) == "m1::op1"
        # Create a block in the diagram of the 3rd module using the operator from the 2nd module
        block = diagram_factory.create_block(diag_m3, m2_op)
        assert block is not None
        assert isinstance(block, swan.Block)
        assert isinstance(block.instance, swan.NamedInstance)
        assert swan.swan_to_str(block.instance) == "M::op2"

    def test_create_def_block(self, operator_factory, diagram_factory):
        operator = operator_factory.create_operator_definition("op2")
        output = operator.add_output("var1", "int32")
        def_block = diagram_factory.create_def_block(output)
        assert def_block is not None
        assert isinstance(def_block, swan.DefBlock)
        assert len(def_block.lhs.lhs_items) == 1
        assert swan.swan_to_str(def_block.lhs.lhs_items[0]) == "var1"

    def test_create_expr_block(self, module_factory, diagram_factory):
        module = module_factory.create_module_body("m0")
        operator = module.add_operator_definition("op2")
        input = operator.add_input("var1", "int32")
        diag0 = operator.add_diagram()
        expr_block = diagram_factory.create_expr_block(diag0, input)
        assert expr_block is not None
        assert isinstance(expr_block, swan.ExprBlock)
        assert isinstance(expr_block.expr, swan.PathIdExpr)
        assert swan.swan_to_str(expr_block.expr) == "var1"

    def test_create_expr_block_with_other_module(self, model, module_factory, diagram_factory):
        # module with operator and diagram
        m0 = module_factory.create_module_body("ns0::m0")
        model.add_body(m0)
        op = m0.add_operator_definition("op")
        diag = op.add_diagram()

        # interface with constant
        # -----------------------
        m1 = module_factory.create_module_interface("ns1::ns2::m1")
        model.add_interface(m1)
        cst1 = m1.add_constant("cst1", "int32", "0")
        # Missing use directive in module ns0::m0 for item ns1::ns2::m1::cst0
        with pytest.raises(ScadeOneException) as excinfo:
            expr_block = diagram_factory.create_expr_block(diag, cst1)
        assert (
            str(excinfo.value)
            == "Missing use directive in module ns0::m0 for item ns1::ns2::m1::cst1."
        )
        # adding the use directive to the module
        m0.use("ns1::ns2::m1")
        expr_block = diagram_factory.create_expr_block(diag, cst1)
        assert expr_block is not None
        assert isinstance(expr_block, swan.ExprBlock)
        assert isinstance(expr_block.expr, swan.PathIdExpr)
        assert swan.swan_to_str(expr_block.expr) == "m1::cst1"

        # body with constant and use with alias
        # -------------------------------------
        m2 = module_factory.create_module_body("m2")
        model.add_body(m2)
        cst2 = m2.add_constant("cst2", "int32", "0")
        m0.use("m2", "M")
        expr_block = diagram_factory.create_expr_block(diag, cst2)
        assert expr_block is not None
        assert isinstance(expr_block, swan.ExprBlock)
        assert isinstance(expr_block.expr, swan.PathIdExpr)
        assert swan.swan_to_str(expr_block.expr) == "M::cst2"

        # use a sensor
        s2 = m2.add_sensor("S2", "int32")
        expr_block = diagram_factory.create_expr_block(diag, s2)
        assert expr_block is not None
        assert isinstance(expr_block, swan.ExprBlock)
        assert isinstance(expr_block.expr, swan.PathIdExpr)
        assert swan.swan_to_str(expr_block.expr) == "M::S2"

    def test_create_simple_wire(self, module_factory, operator_factory):
        module = module_factory.create_module_body("m0")
        op0 = module.add_operator_definition("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator_definition("op1")
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
        module = module_factory.create_module_body("m0")
        op0 = module.add_operator_definition("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator_definition("op1")
        op2 = module.add_operator_definition("op2")
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
        module = module_factory.create_module_body("m0")
        op0 = module.add_operator_definition("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator_definition("op1")
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
        module = module_factory.create_module_body("m0")
        op0 = module.add_operator_definition("op0")
        op0_in0 = op0.add_input("in0", "int32")
        op1 = module.add_operator_definition("op1")
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
        m0 = ScadeOneFactory().module.create_module_body("m0")
        op0 = m0.add_operator_definition("op0")
        group0 = m0.add_group("group0", "(in1:int32, in2:int32)")
        op0_in0 = op0.add_input("in0", group0)
        op1 = m0.add_operator_definition("op1")
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

    def test_create_wire_from_multiple_connections(self):
        m0 = ScadeOneFactory().module.create_module_body("m0")
        op0 = m0.add_operator_definition("op0")
        op = m0.add_operator_definition("op1")
        outputs = [op.add_output("out" + str(i), "int32") for i in range(5)]
        # blocks creation
        diag = op0.add_diagram()
        blk1 = diag.add_block(op)
        defs = [diag.add_def_block(output) for output in outputs]

        # simple connection
        wire10 = diag.connect(blk1, defs[0])
        wire11 = diag.connect(blk1, defs[1])
        assert wire11 is not None and wire11 is not None
        assert wire10 == wire11
        assert swan.swan_to_str(wire10) == "(#6 wire #0 => #1, #2)"

        # connection with named adaptation, new wire only
        wire20 = diag.connect((blk1, "x"), defs[2])
        wire21 = diag.connect((blk1, "x"), defs[3])
        assert wire20 == wire21
        assert wire10 != wire20
        assert swan.swan_to_str(wire20) == "(#7 wire #0 .(x) => #3, #4)"
        # new wire only
        wire30 = diag.connect((blk1, "y"), defs[4])
        assert wire30 is not None
        assert wire30 != wire20 and wire30 != wire10
        assert swan.swan_to_str(wire30) == "(#8 wire #0 .(y) => #5)"

    def test_create_wires_duplicated(self, module_factory, operator_factory):
        module = module_factory.create_module_body("m0")
        op0 = module.add_operator_definition("op0")
        op0.add_output("out0", "int32")
        op1 = module.add_operator_definition("op1")
        op1.add_input("in0", "int32")
        diag = op0.add_diagram()
        op0_block = diag.add_block(op0)
        op1_block = diag.add_block(op1)
        wire = diag.connect((op0_block, "in0"), (op1_block, "out0"))
        diag.connect((op0_block, "in0"), (op1_block, "out0"))  # duplicate wire
        assert wire is not None
        assert isinstance(wire, swan.Wire)
        assert swan.swan_to_str(wire) == "(#2 wire #0 .(in0) => #1 .(out0))"

    def test_create_block_in_existing_diagram(self, parser, operator_factory):
        code = tools.versioned_swan_str(
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
        op0 = body.operator_definitions[0]
        op1 = body.operator_declarations[0]
        diag = op0.diagrams[0]
        diag.add_block(op1)
        assert len(diag.objects) == 4
        assert isinstance(diag.objects[3], swan.Block)
        assert swan.swan_to_str(diag.objects[3]) == "(#21 block operator1)"
