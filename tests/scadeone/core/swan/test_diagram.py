# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

# %%
from typing import Iterator, Union

import pytest
import re

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as S
from ansys.scadeone.core.swan import Operator


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


class TestDiagNav:
    @pytest.fixture(scope="session")
    def model(self, cc_project):
        app = ScadeOne()
        return app.load_project(cc_project).model

    @pytest.fixture(scope="session")
    def regulation(self, model):
        def regulation_filter(obj: S.GlobalDeclaration):
            if isinstance(obj, S.Operator):
                return str(obj.id) == "Regulation"
            return False

        return model.find_declaration(regulation_filter)

    @staticmethod
    def _get_block_expr(expr: S.Expression, diagram) -> Union[Iterator[S.ExprBlock], None]:
        for obj in diagram.objects:
            if not isinstance(obj, S.ExprBlock):
                continue
            if not isinstance(obj.expr, expr):
                continue
            yield obj

    @staticmethod
    def _get_binary_expr_block(
        binary_op: S.BinaryOp, diagram
    ) -> Union[Iterator[S.ExprBlock], None]:
        blocks = TestDiagNav._get_block_expr(S.BinaryExpr, diagram)
        for block in blocks:
            if block.expr.operator == binary_op:
                yield block

    @staticmethod
    def _check(obj, expected, find=False):
        res = str(obj)
        res = re.sub(r"\s+#pragma.*#end\s*\)", ")", res)
        if find:
            assert res.find(expected) == 0
        else:
            assert res == expected

    def test_block(self, regulation):
        diagram = list(regulation.diagrams)[0]
        block = next(filter(lambda obj: isinstance(obj, S.Block), diagram.objects))
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
        assert str(blk.expr) == "#31 pre #32"
        TestDiagNav._check(conn_from, ".(Saturated)")
        assert conn_to is None

    def test_op_with_binary_expr(self, regulation):
        diagram = list(regulation.diagrams)[0]
        blocks = TestDiagNav._get_binary_expr_block(S.BinaryOp.Minus, diagram)
        block = next(blocks, None)
        assert block is not None

        sources = block.sources
        assert len(sources) == 2
        (blk, conn_from, conn_to) = sources[0]
        TestDiagNav._check(blk, "(#0 expr CruiseSpeed)")
        (blk, conn_from, conn_to) = sources[1]
        TestDiagNav._check(blk, "(#1 expr CarSpeed)")

        targets = block.targets
        assert len(targets) == 2
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk.expr, "#6 * #7")
        (blk, conn_from, conn_to) = targets[1]
        TestDiagNav._check(blk.expr, "if #10 then #11 else #12")

    def test_op_with_ifte_expr(self, regulation):
        diagram = list(regulation.diagrams)[0]
        blocks = TestDiagNav._get_block_expr(S.IfteExpr, diagram)
        block = next(blocks, None)
        assert block is not None

        sources = block.sources
        assert len(sources) == 3
        (blk, conn_from, conn_to) = sources[0]
        TestDiagNav._check(blk.expr, "#31 pre #32")
        (blk, conn_from, conn_to) = sources[1]
        TestDiagNav._check(blk, "(#13 expr SpeedZero", True)
        (blk, conn_from, conn_to) = sources[2]
        TestDiagNav._check(blk.expr, "#3 - #4")

        targets = block.targets
        assert len(targets) == 1
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk.expr, "#15 + #16")

    def test_group(self, parser: SwanParser):
        code = SwanString(
            SwanString.gen_version()
            + "\n"
            + """
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
        op = next(body.declarations)
        assert isinstance(op, Operator)
        diagram = list(op.diagrams)[0]
        assert len(diagram.objects) == 14

        group = diagram.objects[0]
        sources = group.sources
        assert len(sources) == 2
        (blk, conn_from, conn_to) = sources[0]
        assert str(blk) == "(#1 expr i0)"
        (blk, conn_from, conn_to) = sources[1]
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
        TestDiagNav._check(blk, "(#0 group )")
        assert conn_from is None
        TestDiagNav._check(conn_to, ".(a)")

        byname = diagram.objects[2]
        sources = byname.sources
        assert len(sources) == 1
        (blk, conn_from, conn_to) = sources[0]
        TestDiagNav._check(blk, "(#0 group )")
        assert conn_from is None
        assert conn_to is None
        targets = byname.targets
        assert len(targets) == 1
        (blk, conn_from, conn_to) = targets[0]
        TestDiagNav._check(blk, "(#5 group )")
        assert conn_from is None
        assert conn_to is None
