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

import os
from pathlib import Path

from typing import cast
from collections import deque
from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.swan import StateMachineBlock, State, Fork, swan_to_str

os.chdir(Path(__file__).parents[4] / "examples" / "models" / "Position")

# Load project and get Position automaton
app = ScadeOne()
app.load_project("Position.sproj")
model = app.model
op = model.operator_definitions[0]
diagram = op.diagrams[0]
# automaton is the 1st object in the diagram
position_automaton = cast(StateMachineBlock, diagram.objects[0]).state_machine

# Get initial Stop state
initial_states = position_automaton.initial_state
assert len(initial_states) == 1
assert str(initial_states[0].id) == "Stop"
stop_state = initial_states[0]

# Get target states from Stop state
stop_state_targets = stop_state.get_targets()
expected = {"Up", "Down", "Left", "Right", "Center"}
target_ids = set(str(state.id) for state in stop_state_targets)
assert target_ids == expected

# Explore all transitions from Stop state
buffer = "digraph G {\n"
for s in position_automaton.states:
    buffer += f'  {s.id} [label="{s.id}[{s.lunum}]"]\n'
d = deque(stop_state.strong_transitions + stop_state.weak_transitions)
while d:
    transition = d.popleft()
    transition_info = ""
    match transition.head:
        case State(id=id_):
            target = str(id_)
            transition_info = "resume" if transition.is_resume else "restart"
        case Fork() as fork:
            target = "fork"
            d.extend(fork.transitions)
    match transition.tail:
        case State(id=id_, lunum=lunum):
            source = str(id_)
            transition_info = "strong" if transition.is_strong else "weak"
        case Fork():
            source = "fork"
    guard = f"{swan_to_str(transition.guard)}\\n" if transition.guard else ""
    edge = f' [label="{guard}<{transition_info}>"]'
    buffer += f"  {source} -> {target} {edge}\n"
buffer += "}\n"
print(buffer)

# Get a specific state by its name:
down_state = position_automaton.get_state("Down")
assert down_state is not None
assert str(down_state.id) == "Down"

# Transition access
transition = down_state.strong_transitions[0]
assert isinstance(transition.head, State) and str(transition.head.id) == "Stop"
assert isinstance(transition.tail, State) and str(transition.tail.id) == "Down"
assert transition.is_resume is False
assert transition.guard is not None
guard = swan_to_str(transition.guard)
assert guard == "not d"
assert transition.action is None
