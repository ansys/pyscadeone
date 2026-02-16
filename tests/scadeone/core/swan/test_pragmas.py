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


# ruff: noqa: W293, W291, W605

import pytest

from pathlib import Path
import re
import difflib
from typing import cast, Union

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model import Model
import ansys.scadeone.core.swan as swan

from ansys.scadeone.core.swan.pragmas import (
    PragmaParser,
    DiagramPragma,
    DiagramPragmaParser,
    Coordinates,
    Coordinate,
    Position,
)

from ansys.scadeone.core.svc.swan_visitor import SwanVisitor, Owner, OwnerProperty

from tools import log_diff

pragma_project_path = Path(__file__).parents[3] / "models" / "pragmas" / "pragmas.sproj"


@pytest.fixture(scope="module")
def model():
    app = ScadeOne()
    assert app.load_project(pragma_project_path)
    app.model.load_all_modules()
    return app.model


class TestDiagramPragmas:
    def test_pragma_filter(self):
        pragma1 = PragmaParser().parse('#pragma diagram {"xy":"h-36150;v54737"} #end')
        pragma2 = PragmaParser().parse('#pragma diagram {"xy":"h-36150;v54737"} #end')
        pragmas = [pragma1, pragma2]
        assert len(swan.Pragma.filter(pragmas, swan.PragmaKey.DIAGRAM)) == 2

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            (
                '#pragma diagram {"xy":"h-36150;v54737","wh":"16000;3200","dir":"nw","orient":"H"} #end',
                '{"xy":"h-36150;v54737","wh":"16000;3200","dir":"nw","orient":"H"}',
            ),
            (
                '#pragma diagram {"wp":"v15505|#1376 h14300[#1379, v13695 #6]"} #end',
                '{"wp":"v15505|#1376 h14300[#1379, v13695 #6]"}',
            ),
        ],
    )
    def test_diagram_pragma(self, pragma_str, expected):
        pragma: DiagramPragma = PragmaParser().parse(pragma_str)
        assert str(pragma) == f"#pragma diagram {expected} #end"
        assert str(pragma.data) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            ('{"xy":"h-36150;v54737"}', "h-36150;v54737"),
            ('{"xy":"H-36150;v54737"}', "H-36150;v54737"),
            ('{"xy":"h-36150;V54737"}', "h-36150;V54737"),
            ('{"xy":"H-36150;V54737"}', "H-36150;V54737"),
        ],
    )
    def test_coordinates_parser(self, pragma_str, expected):
        pragma = DiagramPragmaParser().parse(pragma_str)
        assert str(pragma.coordinates) == expected

    def test_size_parser(self):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse('{"wh":"16000;3200"}')
        assert str(pragma_diag.size) == "16000;3200"

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            ('{"dir":"ne"}', "ne"),
            ('{"dir":"nw"}', "nw"),
            ('{"dir":"es"}', "es"),
            ('{"dir":"en"}', "en"),
            ('{"dir":"se"}', "se"),
            ('{"dir":"sw"}', "sw"),
            ('{"dir":"ws"}', "ws"),
            ('{"dir":"wn"}', "wn"),
        ],
    )
    def test_direction_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.direction) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            ('{"orient":"H"}', "H"),
            ('{"orient":"V"}', "V"),
        ],
    )
    def test_orientation_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.orientation) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            (
                '{"wp":"v15505|#1376 h14300 [#1379, v13695 #6]"}',
                "v15505|#1376 h14300[#1379, v13695 #6]",
            ),
            (
                '{"wp": "#1322 h-7267 [v11635 [v11635 [v16560 [#1078, v-6410 #1070], #8], #1302], #4]"}',
                "#1322 h-7267[v11635[v11635[v16560[#1078, v-6410 #1070], #8], #1302], #4]",
            ),
        ],
    )
    def test_wire_info_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.wire_path_info) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            (
                '{"tp":"h20000;v50|#0 h500 h5781;v10600 h0;v-2000|h-2900;v15925 h2000;v0 h5621 h-20000;v7600|#1"}',
                "h20000;v50|#0 h500 h5781;v10600 h0;v-2000|h-2900;v15925 h2000;v0 h5621 h-20000;v7600|#1",
            )
        ],
    )
    def test_arrow_info_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.transition_path_info) == expected

    def test_detached_diagram(self):
        pragma = DiagramPragmaParser().parse("detached")
        assert pragma and pragma.is_detached
        assert str(pragma) == "#pragma diagram detached #end"

    def test_invalid_diagram(self):
        pragma = PragmaParser().parse("#pragma diagram some invalid pragma #end")
        assert (
            pragma
            and isinstance(pragma, swan.Pragma)
            and not isinstance(pragma, swan.DiagramPragma)
        )
        assert str(pragma) == "#pragma diagram some invalid pragma #end"


