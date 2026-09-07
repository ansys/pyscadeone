# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import re
from typing import Iterator, Union

import pytest

from ansys.scadeone.core import ScadeOne, ScadeOneException
from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as swan
from ansys.scadeone.core.svc.swan_creator import ScadeOneFactory
from ansys.scadeone.core.swan import OperatorDefinition


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(gen_swan_version() + "\n" + swan, module)


@pytest.fixture
def operator(parser):
    code = gen_code(
        """
            node operator0 (i0: int32 default = 0)
              returns (o0: int32);
            """,
        "module0",
    )
    body = parser.module_body(code)
    return body.operator_declarations[0]


@pytest.fixture
def empty_diagram(parser):
    code = gen_code(
        """
            node operator0 (i0: int32;)
               returns (o0: int32;)
            {
                diagram
            }
            """,
        "module0",
    )
    body = parser.module_body(code)
    op = body.operator_definitions[0]
    return op.diagrams[0]


class TestDiagram:
    def test_add_block(self, model, operator):
        module = ScadeOneFactory().module.create_module_body("m0")
        model.add_body(module)
        module.use("module0")
        op = module.add_operator_definition("op")
        diag = op.add_diagram()
        diag.add_block(operator)
        assert len(diag.objects) == 1

    def test_add_block_error(self, model, operator):
        module = ScadeOneFactory().module.create_module_body("m0")
        model.add_body(module)
        op = module.add_operator_definition("op")
        diag = op.add_diagram()
        with pytest.raises(ScadeOneException) as excinfo:
            diag.add_block(operator)
        assert (
            str(excinfo.value) == "Missing use directive in module m0 for item module0::operator0."
        )

    def test_add_def_block(self, operator):
        module = ScadeOneFactory().module.create_module_body("m0")
        op = module.add_operator_definition("op")
        diag = op.add_diagram()
        diag.add_def_block(operator.outputs[0])
        assert len(diag.objects) == 1

    # B1200675: Bar without connections has no owner
    def test_empty_bar_owner(self, parser: SwanParser):
        code = gen_code(
            """
            function emptyBar ()
              returns ()
            {
              diagram
                (#0 group)
            }
            """,
            "test_bar",
        )
        body = parser.module_body(code)
        op = body.declarations[0]
        diag = op.diagrams[0]
        obj = diag.objects[0]
        assert isinstance(obj.owner, swan.Diagram)


