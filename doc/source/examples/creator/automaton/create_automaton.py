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

import shutil
from pathlib import Path

from ansys.scadeone.core import ScadeOne

project_path = Path(r"project1\project1.sproj")

app = ScadeOne()

project = app.new_project(project_path)

# create a module body
module = project.add_module_body("m_automata")

# add an operator with inputs
operator_def = module.add_operator_definition("operator_def")
operator_def.add_input("c", "bool")
operator_def.add_input("u", "bool")
operator_def.add_input("d", "bool")
operator_def.add_input("r", "bool")
operator_def.add_input("l", "bool")
operator_def.add_input("unlock", "bool")

# Diagram with automaton
diagram = operator_def.add_diagram()
automaton = diagram.add_automaton("automaton0")

# states
stop = automaton.add_state("Stop", is_initial=True)
up = automaton.add_state("Up")
down = automaton.add_state("Down")
left = automaton.add_state("Left")
right = automaton.add_state("Right")
center = automaton.add_state("Center")

# transitions
up_to_stop = automaton.add_strong_transition(up, stop, 1, "not u")
down_to_stop = automaton.add_strong_transition(down, stop, 1, "not d")
left_to_stop = automaton.add_strong_transition(left, stop, 1, "not l")
right_to_stop = automaton.add_strong_transition(right, stop, 1, "not r")
stop_to_up = automaton.add_strong_transition(stop, up, 1, "unlock")
stop_to_center = automaton.add_strong_transition(stop, center, 2, "c")
center_to_stop = automaton.add_strong_transition(center, stop, 1, "not c")

# fork
fork, fork_to_up = stop_to_up.add_fork("u")
fork.add_fork_transition(down, 2, "d")
fork.add_fork_transition(left, 3, "l")
fork.add_fork_transition(right, 4, "r")

project.save()

for m in project_path.parent.glob("assets/*.swan*"):
    print(f"{'=' * 20}\nModule: {m.name}\n{'=' * 20}")
    print(m.read_text())

# Remove the project for the next execution
shutil.rmtree(project_path.parent)
print(f"Project removed: {project_path}")


def fork_from_fork(automaton) -> None:
    fork, fork_to_up = stop_to_up.add_fork("u")
    # Another fork is added from the default outgoing transition
    other_fork, other_fork_to_up = fork_to_up.add_fork()
    other_fork.add_fork_transition(down, 2, "d")
