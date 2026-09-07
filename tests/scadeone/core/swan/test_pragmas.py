# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import pytest

from pathlib import Path
import re
import difflib
from typing import cast, Union

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model import Model
from ansys.scadeone.core.model.loader import SwanParser
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
from test_tools import log_diff

pragma_project_path = Path(__file__).parents[3] / "models" / "pragmas" / "pragmas.sproj"


@pytest.fixture(scope="module")
def model():
    app = ScadeOne()
    project = app.load_project(pragma_project_path)
    assert project is not None
    project.model.load_all_modules()
    return project.model


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
                '#pragma diagram {"IsGraphicalVariant":true,"xy":"h-36150;v54737","wh":"16000;3200","dir":"nw","orient":"H","IsGraphicalVariant":true} #end',
                '{"xy":"h-36150;v54737","wh":"16000;3200","dir":"nw","orient":"H","IsGraphicalVariant":true}',
            ),
            (
                '#pragma diagram {"wp":"v15505|#1376 h14300[#1379, v13695 #6]",IsGraphicalVariant":true} #end',
                '{"wp":"v15505|#1376 h14300[#1379, v13695 #6]",IsGraphicalVariant":true}',
            ),
            (
                '#pragma diagram {"xy":"H-45000;V28150","wh":"20000;14000","dir":"es","orient":"V","wp":"v15505|#1376 h14300[#1379, v13695 #6]"} #end',
                '{"xy":"H-45000;V28150","wh":"20000;14000","dir":"es","orient":"V","wp":"v15505|#1376 h14300[#1379, v13695 #6]"}',
            )
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

    def test_is_graphical_variant(self):
        pragma = PragmaParser().parse('#pragma diagram {"IsGraphicalVariant":true} #end')
        assert pragma and pragma.is_graphical_variant
        assert str(pragma) == '#pragma diagram {"IsGraphicalVariant":true} #end'


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
            log_diff(actual=pyscadeone, expected=code, winmerge=False)
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
            "control.swan": r"""--- pyscadone
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
     (#9 block (op_simple_blocks \\ i0: 0)
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
            log_diff(actual=pyscadeone, expected=code, ext=".swan", winmerge=False)

            assert False, "Pragmas from printer and code do not match. "

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            ("", " "),
            ("  ", " "),
            (" " * 5, " " * 4),
            ("key", "key "),
            # only one space after #pragma and before #end is removed, other spaces are kept
            # but one before value is removed and printed as one space
            ("   key    value    ", "  key    value   "),
            (" key v1 v2 ", "key v1 v2"),
            (" key\nv1 v2 ", "key \nv1 v2"),
            (" key\nv1\nv2\n ", "key \nv1\nv2\n"),
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
             #pragma key2  #end S,
             #pragma data  #end {syntax%$$$%syntax},
             S2>> (i: int32;)
  returns (o: int32;);
""",
        ],
    )
    def test_sizes(self, code, parser: SwanParser):
        """Test that the size of the pragma is computed correctly."""
        from ansys.scadeone.core.common.storage import SwanString

        swan_obj = parser.operator_decl_or_def(SwanString(code))
        result = swan.swan_to_str(swan_obj)
        assert result == code

    def test_assertion_pragma(self, parser: SwanParser):
        code = """
function operator0 (i0: int32;)
  returns (o0: int32;)
{
  diagram
    (guarantee
              #pragma guarantee  #end
              #pragma doc guarantee #end {luid%$$$$%luid}: #11;
      where
        (#11 group)
    #pragma diagram {"xy":"H-72050;V40100"} #end)
    (assume
           #pragma assume  #end
           #pragma doc assume #end $A1: #2;
      where
        (#2 group)
    #pragma diagram {"xy":"H-78725;V50025"} #end)
    (assert
           #pragma assert  #end
           #pragma doc assert #end $A2: true;
    #pragma doc equation #end
    #pragma equation  #end
    #pragma diagram {"xy":"H-37700;V39289","wh":"42000;6078"} #end)
}
"""
        from ansys.scadeone.core.common.storage import SwanString

        swan_obj = cast(swan.OperatorDefinition, parser.operator_decl_or_def(SwanString(code)))
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
        # TODO: Check why pragmas in state_machine shall be the same as state_machine_block
        assert state_machine.pragmas == state_machine_block.def_by_case.pragmas

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
        # TODO: Check why pragmas in nested_diagram shall be the same as section_object
        assert nested_diagram.pragmas == section_object.section.pragmas


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


