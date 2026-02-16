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
project = app.load_project(quad_flight_project)

# Direct project dependencies
my_dependency = project.dependencies()

# All dependencies recursively
all_dependencies = project.dependencies(all=True)

# Direct project Swan sources
sources = project.swan_sources()

# All sources, including those from dependencies
all_sources = project.swan_sources(all=True)

# Get the model
model = project.model

# All sensors in the model
sensors = model.sensors

# All operator definitions in the model
operator_defs = model.operator_definitions


# Filter function, looking for an operator of name 'EngineControl'
def op_filter(obj: swan.GlobalDeclaration):
    if isinstance(obj, swan.OperatorDefinition):
        return str(obj.id) == "MotorControl"
    return False


# Get the operator
op_decl = model.find_declaration(op_filter)

# All Swan constructs have a path.
type_list = list(model.types)
print(type_list[1].get_full_path())  # => "QuadFlightControl::EngineHealth"

# Stating op_decl is indeed a Swan operator
operator = cast(swan.OperatorDefinition, op_decl)
print(f"first input: {operator.inputs[0].id}")  # => 'attitudeCmd'
