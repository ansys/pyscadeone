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

"""This script is used to run Vale on the documentation files from pre-commit.

Errors may not be captured after execution of vale, as vale always returns 0. This script
is used to get the errors from Vale and return 1 if there are any errors.

It is written in Python to be used on any platform.
Bash might not be available on Windows, and PowerShell may have different names on Linux.
"""

import subprocess
import sys
from pathlib import Path

if not Path("OSS").exists():
    # Not on github repository
    sys.exit(0)
config = "--config=doc/.vale.ini"
proc = subprocess.run(["vale", "sync", config], capture_output=True, text=True)
proc.check_returncode()  # Note: Vale returns 0 even if there are errors
proc = subprocess.run(
    ["vale", "--output=line", config, "doc/source"], capture_output=True, text=True
)
if proc.stdout:  # Message from Vale if there are errors
    print(proc.stdout)
    sys.exit(1)
sys.exit(0)
