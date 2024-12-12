# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""
This example demonstrates the use of the generated code API (see: :ref:`Generated Code`).
"""

from pathlib import Path

from ansys.scadeone.core.scadeone import ScadeOne
from ansys.scadeone.core.svc.generated_code import GeneratedCode

# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

app = ScadeOne(install_dir=s_one_install)

project = app.load_project(quad_flight_project)

# get generated code from CodeGen job
code_gen = GeneratedCode(project, "CodeGen")

if not code_gen.is_code_generated:
    print("The Generated Code API cannot be used if the job is not executed first.")
    exit()

# get the list of all operators
for op in code_gen.get_model_operators():
    print(f'operator {op.path} {"** root operator **" if op.root else ""}')

# get the list of all monomorphic instances of polymorphic operators
for op in code_gen.get_model_monomorphic_instances():
    print(f"monomorphic instance {op.path}, source operator: {op.source.path}")

# get model of root operator
root_op = code_gen.get_model_operator(code_gen.root_operators[0])

# get the corresponding cycle function
cfunc = root_op.cycle_method
print(f"\nOperator {root_op.path} => cycle function {cfunc.name}")

# print list of cycle function parameters
print(f"\nCycle function {cfunc.name}:")

for idx, p in enumerate(cfunc.parameters):
    print(f"- param {idx+1}: {p.name} of type {p.type_name}")

# print list of inputs
for idx, elem in enumerate(root_op.inputs):
    print(
        f'- input {idx+1}: {elem.full_name(".")} => '
        + f'param {elem.code_name} of type {elem.code_type["name"]}'
    )

# print list of outputs
for idx, elem in enumerate(root_op.outputs):
    print(
        f'- output {idx+1}: {elem.full_name(".")} => '
        + f'param {elem.code_name} of type {elem.code_type["name"]}'
    )