class TestDiagramCoordinates:
    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (
                Coordinate(Position.RELATIVE, 10),
                Coordinate(Position.ABSOLUTE, -20),
                "h10;V-20",
            ),
            (None, Coordinate(Position.ABSOLUTE, -20), "V-20"),
            (Coordinate(Position.RELATIVE, 10), None, "h10"),
            (None, None, ""),
        ],
    )
    def test_str(self, x, y, expected):
        coordinates = Coordinates(x, y)
        assert str(coordinates) == expected


class PragmaVisitor(SwanVisitor):
    def __init__(self):
        super().__init__()
        self.pragmas = []

    def visit_Pragma(self, swan_obj: swan.Pragma, owner: Owner, owner_property: OwnerProperty):
        assert owner is swan_obj.owner
        pragma = str(swan_obj)
        self.pragmas.append(pragma)


class TestPragmas:
    PragmaRe = re.compile(r"(#pragma .*? #end)", re.DOTALL)
    ProtectedPragmaRe = re.compile(r"\{(\w+)%.*?(#pragma.*?#end).*?%\1\}")

    def _fix_for_test(self, pragma: str) -> str:
        """Fixes the pragma string by removing extra spaces and normalizing the format."""

        pragma = re.sub(r" +", " ", pragma)
        pragma = re.sub(r"^[ \t]+", "", pragma, flags=re.MULTILINE)

        # if pragma.find("diagram") != -1:
        #     pragma = "diagram"
        return pragma

    def test_visitor(self, model: Model, tmp_path):
        """Test that the pragmas extracted by the visitor match those found in the code.
        The test does not check for exact whitespaces (formatting) but rather
        that the pragmas are the same in both cases.
        """

        visitor = PragmaVisitor()
        # Extract pragmas from all modules
        for item in model.all_modules:
            visitor.visit(item)
        # Extract pragmas from code using regex
        code_pragmas = []
        protected_pragmas = []
        for module in model.modules:
            source_file = module.source
            code = Path(source_file).read_text()
            # capture pragmas
            code_pragmas.extend(self.PragmaRe.findall(code))
            # capture "protected" pragmas in {%...%} format
            protected_pragmas.extend(m[2] for m in self.ProtectedPragmaRe.finditer(code))
        assert protected_pragmas, "Protected pragmas not found in code"

        # Now, check
        # sort and fix pragmas
        all_pragmas = sorted(self._fix_for_test(p) for p in visitor.pragmas)
        # for and fix while discarding protected pragmas from code
        code_pragmas = sorted(
            self._fix_for_test(p) for p in code_pragmas if p not in protected_pragmas
        )
        # code_pragmas.append("<force diff>")  # to test diff
        if all_pragmas != code_pragmas:
            code = "\n".join(code_pragmas)
            pyscadeone = "\n".join(all_pragmas)
            log_diff(actual=pyscadeone, expected=code, winmerge=True)
            assert False, (
                "Pragmas from visitor and code do not match. Set log_merge=True in log_diff() to see differences."
            )

    def test_printer(self, model: Model):
        """Test that the pragmas extracted by the Swan printer match those found in the code.
        The test does not check for exact whitespaces (formatting) but rather
        that the pragmas are the same in both cases.
        """
        # Table of expected differences between the printer and the code.
        # Some modifications are expected in the printer output, as formatting may differ.
        # FIXME: some of these differences are not expected, but they are there, and should be fixed. (op_expr, etc.)
        is_ok = {
            "basic.swan": """--- pyscadone
+++ source
@@ -19,6 +19,7 @@
 group #pragma cg C:name group? #end group0 = (int32, int32);
 
 const 
+
 #pragma   with 2 spaces before #end
 #pragma #toto # #end
 #pragma two spaces at the end   #end pragma_tests: int32 = 0;
@@ -99,6 +100,6 @@
 
 const 
 #pragma hi there #end
-#pragma ######end #end check_end: int32 = 0;
+#pragma ######end #end check_end : int32 = 0;
 
 #pragma basic #end
""",
            "errors.swan": """--- pyscadone
+++ source
@@ -45,6 +45,5 @@
 
 {const%const #pragma error #end  int32 = 0;%const}
 
-const 
-#pragma hello world #end
-#pragma ??? #end foo: int32 = 0;
+const #pragma hello world #end
+      #pragma ??? #end foo: int32 = 0;
""",
            "control.swan": """--- pyscadone
+++ source
@@ -9,17 +9,19 @@
       where
         (#1 group)
     #pragma diagram {"xy":"H-40000;V9750","wh":"10000;7000"} #end)
-    (#2 block (fold (map (+)) <<4>>) <<4>>
+    (#2 block (fold 
+                (map ({op_expr%+%op_expr})) <<4>>)
+               <<4>>
     #pragma diagram {"xy":"H-8000;V4950","wh":"20000;21000"} #end)
     (#4 expr i0
     #pragma diagram {"xy":"H-51500;V9750"} #end)
-    (#5 expr 0_i32 ^ 4
+    (#5 expr 0_i32^4
     #pragma diagram {"xy":"H-39000;V-5450","wh":"12000;3200"} #end)
     (#6 expr #7 ^ (4)
       where
         (#7 group)
     #pragma diagram {"xy":"H-27500;V9750","wh":"10000;7000"} #end)
-    (#8 block (function x, y => x * y)
+    (#8 block ({op_expr%function x,y => x*y%op_expr})
     #pragma diagram {"xy":"H-45000;V28150","wh":"20000;14000"} #end)
     (#9 block (op_simple_blocks \ i0: 0)
     #pragma diagram {"xy":"H-5500;V28150","wh":"20000;14000"} #end)
""",
            "multiline.swan": """--- pyscadone
+++ source
@@ -10,7 +10,7 @@
   returns (o0: int32;)
 {
   diagram
-    (#0 block (function x => x)
+    (#0 block ({op_expr%function x => x%op_expr})
     #pragma diagram {"xy":"H-9075;V-10350","wh":"20000;14000"} #end)
     (#1 expr i0
     #pragma diagram {"xy":"H-38575;V-10350"} #end)
""",
        }
        for module in [m for m in model.modules if m.file_name in ("multiline.swan",)]:
            code = Path(module.source).read_text()
            pyscadeone = swan.swan_to_str(module, True)
            # capture pragmas
            if code == pyscadeone:
                continue
            # Compute the diff
            diff = "".join(
                difflib.unified_diff(
                    pyscadeone.splitlines(keepends=True),
                    code.splitlines(keepends=True),
                    fromfile="pyscadone",
                    tofile="source",
                )
            )
            accepted_diff = is_ok.get(module.file_name, "")
            if accepted_diff is True or diff == accepted_diff:
                continue
            print(diff)
            log_diff(actual=pyscadeone, expected=code, ext=".swan", winmerge=True)

            assert False, "Pragmas from printer and code do not match. "

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            ("", ""),
            ("  ", ""),
            (" " * 5, " " * 3),
            ("key", "key"),
            # only one space after #pragma and before #end is removed, other spaces are kept
            # but one before value is removed and printed as one space
            ("   key    value    ", "  key    value   "),
            (" key v1 v2 ", "key v1 v2"),
            (" key\nv1 v2 ", "key\nv1 v2"),
            (" key\nv1\nv2\n ", "key\nv1\nv2\n"),
        ],
    )
    def test_misc(self, content, expected):
        """Test that the pragma parser can handle various pragma content.
        content: str
            The content of the pragma, which may include leading or trailing spaces,
            multiple spaces, or newlines.
        expected: str
            The expected output after parsing the pragma content, with 2 spaces around.
        """
        pragma = PragmaParser().parse(f"#pragma{content}#end")
        assert isinstance(pragma, swan.Pragma)

        assert str(pragma) == f"#pragma {expected} #end"

    def test_print(self):
        """Test that the pragma parser can handle printing pragmas."""
        src = "#pragma key value #end"
        pragma = PragmaParser().parse(src)
        assert str(pragma) == src
        assert swan.swan_to_str(pragma) == src

    @pytest.mark.parametrize(
        "code",
        [
            """\
function F <<S, {syntax%$$$%syntax}, S2>> (i: int32;)
  returns (o: int32;);
""",
            """\
function F <<#pragma key value #end
             #pragma key2 #end S,
             #pragma data #end {syntax%$$$%syntax},
             S2>> (i: int32;)
  returns (o: int32;);
""",
        ],
    )
    def test_sizes(self, code, swan_parser):
        """Test that the size of the pragma is computed correctly."""
        from ansys.scadeone.core.common.storage import SwanString

        swan_obj = swan_parser.operator_decl_or_def(SwanString(code))
        result = swan.swan_to_str(swan_obj)
        assert result == code

    def test_assertion_pragma(self, swan_parser):
        code = """
function operator0 (i0: int32;)
  returns (o0: int32;)
{
  diagram
    (guarantee
              #pragma guarantee #end
              #pragma doc guarantee #end {luid%$$$$%luid}: #11;
      where
        (#11 group)
    #pragma diagram {"xy":"H-72050;V40100"} #end)
    (assume
           #pragma assume #end
           #pragma doc assume #end $A1: #2;
      where
        (#2 group)
    #pragma diagram {"xy":"H-78725;V50025"} #end)
    (assert
           #pragma assert #end
           #pragma doc assert #end $A2: true;
    #pragma doc equation #end
    #pragma equation #end
    #pragma diagram {"xy":"H-37700;V39289","wh":"42000;6078"} #end)
}
"""
        from ansys.scadeone.core.common.storage import SwanString

        swan_obj = cast(swan.OperatorDefinition, swan_parser.operator_decl_or_def(SwanString(code)))
        result = "\n" + swan.swan_to_str(swan_obj)
        # log_diff(actual=result, expected=code, winmerge=True)
        assert result == code

    def test_def_by_case_pragmas(self, model: Model):
        """Test availability and validity of pragmas property for DefByCase objects."""
        basic_module = next(filter(lambda mod: mod.file_name == "basic.swan", model.modules))
        assert basic_module is not None

        # focus on Operator 'op_control' for testing DefByCase
        op_control = next(
            filter(lambda op: op.id.value == "op_control", basic_module.operator_definitions)
        )
        assert op_control is not None

        diagram = next(iter(op_control.diagrams))
        state_machine_block = next(iter(diagram.objects)) if diagram is not None else None
        assert state_machine_block is not None

        state_machine = state_machine_block.def_by_case
        assert isinstance(state_machine, swan.StateMachine)
        assert isinstance(state_machine_block, swan.StateMachineBlock)
        assert state_machine.pragmas == state_machine_block.pragmas

    def test_scope_section_pragmas(self, model: Model):
        """Test availability and validity of pragmas property for ScopeSection objects."""
        basic_module = next(filter(lambda mod: mod.file_name == "basic.swan", model.modules), None)
        assert basic_module is not None

        # focus on Operator 'subdiagram' for testing ScopeSection
        subdiagram = next(
            filter(lambda op: op.id.value == "subdiagram", basic_module.operator_definitions)
        )
        assert subdiagram is not None

        diagram = next(iter(subdiagram.diagrams))
        section_object = next(iter(diagram.objects)) if diagram is not None else None
        assert section_object is not None

        nested_diagram = section_object.section
        assert isinstance(section_object, swan.SectionObject)
        assert isinstance(nested_diagram, swan.Diagram)
        assert nested_diagram.pragmas == section_object.pragmas


