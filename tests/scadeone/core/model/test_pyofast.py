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

"""
Tests of pyofast.py, with transforms F# Ast into language.* classes
"""

from difflib import Differ
import logging
import re
from typing import Union
from pathlib import Path
import pytest

from ansys.scadeone.core.common.storage import SwanStorage, SwanString
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as S

logging.basicConfig(level=logging.DEBUG)

parser = SwanParser(logging.getLogger("pyofast"))


# Helpers
def cmp_string(orig, new, no_markup=False, diff=False):
    """Compare two string, after replacing spaces

    Parameters
    ----------
    orig : str
        original string
    new : str
        new string
    no_markup : bool, optional
        attempt to remove markups in original string. Default False
    diff : bool, optional
        Call diff.Differ() on strings, by default False
    """
    orig_strip = re.sub(r"\s+", " ", orig).strip()
    new_strip = re.sub(r"\s+", " ", new).strip()
    if no_markup:
        orig_strip = re.sub(r"(?s)\{(\w*)%(.*)%\1\}", r"\2", orig_strip)
    cmp = orig_strip == new_strip
    if not cmp:
        with Path("test_pyofast.txt").open("w") as fd:
            fd.write("===== Original =====\n")
            fd.write(orig_strip)
            fd.write("\n=====   New  =====\n")
            fd.write(new_strip)
    else:
        Path("test_pyofast.txt").unlink(True)
    if not cmp and diff:
        d = Differ()
        # keep newlines this time
        orig_strip = re.sub(" +", " ", orig).strip()
        new_strip = re.sub(" +", " ", new).strip()
        res = "".join(
            d.compare(orig_strip.splitlines(keepends=True), new_strip.splitlines(keepends=True))
        )
        res_str = f"""
---- DIFF ----
{res}
--------------
"""
        # Ok, its false...
        assert "" == res_str
    assert orig_strip == new_strip


def check_fragment(rule, fragment: Union[SwanStorage, str], no_markup=False, diff=False):
    """Check a fragment of Swan text using rule
    This check performs a string comparison which may fails due
    to language print. Ex: binary op adds '()', so they should be
    in the original fragment

    Parameters
    ----------
    rule :parser function
        rule to be applied
    fragment : Union[SwanStorage, str]
        Swan code
    no_markup : bool, optional
        suppress markups in pragma, by default False
    diff : bool, optional
        apply diff.Differ() instead of string equality, by default False
    """
    code = SwanString(fragment) if isinstance(fragment, str) else fragment
    obj = rule(code)
    obj_str = str(obj)
    cmp_string(code.content(), obj_str, no_markup, diff)


def check_expr(expr: str, diff=False):
    "Check Swan expression as a string"
    check_fragment(parser.expression, SwanString(expr), diff=diff)


def check_decl(expr: str, diff=False):
    "Check Swan declaration as a string"
    check_fragment(parser.declaration, SwanString(expr), diff=diff)


def check_body(code: str, no_markup=False, diff=False):
    "Check Swan module body"
    swan = SwanString(f"{SwanStorage.gen_version()}\n{code}")
    obj = parser.module_body(swan)
    obj_str = str(obj)
    cmp_string(code, obj_str, no_markup, diff)


def check_section(code: SwanString, no_markup=False, diff=False):
    "Check Swan module body"
    check_fragment(parser.scope_section, code, no_markup, diff)


# Test classes


