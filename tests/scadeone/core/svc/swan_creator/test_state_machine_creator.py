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
from ansys.scadeone.core import ScadeOneException
from ansys.scadeone.core.swan import CGPragmaKind, Scope, EmitSection, LetSection, ScopeSection
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.svc import swan_printer as printer


@pytest.fixture
def state_machine(parser):
    code = test_tools.versioned_swan_str(
        """
            node operator0 (i0: int32; i1: bool)
              returns (o0: int32)
              {
                diagram
                  (automaton #0
                    state #1 State0:
                  )
              }
            """,
        "module0",
    )
    body = parser.module_body(code)
    op0 = body.operator_definitions[0]
    diag = op0.diagrams[0]
    return diag.objects[0].state_machine


@pytest.fixture
def s1_to_s2_transition(state_machine):
    s1 = state_machine.add_state("State1", is_initial=True)
    s2 = state_machine.add_state("State2", is_default=True)
    return state_machine.add_strong_transition(s1, s2)


@pytest.fixture
def s3_to_s4_transition(state_machine):
    s3 = state_machine.add_state("State3", is_initial=True)
    s4 = state_machine.add_state("State4", is_default=True)
    return state_machine.add_weak_transition(s3, s4)


class TestStateMachineCreator:
    def test_create_state(self, state_machine) -> None:
        s1 = state_machine.add_state("State1", is_initial=True)
        s2 = state_machine.add_state("State2", is_default=True)
        assert s1 is not None
        assert s1.owner is state_machine
        assert s1.id.value == "State1"
        assert s1.is_initial
        assert state_machine.initial_state[0] is s1
        assert s2 is not None
        assert s2.owner is state_machine
        assert s2.id.value == "State2"
        assert s2.pragmas[0].kind == CGPragmaKind.DEFAULT
        assert state_machine.default_state[0] is s2

    def test_create_state_not_name(self, state_machine) -> None:
        with pytest.raises(ScadeOneException) as exception:
            state_machine.add_state("", is_initial=True)
        assert "State name is required." in str(exception.value)

    def test_add_local_variable(self, state_machine) -> None:
        s1 = state_machine.add_state("State1", is_initial=True)
        x0 = s1.add_local_variable("x0", "int32")
        x1 = s1.add_local_variable("x1", "bool")
        var_decls = s1.diagram.objects[0].section.var_decls
        assert len(var_decls) == 2
        assert x0 is not None
        assert x0 in var_decls
        assert x0.owner.owner.owner.owner is s1
        assert x0.id.value == "x0"
        assert x0.type.name == "int32"
        assert x1 is not None
        assert x1 in var_decls
        assert x1.owner.owner.owner.owner is s1
        assert x1.id.value == "x1"
        assert x1.type.name == "bool"

    @pytest.mark.parametrize(
        "name, type, expected_msg",
        [
            ("", "int32", "Local variable name cannot be empty."),
            ("x0", "", "Local variable type cannot be empty."),
        ],
    )
    def test_add_local_variable_not_name_type(
        self, state_machine, name, type, expected_msg
    ) -> None:
        s1 = state_machine.add_state("State1", is_initial=True)
        with pytest.raises(ScadeOneException) as exception:
            s1.add_local_variable(name, type)
        assert expected_msg in str(exception.value)

    def test_add_section(self, parser, state_machine) -> None:
        s1 = state_machine.add_state("State1", is_initial=True)
        sec1_str = test_tools.versioned_swan_str("var x: int32;", "var0")
        sec1 = parser.scope_section(sec1_str)
        s1.add_section(sec1)
        s1.add_section("var y: bool;")
        assert sec1 in s1.body.sections
        assert sec1.owner is s1.body
        sec2 = s1.body.sections[1]
        assert sec2 in s1.body.sections
        assert sec2.owner is s1.body

    def test_create_remove_transition(self, parser, state_machine) -> None:
        s1 = state_machine.add_state("State1", is_initial=True)
        s2 = state_machine.add_state("State2", is_default=True)
        s3 = state_machine.add_state("State3")

        # Strong ones
        strong_trans1 = state_machine.add_strong_transition(s1, s2, guard="i0 > 0")
        assert strong_trans1.is_strong
        assert strong_trans1.guard
        assert not strong_trans1.action.sections

        strong_trans2 = state_machine.add_strong_transition(
            s2, s3, action="emit 'sig1, 'sig2 if i1;"
        )
        assert strong_trans2.is_strong
        assert printer.swan_to_str(strong_trans2.guard) == "true"
        assert isinstance(strong_trans2.action.sections[0], EmitSection)

        # Weak ones
        weak_trans1 = state_machine.add_weak_transition(s1, s2, None)
        assert not weak_trans1.is_strong
        assert not weak_trans1.priority
        assert printer.swan_to_str(weak_trans1.guard) == "true"
        assert not weak_trans1.action.sections

        guard = parser.expression(SwanString("i0 > i1"))
        action = Scope(
            [parser.scope_section(SwanString("let y = Flows::Times(TIME_TO_MOTORS_NORMAL, true);"))]
        )
        weak_trans2 = state_machine.add_weak_transition(s2, s3, 1, guard=guard, action=action)
        assert not weak_trans2.is_strong
        assert weak_trans2.priority.value == "1"
        assert weak_trans2.guard
        assert isinstance(weak_trans2.action.sections[0], LetSection)

        weak_trans3 = state_machine.add_weak_transition(
            s1, s3, 3, guard="not i1", action="emit 'sig1, 'sig2 if i1;"
        )
        assert not weak_trans3.is_strong
        assert weak_trans3.priority.value == "3"
        assert weak_trans3.guard
        assert isinstance(weak_trans3.action.sections[0], EmitSection)

        assert len(state_machine.all_transitions) == 5
        assert len(state_machine.transition_decls) == 5

        state_machine.remove_transition(strong_trans1)
        state_machine.remove_transition(strong_trans2)
        state_machine.remove_transition(weak_trans1)
        state_machine.remove_transition(weak_trans2)
        state_machine.remove_transition(weak_trans3)
        assert not state_machine.transition_decls

    @pytest.mark.parametrize(
        "guard",
        [
            None,
            "not i1",
            "i0 > 0",
            "Flows::Times(TIME_TO_MOTORS_FAILURE, true)",
            "(restart Flows::Times every isMotorFaulty) (TIME_TO_MOTORS_NORMAL, true)",
        ],
    )
    def test_transition_guard(self, s1_to_s2_transition, parser, guard) -> None:
        expr_guard = parser.expression(SwanString(guard)) if guard else None
        s1_to_s2_transition.guard = expr_guard
        assert s1_to_s2_transition.guard is expr_guard

    @pytest.mark.parametrize(
        "action",
        [
            None,
            "emit 'sig1;",
            "emit 'sig1, 'sig2 if i1;",
            "let y = Flows::Times(TIME_TO_MOTORS_NORMAL, true);",
        ],
    )
    def test_transition_action(self, s1_to_s2_transition, parser, action) -> None:
        if action:
            scope_section = parser.scope_section(SwanString(action))
        scope = Scope([scope_section] if action else None)
        s1_to_s2_transition.action = scope
        assert s1_to_s2_transition.action is scope
        if action:
            assert isinstance(s1_to_s2_transition.action.sections[0], ScopeSection)
        else:
            assert not s1_to_s2_transition.action.sections

    def test_fork_creation_from_transition(self, state_machine, s1_to_s2_transition) -> None:
        # Before conversion: two States, One transition
        # After: One (tail) State, One transition containing the Fork.
        # The Fork contains one Transition leading to the (head) State.
        original_src = s1_to_s2_transition.tail
        original_tgt = s1_to_s2_transition.head

        fork, out_trans = s1_to_s2_transition.add_fork()

        # Checks on altered existing transition
        assert s1_to_s2_transition in state_machine._items
        assert s1_to_s2_transition.target is fork
        assert s1_to_s2_transition.tail is original_src
        assert s1_to_s2_transition.head is fork
        assert s1_to_s2_transition.owner is state_machine

        # Checks on created Fork (first value of the returned tuple)
        assert fork.owner is s1_to_s2_transition
        assert fork.from_transition is s1_to_s2_transition
        assert len(fork.transitions) == 1

        # Checks on additional created Transition (second value of the returned tuple)
        assert out_trans not in state_machine._items
        assert out_trans in fork.transitions
        assert out_trans.source is None
        assert out_trans.tail is fork
        assert out_trans.head is original_tgt
        assert out_trans.owner is fork

    def test_fork_of_fork_creation_from_transition(
        self, state_machine, s3_to_s4_transition
    ) -> None:
        original_tgt = s3_to_s4_transition.head

        first_fork, first_out_trans = s3_to_s4_transition.add_fork()
        second_fork, second_out_trans = first_out_trans.add_fork()

        assert first_out_trans in first_fork.transitions
        assert first_out_trans.source is None
        assert first_out_trans.target is second_fork
        assert first_out_trans.tail is first_fork
        assert first_out_trans.head is second_fork
        assert first_out_trans.owner is first_fork

        assert second_out_trans in second_fork.transitions
        assert second_out_trans.source is None
        assert second_out_trans.tail is second_fork
        assert second_out_trans.head is original_tgt
        assert second_out_trans.owner is second_fork

        assert first_out_trans and second_out_trans not in state_machine._items
        assert first_out_trans and second_out_trans not in state_machine.all_transitions

    def test_fork_add_branch_transition(
        self, state_machine, s1_to_s2_transition, s3_to_s4_transition
    ) -> None:
        # From a strong transition
        fork, outgoing_trans = s1_to_s2_transition.add_fork()

        s5 = state_machine.add_state("State5")
        branch1 = fork.add_fork_transition(s5, 2)
        assert branch1.is_strong
        assert branch1._owner is fork
        assert branch1.tail is fork
        assert branch1.head is s5
        assert not branch1.is_resume

        s6 = state_machine.add_state("State6")
        guard = "i0 > i1"
        action = "emit 'sig1;"
        branch2 = fork.add_fork_transition(s6, 3, guard, action, True)
        assert branch2.is_strong
        assert branch2.is_resume
        assert printer.swan_to_str(branch2.guard) == guard

        # From a weak transition
        fork, outgoing_trans = s3_to_s4_transition.add_fork()

        s7 = state_machine.add_state("State7")
        branch3 = fork.add_fork_transition(s7, 2)
        assert not branch3.is_strong
        assert branch3._owner is fork
        assert branch3.tail is fork
        assert branch3.head is s7
        assert not branch3.is_resume

        s8 = state_machine.add_state("State8")
        branch4 = fork.add_fork_transition(s8, 3, "i0 > i1", "emit 'sig1, 'sig2 if i1;", True)
        assert not branch4.is_strong
        assert branch4.is_resume

        assert printer.swan_to_str(branch4.guard) == guard
        assert len(state_machine.states) == 9

    def test_fork_add_else_branch_transition(self, state_machine, s1_to_s2_transition) -> None:
        # From a strong transition
        fork, outgoing_trans = s1_to_s2_transition.add_fork()

        s3 = state_machine.add_state("State3")
        branch1 = fork.add_fork_transition(s3, 2)

        s4 = state_machine.add_state("State4")
        else_branch = fork.add_fork_transition(s4, 3, is_resume=True, is_else=True)

        assert branch1.is_strong
        assert not branch1.is_resume
        assert branch1.tail is fork
        assert branch1.head is s3

        assert else_branch.is_strong
        assert else_branch.is_resume
        assert else_branch.tail is fork
        assert else_branch.head is s4
        assert else_branch.guard is None

        assert len(state_machine.states) == 5