class TestCGPragma:
    @pytest.mark.parametrize(
        "pragma, expected",
        [
            ("C:const", True),
            ("keep", True),
            ("default", True),
            ("C:scalar", True),
            ("probe", True),
            ("C:enum_val 42", "42"),
            ("C:initializer 0x1234", "0x1234"),
            ("C:name my_name", "my_name"),
        ],
    )
    def test_cg_pragma(self, pragma, expected: Union[bool, str]):
        """Test that the CG pragma is parsed correctly."""
        pragma = PragmaParser().parse(f"#pragma cg {pragma} #end")
        assert isinstance(pragma, swan.CGPragma)
        pragma = cast(swan.CGPragma, pragma)
        match pragma.kind:
            case (
                swan.CGPragmaKind.CONST
                | swan.CGPragmaKind.KEEP
                | swan.CGPragmaKind.DEFAULT
                | swan.CGPragmaKind.SCALAR
                | swan.CGPragmaKind.PROBE
            ):
                assert expected
            case swan.CGPragmaKind.ENUM_VALUE:
                assert pragma.get_enum_value() == expected
            case swan.CGPragmaKind.INITIALIZER:
                assert pragma.get_initializer() == expected
            case swan.CGPragmaKind.NAME:
                assert pragma.get_name() == expected
            case _:
                assert False, f"Expected CGPragma, got {pragma.kind}"


