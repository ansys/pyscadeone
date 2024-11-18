from pathlib import Path
from typing import cast

from ansys.scadeone.core.scadeone import ScadeOne
import ansys.scadeone.core.swan as swan

# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

app = ScadeOne(install_dir=s_one_install)
model = app.load_project(quad_flight_project).model


def quad_fight_control_op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.Operator):
        return str(obj.id) == "QuadFlightControl"
    return False


# Get the 'QuadFightControl' operator from model
quad_fight_control_op = cast(swan.Operator, model.find_declaration(quad_fight_control_op_filter))

# Get the diagram of the 'QuadFightControl' operator
diag = next(quad_fight_control_op.diagrams, None)

# Get the diagram blocks ('MotorControl', 'FlightControl')
blocks = list(filter(lambda obj: isinstance(obj, swan.Block), diag.objects))

# Get the 'MotorControl' block
motor_control_block = next(
    filter(lambda block: block.instance.path_id.as_string == "MotorControl", blocks)
)

# Get the 'MotorControl' sources ('FlightControl', 'motorStates')
sources = motor_control_block.sources

# Get the 'MotorControl' targets ('motorHealthState', 'rotorCmd',  'byname' group)
targets = motor_control_block.targets


print("The object diagram sources of 'MotorControl' operator are:")
print("-----------------------------------")
message = "Operator name: {block}, Adaptation: {src} => {dst}"
for block, from_adapt, to_adapt_list in sources:
    src = str(from_adapt)
    dst = ", ".join(str(adapt) for adapt in to_adapt_list)
    if isinstance(block, swan.ExprBlock):
        print(message.format(block=str(block.expr), src=src, dst=dst))
    elif isinstance(block, swan.Block):
        print(message.format(block=str(block.instance.path_id), src=str(from_adapt), dst=dst))

print("-----------------------------------")
print("")
print("The object diagram targets of 'MotorControl' operator are:")
print("-----------------------------------")
for block, from_adapt, to_adapt in targets:
    if isinstance(block, swan.DefBlock):
        print(message.format(block=str(block.lhs), src=str(from_adapt), dst=str(to_adapt)))
    elif isinstance(block, swan.Bar):
        print(
            message.format(block=str(block.operation.name), src=str(from_adapt), dst=str(to_adapt))
        )
print("-----------------------------------")


def motor_control_op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.Operator):
        return str(obj.id) == "MotorControl"
    return False


# Get the 'MotorControl' operator from model
motor_control_op = cast(swan.Operator, model.find_declaration(motor_control_op_filter))

# Get the diagram of the 'MotorControl' operator
diag = next(motor_control_op.diagrams, None)


def input_filter(obj: swan.DiagramObject):
    if not isinstance(obj, swan.ExprBlock):
        return False
    if not isinstance(obj.expr, swan.StructProjection):
        return False
    return str(obj.expr.expr) == "attitudeCmd"


# Get the 'attitudeCmd' fields from the diagram (expression blocks)
attitude_cmd_fields = list(filter(lambda obj: input_filter(obj), diag.objects))


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
    if isinstance(source.instance, swan.PathIdOpCall):
        print(f"Operator name: {source.instance.path_id}")
    elif isinstance(source.instance, swan.PrefixOperatorExpression):
        print(f"Operator name: {source.instance.op_expr.operator.path_id}")
        print(f"Instance name: {source.luid}")
    print("-----------------------------------")