class TestNewLocationPragmas:
    """Test new location pragmas"""

    def _parse_and_verify_roundtrip(
        self, parser: SwanParser, content: str
    ) -> swan.OperatorDefinition:
        """Helper method to parse Swan content and verify roundtrip printing."""
        from ansys.scadeone.core.common.storage import SwanString

        swan_obj = cast(swan.OperatorDefinition, parser.operator_decl_or_def(SwanString(content)))
        result = "\n" + swan.swan_to_str(swan_obj)
        if result != content:
            log_diff(actual=result, expected=content, winmerge=False)
        assert result == content, "Roundtrip parsing/printing failed"
        return swan_obj

    def _verify_pragmas(self, pragmas: list, expected_keys: list[str]):
        """Helper method to verify pragma count and keys."""
        assert len(pragmas) == len(expected_keys), (
            f"Expected {len(expected_keys)} pragmas, got {len(pragmas)}"
        )
        for i, expected_key in enumerate(expected_keys):
            assert pragmas[i].key == expected_key, (
                f"Expected pragma key '{expected_key}', got '{pragmas[i].key}'"
            )

    def test_new_location_automaton_pragma(self, parser: SwanParser):
        content = """
node automaton_pragma ()
  returns ()
{
  diagram
    (#pragma auto_1  #end
     #pragma auto_2  #end
     automaton #2
       initial state #3 state0
       #pragma diagram {"xy":"h-14250;v0","wh":"12000;12000"} #end :
       state #4 state1
       #pragma diagram {"xy":"h14250;v0","wh":"12000;12000"} #end :
       :1: #3 until 
       restart #4
       #pragma diagram {"tp":"h6000;v0|#3 h5500 h5500 h-6000;v0|#4"} #end;
    #pragma diagram {"xy":"H-112275;V-92350","wh":"48500;20000"} #end)
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        diagram = next(iter(swan_obj.diagrams))
        assert diagram is not None, "Diagram should exist"

        automaton_block = next(iter(diagram.objects))
        assert isinstance(automaton_block, swan.StateMachineBlock)
        state_block = automaton_block.def_by_case
        assert isinstance(state_block, swan.StateMachine)

        self._verify_pragmas(state_block.pragmas, ["auto_1", "auto_2"])

    def test_new_location_activeIf_pragma(self, parser: SwanParser):
        content = """
