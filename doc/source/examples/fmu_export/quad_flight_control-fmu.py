"""
This example demonstrates the use of the FMU export (see: :ref:`FMU Export`).
"""

from pathlib import Path

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.svc.fmu import FMU_2_Export

# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

app = ScadeOne(install_dir=s_one_install)

project = app.load_project(quad_flight_project)

print("Create FMU_Export object")
fmu = FMU_2_Export(project, "CodeGen")

if not fmu.codegen.is_code_generated:
    print("FMU package cannot be generated if the job is not executed first.")
    exit()

library_include = s_one_install / r"libraries\Math\resources\math_stdc.h"
args = {"swan_config_end": f'#include "{library_include}"'}

print("- generate and build the FMI 2.0 files for Model Exchange into QuadFlight_FMU_ME")
fmu.generate("ME", "QuadFlight_FMU_ME")
fmu.build(True, args)

print(
    "- generate and build the FMI 2.0 files for Co-Simulation into QuadFlight_FMU_CS, "
    + "with no source code"
)
fmu.generate("CS", "QuadFlight_FMU_CS")
fmu.build(False, args)
