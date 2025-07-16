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

import shutil
from pathlib import Path

from ansys.scadeone.core import ScadeOne

project_path = Path(r"project1\project1.sproj")

app = ScadeOne()

project = app.new_project(project_path)

m0_int = project.add_module_interface("module0")
m0 = project.add_module("module0")
lib_m0 = project.add_module("lib::module1")

type0 = m0_int.add_declaration("type type0 = int32")
const0 = m0.add_constant("const0", "type0", "5")
op0_int = m0_int.add_signature("op0")
op0_int.add_input("in0", "int32")
op0_int.add_input("in1", "int32")
op0_int.add_output(declaration="out0: int32")
op0_int.add_output(declaration="out1: int32")

op0 = m0.add_operator("op0")
op0_in0 = op0.add_input("in0", "int32")
op0_in1 = op0.add_input("in1", "int32")
op0_out0 = op0.add_output("out0", "int32", default="5")
op0_out1 = op0.add_output(declaration="out1: int32")

op1_str = """
    function op1 (in0: int32; in1: int32)
    returns (out0: int32)
    {
        let out0 = in0 + in1;
    }
"""
op1 = m0.add_textual_operator(op1_str)

lib_op = lib_m0.add_operator("libOp")
lib_op_in0 = lib_op.add_input("in0", "int32")
lib_op_out0 = lib_op.add_output("out0", "int32")

m0.use(lib_m0)  # or m0.use("lib::module0")

diag_lib = lib_op.add_diagram()
lib_op_in0_block = diag_lib.add_expr_block(lib_op_in0)
lib_op_out0_block = diag_lib.add_def_block(lib_op_out0)
diag_lib.connect(lib_op_in0_block, lib_op_out0_block)

diag = op0.add_diagram()
op1_block = diag.add_block(op1)
op0_in0_block = diag.add_expr_block(op0_in0)
op0_in1_block = diag.add_expr_block(op0_in1)
const0_block = diag.add_expr_block(const0)
op0_out0_block = diag.add_def_block(op0_out0)
lib_op_block = diag.add_block(lib_op)
op0_out1_block = diag.add_def_block(op0_out1)

diag.connect(op0_in0_block, (op1_block, "in0"))
diag.connect(const0_block, (op1_block, "in1"))
diag.connect((op1_block, "out0"), op0_out0_block)
diag.connect(op0_in1_block, lib_op_block)
diag.connect(lib_op_block, op0_out1_block)

project.save()

for m in project_path.parent.glob("assets/*.swan*"):
    print(f"{'=' * 20}\nModule: {m.name}\n{'=' * 20}")
    print(m.read_text())

# Remove the project for the next execution
shutil.rmtree(project_path.parent)
print(f"Project removed: {project_path}")
