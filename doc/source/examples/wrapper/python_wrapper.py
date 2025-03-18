# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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
from ansys.scadeone.core.svc.generated_code import GeneratedCode
from ansys.scadeone.core.svc.wrapper.python_wrapper import PythonWrapper


# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

# Job name
job_name = "CodeGen"

# Operator name
operator_name = "QuadFlightControl::QuadFlightControl"

# Wrapper name
out_name = "flight_control_wrapper"

app = ScadeOne(install_dir=s_one_install)
prj = app.load_project(quad_flight_project)

# Load and run the Code Generation job
prj.load_jobs()
cg_job = prj.get_job(job_name)
result = cg_job.run()
assert result.code == 0

# Generate the Python wrapper
_out_name = out_name
_code_gen = GeneratedCode(prj, job_name)
_gen = PythonWrapper(project=prj, code_gen=_code_gen, opt_name=operator_name, out_name=_out_name)
_gen.generate()
