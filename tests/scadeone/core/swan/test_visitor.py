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

# %%
from pathlib import Path

from ansys.scadeone.core import ScadeOne
from tools import log_diff, swan_to_xml


class Test:
    def test_dump(self, tmp_path: Path):
        app = ScadeOne()
        script_dir = Path(__file__).parents[4]
        cc_project = script_dir / "examples/models/CC/CruiseControl/CruiseControl.sproj"
        app.load_project(cc_project)
        model = app.model
        model.load_all_modules()
        # Get module[0]
        module = list(model.modules)[0]
        # Save in file
        result = tmp_path / "test_dump.xml"
        result.write_text(swan_to_xml(module))
        # compare with oracle (previous correct run)
        oracle = Path(__file__).parent / "oracle_cc_dump.xml"
        a = oracle.read_text()
        b = result.read_text()
        log_diff(actual=b, expected=a, winmerge=True)
        res = a == b
        assert res