class TestDecl:
    def test_sensor(self):
        decl = parser.declaration(SwanString("sensor S: int32;"))
        assert isinstance(decl, S.SensorDeclarations)
        sensor = decl.sensors[0]
        assert isinstance(sensor, S.SensorDecl)
        assert sensor.id.value == "S"
        assert isinstance(sensor.type, S.Int32Type)

    def test_constant_no_init(self):
        decl = parser.declaration(SwanString("const C: int32;"))
        assert isinstance(decl, S.ConstDeclarations)
        constant = decl.constants[0]
        assert isinstance(constant, S.ConstDecl)
        assert constant.id.value == "C"
        assert isinstance(constant.type, S.Int32Type)
        assert constant.value is None

    def test_constant_init(self):
        decl = parser.declaration(SwanString("const C: int32 = 41+1;"))
        constant = decl.constants[0]
        assert isinstance(constant, S.ConstDecl)
        assert isinstance(constant, S.ConstDecl)
        value = constant.value
        assert isinstance(value, S.BinaryExpr)
        assert value.operator == S.BinaryOp.Plus
        left = value.left
        assert isinstance(left, S.Literal)
        assert left.is_integer
        assert left.value == "41"

    @pytest.mark.parametrize(
        "decl",
        [
            "const C: int8;",
            "const C: int8 = 42;",
            "const C: int8 = 6 * 7;",
            "const C = 42;",
            "const C1 = 1; C2: int8; C3: int8 = 2;",
        ],
    )
    def test_constants(self, decl):
        check_decl(decl)

    @pytest.mark.parametrize(
        "t",
        [
            "bool",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
            "char",
            "P::Q::T",
            "'T",
        ],
    )
    def test_basic_types(self, t):
        check_decl(f"type T = {t};")

    @pytest.mark.parametrize(
        "decl",
        [
            "type T;",
            "type T = signed <<42>>;",
            "type T = unsigned <<2 * N + 1>>;",
            r" type T = {a: bool};",
            "type T = T1 ^ 666 ^ (42 * N + 1);",
            "type T = enum {A, B, C};",
            r"type T = A {};",
            "type T = A { X };",
            r"""type either3 =
                        Either1 {}
                      | Either2 { int32 }
                      | Either3 {a: bool, b: int32};""",
        ],
    )
    def test_types(self, decl):
        check_decl(decl)

    @pytest.mark.parametrize("use", ["use P::Q;", "use P::Q as X;"])
    def test_use_directive(self, use):
        check_decl(use)

    @pytest.mark.parametrize(
        "grp",
        (
            "int8",
            "(int8, bool)",
            "(a: int8, c: bool)",
            "((bool, a: int8), char, c: (bool, x: bool))",
        ),
    )
    def test_groups(self, grp):
        check_decl(f"group G = {grp};")

    @pytest.mark.parametrize("markup", ["const", "sensor", "group", "type", "use", "syntax_text"])
    def test_protected(self, markup):
        content = "node $$$" if markup == "syntax_text" else f"{markup} $$$"
        code = f"{{{markup}%{content}%{markup}}}"
        check_decl(code)

    @pytest.mark.parametrize("decl", ["const", "sensor", "type", "group"])
    def test_misc(self, decl):
        check_decl(decl)


