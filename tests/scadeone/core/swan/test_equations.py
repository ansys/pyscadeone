# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

import test_tools
from ansys.scadeone.core import swan


def state_machine(swan_code, parser):
    body_str = f"""
            node operator0 (i0: int32)
              returns (o0: int32)
              {{
                diagram
                  (automaton #0
                    {swan_code}
                  )
              }}
    """
    code = test_tools.versioned_swan_str(body_str, "module0")
    body = parser.module_body(code)
    op0 = body.operator_definitions[0]
    diag = op0.diagrams[0]
    return diag.objects[0].state_machine


class TestStateMachine:
    @pytest.mark.parametrize(
        "swan_code, expected",
        [("initial state #1 state0:", True), ("state #1 state0:", False)],
    )
    def test_has_initial_state(self, swan_code, expected, parser):
        sm0 = state_machine(swan_code, parser)
        assert sm0._has_initial_state() is expected


class TestState:
    @pytest.mark.parametrize(
        "swan_code",
        [
            "initial state #1 state0:",
            """initial state #1 state0:
              diagram
                (automaton #2
                  state #3 state1:
                )
            """,
            """initial state #1 state0:
                 var x0: int32;
            """,
        ],
    )
    def test_get_diagram(self, swan_code, parser):
        sm0 = state_machine(swan_code, parser)
        s0 = sm0.states[0]
        assert isinstance(s0.diagram, swan.Diagram)
        assert s0.diagram.owner is s0.body

    def test_set_initial_state(self, parser):
        swan_code = """
            initial state #1 state0:
            state #2 state1:
        """
        sm0 = state_machine(swan_code, parser)
        s0 = sm0.states[0]
        s1 = sm0.states[1]
        assert s0.is_initial
        assert not s1.is_initial
        s1.set_as_initial()
        assert not s0.is_initial
        assert s1.is_initial

    def test_is_default(self, parser):
        swan_code = """
            initial state #1 state0:
            state #2 state1
            #pragma cg default #end:
        """
        sm0 = state_machine(swan_code, parser)
        s0 = sm0.states[0]
        s1 = sm0.states[1]
        assert not s0.is_default
        assert s1.is_default