class TestDiagNav:
    @pytest.fixture(scope="session")
    def model(self, cc_project):
        app = ScadeOne()
        project = app.load_project(cc_project)
        return project.model

    @pytest.fixture(scope="session")
    def regulation(self, model):
        def regulation_filter(obj: swan.GlobalDeclaration):
            if isinstance(obj, swan.OperatorDefinition):
                return swan.swan_to_str(obj.id) == "Regulation"
            return False

        return model.find_declaration(regulation_filter)

    @staticmethod
    def _get_block_expr(expr: swan.Expression, diagram) -> Union[Iterator[swan.ExprBlock], None]:
        for obj in diagram.objects:
            if not isinstance(obj, swan.ExprBlock):
                continue
            if not isinstance(obj.expr, expr):
                continue
            yield obj

    @staticmethod
    def _get_binary_expr_block(
        binary_op: swan.BinaryOp, diagram
    ) -> Union[Iterator[swan.ExprBlock], None]:
        blocks = TestDiagNav._get_block_expr(swan.BinaryExpr, diagram)
        for block in blocks:
            if block.expr.operator == binary_op:
                yield block

    @staticmethod
    def _check(obj, expected, find=False):
        res = swan.swan_to_str(obj)
        res = re.sub(r"\s+#pragma.*#end\s*\)", ")", res)
        if find:
            assert res.find(expected) == 0
        else:
            assert res == expected

    def test_block(self, regulation):
        diagram = list(regulation.diagrams)[0]
        block = next(filter(lambda obj: isinstance(obj, swan.Block), diagram.objects))
        TestDiagNav._check(block, "(#28 block SaturateThrottle)")

        sources = block.sources
        assert len(sources) == 1
        (blk, conn_from, conn_to) = sources[0]
        TestDiagNav._check(blk, "(#25 expr #26 + #27", True)
        assert conn_from is None
        assert len(conn_to) == 1
        TestDiagNav._check(conn_to[0], ".(ThrottleIn)")

        targets = block.targets
        assert len(targets) == 2
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk, "(#29 def Throttle)")
        TestDiagNav._check(conn_from, ".(ThrottleOut)")
        assert conn_to is None
        (blk, conn_from, conn_to) = targets[1]
        assert swan.swan_to_str(blk.expr) == "#31 pre #32"
        TestDiagNav._check(conn_from, ".(Saturated)")
        assert conn_to is None

    def test_op_with_binary_expr(self, regulation):
        diagram = list(regulation.diagrams)[0]
        blocks = TestDiagNav._get_binary_expr_block(swan.BinaryOp.Minus, diagram)
        block = next(blocks, None)
        assert block is not None

        sources = block.sources
        assert len(sources) == 2
        (blk, _, _) = sources[0]
        TestDiagNav._check(blk, "(#0 expr CruiseSpeed)")
        (blk, _, _) = sources[1]
        TestDiagNav._check(blk, "(#1 expr CarSpeed)")

        targets = block.targets
        assert len(targets) == 2
        (blk, _, _) = targets[0]
        TestDiagNav._check(blk.expr, "#6 * #7")
        (blk, _, _) = targets[1]
        TestDiagNav._check(blk.expr, "if #10 then #11 else #12")

    def test_op_with_ifte_expr(self, regulation):
        diagram = list(regulation.diagrams)[0]
        blocks = TestDiagNav._get_block_expr(swan.IfteExpr, diagram)
        block = next(blocks, None)
        assert block is not None

        sources = block.sources
        assert len(sources) == 3
        (blk, _, _) = sources[0]
        TestDiagNav._check(blk.expr, "#31 pre #32")
        (blk, _, _) = sources[1]
        TestDiagNav._check(blk, "(#13 expr SpeedZero", True)
        (blk, _, _) = sources[2]
        TestDiagNav._check(blk.expr, "#3 - #4")

        targets = block.targets
        assert len(targets) == 1
        (blk, _, _) = targets[0]
        TestDiagNav._check(blk.expr, "#15 + #16")

    def test_group(self, parser: SwanParser):
        code = gen_code(
            """
            inline function operator0 (i0: int32;
                                       i1: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 group)
                (#1 expr i0)
                (#2 group byname)
                (#3 group bypos)
                (#4 def o0)
                (#5 group)
                (#12 expr i1)

                (#6 wire #1 => #0 .(a))
                (#7 wire #0 => #2)
                (#8 wire #0 => #3)
                (#9 wire #2 => #5)
                (#10 wire #5 .(a) => #4)
                (#11 wire #3 => #5)
                (#13 wire #12 => #0 .(b))
            }
            """,
            "test_group",
        )
        body = parser.module_body(code)
        op = body.declarations[0]
        assert isinstance(op, OperatorDefinition)
        diagram = list(op.diagrams)[0]
        assert len(diagram.objects) == 14

        group = diagram.objects[0]
        sources = group.sources
        assert len(sources) == 2
        (blk, _, _) = sources[0]
        assert swan.swan_to_str(blk) == "(#1 expr i0)"
        (blk, _, _) = sources[1]
        TestDiagNav._check(blk, "(#12 expr i1)")
        targets = group.targets
        assert len(targets) == 2
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk, "(#2 group byname)")
        assert conn_from is None
        assert conn_to is None
        (blk, conn_from, conn_to) = targets[1]
        TestDiagNav._check(blk, "(#3 group bypos)")
        assert conn_from is None
        assert conn_to is None

        i0 = diagram.objects[1]
        targets = i0.targets
        assert len(targets) == 1
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk, "(#0 group)")
        assert conn_from is None
        TestDiagNav._check(conn_to, ".(a)")

        byname = diagram.objects[2]
        sources = byname.sources
        assert len(sources) == 1
        (blk, conn_from, conn_to) = sources[0]
        TestDiagNav._check(blk, "(#0 group)")
        assert conn_from is None
        assert conn_to is None
        targets = byname.targets
        assert len(targets) == 1
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk, "(#5 group)")
        assert conn_from is None
        assert conn_to is None

    # B1181579: Invalid target adaptation from a source block
    def test_wire_with_two_targets_one_source(self, parser: SwanParser):
        code = gen_code(
            """
            node root1 ()
              returns (typeField: int32;)
            {
              diagram
                (#0 block consumer)
                (#1 def typeField)
                (#2 block producer)
                (#3 wire #2 .(typeField) => #0 .(typeField_in), #1)
            }
            """,
            "test_root1",
        )
        body = parser.module_body(code)
        op = [op for op in body.operator_definitions if str(op.id) == "root1"][0]
        d = op.diagrams[0]
        for o in d.objects:
            if isinstance(o, swan.DefBlock):
                break
        src = o.sources
        source_adaptation = swan.swan_to_str(src[0][1])
        target_adaptations = src[0][2]
        assert source_adaptation == ".(typeField)"
        assert target_adaptations is None

    # B1181579: Invalid target adaptation from a source block
    def test_wire_with_three_targets_one_source(self, parser: SwanParser, capsys):
        code = gen_code(
            """
            node root2 ()
              returns (typeField: int32;)
            {
              diagram
                (#0 block consumer2)
                (#1 def typeField)
                (#2 block producer)
                (#3 wire #2 .(typeField) => #0 .(typeField_in1), #1, #0 .(typeField_in2))
            }
            """,
            "test_root1",
        )
        body = parser.module_body(code)
        op = [op for op in body.operator_definitions if str(op.id) == "root2"][0]
        d = op.diagrams[0]
        for o in d.objects:
            if isinstance(o, swan.Block) and str(o.instance.path_id) == "consumer2":
                break
        src = o.sources
        source_adaptation = swan.swan_to_str(src[0][1])
        target_adaptations = [swan.swan_to_str(t) for t in src[0][2]]
        with capsys.disabled():
            print("\nSource: ", source_adaptation)
            print("Targets:", target_adaptations)
        assert source_adaptation == ".(typeField)"
        assert {".(typeField_in1)", ".(typeField_in2)"}.issubset(target_adaptations)