class TestExpression:
    def gen_expr_test(self, expr: str):
        swan = SwanString(expr)
        py_expr = parser.expression(swan)
        py_expr_str = str(py_expr)
        cmp_string(expr, py_expr_str)

    @pytest.mark.parametrize("expr", ["X", "true", "false", "'!'", r"'\xFF'"])
    def test_atom_expr(self, expr):
        self.gen_expr_test(expr)

    @pytest.mark.parametrize("op ", ["-", "+", "lnot", "not", "pre"])
    def test_unary_expr(self, op):
        self.gen_expr_test(f"{op} X")

    @pytest.mark.parametrize(
        "op",
        [
            "+",
            "-",
            "*",
            "/",
            "mod",
            "land",
            "lor",
            "lxor",
            "lsl",
            "lsr",
            "=",
            "<>",
            "<",
            ">",
            "<=",
            ">=",
            "and",
            "or",
            "xor",
            "->",
            "pre",
            "@",
        ],
    )
    def test_binary_expr(self, op):
        self.gen_expr_test(f"x {op} y")

    @pytest.mark.parametrize(
        "clock_expr",
        [
            "CK",
            "not CK",
            "(CK match A)",
            "(CK match A::B)",
            "(CK match A::B _)",
            "(CK match A::B { })",
            "(CK match 'X')",
            "(CK match 42)",
            "(CK match -42)",
            "(CK match -42_ui32)",
            "(CK match true)",
            "(CK match false)",
            "(CK match _)",
            "(CK match default)",
        ],
    )
    def test_clock_expr(self, clock_expr):
        # clock expr
        self.gen_expr_test(f"X when {clock_expr}")

    @pytest.mark.parametrize(
        "expr",
        [
            "last 'X",
            "X when match A::B",
            "(X :> A::B)",
            "window <<17>> (1, 3) (a, b)",
            "merge (a, b) (c, d) ",
            # port expr
            "#123",
            "$foo",
            "self",
        ],
    )
    def test_misc_expr(self, expr):
        self.gen_expr_test(expr)

    @pytest.mark.parametrize(
        "group_expr",
        [
            "(42, a: 666)",
            "42 .(a)",
            "42 .(a: b)",
            "42 .(3)",
            "42 .(0b1)",
            "42 .(3: b)",
            "42 .(1, 2: a, b: c, d:)",
            r"42 .({syntax%$$$%syntax})",
        ],
    )
    def test_group_expr(self, group_expr):
        self.gen_expr_test(group_expr)

    @pytest.mark.parametrize(
        "oracle",
        [
            "array[42]",
            "s.field",
            "a::b group (42)",
            "a[1 .. 3]",
            "(a + b) * c",
            "(x . [1].f[4][5].g default 0)",
            "(42 + 1)^n",
            "[a, b, c]",
            "{1, 3, 3}",
            "{4, 5, (42 + 1)} : x::y",
            "X {3}",
            "{syntax%foo bar%syntax} {x: 3, y: 4}",
            "(X with .f = 42; [0] = 666)",
            r"""(X with {syntax%foo bar%syntax} = 4;
                            [0] = 666;
                            .f[4].j = {syntax%hello!%syntax})""",
        ],
    )
    def test_composite_expr(self, oracle):
        ## Composite
        self.gen_expr_test(oracle)

    def test_switch_expr(self):
        self.gen_expr_test("if X > Y then X - Y else Y - X")
        switch_expr = """(case X of
                 | A: 1
                 | A _: 2
                 | A { }: 3
                 | 'A': 4
                 | -5: 5
                 | 6_ui8: 6
                 | true: 7
                 | false: 8
                 | _: 9
                 | default: 10
                 | {syntax%$$$%syntax}: 42)"""
        self.gen_expr_test(switch_expr)
        check_fragment(parser.expression, switch_expr)

    @pytest.mark.parametrize(
        "oracle",
        [
            "forward <<42>> returns ()",
            "forward $foo <<42>> returns ()",
            "forward <<42>> <<40 + 2>> returns ()",
            "forward <<42>> with <<X>> returns ()",
            "forward <<42>> with <<X>> u = U; [v] = V; [[y]] = Y; returns ()",
            "forward <<42>> with <<X>> returns (Z)",
            "forward <<42>> with <<X>> returns (Z: last = 42)",
            "forward <<42>> with <<X>> returns (Z: default = 42)",
            "forward <<42>> with <<X>> returns (Z: last = 666 default = 42)",
            "forward <<42>> with <<X>> returns (Z: last = default = 42)",
            "forward <<42>> with <<X>> unless STRONG returns ()",
            "forward <<42>> with <<X>> until WEAK returns ()",
            "forward <<42>> with <<X>> var x: int8; var y; until WEAK returns ()",
            "forward restart <<N>> unless {%$$$%} until {%£££%} returns ()",
            r"forward resume <<N>> unless {stx%$$$%stx} until {%£££%} returns ()",
            "forward <<42>> returns ([ID: last = 42], X = [[Z]])",
        ],
    )
    def test_fwd(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        ["Op ()", "P::Op $luid ()", "Op (x, y)", "Op ((42 + 1), y)", "Op <<41 + 1, 666>> ()"],
    )
    def test_instances(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            "pack <<k, n>> (V)",
            "reverse (V)",
            "flatten (V)",
            "transpose (V)",
            "transpose {4} (V)",
            "transpose {4, 5} (V)",
        ],
    )
    def test_prefix_op(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            "(map Op) ()",
            "(fold Op) ()",
            "(mapfold Op) ()",
            "(mapi Op) ()",
            "(foldi Op) ()",
            "(mapfoldi Op) ()",
            "(map (map Op)) ()",
            "(map (map Op) <<5>>) ()",
            "(map {empty%%empty}) ()",
        ],
    )
    def test_iterators(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            "(activate (map op) every ck) ()",  # clock_expr tested elsewhere
            "(activate operator every cond default value) ()",
            "(activate operator every cond last value) ()",
            "(restart operator every cond) ()",
        ],
    )
    def test_activate(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            "(function x => x + 1) ()",
            "(node x => O -> pre x) ()",
            "(function x, y => x + y) ()",
            """(function x, y
                       var z;
                       let z = x * y;
                       => z) ()""",
            r"""((function (x; y) returns (a; b)
                     { var X;
                       let z = x * y;
                     }) \ x = 2) ()""",
            "42 = (function (x) returns (y) y = 6 * x;) (7)",
        ],
    )
    def test_anonymous(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            "(+) (1, 2, 4, 5)",
            "(*) ()",
            "(@) ()",
            "(and) ()",
            "(or) ()",
            "(xor) ()",
            "(land) ()",
            "(lor) ()",
        ],
    )
    def test_nary(self, oracle):
        self.gen_expr_test(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            r"(G \ _, 42) ()",
            r"(G \ _, 42, i = 40 + 2) ()",
            r"((function x, y => x * y) \ x = 2) ()",
        ],
    )
    def test_partial(self, oracle):
        self.gen_expr_test(oracle)


