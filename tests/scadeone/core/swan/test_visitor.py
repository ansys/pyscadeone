# %%
from io import StringIO
from pathlib import Path
import textwrap
from typing import Any, Union

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor


class DumpVisitor(SwanVisitor):
    Indent = 0

    def __init__(self, fd):
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
            self.print(f"Object name:: {swan_obj.id}")
        if hasattr(swan_obj, "luid"):
            self.print(f"Object luid:: {swan_obj.luid}")

    def visit_builtin(self, object, owner_class, property):
        pass


class Test:
    def test_dump(self):
        app = ScadeOne()
        script_dir = Path(__file__).parents[4]
        cc_project = script_dir / "examples/models/CC/CruiseControl/CruiseControl.sproj"
        model = app.load_project(cc_project).model
        model.load_all_modules()
        # Get module[1]
        module = list(model.modules)[1]
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