class TestDiagramVariables:
    """Class focused on access of property **local_variables** of a **Diagram** object"""

    @pytest.fixture
    def diagram(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (var
                        temperature: int32;
                        temp_max: int32;
                        temp_min: int32;)
                    (let
                        delta_max = temp_max - temperature;)
                    (emit
                        'delta_max if true;)
                    (assume
                        $t: temperature > temp_max;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op = body.operator_definitions[0]
        return op.diagrams[0]

    @pytest.fixture
    def diagram_several_var_sections(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (emit
                        'delta_max if true;)
                    (var
                        temperature: int32;
                        temp_max: int32;
                        temp_min: int32;)
                    (let
                        t_max = temperature > temp_max;)
                    (let
                        t_min = temperature < temp_min;)
                    (assume
                        $t: temperature > temp_max;)
                    (var
                        frequency: int32;
                        freq_max: int32;
                        freq_min: int32;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op = body.operator_definitions[0]
        return op.diagrams[0]

    def test_diagrams_variables(self, diagram):
        diag_variables = diagram.local_variables
        assert len(diag_variables) == 3
        assert diag_variables[0].id.value == "temperature"
        assert diag_variables[1].id.value == "temp_max"
        assert diag_variables[2].id.value == "temp_min"

    def test_diagrams_variables_from_several_sections(self, diagram_several_var_sections):
        diag_variables = diagram_several_var_sections.local_variables
        assert len(diag_variables) == 6
        assert diag_variables[3].id.value == "frequency"
        assert diag_variables[4].id.value == "freq_max"
        assert diag_variables[5].id.value == "freq_min"

    def test_diagrams_with_no_variables(self, empty_diagram):
        diag_variables = empty_diagram.local_variables
        assert len(diag_variables) == 0


class TestDiagramSubdiagrams:
    """Class focused on access of property **diagrams** of a **Diagram** object"""

    @pytest.fixture
    def diagram(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (diagram $Subdiagram1
                        (diagram $NotReachable1)
                    )
                    (diagram $Subdiagram2
                        (diagram $NotReachable2)
                    )
                    (diagram $Subdiagram3
                        (diagram $NotReachable3)
                    )
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op = body.operator_definitions[0]
        return op.diagrams[0]

    def test_diagrams_without_subdiagrams(self, empty_diagram):
        subdiagrams = empty_diagram.diagrams
        assert not subdiagrams

    def test_diagrams_subdiagrams(self, diagram):
        subdiagrams = diagram.diagrams
        assert len(subdiagrams) == 3
        assert all(isinstance(diag.owner, swan.SectionObject) for diag in subdiagrams)
        assert all(diag.owner.owner == diagram for diag in subdiagrams)