class TestOperator:
    @pytest.mark.parametrize(
        "decl",
        [
            """
                node FOO () returns ();
                """,
            """
                node FOO () returns ()
                {
                }
                """,
            """
                inline node FOO () returns ()
                {
                }
                """,
        ],
    )
    def test_empty(self, decl):
        check_body(decl)

    def test_var(self):
        oracle = """
node FOO () returns ()
{
    var X: int8;
}
"""
        check_body(oracle)
        oracle = """
node FOO () returns ()
{
    var clock #pragma cg probe #end X1: int8 default = 42 last = 666;
        X2;
    var X3;
}
"""
        check_body(oracle)

    def test_formal_emit(self):
        oracle = """
node FOO () returns ()
{
    assume $H1: (a) and (b);
           $H2: (a) or (b);
    guarantee $G1: a and b;
    emit 'S;
         'S1, 'S2 if true;
}
"""
        check_body(oracle)

    def test_F_G(self):
        oracle = r"""node  F_G ( i: int32 )
                    returns ( o: int32 )
{
                    diagram
                        (#1 block F)
                        (#2 block (G <<{syntax%X1: 1%syntax}>> \ X0: 0))
                        (#3 expr i)
                        (#4 def o)

                        (#5 wire #3 => #1 .(i))
                        (#6 wire #2 .(o) => #4)
                        (#7 wire #1 .(1, 2) => #2)
}"""
        check_body(oracle)

    def test_op_text(self):
        oracle = """{text%node textualOperator ( i0: int32 )
     returns ( o0: int32 )
     {
       let o0 = i0;
     }%text}"""
        check_body(oracle, no_markup=True)


