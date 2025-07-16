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
from ansys.scadeone.core.svc.swan_creator import ScadeOneFactory
from ansys.scadeone.core.model import Model


@pytest.fixture
def module_factory():
    return ScadeOneFactory().module


@pytest.fixture
def operator_factory():
    return ScadeOneFactory().operator


@pytest.fixture
def model():
    return Model()


class TestOperatorCreator:
    def test_singleton(self, operator_factory):
        factory1 = ScadeOneFactory().operator
        factory2 = ScadeOneFactory().operator
        assert operator_factory is factory1
        assert operator_factory is factory2

    def test_create_invalid_variable_by_name(self, operator_factory):
        with pytest.raises(swan.ScadeOneException):
            operator_factory.create_variable(name="var$", type="int32")

    def test_create_invalid_variable_by_type(self, operator_factory):
        with pytest.raises(swan.ScadeOneException):
            operator_factory.create_variable(name="var1", type="in&")

    def test_create_variable(self, operator_factory):
        variable = operator_factory.create_variable(name="var1", type="int32")
        assert variable is not None
        assert isinstance(variable, swan.VarDecl)
        assert swan.swan_to_str(variable) == "var1: int32"

    def test_create_variable_expr(self, operator_factory):
        variable = operator_factory.create_variable(
            declaration="var1: int32 when x0 default = 0 last = 0"
        )
        assert variable is not None
        assert isinstance(variable, swan.VarDecl)
        assert swan.swan_to_str(variable) == "var1: int32 when x0 default = 0 last = 0"

    def test_create_variable_with_when(self, operator_factory):
        variable = operator_factory.create_variable(name="var2", type="int32", when="x0")
        assert variable is not None
        assert isinstance(variable, swan.VarDecl)
        assert swan.swan_to_str(variable) == "var2: int32 when x0"

    def test_create_variable_with_default(self, operator_factory):
        variable = operator_factory.create_variable(name="var3", type="int32", default="0")
        assert variable is not None
        assert isinstance(variable, swan.VarDecl)
        assert swan.swan_to_str(variable) == "var3: int32 default = 0"

    def test_create_variable_with_last(self, operator_factory):
        variable = operator_factory.create_variable(name="var4", type="int32", last="0")
        assert variable is not None
        assert isinstance(variable, swan.VarDecl)
        assert swan.swan_to_str(variable) == "var4: int32 last = 0"

    def test_create_variable_with_type(self, model, module_factory, operator_factory):
        m0 = module_factory.create_module("ns0::m0")
        model.add_body(m0)

        # Type in the module
        typ0 = m0.add_type("typ0", "int32")
        variable = operator_factory.create_variable(name="var0", type=typ0, module=m0)
        assert variable is not None
        assert isinstance(variable, swan.VarDecl)
        assert swan.swan_to_str(variable) == "var0: typ0"

        # Type is another module
        m1 = module_factory.create_module("ns1::m1")
        model.add_body(m1)
        typ1 = m1.add_type("typ1", "int32")
        m0.use("ns1::m1")
        variable = operator_factory.create_variable(name="var1", type=typ1, module=m0)
        assert swan.swan_to_str(variable) == "var1: m1::typ1"

        # Type is another module with alias
        m2 = module_factory.create_module("ns2::m2")
        model.add_body(m2)
        typ2 = m2.add_type("typ2", "int32")
        m0.use("ns2::m2", "M2")
        variable = operator_factory.create_variable(name="var2", type=typ2, module=m0)
        assert swan.swan_to_str(variable) == "var2: M2::typ2"

        # Group is another module (reuse m1)
        grp1 = m1.add_group("grp1", "int32")
        variable = operator_factory.create_variable(name="var1", type=grp1, module=m0)
        assert swan.swan_to_str(variable) == "var1: m1::grp1"

        # missing use statement
        m3 = module_factory.create_module("m3")
        model.add_body(m3)
        typ3 = m3.add_type("typ3", "int32")
        with pytest.raises(swan.ScadeOneException) as excInfo:
            variable = operator_factory.create_variable(name="var3", type=typ3, module=m0)
        assert str(excInfo.value) == "Missing use directive in module ns0::m0 for item m3::typ3."

    def test_create_signature(self, operator_factory):
        signature = operator_factory.create_signature("op1")
        assert signature is not None
        assert isinstance(signature, swan.Signature)
        assert swan.swan_to_str(signature.id) == "op1"
        assert signature.is_node

    def test_create_operator(self, operator_factory):
        operator = operator_factory.create_operator("op2")
        assert operator is not None
        assert isinstance(operator, swan.Operator)
        assert swan.swan_to_str(operator.id) == "op2"
        assert operator.is_node

    def test_create_diagram(self, operator_factory):
        operator = operator_factory.create_operator("op2")
        diagram = operator.add_diagram()
        assert diagram is not None
        assert isinstance(diagram, swan.Diagram)
        assert len(operator.diagrams) == 1
        assert diagram.objects is not None
        assert len(diagram.objects) == 0

    def test_add_methods(self, module_factory):
        module = module_factory.create_module("module")

        # check adding textual operator
        op1 = module.add_textual_operator("inline node op1 (a: int32) returns (b: int32) {}")
        assert isinstance(op1, swan.Operator)
        assert swan.swan_to_str(op1.id) == "op1"
        assert op1.is_node
        assert op1.is_inlined
        assert len(op1.diagrams) == 0
        op1_str = swan.swan_to_str(op1)
        assert op1_str.startswith("{text%") and op1_str.endswith("%text}")
        assert "signature" not in op1_str

        # check adding textual signature
        op2 = module.add_textual_signature("inline function op2 (a: int32) returns (b: int32);")
        assert isinstance(op2, swan.Signature)
        assert swan.swan_to_str(op2.id) == "op2"
        assert not op2.is_node
        assert op2.is_inlined
        op2_str = swan.swan_to_str(op2)
        assert op2_str.startswith("{signature%") and op2_str.endswith("%signature}")