function activeIf_pragma ()
  returns ()
{
  diagram
    (#pragma act_if_1  #end
     activate #3 $activate_if
      if true
      then
        {
        #pragma diagram {"xy":"h0;v-10000","wh":"50000;20000"} #end
        }
      else
        {
        #pragma diagram {"xy":"h0;v13859","wh":"50000;20000"} #end
        }
  #pragma diagram {"xy":"H-143775;V-71998","wh":"50000;47719"} #end)
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        diagram = next(iter(swan_obj.diagrams))
        assert diagram is not None, "Diagram should exist"

        activate_block = next(iter(diagram.objects))
        assert isinstance(activate_block, swan.ActivateIfBlock)
        activate_if = activate_block.def_by_case
        assert isinstance(activate_if, swan.ActivateIf)

        self._verify_pragmas(activate_if.pragmas, ["act_if_1"])

    def test_new_location_activeWhen_pragma(self, parser: SwanParser):
        content = """
function activeWhen_pragma (i1: int32 default = 1;)
  returns ()
{
  diagram
    (#pragma act_when  #end
     activate #4 $pattern2 when i1 > 0 match
      | true :
        {
        #pragma diagram {"xy":"h0;v-8570","wh":"50000;20209"} #end
        }
      | false :
        {
        #pragma diagram {"xy":"h0;v15394","wh":"50000;20000"} #end
        }
#pragma diagram {"xy":"H-134650;V-73575","wh":"50000;50788"} #end)
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        diagram = next(iter(swan_obj.diagrams))
        assert diagram is not None, "Diagram should exist"

        activate_block = next(iter(diagram.objects))
        assert isinstance(activate_block, swan.ActivateWhenBlock)
        activate_when = activate_block.def_by_case
        assert isinstance(activate_when, swan.ActivateWhen)

        self._verify_pragmas(activate_when.pragmas, ["act_when"])

    def test_new_location_let_pragma(self, parser: SwanParser):
        content = """
function let_pragma (i0: int32;)
  returns (o0: int32;)
{
  #pragma let_eq_text  #end
  #pragma incr ment #end
  let o0 = i0 + 1;
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        text_body = swan_obj.body
        assert text_body is not None
        assert isinstance(text_body, swan.Scope)

        sct = text_body.sections[0]
        self._verify_pragmas(sct.pragmas, ["let_eq_text", "incr"])

    def test_new_location_var_pragma(self, parser: SwanParser):
        content = """
function var_pragma ()
  returns ()
{
  #pragma var_equ  #end
  var
     t: bool default = true;
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        text_body = swan_obj.body
        assert text_body is not None
        assert isinstance(text_body, swan.Scope)

        sct = text_body.sections[0]
        self._verify_pragmas(sct.pragmas, ["var_equ"])

    @pytest.mark.parametrize(
        "pragma_type, content, expected_keys",
        [
            (
                "assert",
                """
function assert_pragma (i0: int32;)
  returns ()
{
  assert
        #pragma assert_pgm  #end $true: i0 > 0;
}
""",
                ["assert_pgm"],
            ),
            (
                "assume",
                """
function assume_pragma ()
  returns ()
{
  assume
        #pragma assu_pgm  #end $assume_block: true;
}
""",
                ["assu_pgm"],
            ),
            (
                "guarantee",
                """
function guarantee_pragma ()
  returns ()
{
  guarantee
           #pragma gua_tee  #end $G1: true;
}
""",
                ["gua_tee"],
            ),
        ],
    )
    def test_new_location_assertion_pragmas(
        self, parser: SwanParser, pragma_type: str, content: str, expected_keys: list[str]
    ):
        """Test pragmas on assert, assume, and guarantee statements."""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        text_body = swan_obj.body
        assert text_body is not None
        assert isinstance(text_body, swan.Scope)

        sct = text_body.sections[0]
        assert_section = sct.assertions[0]
        assert isinstance(assert_section, swan.Assertion)

        self._verify_pragmas(assert_section.pragmas, expected_keys)

    def test_new_location_equation_pragma(self, parser: SwanParser):
        content = """
function equation_pragma (i0: int32;)
  returns (o0: int32;) o0 #pragma sim_pgm  #end  = i0 - 1;"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        text_body = swan_obj.body
        assert text_body is not None
        assert isinstance(text_body, swan.ExprEquation)

        self._verify_pragmas(text_body.pragmas, ["sim_pgm"])

    def test_new_location_let_eq_pragma(self, parser: SwanParser):
        content = """
function let_eq_pragma (i0: int32;)
  returns (o0: int32;)
{
  let o0 #pragma sim_pgm  #end  = i0 - 1;
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        text_body = swan_obj.body
        assert text_body is not None
        assert isinstance(text_body, swan.Scope)

        sct = text_body.sections[0]
        assert isinstance(sct, swan.LetSection)
        eqt = sct.equations[0]
        assert isinstance(eqt, swan.Equation)

        self._verify_pragmas(eqt.pragmas, ["sim_pgm"])

    def test_new_location_operator_instance_group_pragma(self, parser: SwanParser):
        content = """
function operator_instance_group_pragma ()
  returns ()
{
  diagram
    (expr let_eq_pragma $op8 #pragma grp_pgm  #end (1))
}
"""
        swan_obj = self._parse_and_verify_roundtrip(parser, content)

        diagram = next(iter(swan_obj.diagrams))
        assert diagram is not None

        text_body = diagram.objects[0]
        assert isinstance(text_body, swan.ExprBlock)

        self._verify_pragmas(text_body.expr.pragmas, ["grp_pgm"])


class TestAddPragma:
    def test_add_pragma(self):
        const = swan.ConstDecl(
            swan.Identifier("my_const"), is_elaborated=False, type=swan.Int8Type()
        )
        p1 = PragmaParser().parse("#pragma p1  #end")
        p2 = PragmaParser().parse("#pragma p2  #end")
        p3 = PragmaParser().parse("#pragma p3  #end")
        const.add_pragmas(p1)
        assert const.pragmas == [p1]
        const.add_pragmas(p2, p3)
        assert const.pragmas == [p1, p2, p3]
        const_str = swan.swan_to_str(const)
        assert "#pragma p1  #end" in const_str
        assert "#pragma p2  #end" in const_str
        assert "#pragma p3  #end" in const_str
