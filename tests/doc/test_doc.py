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

import os
import subprocess
from pathlib import Path
import pytest

PYTHON = Path(__file__).parents[2] / ".venv/Scripts/python.exe"

# Examples require C:\Scade One. check if it is installed
s_one_install = "C:/Scade One"
s_one_exists = Path(s_one_install).exists()


def check_example(example: Path):
    """Check if example requires 's_one_install'"""
    with example.open() as fd:
        for line in fd:
            if line.find(s_one_install) > 0:
                return s_one_exists
    return True


def collect():
    """Collect Python files in documentation tree"""
    # Root directory for doc tree analysis
    doc_root = "doc/source"
    # Python files to skip
    skip = "conf.py"
    examples = []
    for dirpath, _, files in os.walk(doc_root):
        examples.extend(
            os.path.join(dirpath, f) for f in files if f[-3:] == ".py" and f not in skip
        )
    return examples


class TestDocumentation:
    @pytest.mark.parametrize(
        "example",
        collect(),
    )
    def test_example(self, example, capsys):
        if check_example(Path(example)):
            proc = subprocess.run([PYTHON, example])
            assert proc.returncode == 0
        else:
            with capsys.disabled():
                print(f"Example {example} requires Scade One")
