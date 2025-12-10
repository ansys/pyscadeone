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

from pathlib import Path
from typing import cast

from ansys.scadeone.core.scadeone import ScadeOne
import ansys.scadeone.core.swan as swan
from ansys.scadeone.core.svc.swan_printer import swan_to_str

# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

app = ScadeOne(install_dir=s_one_install)
project = app.load_project(quad_flight_project)
model = project.model


# Step 1
# Get operator
def quad_fight_control_op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.OperatorDefinition):
        return str(obj.id) == "QuadFlightControl"
    return False


# Get the 'QuadFightControl' operator from model
quad_flight_control_op = cast(
    swan.OperatorDefinition, model.find_declaration(quad_fight_control_op_filter)
)

# Step 2: Get the diagram of the 'QuadFightControl' operator
diag = quad_flight_control_op.diagrams[0]


# Step 3: Get the diagram blocks ('MotorControl', 'FlightControl')
blocks = list(filter(lambda obj: isinstance(obj, swan.Block), diag.objects))

# Step 4
# Get the 'MotorControl' block
motor_control_block = next(
    filter(lambda block: block.instance.path_id.as_string == "MotorControl", blocks)
)

# Get the 'MotorControl' sources ('FlightControl', 'motorStates')
sources = motor_control_block.sources

# Step 5
# Get the 'MotorControl' targets ('motorHealthState', 'rotorCmd',  'byname' group)
targets = motor_control_block.targets


print("The object diagram sources of 'MotorControl' operator are:")
print("-----------------------------------")
message = "Operator name: {block}, Adaptation: {src} => {dst}"
for block, from_adapt, to_adapt_list in sources:
    src = swan_to_str(from_adapt)
    dst = ", ".join(swan_to_str(adapt) for adapt in to_adapt_list)
    if isinstance(block, swan.ExprBlock):
        print(message.format(block=swan_to_str(block.expr), src=src, dst=dst))
    elif isinstance(block, swan.Block):
        print(
            message.format(block=str(block.instance.path_id), src=swan_to_str(from_adapt), dst=dst)
        )

print("-----------------------------------")
print("")
print("The object diagram targets of 'MotorControl' operator are:")
print("-----------------------------------")
for block, from_adapt, to_adapt in targets:
    if isinstance(block, swan.DefBlock):
        print(
            message.format(
                block=swan_to_str(block.lhs),
                src=swan_to_str(from_adapt),
                dst=swan_to_str(to_adapt),
            )
        )
    elif isinstance(block, swan.Bar):
        print(
            message.format(
                block=swan_to_str(block.operation),
                src=swan_to_str(from_adapt),
                dst=swan_to_str(to_adapt),
            )
        )
print("-----------------------------------")


def motor_control_op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.OperatorDefinition):
        return str(obj.id) == "MotorControl"
    return False


# Get the 'MotorControl' operator from model
motor_control_op = cast(swan.OperatorDefinition, model.find_declaration(motor_control_op_filter))

# Get the diagram of the 'MotorControl' operator
diag = motor_control_op.diagrams[0]


def subdiagrams(diag: swan.Diagram):
    return [
        cast(swan.SectionObject, obj).section
        for obj in diag.objects
        if isinstance(obj, swan.SectionObject) and isinstance(obj.section, swan.Diagram)
    ]


control_diag = subdiagrams(diag)[1]


def input_filter(obj: swan.DiagramObject):
    if not isinstance(obj, swan.ExprBlock):
        return False
    if not isinstance(obj.expr, swan.StructProjection):
        return False
    return swan_to_str(obj.expr.expr) == "attitudeCmd"


# Get the 'attitudeCmd' fields from the diagram (expression blocks)
attitude_cmd_fields = list(filter(lambda obj: input_filter(obj), control_diag.objects))


def contains_output(objs):
    return next(filter(lambda obj: isinstance(obj, swan.DefBlock), objs), None) is not None


# Get the blocks following the flows from the 'attitudeCmd' input to the 'rotorCmd' output
blocks = set()
while not contains_output(attitude_cmd_fields):
    targets = set()
    for obj in attitude_cmd_fields:
        for target in obj.targets:
            targets.add(target[0])
            if isinstance(target[0], swan.Block):
                blocks.add(target[0])
    attitude_cmd_fields = targets

print("")
print(
    "In the 'MotorControl' operator, the 'attitudeCmd' input "
    + "passes through the following object diagrams:"
)
print("-----------------------------------")
for source in blocks:
    if isinstance(source.instance, swan.NamedInstance):
        print(f"Operator name: {source.instance.path_id}")
    elif isinstance(source.instance, swan.OperatorExpressionInstance):
        print(f"Operator name: {source.instance.op_expr.operator.path_id}")
        print(f"Instance name: {source.luid}")
    print("-----------------------------------")
