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

# %%
from io import StringIO
from pathlib import Path
import textwrap
from typing import Any, Union

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor
from ansys.scadeone.core.swan import swan_to_str


class DumpVisitor(SwanVisitor):
    Indent = 0

    def __init__(self, fd) -> None:
        self._fd = fd

    def print(self, text):
        self._fd.write(textwrap.indent(text, " " * DumpVisitor.Indent) + "\n")

    def _visit(self, swan_obj: Any, owner: Union[Any, None], property: Union[str, None]) -> None:
        self.print(f"visiting class: {swan_obj.__class__.__name__}")
        DumpVisitor.Indent += 1
        super()._visit(swan_obj, owner, property)
        DumpVisitor.Indent -= 1

    def visit_SwanItem(self, swan_obj, owner, property):
        self.print(
            f"From: {owner.__class__.__name__} "
            + f"as property: {swan_obj.__class__.__name__}.{property}"
        )
        if hasattr(swan_obj, "id"):
            self.print(
                f"Object name:: {swan_to_str(swan_obj.id) if swan_obj.id is not None else 'None'}"
            )
        if hasattr(swan_obj, "luid"):
            self.print(
                f"Object luid:: {swan_to_str(swan_obj.luid) if swan_obj.luid is not None else 'None'}"
            )

    def visit_builtin(self, object, owner_class, property):
        pass


class Test:
    def test_dump(self):
        app = ScadeOne()
        script_dir = Path(__file__).parents[4]
        cc_project = script_dir / "examples/models/CC/CruiseControl/CruiseControl.sproj"
        app.load_project(cc_project)
        model = app.model
        model.load_all_modules()
        # Get module[0]
        module = list(model.modules)[0]
        # Visit, save content in buffer
        buffer = StringIO()
        visitor = DumpVisitor(buffer)
        visitor.visit(module)
        # Save in file
        result = Path(__file__).parent / "test_dump.txt"
        result.write_text(buffer.getvalue())
        buffer.close()
        # compare with oracle (previous correct run)
        oracle = Path(__file__).parent / "oracle_cc_dump.txt"
        a = oracle.read_text()[len("# Oracle for test_visitor.Test.test_dump\n") :]
        b = result.read_text()
        res = a == b
        assert res
        result.unlink(True)