class TestDocumentationPragma:
    def test_documentation_pragma(self):
        text = "This is a test"
        pragma_str = f"#pragma doc {text} #end"
        pragma = PragmaParser().parse(pragma_str)
        assert isinstance(pragma, swan.DocumentationPragma)
        assert pragma.text == text
        assert swan.swan_to_str(pragma) == pragma_str

    def test_multiline_documentation_pragma(self):
        text = "This is \na\n      test    multiline"
        pragma_str = f"#pragma doc {text} #end"
        pragma = PragmaParser().parse(pragma_str)
        assert isinstance(pragma, swan.DocumentationPragma)
        assert pragma.text == text
        assert swan.swan_to_str(pragma) == pragma_str


class TestTraceabilityPragma:
    def test_traceability_pragma(self):
        ref = "req1"
        pragma_str = f"#pragma requirement {ref} #end"
        pragma = PragmaParser().parse(pragma_str)
        assert isinstance(pragma, swan.TraceabilityPragma)
        assert pragma.reference == ref
        assert swan.swan_to_str(pragma) == pragma_str

    def test_multiline_traceability_pragma(self):
        ref = "req \nreq1 \n   req2 \n\nreq3"
        pragma_str = f"#pragma requirement {ref} #end"
        pragma = PragmaParser().parse(pragma_str)
        assert isinstance(pragma, swan.TraceabilityPragma)
        assert pragma.reference == ref
        assert swan.swan_to_str(pragma) == pragma_str