class TestEquation:
    def gen_eq_test(self, eq: str):
        swan = SwanString(eq)
        py_eq = parser.equation(swan)
        py_eq_str = str(py_eq)
        cmp_string(eq, py_eq_str)

    def test_simple_eq(self, make_lhs, make_path_identifier):
        eq = S.ExprEquation(make_lhs(1), S.PathIdExpr(make_path_identifier()))
        oracle = "ID1 = ID2::ID3::ID4;"
        cmp_string(oracle, str(eq))
        # lhs
        for eq in [
            "() = X;",
            "A = X;",
            "A, B = X;",
            "A, _, _, C = X;",
            "A, B, C, .. = X;",
        ]:
            self.gen_eq_test(eq)

    def test_simple_let(self, make_let):
        let = make_let(True)
        oracle = """
let
  ID1 = ID1::ID2::ID3;
  ID2 = ID1::ID2::ID3;
"""
        cmp_string(oracle, str(let))

    @pytest.mark.parametrize(
        "oracle",
        [
            """
() : activate if true then { } else { };
                """,
            """
() : activate
     if true then { }
     elsif false then { }
     elsif true then { }
     else { };
                """,
            """
() : activate
     if i > 42 then
        if i > 50 then x = 50;
        elsif i > 100 then x = 100;
        else x = 42;
     elsif false then {
         var x;
         let x = 50;
     }
     elsif true then { }
     else {
        let x = 666;
     };
                """,
            """
() : activate $activate0
     if i > 42 then { }
     elsif false then
        if i > 50 then x = 50;
        elsif i > 100 then x = 100;
        else x = 42;
     elsif true then { }
     else
        if j > 50 then y = 50;
        elsif j > 100 then y = 100;
        else y = 42;;
                """,
        ],
    )
    def test_activate_if(self, oracle):
        self.gen_eq_test(oracle)

    @pytest.mark.parametrize(
        "pattern",
        [
            "| true : { }",
            "| false : { }",
            "| 'z' : { }",
            "| default : { }",
            "| 42 : { }",
            "| -42 : { }",
            "| 42_ui32 : { }",
            "| -42_ui32 : { }",
            # path_id
            "|  A : { }",
            "| A::B::C : { }",
            # path_id _
            "| A _ : { }",
            "| A::B::C _ : { }",
            # path_id { }
            "| A { } : { }",
            "| A::B::C { } : { }",
            # path_id { id }
            "| A { X } : { }",
            "| A::B::C { X } : { }",
            # more patterns
            "| A : { } | B : { } | C : { }",
            # actions
            "| A : x = 42;",
            """| A : {
                  var X; Y;
                  let
                      X = 42;
                      Y = X * 2;
                  var Z;
                  let Z = 0;
                 }""",
        ],
    )
    def test_activate_when(self, pattern):
        self.gen_eq_test(f"() : activate when x match {pattern};")

    @pytest.mark.parametrize(
        "item",
        [
            "state state1:",
            "state #123:",
            """initial state S1:
                   state S2:""",
            """state S:
                var x;
                let x = 42;""",
            # transition Swan
            ":2: #421 unless if (true) restart S1;",
            ":0x1: #421 unless if (true) resume #666;",
            ":3: #421 unless if (true) { let x = 1; } restart S1;",
            ":4: #421 unless if (true) :1: else restart S1 end;",
            ":5: #421 unless if (true) :1: if (false) restart S1 end;",
            """:6: #1 unless if (true)
                       :1: if (A) restart SA
                       :1: if (B) restart SB
                       :2: else
                           :3: if (C) restart SC
                           :4: else restart SD
                           end
                       end;""",
            """: : #2 unless if (true)
                       : : if (B) restart SB
                       : : else restart SC
                       end;""",
            # transition "Classic"
            """state simple:
                unless if (start) restart s1;
                until if (stop) restart s2;""",
            """state if_tree:
                unless
                if (start)
                  if (c1) restart s1
                  elsif (c2) restart s2
                  elsif (c3) restart s3
                  else resume s4
                  end;""",
            """initial state #3 bug_order:
                        let
                            iO1 = 0_i32 -> pre iO1 + 1_i32;
                        until
                            if (iO1 > 3_i32) {
                            emit
                                'sig1;
                            } restart #1;
                            if (bI1) {
                            emit
                                'sig2;
                            } resume #2;""",
        ],
    )
    def test_state_machine(self, item):
        self.gen_eq_test(f"() : automaton $test {item};")

    @pytest.mark.parametrize(
        "item",
        [
            "automaton;",
            "activate when P match | X : Y = 3;;",
            "activate when P match | X : Y = 3;;",
            "activate if true then X = 1; else X = 2;;",
        ],
    )
    def test_no_lhs(self, item):
        self.gen_eq_test(item)


