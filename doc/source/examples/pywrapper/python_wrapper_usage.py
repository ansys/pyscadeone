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

import matplotlib.pyplot as plt
import project.jobs.code_gen.out.code.flight_control_wrapper as flight_control_wrapper
from sources import Ramp

flight_control = flight_control_wrapper.QuadFlightControl()

flight_control.reset()

flight_control.inputs.isReset = False
flight_control.motorStates = (False, False, False, False)
flight_control.inputs.desiredAttitude = (0.0, 0.0, 0.0)
flight_control.inputs.currentAttitude = (0.0, 0.0, 0.0)

cycles = range(20)
ramp = Ramp(0.1, cycles)
frontLeftRotor_sim = []
for cycle in cycles:
    flight_control.inputs.desiredVerticalAccel = ramp[cycle]
    flight_control.cycle()
    frontLeftRotor_sim.append(flight_control.outputs.rotorCmd.frontLeftRotor)

plt.plot(cycles, frontLeftRotor_sim)
plt.show()
