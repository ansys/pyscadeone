# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model import Model
import ansys.scadeone.core.swan as swan

# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

app = ScadeOne(install_dir=s_one_install)
model = app.load_project(quad_flight_project).model

model.load_all_modules()


def get_module(name: str, model: Model) -> swan.Module:
    return next(filter(lambda module: module.name.as_string == name, model.modules), None)


quad_flight_ctrl_module = get_module("QuadFlightControl", model)

# Get the 'MotorControl' operator from the 'QuadFlightControl' module
motor_control_op = quad_flight_ctrl_module.get_declaration("MotorControl")

# Get the 'MotorControl' scope
scope = motor_control_op.body

# Get the 'MotorsHealth' group, defined in the 'QuadTypes' module (alias 'T'),
# from the 'MotorControl' scope
mh_group = scope.get_declaration("T::MotorsHealth")

# Get the 'AttitudeType' type, defined in the 'QuadTypes' module (alias 'T'),
# from the 'MotorControl' scope
att_type = scope.get_declaration("T::AttitudeType")

# Get the 'PI' constant from the 'MotorControl' scope
pi_const = scope.get_declaration("PI")

# Get the 'RotorControl' operator from the 'MotorControl' scope
rotor_ctrl_op = scope.get_declaration("RotorControl")

# Get the 'RotateXY' operator, defined in the 'QuadUtils' module, from the 'MotorControl' scope
rotate_xy_op = scope.get_declaration("QuadUtils::RotateXY")

# Get the 'thrustControlCmd' input from the 'MotorControl' scope
thrust_ctrl_cmd_var = scope.get_declaration("thrustControlCmd")