class TestDiagram:
    def check(self, object, no_markup=False):
        swan = SwanString(f"diagram {object}")
        check_section(swan, no_markup=no_markup)

    @pytest.mark.parametrize(
        "object",
        [
            "(#1 expr 4 + 3)",
            "(#1 expr {syntax%$$$%syntax})",
            "(#1 def X, Y)",
            "(#1 def ())",
            "(def {x%$$$%x})",
            "",
        ],
    )
    def test_def_expr(self, object):
        self.check(object)

    @pytest.mark.parametrize(
        "object",
        [
            "(block {x%$$$%x})",
            "(block P::O)",
            "(#1 $foo block P::O)",
            r"(#1 $foo block (P::O \ x: 42))",
            r"($syntax block (G <<{syntax%X1: 1%syntax}>> \ X0: 0))",
            "($text block {text%(mapfold mapfold2Iterated) <<4>>%text})",
            """($op_exp block ({op_expr%function (a: int32; b: int32)
                                    returns (c: int32) c = a * b;%op_expr}))"""
            "",
        ],
    )
    def test_block(self, object):
        # suppress specific markups while comparing
        no_markup = re.search(r"\{(?:op_expr|text)%", object) is not None
        self.check(object, no_markup=no_markup)

    @pytest.mark.parametrize(
        "source,target",
        [
            ["#123", "#456"],
            ["self", "self"],
            ["()", "()"],
            ["#123", "#456, #789"],
            ["#123 .()", "()"],
            ["#123 .(A1)", "()"],
            ["#123 .(42)", "()"],
            ["#123 .(A1:)", "()"],
            ["#123 .(42:)", "()"],
            ["#123 .(A1: B1)", "()"],
            ["#123 .(42: B1)", "()"],
            ["#123 .(A1, A2, A3)", "()"],
            ["#123 .(42, 421, 4213)", "()"],
            ["#123 .(A1:, A2:, A3)", "()"],
            ["#123 .(42:, 421:, 4213:)", "()"],
            ["#123 .(A1: B1, A2: B2, A3: B4)", "()"],
            ["#123 .(42: B1, 421: B2, 4123: B3)", "()"],
            ["#123", "#456 .(A, 42, A:, 42:, A: B1, 42: B2)"],
        ],
    )
    def test_wire(self, source, target):
        self.check(f"(wire {source} => {target})")

    @pytest.mark.parametrize(
        "group_op",
        [
            "()",
            "byname",
            "bypos",
            "",
            # check local
            "byname where (#123 group )",
        ],
    )
    def test_group(self, group_op):
        self.check(f"(group {group_op})")

    @pytest.mark.parametrize(
        "section",
        [
            "let x = 42;",
            "var x: T1;",
            "automaton initial state S0:",
            r"{text%let automaton initial state S0:;%text}",
        ],
    )
    def test_section(self, section):
        self.check(f"({section})")


