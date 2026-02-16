# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path
import ansys.scadeone.core.swan.expressions as expressions
from ansys.scadeone.core.swan.harness import TestModule
from ansys.scadeone.core.swan.modules import ConstDeclarations
from ansys.scadeone.core.common.storage import SwanFile
from ansys.scadeone.core.model.loader import SwanParser
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.swan.pragmas import DiagramPragma, TestPragma
from ansys.scadeone.core.swan import swan_to_str


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


@pytest.fixture
def test() -> TestModule:
    file_path = Path(
        r"C:\Scade One\examples\QuadFlightControl\QuadFlightControl\assets\QuadTest.swant"
    )
    test_file = SwanFile(file_path)
    if not test_file.is_test:
        raise ScadeOneException(f"File {file_path} is not a test module.")

    return SwanParser(LOGGER).test_module(test_file)


class TestModuleLoading:
    def test_name_extension(self, test: TestModule) -> None:
        assert str(test.name) == "QuadTest"
        assert test.extension == ".swant"

    def test_use_directives(self, test: TestModule) -> None:
        assert len(test.use_directives) == 5
        assert str(test.use_directives[0].path) == "Harness::Sources::N"
        assert str(test.use_directives[0].alias) == "Sources"
        assert str(test.use_directives[1].path) == "QuadFlightControl"
        assert str(test.use_directives[1].alias) == "Q"
        assert str(test.use_directives[2].path) == "QuadTypes"
        assert str(test.use_directives[2].alias) == "T"
        assert str(test.use_directives[3].path) == "Harness::Check"
        assert test.use_directives[3].alias is None
        assert str(test.use_directives[4].path) == "Float"
        assert test.use_directives[4].alias is None

    def test_declarations(self, test: TestModule) -> None:
        for idx, decl in enumerate(test.declarations):
            if isinstance(decl, ConstDeclarations):
                if isinstance(decl.constants[0].value, expressions.StructConstructor):
                    assert str(decl.constants[0]._id) == "ZERO_ATTITUDE"
                    assert str(decl.constants[0].value.type) == "T::AttitudeType"
                    assert [
                        f"{it.label}: {it.expr}" for it in decl.constants[0].value.group.items
                    ] == ["pitch: 0.0", "roll: 0.0", "yaw: 0.0"]
            else:
                if idx == 0:
                    assert str(decl._id) == "TestVerticalAccel"
                else:
                    assert str(decl._id) == "TestRightRoll"
                # Check inputs and outputs by default
                assert decl._inputs[0].id.value == "_current_cycle"
                assert decl._inputs[0].type.name == "uint64"
                assert decl._outputs[0].id.value == "_stop_condition"
                assert decl._outputs[0].type.name == "bool"

    def test_reference_block(self, test: TestModule) -> None:
        decl = test.declarations[0]
        assert decl.body is not None
        assert decl.body.sections is not None
        sct = decl.body.sections[0]
        assert sct is not None
        first_obj = sct.objects[0]
        assert first_obj is not None
        prefix = first_obj.instance
        assert prefix is not None
        first_decl = ", ".join(
            [f"{elm.item.label}: {elm.item.expr}" for elm in prefix.op_expr.partial_group]
        )
        assert (
            rf"{first_obj.lunum.value} block ({first_obj.instance.op_expr.operator.path_id} \ {first_decl})"
            == "#0 block (Sources::Ramp \\ amplitude: 0.1, cycles: 20_ui32, offset: 0.0)"
        )

    def test_block_pragmas(self, test: TestModule) -> None:
        first_dect = test.declarations[0]
        assert first_dect.body is not None
        assert first_dect.body.sections is not None
        sct = first_dect.body.sections[0]
        assert sct is not None
        block = sct.objects[1]
        assert block is not None
        assert len(block.pragmas) == 2
        # pragma order depends on version, so check both
        assert (
            isinstance(block.pragmas[1], DiagramPragma) and isinstance(block.pragmas[0], TestPragma)
        ) or (
            isinstance(block.pragmas[0], DiagramPragma) and isinstance(block.pragmas[1], TestPragma)
        )

    def test_pragma_block(self, test: TestModule) -> None:
        first_dect = test.declarations[0]
        assert first_dect.body is not None
        assert first_dect.body.sections is not None
        sct = first_dect.body.sections[0]
        assert sct is not None
        block = sct.objects[1]
        assert block is not None
        prefix = block.instance
        assert prefix is not None
        _dta = []
        for elm in prefix.op_expr.partial_group:
            if isinstance(elm.item.expr, expressions.GroupConstructor):
                _val = ", ".join([f"{grp.label}: {grp.expr}" for grp in elm.item.expr.group.items])
                _val = f"({_val})" if _val else "()"
            elif isinstance(elm.item.expr, expressions.PathIdExpr):
                _val = f"{elm.item.expr.path_id}"
            else:
                _val = f"{elm.item.expr}"
            _dta.append(f"{elm.item.label}: {_val}")
        decl = ", ".join(_dta)
        # check pragmas, which should be in the same order, depending on version
        assert (
            isinstance(block.pragmas[1], DiagramPragma) and isinstance(block.pragmas[0], TestPragma)
        ) or (
            isinstance(block.pragmas[0], DiagramPragma) and isinstance(block.pragmas[1], TestPragma)
        )
        # check block string representation, without pragma
        assert (
            rf"{block.lunum.value} block ({block.instance.op_expr.operator.path_id} \ {decl})"
            == "#1 block (Q::QuadFlightControl \\ isReset: false, motorStates: (frontLeftFaulty: false, frontRightFaulty: false, rearLeftFaulty: false, rearRightFaulty: false), desiredAttitude: ZERO_ATTITUDE, currentAttitude: ZERO_ATTITUDE)"
        )

    def test_oracle_block(self, test: TestModule) -> None:
        decl = test.declarations[0]
        assert decl.body is not None
        assert decl.body.sections is not None
        sct = decl.body.sections[0]
        assert sct is not None
        block = sct.objects[5]
        assert block is not None
        assert block.instance.op_expr.id
        assert (
            rf"{block.lunum.value} block (_oracle {block.instance.op_expr.id})"
            == "#7 block (_oracle SimVerticalAccelOracle)"
        )

    def test_harness_block(self, parser) -> None:
        from ansys.scadeone.core.swan.harness import TestHarness

        code = """_harness #pragma something #end harness0
{
  diagram
    (#0 _sensor SENSOR
    #pragma diagram {"xy":"H-49450;V-29450","wh":"16000;3200"} #end)
    (#1 block G
    #pragma swt under_test #end
    #pragma diagram {"xy":"H1050;V-6350","wh":"20000;14000"} #end)
    (#2 block (_source Key1)
    #pragma diagram {"xy":"H-39850;V-12850","wh":"12000;7000"} #end)
    (#3 block (_oracle Key2)
    #pragma diagram {"xy":"H-30550;V2350","wh":"12000;7000"} #end)
    (#4 _sensor {syntax%$$$%syntax}
    #pragma diagram {"xy":"H-12250;V-30350","wh":"12000;3200"} #end)
}
"""
        gen_code = tools.versioned_swan_str(code, "test_module", True)
        test_module = parser.test_module(gen_code)
        test_harness = test_module.test_harnesses[0]
        assert isinstance(test_harness, TestHarness)
        assert test_harness.body is not None
        res = swan_to_str(test_harness)
        assert res == code
