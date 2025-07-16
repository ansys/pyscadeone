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

# cSpell: ignore autouse

import os
import subprocess
import shutil
from pathlib import Path
import pytest

PYTHON = Path(__file__).parents[2] / ".venv/Scripts/python.exe"

# Examples require C:\Scade One. check if it is installed
s_one_install = "C:/Scade One"
s_one_exists = Path(s_one_install).exists()


# Following fixture cleans up FMU data after tests
# - it is module scoped: called once before and after all tests
# - it is autouse: called automatically
# - it is a yield fixture: the code after yield is executed after all tests
@pytest.fixture(scope="module", autouse=True)
def clean_fmu_data():
    # nothing to do
    yield
    # Tear down
    print("\nTearing down unnecessary files...")
    shutil.rmtree("QuadFlight_FMU_ME", ignore_errors=True)
    shutil.rmtree("QuadFlight_FMU_CS", ignore_errors=True)


def check_example(example: Path):
    """Return True if Scade One is not required for example or if it is installed."""
    with example.open() as fd:
        for line in fd:
            if line.find(s_one_install) > 0:
                return s_one_exists
    return True


def collect():
    """Collect Python files in documentation tree"""
    # Root directory for doc tree analysis
    doc_root = "doc/source"
    examples = []
    for dirpath, _, files in os.walk(doc_root):
        # python_wrapper.py is an example to illustrate the use of the Python Wrapper, but
        # the used example is not supported yet.
        examples.extend(
            Path(dirpath) / f
            for f in files
            if f[-3:] == ".py"
            and f not in ("conf.py", "python_wrapper.py", "python_wrapper_usage.py")
        )
    return examples


def test_example(capsys):
    success = 0
    examples = collect()
    failed = []
    with capsys.disabled():
        print(f"Found {len(examples)} examples")
    for example in examples:
        if check_example(example):
            proc = subprocess.run([PYTHON, str(example)])
            if proc.returncode == 0:
                success += 1
            else:
                failed.append(example)
        else:
            with capsys.disabled():
                print(f"Example {example} requires Scade One")
            success += 1
    with capsys.disabled():
        if failed:
            print("Failed examples:")
            for example in failed:
                print(example)
    assert success == len(examples)