class TestModuleAndSignature:
    @pytest.mark.parametrize(
        "code",
        [
            """type T1; T2;""",
            """
use P::Q as Plop;
type T;
     T2 = int8;
const C1: T;
      C2: T;
group G1 = (bool, x: char);
      G2 = float32;
sensor S1: int8; S2: int8;""",
            """function F ( a: int8 ) returns ( b: int8 ) b = a;""",
            """function F ( a: int8 ) returns ( b: int8 )
               {
                  var x;
                  let x = a; b = x;
               }""",
        ],
    )
    def test_module(self, code):
        check_body(code)

    @pytest.mark.parametrize(
        "name,expected",
        [
            (None, "from_string"),
            ("foo", "foo"),
            ("ns1-ns2-foo", "ns1::ns2::foo"),
            ("ns1::ns2::foo", "ns1::ns2::foo"),
        ],
    )
    def test_module_name(self, name, expected):
        code = SwanString(SwanStorage.gen_version(), name)
        obj = parser.module_body(code)
        obj_name = str(obj.name)
        assert obj_name == expected

    def test_signature(self, make_identifier, make_path_identifier, make_var_decl, make_type_var):
        # test 1: inputs/outputs
        sig = S.Signature(
            make_identifier(),
            False,
            True,
            [make_var_decl(), make_var_decl()],
            [make_var_decl(False)],
        )
        sig_str = str(sig)
        oracle = r"""node ID1 (
  ID2: bool; ID3: bool
) returns (
  ID4: {a: int8}
);"""

        assert sig_str == oracle

        # test 2: empty list
        sig = S.Signature(make_identifier(True), False, True, [make_var_decl()], [])
        sig_str = str(sig)
        oracle = r"""node ID1 (
  ID2: bool
) returns ();"""
        assert sig_str == oracle

        # test 3, no signals, sizes + specialization
        sig = S.Signature(
            make_identifier(True),
            False,
            True,
            [],
            [],
            sizes=[make_identifier(), make_identifier()],
            specialization=make_path_identifier(),
        )
        sig_str = str(sig)
        oracle = r"""node ID1 <<ID2, ID3>> () returns () specialize ID4::ID5::ID6;"""
        assert sig_str == oracle

        # test 4 : constraints
        sig = S.Signature(
            make_identifier(True),
            False,
            False,
            [],
            [],
            constraints=[
                S.TypeConstraint([make_type_var(), make_type_var()], S.NumericKind.Signed),
                S.TypeConstraint([make_type_var()], S.NumericKind.Integer),
            ],
        )
        sig_str = str(sig)
        oracle = r"""function ID1 () returns () where 'T1, 'T2 signed where 'T3 integer;"""
        assert sig_str == oracle

        # test 5: pragmas
        sig = S.Signature(
            make_identifier(True),
            False,
            False,
            [],
            [],
            pragmas=[S.Pragma("#pragma x #end"), S.Pragma("#pragma y #end")],
        )
        sig_str = str(sig)
        oracle = """function #pragma x #end #pragma y #end ID1 () returns ();"""
        assert str(sig) == oracle

        # test 6 - parsing with care (error see next test_signature_parsing)
        oracle = """
function
    #pragma x #end
FOO <<S, {syntax%$Size%syntax}>> (
    a: int8;
    {var%$V := ?%var}
) returns ()
    where 'T1 integer
    where {syntax%$T%syntax} signed
    specialize A::B;
"""
        check_decl(oracle)

    @pytest.mark.parametrize(
        "oracle",
        [
            """
function
    #pragma x #end #pragma y #end
FOO <<S, {syntax%$Size%syntax}>> (
    a: int8;
    {var%$V := ?%var}
) returns ()
    where 'T1, 'T2 integer
    where {syntax%$T%syntax} signed
    specialize A::B;
""",
            """node CruiseControl (
                    On: bool;
                    Off: bool;
                    Set: bool;
                    Resume: bool;
                    QuickAccel: bool;
                    QuickDecel: bool;
                    Accel: CarTypes::tPercent;
                    Brake: CarTypes::tPercent;
                    CarSpeed: CarTypes::tSpeed
                )
  returns (
    CruiseSpeed: CarTypes::tSpeed default = 0.0;
    ThrottleCmd: CarTypes::tPercent default = 0.0;
    CruiseState: tCruiseState default = OFF
  );
        """,
        ],
    )
    def test_signature_parsing(self, oracle):
        check_decl(oracle)
