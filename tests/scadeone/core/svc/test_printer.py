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

# Flake8: noqa
import logging

import pytest

from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser
from ansys.scadeone.core.svc.swan_printer import swan_to_str

logging.basicConfig(level=logging.DEBUG)

parser = SwanParser(logging.getLogger("pprinter"))


class TestPrinterGlobals:
    """
    Test Swan global declarations
    """

    @pytest.mark.parametrize(
        "constant, expected",
        [
            ("const C1: int32;", True),
            ("const C7 = 5;", True),
            (
                "const C8: bool = false; C9 = 1;",
                """\
const C8: bool = false;
      C9 = 1;
""",
            ),
            ("const SpeedInc: CarTypes::tSpeed = 2.5;", True),
            (
                "const THRESHOLD: float32 = 5.0; N: int16 = 8;",
                """\
const THRESHOLD: float32 = 5.0;
      N: int16 = 8;
""",
            ),
        ],
    )
    def test_constants(self, constant, expected):
        swan_obj = parser.declaration(SwanString(constant))
        res = swan_to_str(swan_obj)
        if expected is True:
            expected = constant + "\n"
        assert res == expected

    @pytest.mark.parametrize(
        "constant, expected",
        [
            ("const C1: int32;", "const C1: int32;\n"),
            ("const C7 = 5;", "const C7 = 5;\n"),
            (
                "const C8: bool = false; C9 = 1;",
                """\
const C8: bool = false;

const C9 = 1;
""",
            ),
            (
                "const SpeedInc: CarTypes::tSpeed = 2.5;",
                "const SpeedInc: CarTypes::tSpeed = 2.5;\n",
            ),
            (
                "const THRESHOLD: float32 = 5.0; N: int16 = 8;",
                """\
const THRESHOLD: float32 = 5.0;

const N: int16 = 8;
""",
            ),
        ],
    )
    def test_constants_normalize(self, constant, expected):
        swan_obj = parser.declaration(SwanString(constant))
        res = swan_to_str(swan_obj, normalize=True)
        assert res == expected

    @pytest.mark.parametrize(
        "sensor, expected",
        [
            ("sensor K1: float32;", "sensor K1: float32;\n"),
            ("sensor K2: int8;", "sensor K2: int8;\n"),
            (
                "sensor K3: bool; K4: int16;",
                """\
sensor K3: bool;
       K4: int16;
""",
            ),
        ],
    )
    def test_sensors(self, sensor, expected):
        swan_obj = parser.declaration(SwanString(sensor))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "sensor, expected",
        [
            (
                "sensor K1: float32; K2: int8;",
                """\
sensor K1: float32;

sensor K2: int8;
""",
            ),
            (
                "sensor K3: bool; K4: int16;",
                """\
sensor K3: bool;

sensor K4: int16;
""",
            ),
        ],
    )
    def test_sensors_normalize(self, sensor, expected):
        swan_obj = parser.declaration(SwanString(sensor))
        res = swan_to_str(swan_obj, normalize=True)
        assert res == expected

    @pytest.mark.parametrize(
        "group, expected",
        [
            ("group G0 = float32;", True),
            ("group G5 = (G4: bool);", True),
            ("group G2 = (G3: bool, G4: int8, G5: char, G6: uint64);", True),
            ("group G3 = (int8, bool);", True),
            ("group G4 = ((bool, a: int8), char, c: (bool, x: bool));", True),
            (
                "group G1 = (bool, x: char); G2 = float32;",
                """\
group G1 = (bool, x: char);
      G2 = float32;
""",
            ),
            (
                "group G6 = ((uint8, G1: int32), char, G2: (uint32, G3: (bool, G4: (int16, G5: (uint16, float64)))));",
                True,
            ),
            (
                "group G7 = (int8, bool, float32, (float64, G0: (uint8, uint16, G1: (int32, uint32, int64, uint64))));",
                True,
            ),
            (
                "group G8 = ((uint8, G1: int32), char, G2: (uint32, G3: (bool, G4: (int16, G5 : (uint16, float64))))); G9 = (bool, char); G10 = float32;",
                """\
group G8 = ((uint8, G1: int32), char, G2: (uint32, G3: (bool, G4: (int16, G5: (uint16, float64)))));
      G9 = (bool, char);
      G10 = float32;
""",
            ),
        ],
    )
    def test_groups(self, group, expected):
        swan_obj = parser.declaration(SwanString(group))
        res = swan_to_str(swan_obj)
        if expected is True:
            expected = group + "\n"
        assert res == expected

    @pytest.mark.parametrize(
        "group,expected",
        [
            (
                "group G1 = (bool, x: char); G2 = float32;",
                "group G1 = (bool, x: char);\n\ngroup G2 = float32;\n",
            ),
            (
                "group G8 = ((uint8, G1: int32), char, G2: (uint32, G3: (bool, G4: (int16, G5: (uint16, float64))))); G9 = (bool, char); G10 = float32;",
                "group G8 = ((uint8, G1: int32), char, G2: (uint32, G3: (bool, G4: (int16, G5: (uint16, float64)))));\n\ngroup G9 = (bool, char);\n\ngroup G10 = float32;\n",
            ),
        ],
    )
    def test_groups_normalize(self, group, expected):
        swan_obj = parser.declaration(SwanString(group))
        res = swan_to_str(swan_obj, normalize=True)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type A = signed << 1.40_f32 * N >>;",
                "type A = signed << 1.40_f32 * N >>;\n",
            ),  # signed (with expression type)
            (
                "type A1 = unsigned << not A >>;",
                "type A1 = unsigned << not A >>;\n",
            ),  # unsigned (with unary operator)
            (
                "type A3 = signed << - A + 1 >>;",
                "type A3 = signed << - A + 1 >>;\n",
            ),  # signed (with binary operator)
            (
                "type SIG = unsigned << PD::ID >>;",
                "type SIG = unsigned << PD::ID >>;\n",
            ),  # signed (with expression type is id_expr ::= ID)
        ],
    )
    def test_unsigned_signed(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            ("type T;", "type T;\n"),  # only with ID
            ("type tBool; tInt;", ("type tBool;\n     tInt;\n")),
            (
                "type P = ID2::ID3::ID4;",
                "type P = ID2::ID3::ID4;\n",
            ),  # expression type is path_id ::= ID
        ],
    )
    def test_id_expr_type(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            ("type type1 = uint32;", "type type1 = uint32;\n"),
            (
                "type tU = uint32; tI = int64; t8 = int8; tC = char;",
                ("type tU = uint32;\n     tI = int64;\n     t8 = int8;\n     tC = char;\n"),
            ),  # predef type
            (
                "type tCruiseState = enum {OFF, INT, STDBY, ON};",
                "type tCruiseState = enum {OFF, INT, STDBY, ON};\n",
            ),  # enum type
            (
                "type E1 = enum {OFF, INT, STDBY, ON}; E2 = E1;",
                "type E1 = enum {OFF, INT, STDBY, ON};\n     E2 = E1;\n",
            ),  # enum and typevar
        ],
    )
    def test_predef_enum_type(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type V = B { bool } | C { char } | I { int8 } | U { uint8 };",
                "type V = B { bool } | C { char } | I { int8 } | U { uint8 };\n",
            ),  # variant predef type
            ("type T = A { N ^ 5 };", "type T = A { N ^ 5 };\n"),  # variant with array type
            (
                "type VS = B {T1: int16, T2: int64, T3: uint32, T4: char} | C {T1: PID::VID, T2: PID2, T3: int32, T4: uint64};",
                "type VS = B {T1: int16, T2: int64, T3: uint32, T4: char} | C {T1: PID::VID, T2: PID2, T3: int32, T4: uint64};\n",
            ),  # variant type with struct type
            (
                "type coord2D = Polar {r: float32, t: float32} | Cartesian {x: float32, y: float32};",
                "type coord2D = Polar {r: float32, t: float32} | Cartesian {x: float32, y: float32};\n",
            ),
            (
                "type int_opt = Some { int32 } | None {};",
                "type int_opt = Some { int32 } | None {};\n",
            ),  # variant with None
        ],
    )
    def test_variant_type(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type FT; FB; SV = {T1: FT, T2: FB, T3: uint8, T4: uint16};",
                "type FT;\n     FB;\n     SV = {T1: FT, T2: FB, T3: uint8, T4: uint16};\n",
            ),  # struct type with typevar
            (
                "type VS = {T1: int16 ^ last 'Speed, T2: A, T3: unsigned << pre B >>, T4: signed << A + B >>};",
                "type VS = {T1: int16 ^ last 'Speed, T2: A, T3: unsigned << pre B >>, T4: signed << A + B >>};\n",
            ),  # struct type with expr
            (
                "type Either = Either1 {} | Either2 { int32 } | Either3 {a: bool, b: int32};",
                "type Either = Either1 {} | Either2 { int32 } | Either3 {a: bool, b: int32};\n",
            ),  # structure type with variant
        ],
    )
    def test_structure_type(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            ("type matrix = float32 ^ 5;", "type matrix = float32 ^ 5;\n"),
        ],
    )
    def test_expr_type(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [("type tBool; tInt;", "type tBool;\n\ntype tInt;\n")],
    )
    def test_types_normalize(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj, normalize=True)
        assert res == expected


class TestPrinterExpr:
    """
    Test Swan expressions
    """

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type C = signed << - A + B when B >>;",
                "type C = signed << - A + B when B >>;\n",
            ),  # with ID
            (
                "type C = unsigned << A when not B >>;",
                "type C = unsigned << A when not B >>;\n",
            ),  # not ID
            (
                "type C = signed << T1 ^ T2 when (B match true) >>;",
                "type C = signed << T1 ^ T2 when (B match true) >>;\n",
            ),  # bool pattern
            (
                "type C = unsigned << T1 when (C match A::B) >>;",
                "type C = unsigned << T1 when (C match A::B) >>;\n",
            ),  # path_id pattern
            (
                "type C = signed << T2 mod T1 when (A match 42_i8) >>;",
                "type C = signed << T2 mod T1 when (A match 42_i8) >>;\n",
            ),  # int pattern
            (
                "type C = signed << 0.8_f64 * T when (C match -1) >>;",
                "type C = signed << 0.8_f64 * T when (C match -1) >>;\n",
            ),  # int pattern
            (
                "type C = signed << T2 * T1 when (C match A::B {}) >>;",
                "type C = signed << T2 * T1 when (C match A::B {}) >>;\n",
            ),  # variant pattern
            (
                "type C = unsigned << T / 3 when (C match A::B _) >>;",
                "type C = unsigned << T / 3 when (C match A::B _) >>;\n",
            ),  # variant pattern
            (
                "type C = signed << PID::ID when (C match default) >>;",
                "type C = signed << PID::ID when (C match default) >>;\n",
            ),  # default pattern
            (
                "type C = unsigned << last 'T when (C match _) >>;",
                "type C = unsigned << last 'T when (C match _) >>;\n",
            ),  # underscore pattern
            (
                "type C = signed << A when not B when (C match _) >>;",
                "type C = signed << A when not B when (C match _) >>;\n",
            ),  # underscore pattern
            (
                "type C = signed << pre T when (C match 'C') >>;",
                "type C = signed << pre T when (C match 'C') >>;\n",
            ),  # char pattern
            (
                "type C = unsigned << 'A' ^ 5 when B when (C match false) >>;",
                "type C = unsigned << 'A' ^ 5 when B when (C match false) >>;\n",
            ),  # bool pattern
            (
                "type tU = float32 ^ 3; tC = tU ^ 2; tA = signed << 0.4_f32 * T when not A >>;",
                "type tU = float32 ^ 3;\n     tC = tU ^ 2;\n     tA = signed << 0.4_f32 * T when not A >>;\n",
            ),
        ],
    )
    def test_clock_expr_type(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type C = signed << A when match B >>;",
                "type C = signed << A when match B >>;\n",
            ),
            (
                "type C = unsigned << P::Q::R when match T::U >>;",
                "type C = unsigned << P::Q::R when match T::U >>;\n",
            ),
            (
                "type C = unsigned << T::U::V::Y::X::Q::R::S::P::Z when match B >>;",
                "type C = unsigned << T::U::V::Y::X::Q::R::S::P::Z when match B >>;\n",
            ),
            (
                "type C = signed << T1 ^ T2 when match T::U::V::Y::X::Q::R::S::P::Z >>;",
                "type C = signed << T1 ^ T2 when match T::U::V::Y::X::Q::R::S::P::Z >>;\n",
            ),
            (
                "type C = unsigned << 4_i8 + 84_ui8 when match C >>;",
                "type C = unsigned << 4_i8 + 84_ui8 when match C >>;\n",
            ),
            (
                "type C = signed << - A when match C::B::D >>;",
                "type C = signed << - A when match C::B::D >>;\n",
            ),
            (
                "type C = signed << 0.8_f64 * T when A when match B >>;",
                "type C = signed << 0.8_f64 * T when A when match B >>;\n",
            ),
            (
                "type C = signed << T2 mod T1 when (C match A::B {}) when match T>>;",
                "type C = signed << T2 mod T1 when (C match A::B {}) when match T >>;\n",
            ),
            (
                "type C = unsigned << T / 3 when (C match A::B _) when match T::U::V >>;",
                "type C = unsigned << T / 3 when (C match A::B _) when match T::U::V >>;\n",
            ),
            (
                "type C = unsigned << 'A' ^ 5 when match T >>;",
                "type C = unsigned << 'A' ^ 5 when match T >>;\n",
            ),
        ],
    )
    def test_when_match(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type C = signed << (A :> T1) >>;",
                "type C = signed << (A :> T1) >>;\n",
            ),
            (
                "type C = unsigned << (A :> T::U) >>;",
                "type C = unsigned << (A :> T::U) >>;\n",
            ),
            (
                "type C = signed << (4_i8 + 84_ui8 :> float32) >>;",
                "type C = signed << (4_i8 + 84_ui8 :> float32) >>;\n",
            ),
            (
                "type C = unsigned << (true :> char) >>;",
                "type C = unsigned << (true :> char) >>;\n",
            ),
            (
                "type C = unsigned << ('A' :> unsigned << A + B when match B >>) >>;",
                "type C = unsigned << ('A' :> unsigned << A + B when match B >>) >>;\n",
            ),
            (
                "type C = unsigned << (A when not B :> unsigned << A * 1.0_f64 >>) >>;",
                "type C = unsigned << (A when not B :> unsigned << A * 1.0_f64 >>) >>;\n",
            ),
            (
                "type C = unsigned << (A :> bool) >>;",
                "type C = unsigned << (A :> bool) >>;\n",
            ),
            (
                "type C = unsigned << (3.145789456201_f64 :> int64) >>;",
                "type C = unsigned << (3.145789456201_f64 :> int64) >>;\n",
            ),
        ],
    )
    def test_numeric_cast(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            ("type T = signed << (A + B) >>;", "type T = signed << (A + B) >>;\n"),
            ("type T = unsigned << (A when B) >>;", "type T = unsigned << (A when B) >>;\n"),
            ("type T = unsigned << (true) >>;", "type T = unsigned << (true) >>;\n"),
            ("type T = signed << (- B) >>;", "type T = signed << (- B) >>;\n"),
            ("type T = unsigned << (4_i16) >>;", "type T = unsigned << (4_i16) >>;\n"),
            ("type T = unsigned << (A::B) >>;", "type T = unsigned << (A::B) >>;\n"),
            ("type T = signed << (a: B::C) >>;", "type T = signed << (a: B::C) >>;\n"),
            (
                "type T = unsigned << (a: A -> B when (C match 5)) >>;",
                "type T = unsigned << (a: A -> B when (C match 5)) >>;\n",
            ),
            (
                "type T = unsigned << (a: A mod B when (C match D::E _)) >>;",
                "type T = unsigned << (a: A mod B when (C match D::E _)) >>;\n",
            ),
            (
                "type T = signed << (A * B, a: (A :> T1)) >>;",
                "type T = signed << (A * B, a: (A :> T1)) >>;\n",
            ),
            (
                "type T = unsigned << (a: 42_i8, b: P::Q::R when match T::U, c: true) >>;",
                "type T = unsigned << (a: 42_i8, b: P::Q::R when match T::U, c: true) >>;\n",
            ),
            ("type T = signed << (42, a: 666) >>;", "type T = signed << (42, a: 666) >>;\n"),
        ],
    )
    def test_group_expr(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "type, expected",
        [
            (
                "type A = signed << - A + B .(C) >>;",
                "type A = signed << - A + B .(C) >>;\n",
            ),
            (
                "type A = signed << true .(C, D, E, F) >>;",
                "type A = signed << true .(C, D, E, F) >>;\n",
            ),
            (
                "type A = signed << (4_i8 + 84_ui8 :> float32) .(1, 2, 3, 4) >>;",
                "type A = signed << (4_i8 + 84_ui8 :> float32) .(1, 2, 3, 4) >>;\n",
            ),
            (
                "type T = unsigned << A ^ 5_ui8 .(a: B1, b: B2, c: B4) >>;",
                "type T = unsigned << A ^ 5_ui8 .(a: B1, b: B2, c: B4) >>;\n",
            ),
            (
                "type T = signed << 42_i16 .(1, 2: a, b: c, d) >>;",
                "type T = signed << 42_i16 .(1, 2: a, b: c, d) >>;\n",
            ),
            (
                "type T = unsigned << A * 3.2_f64 when B .(a: B, 1: C) >>;",
                "type T = unsigned << A * 3.2_f64 when B .(a: B, 1: C) >>;\n",
            ),
            (
                "type A = signed << P::Q::R when match T::U .(0b1) >>;",
                "type A = signed << P::Q::R when match T::U .(0b1) >>;\n",
            ),
            (
                "type C = signed << T2 * T1 when (C match A::B {}) .(1) >>;",
                "type C = signed << T2 * T1 when (C match A::B {}) .(1) >>;\n",
            ),
        ],
    )
    def test_group_adaption(self, type, expected):
        swan_obj = parser.declaration(SwanString(type))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "const, expected",
        [
            (
                "const C = - A + B.C;",
                "const C = - A + B.C;\n",
            ),
            (
                "const C = A when B[A mod B when (C match D::E _)];",
                "const C = A when B[A mod B when (C match D::E _)];\n",
            ),
            (
                "const C = A[(a: 42_i8, b: P::Q::R when match T::U, c: true)];",
                "const C = A[(a: 42_i8, b: P::Q::R when match T::U, c: true)];\n",
            ),
            (
                "const C = A[B];",
                "const C = A[B];\n",
            ),
            (
                "const C = A[B::C::D::E];",
                "const C = A[B::C::D::E];\n",
            ),
            (
                "const C = T group (- A + B);",
                "const C = T group (- A + B);\n",
            ),
            (
                "const C = T group (true);",
                "const C = T group (true);\n",
            ),
            (
                "const C = U::V::Z group ((A * B, a: (A :> T1)));",
                "const C = U::V::Z group ((A * B, a: (A :> T1)));\n",
            ),
            (
                "const C = T group (42_i8);",
                "const C = T group (42_i8);\n",
            ),
            (
                "const C = a[1 .. 3];",
                "const C = a[1 .. 3];\n",
            ),
            (
                "const C = 25_i16[A .. B];",
                "const C = 25_i16[A .. B];\n",
            ),
            (
                "const C = A::B[A .. C::D];",
                "const C = A::B[A .. C::D];\n",
            ),
            (
                "const C = 'A'[A mod B when (C match D::E _) .. (A :> T1)];",
                "const C = 'A'[A mod B when (C match D::E _) .. (A :> T1)];\n",
            ),
            (
                "const C = (x . [1].f[4][5].g default 0);",
                "const C = (x . [1].f[4][5].g default 0);\n",
            ),
            (
                "const C = (A . [C + D] default - B);",
                "const C = (A . [C + D] default - B);\n",
            ),
            (
                "const C = (42 . .A.B.C default D::E::T);",
                "const C = (42 . .A.B.C default D::E::T);\n",
            ),
            (
                "const C = (0.75_f32 . [A mod B when (C match D::E _)] default true);",
                "const C = (0.75_f32 . [A mod B when (C match D::E _)] default true);\n",
            ),
            (
                "const C = {A, B, C} : D;",
                "const C = {A, B, C} : D;\n",
            ),
            (
                "const C = {a: - A + B, c: A when B} : D::E;",
                "const C = {a: - A + B, c: A when B} : D::E;\n",
            ),
            (
                "const C = {42} : T;",
                "const C = {42} : T;\n",
            ),
            (
                "const C = {4, 5, (42 + 1)} : x::y;",
                "const C = {4, 5, (42 + 1)} : x::y;\n",
            ),
            (
                "const C = T {A, B, C};",
                "const C = T {A, B, C};\n",
            ),
            (
                "const C = T {A: D * E, B: - 42, C};",
                "const C = T {A: D * E, B: - 42, C};\n",
            ),
            (
                "const C = D::E {1, 2, 3_i8};",
                "const C = D::E {1, 2, 3_i8};\n",
            ),
            (
                "const C = T {- A + B};",
                "const C = T {- A + B};\n",
            ),
            (
                "const C = (X with .f = 42; [0] = 666);",
                "const C = (X with .f = 42; [0] = 666);\n",
            ),
            (
                "const C = (X with .f = 42.0_f64);",
                "const C = (X with .f = 42.0_f64);\n",
            ),
            (
                "const C = (A when B with .field = C when (D match E::F _); [true] = true);",
                "const C = (A when B with .field = C when (D match E::F _); [true] = true);\n",
            ),
        ],
    )
    def test_composite(self, const, expected):
        swan_obj = parser.declaration(SwanString(const))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "const, expected",
        [
            (
                "const C = if true then B else C;",
                "const C = if true then B else C;\n",
            ),
            (
                "const C = if D::E then - A + B else C ^ N ^ M;",
                "const C = if D::E then - A + B else C ^ N ^ M;\n",
            ),
            (
                "const C = (case A of | P: B + C| T0: true| T1: 1_i8| T2::U::V: D when E| T3: D {A, B, C}| T4: (X with .f = 42; [0] = 666)| T5: U.V| T6: M[N::O::P::Q]| T7: a[0 .. N - 1]);",
                "const C = (case A of | P: B + C| T0: true| T1: 1_i8| T2::U::V: D when E| T3: D {A, B, C}| T4: (X with .f = 42; [0] = 666)| T5: U.V| T6: M[N::O::P::Q]| T7: a[0 .. N - 1]);\n",
            ),
            (
                "const C = if X > Y then X - Y else Y - X;",
                "const C = if X > Y then X - Y else Y - X;\n",
            ),
            (
                "const C = (case X of | A: 1| A _: 2| A {}: 3| 'A': 4| -5: 5| 6_ui8: 6| true: 7| false: 8| _: 9| default: 10);",
                "const C = (case X of | A: 1| A _: 2| A {}: 3| 'A': 4| -5: 5| 6_ui8: 6| true: 7| false: 8| _: 9| default: 10);\n",
            ),
            (
                "const C = (case X of | _: e);",
                "const C = (case X of | _: e);\n",
            ),
            (
                "const C = if c .(u) mod 2 = 1 then n = last 'n * a .(m) else a .(m);",
                "const C = if c .(u) mod 2 = 1 then n = last 'n * a .(m) else a .(m);\n",
            ),
            (
                "const C = if c and last 'n >= 0 then n = last 'n - 1 else c;",
                "const C = if c and last 'n >= 0 then n = last 'n - 1 else c;\n",
            ),
            (
                "const C = (case X of | Polar: true| _: false);",
                "const C = (case X of | Polar: true| _: false);\n",
            ),
        ],
    )
    def test_switch_expr(self, const, expected):
        swan_obj = parser.declaration(SwanString(const))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "const, expected",
        [
            (
                "const C = forward <<42>> returns ();",
                "const C = forward\n<<42>>\n\nreturns ();\n",
            ),
            (
                "const C = forward <<42>> returns ();",
                "const C = forward\n<<42>>\n\nreturns ();\n",
            ),
            (
                "const C = forward <<42>> assume $D: A mod 3; assume $B: A / 3; returns ();",
                "const C = forward\n<<42>>\nassume\n      $D: A mod 3;\nassume\n      $B: A / 3;\nreturns ();\n",
            ),
            (
                "const C = forward <<42>> guarantee $D: A mod 3; $B: A / 3; returns ();",
                "const C = forward\n<<42>>\nguarantee\n      $D: A mod 3;\n      $B: A / 3;\nreturns ();\n",
            ),
            (
                "const C = forward <<42>> emit 'D, 'C if true; 'L; returns ();",
                "const C = forward\n<<42>>\nemit\n      'D, 'C if true;\n      'L;\nreturns ();\n",
            ),
            (
                "const C = forward <<42>> with <<X>> u = U; [v] = V; [[y]] = Y; returns ();",
                "const C = forward\n<<42>> with <<X>> u = U; [v] = V; [[y]] = Y;\n\nreturns ();\n",
            ),
            (
                "const C = forward $xy resume <<2>> var x: int8; var y; until WEAK returns (I);",
                "const C = forward $xy resume\n<<2>>\nvar\n      x: int8;\nvar\n      y;\nuntil WEAK\nreturns (I);\n",
            ),
            (
                "const C = forward $foo resume <<2>> var clock I1; var #pragma x probe #end #pragma y probe #end I2; returns (I);",
                "const C = forward $foo resume\n<<2>>\nvar\n      clock I1;\nvar\n      #pragma x probe #end #pragma y probe #end I2;\nreturns (I);\n",
            ),
            (
                "const C = forward restart <<A>> var I1 default = B / 4; I2 last = C * 4; returns (B: last = D + C);",
                "const C = forward restart\n<<A>>\nvar\n      I1 default = B / 4;\n      I2 last = C * 4;\nreturns (B: last = D + C);\n",
            ),
            (
                "const C = forward $x resume <<A + B>> var clock I1; var #pragma cg probe #end I2; returns (I = [I5: default = 3 * A]);",
                "const C = forward $x resume\n<<A + B>>\nvar\n      clock I1;\nvar\n      #pragma cg probe #end I2;\nreturns (I = [I5: default = 3 * A]);\n",
            ),
            (
                "const C = forward $x <<A>> var I1; returns (B: last = D + C);",
                "const C = forward $x\n<<A>>\nvar\n      I1;\nreturns (B: last = D + C);\n",
            ),
            (
                "const C = forward $x <<A>> var I1; returns ([ID: last = 42], X = [[Z]]);",
                "const C = forward $x\n<<A>>\nvar\n      I1;\nreturns ([ID: last = 42], X = [[Z]]);\n",
            ),
            (
                "const C = forward $x <<I = - A + B>> with I2 = I3 mod 2; var clock I1; returns (I6, I4 = [I5: default = 3 * A]);",
                "const C = forward $x\n<<I = - A + B>> with I2 = I3 mod 2;\nvar\n      clock I1;\nreturns (I6, I4 = [I5: default = 3 * A]);\n",
            ),
            (
                "const C = forward <<2>> unless A - C var V1 when A; until B + 4 returns (I: last = default = A * B);",
                "const C = forward\n<<2>>\nunless A - C\nvar\n      V1 when A;\nuntil B + 4\nreturns (I: last = default = A * B);\n",
            ),
        ],
    )
    def test_fwd_expr(self, const, expected):
        swan_obj = parser.declaration(SwanString(const))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "const, expected",
        [
            (
                "const C = window <<42 ^ N>> (G: A + B) (D * C);",
                "const C = window <<42 ^ N>> (G: A + B) (D * C);\n",
            ),
            (
                "const C = merge (A) (true);",
                "const C = merge (A) (true);\n",
            ),
        ],
    )
    def test_multigroup_prefix(self, const, expected):
        swan_obj = parser.declaration(SwanString(const))
        res = swan_to_str(swan_obj, normalize=True)
        assert res == expected

    @pytest.mark.parametrize(
        "const, expected",
        [
            (
                "const C = $luid1;",
                "const C = $luid1;\n",
            ),
            (
                "const C = self;",
                "const C = self;\n",
            ),
        ],
    )
    def test_port(self, const, expected):
        swan_obj = parser.declaration(SwanString(const))
        res = swan_to_str(swan_obj, normalize=True)
        assert res == expected


class TestPrinterDiagram:
    """
    Test Swan expressions
    """

    @pytest.mark.parametrize(
        "object, expected",
        [
            ("diagram (#1 expr A + B)", "diagram\n(#1 expr A + B)"),
            ("diagram (expr last 'A)", "diagram\n(expr last 'A)"),
            (
                "diagram (#1 expr A where (expr last 'B))",
                "diagram\n(#1 expr A where (expr last 'B))",
            ),
            (
                "diagram (#0 expr (e1: T::P, e2: T::Q, e3: T::V, e4: T::U))",
                "diagram\n(#0 expr (e1: T::P, e2: T::Q, e3: T::V, e4: T::U))",
            ),
            (
                "diagram (expr (G: not #3 when match A::B) where (expr A ^ 3_ui8 * last 'T))",
                "diagram\n(expr (G: not #3 when match A::B) where (expr A ^ 3_ui8 * last 'T))",
            ),
            (
                "diagram (diagram (diagram (expr true)))",
                "diagram\n(diagram\n(diagram\n(expr true)))",
            ),
            ("diagram ($exp1 expr A + B)", "diagram\n($exp1 expr A + B)"),
            ("diagram (#1 $exp_1 expr last 'A)", "diagram\n(#1 $exp_1 expr last 'A)"),
        ],
    )
    def test_expr_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            ("diagram (#1 def ())", "diagram\n(#1 def ())"),
            ("diagram (#1 def d, a, _, ..)", "diagram\n(#1 def d, a, _, ..)"),
            ("diagram (#1 group ())", "diagram\n(#1 group ())"),
            ("diagram (#1 group byname)", "diagram\n(#1 group byname)"),
            ("diagram (#1 group bypos)", "diagram\n(#1 group bypos)"),
            (
                "diagram (#1 expr #2 pre #3 where (#2 group) (#3 group))",
                "diagram\n(#1 expr #2 pre #3 where (#2 group)\n(#3 group))",
            ),
            (
                "diagram (#1 expr if #2 then #3 else #4 where (#2 group) (#3 group) (#4 group))",
                "diagram\n(#1 expr if #2 then #3 else #4 where (#2 group)\n(#3 group)\n(#4 group))",
            ),
            (
                "diagram (#1 expr #2 * #3 where (#2 group) (#3 group))",
                "diagram\n(#1 expr #2 * #3 where (#2 group)\n(#3 group))",
            ),
            (
                "diagram (#1 expr B) (#3 def C) (#0 expr (A: T::B)) (#1 expr true where (#3 group byname))",
                "diagram\n(#1 expr B)\n(#3 def C)\n(#0 expr (A: T::B))\n(#1 expr true where (#3 group byname))",
            ),
            (
                "diagram (#1 expr pre #3 where (#3 group where (#2 group) (#1 group where (#4 group))) (#0 group ()))",
                "diagram\n(#1 expr pre #3 where (#3 group where (#2 group)\n(#1 group where (#4 group)))\n(#0 group ()))",
            ),
        ],
    )
    def test_def_group_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            (
                "diagram (var clock V when (A match B::C {}) last = last 'T;)",
                "diagram\n(var\nclock V when (A match B::C {}) last = last 'T;)",
            ),
        ],
    )
    def test_scope_section_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            ("diagram (#1 wire #2 => self)", "diagram\n(#1 wire #2 => self)"),
            (
                "diagram (#1 wire self => #2, #3, self, #4 .(A))",
                "diagram\n(#1 wire self => #2, #3, self, #4 .(A))",
            ),
            ("diagram (#1 wire () => self)", "diagram\n(#1 wire () => self)"),
            ("diagram (#1 wire self => self)", "diagram\n(#1 wire self => self)"),
            ("diagram (#1 wire () => ())", "diagram\n(#1 wire () => ())"),
            ("diagram (#1 wire self => ())", "diagram\n(#1 wire self => ())"),
            ("diagram (wire #6 => #3)", "diagram\n(wire #6 => #3)"),
            (
                "diagram (wire #2 .(cmd) => #3 .(dvt, 1, 2))",
                "diagram\n(wire #2 .(cmd) => #3 .(dvt, 1, 2))",
            ),
            ("diagram (#1 wire #2 => self .(0b1: A))", "diagram\n(#1 wire #2 => self .(0b1: A))"),
            (
                "diagram (#1 wire #2 => #3 .(0o5: A, B: C, A:, 42:), #4 .(0xF: F), #5 .(1))",
                "diagram\n(#1 wire #2 => #3 .(0o5: A, B: C, A:, 42:), #4 .(0xF: F), #5 .(1))",
            ),
            ("diagram (wire #2 => self)", "diagram\n(wire #2 => self)"),
            ("diagram (#1 wire $expr_2 => self)", "diagram\n(#1 wire $expr_2 => self)"),
            ("diagram (#1 wire $expr_1 => $expr_2)", "diagram\n(#1 wire $expr_1 => $expr_2)"),
        ],
    )
    def test_wire_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            ("diagram (#1 block ABC)", "diagram\n(#1 block ABC)"),
            ("diagram (#1 block A::B)", "diagram\n(#1 block A::B)"),
            ("diagram (#1 block reserve)", "diagram\n(#1 block reserve)"),
            (
                "diagram (#1 block transpose) (#1 block transpose {42})",
                "diagram\n(#1 block transpose)\n(#1 block transpose {42})",
            ),
            (
                "diagram (#1 block transpose {42, 10, 3})",
                "diagram\n(#1 block transpose {42, 10, 3})",
            ),
            ("diagram (#1 block pack <<k, n>>)", "diagram\n(#1 block pack <<k, n>>)"),
            (
                "diagram (#1 block flatten) (#1 block flatten)",
                "diagram\n(#1 block flatten)\n(#1 block flatten)",
            ),
        ],
    )
    def test_block_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    params = []
    for _id in ["map", "fold", "mapfold", "mapi", "foldi", "mapfoldi"]:
        params.append((f"diagram (block {_id} A)", f"diagram\n(block {_id} A)"))
        params.append((f"diagram (block {_id} A::B::C)", f"diagram\n(block {_id} A::B::C)"))
        params.append((f"diagram (block {_id} reserve)", f"diagram\n(block {_id} reserve)"))
        params.append((f"diagram (block {_id} transpose)", f"diagram\n(block {_id} transpose)"))
        params.append((f"diagram (block {_id} pack)", f"diagram\n(block {_id} pack)"))
        params.append((f"diagram (block {_id} flatten)", f"diagram\n(block {_id} flatten)"))
        params.append(
            (
                f"diagram (block {_id} ({_id} ({_id} transpose {{4, 5, 6}})))",
                f"diagram\n(block {_id} ({_id} ({_id} transpose {{4, 5, 6}})))",
            )
        )

    @pytest.mark.parametrize("object, expected", params)
    def test_iter_op_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            (
                "diagram (#1 block (+) where (#3 block (*) where (#4 block (or) where (#5 block (land)))))",
                "diagram\n(#1 block (+) where (#3 block (*) where (#4 block (or) where (#5 block (land)))))",
            ),
        ],
    )
    def test_NAryOp_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            (
                "diagram (#1 block node A, B, C var V; assume $D: true; => false)",
                "diagram\n(#1 block node A, B, C var\nV; assume\n$D: true; => false)",
            ),
            (
                "diagram (#1 block (function A, B, C => A ^ last 'B ^ (C + 5)))",
                "diagram\n(#1 block (function A, B, C => A ^ last 'B ^ (C + 5)))",
            ),
            (
                "diagram (#1 block (function fast_exp var u; v; => u * v) where (expr last 'u))",
                "diagram\n(#1 block (function fast_exp var\nu;\nv; => u * v) where (expr last 'u))",
            ),
        ],
    )
    def test_anonymous_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        print(res)
        assert res == expected

    @pytest.mark.parametrize(
        "object, expected",
        [
            ("diagram (#1 def {x%$$$%x})", "diagram\n(#1 def {x%$$$%x})"),
            (
                "diagram (#1 expr forward restart <<N>> unless {%$$$%} until {%£££%} returns ())",
                "diagram\n(#1 expr forward restart\n<<N>>\nunless {%$$$%}\nuntil {%£££%}\nreturns ())",
            ),
            (
                "diagram (wire #2 => #3 .({syntax%!$$%syntax}))",
                "diagram\n(wire #2 => #3 .({syntax%!$$%syntax}))",
            ),
            (
                "diagram (#1 block {empty%%empty})",
                "diagram\n(#1 block {empty%%empty})",
            ),
            ("diagram (#1 block {x%$$$%x})", "diagram\n(#1 block {x%$$$%x})"),
        ],
    )
    def test_protected_diagram(self, object, expected):
        swan_obj = parser.scope_section(SwanString(object))
        res = swan_to_str(swan_obj)
        assert res == expected


class TestPrinterInterface:
    """
    Test Swan Interface
    """

    @pytest.mark.parametrize(
        "interface, expected",
        [
            ("{type%type type = int3;%type}", "{type%type type = int3;%type}"),
            ("{const%const C: int32 = 4 + 3j;%const}", "{const%const C: int32 = 4 + 3j;%const}"),
            (
                "{const%const const2: int32 = 0_t8;%const}",
                "{const%const const2: int32 = 0_t8;%const}",
            ),
            ("{type%type type% = int32;%type}", "{type%type type% = int32;%type}"),
            ("{const%const const: int2 = 0;%const}", "{const%const const: int2 = 0;%const}"),
            ("{sensor%sensor sensor: int3;%sensor}", "{sensor%sensor sensor: int3;%sensor}"),
            (
                "{group%group group = (int3, int32);%group}",
                "{group%group group = (int3, int32);%group}",
            ),
            ("{const%const const1: int32 : 0;%const}", "{const%const const1: int32 : 0;%const}"),
            ("{type%type type1 = int32 : 5;%type}", "{type%type type1 = int32 : 5;%type}"),
            (
                "{sensor%sensor sensor1: int32 = 2;%sensor}",
                "{sensor%sensor sensor1: int32 = 2;%sensor}",
            ),
            (
                "{group%group group1 = (int32, int32);;%group}",
                "{group%group group1 = (int32, int32);;%group}",
            ),
            ("{type%type2 type = int32;%type}", "{type%type2 type = int32;%type}"),
        ],
    )
    def test_markups_interface(self, interface, expected):
        swan_obj = parser.declaration(SwanString(interface))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "interface, expected",
        [
            (
                "inline function F1 (i0: int32) returns (o0: int32);",
                "inline function F1 (i0: int32;)\nreturns (o0: int32;);",
            ),
            (
                "function Op <<N1, N2>> (i0: int32) returns (o0: int32);",
                "function Op <<N1, N2>> (i0: int32;)\nreturns (o0: int32;);",
            ),
            (
                "function Op (a: 'T1;) returns (b: 'T2; c: 'T3;) where 'T1, 'T2 integer where 'T3 float;",
                "function Op (a: 'T1;)\nreturns (b: 'T2; c: 'T3;) where 'T1, 'T2 integer where 'T3 float;",
            ),
            (
                "function Op (a: int32;) returns (b: int32;) specialize Foo::Bar;",
                "function Op (a: int32;)\nreturns (b: int32;) specialize Foo::Bar;",
            ),
            (
                "inline function Op <<N1, N2>> (a: 'T1;) returns (b: 'T2; c: 'T3;) where 'T1, 'T2 integer where 'T3 float specialize Foo::Bar;",
                "inline function Op <<N1, N2>> (a: 'T1;)\nreturns (b: 'T2; c: 'T3;) where 'T1, 'T2 integer where 'T3 float specialize Foo::Bar;",
            ),
        ],
    )
    def test_signature(self, interface, expected):
        swan_obj = parser.declaration(SwanString(interface))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "interface, expected",
        [
            (
                """\
use P::Q as Plop;
type T; T2 = int8;
const C1: T; C2: T2;
group G1 = (bool, x: char); G2 = float32;
sensor S1: int8; S2: uint8;
function F (a: int8;)
returns (b: int8;);""",
                """\
use P::Q as Plop;
type T;
     T2 = int8;\n
const C1: T;
      C2: T2;\n
group G1 = (bool, x: char);
      G2 = float32;\n
sensor S1: int8;
       S2: uint8;\n
function F (a: int8;)
returns (b: int8;);\n""",
            ),
        ],
    )
    def test_interface(self, interface, expected):
        swan_obj = parser.module_interface(SwanString(SwanString.gen_version() + "\n" + interface))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "interface, expected",
        [
            (
                """\
use P::Q as Plop;
type T; T2 = uint8;
const C1: T; C2: T2;
group G1 = (bool, x: char); G2 = float32;
sensor S1: int8; S2: bool;
function F (a: int8;)
returns (b: int8;);""",
                """\
use P::Q as Plop;
type T;\n
type T2 = uint8;\n
const C1: T;\n
const C2: T2;\n
group G1 = (bool, x: char);\n
group G2 = float32;\n
sensor S1: int8;\n
sensor S2: bool;\n
function F (a: int8;)
returns (b: int8;);\n""",
            ),
        ],
    )
    def test_normalize_interface(self, interface, expected):
        swan_obj = parser.module_interface(SwanString(SwanString.gen_version() + "\n" + interface))
        res = swan_to_str(swan_obj, True)
        assert res == expected


class TestPrinterModule:
    @pytest.mark.parametrize(
        "body, expected",
        [
            (
                """\
use P::Q as Plop;
type T; T2 = int8;
const C1: T; C2: T2;
group G1 = (bool, x: char); G2 = float32;
sensor S1: int8; S2: uint8;
inline function f1 (A: bool;)
returns (B: bool;)
;
""",
                """\
use P::Q as Plop;
type T;
     T2 = int8;\n
const C1: T;
      C2: T2;\n
group G1 = (bool, x: char);
      G2 = float32;\n
sensor S1: int8;
       S2: uint8;\n
inline function f1 (A: bool;)
returns (B: bool;)
;\n""",
            ),
            (
                """\
use P::Q as Plop;
type T; T2 = int8;
const C1: T; C2: T2;
group G1 = (bool, x: char); G2 = float32;
sensor S1: int8; S2: uint8;
inline function function1 <<E, F>> (A: bool;)
returns (B: bool;) where 'T1, 'T2 numeric where 'T3 unsigned specialize P::D
;
""",
                """\
use P::Q as Plop;
type T;
     T2 = int8;\n
const C1: T;
      C2: T2;\n
group G1 = (bool, x: char);
      G2 = float32;\n
sensor S1: int8;
       S2: uint8;\n
inline function function1 <<E, F>> (A: bool;)
returns (B: bool;) where 'T1, 'T2 numeric where 'T3 unsigned specialize P::D
;\n""",
            ),
            (
                """\
use P::Q as Plop;
type T;
const C1: T;
group G1 = (bool, x: char);
sensor S1: int8;
node #pragma kcg expand #end ramp (start: 'T; limit: 'T; incr: 'T;)
returns (data: 'T;) where 'T numeric specialize A::B
;""",
                """\
use P::Q as Plop;
type T;\n
const C1: T;\n
group G1 = (bool, x: char);\n
sensor S1: int8;\n
node #pragma kcg expand #end ramp (start: 'T; limit: 'T; incr: 'T;)
returns (data: 'T;) where 'T numeric specialize A::B
;\n""",
            ),
        ],
    )
    def test_body(self, body, expected):
        swan_obj = parser.module_body(SwanString(SwanString.gen_version() + "\n" + body))
        res = swan_to_str(swan_obj)
        assert res == expected

    @pytest.mark.parametrize(
        "body, expected",
        [
            (
                """\
{const%const const: int32 = 0;%const}
{type%type type = int32;%type}
{sensor%sensor sensor: int32;%sensor}
{group%group group = (int8, int8);%group}
inline function {syntax%1%syntax} (i0: int16;)
returns (o0: int16;)
;
""",
                """\
{const%const const: int32 = 0;%const}
{type%type type = int32;%type}
{sensor%sensor sensor: int32;%sensor}
{group%group group = (int8, int8);%group}
inline function 1 (i0: int16;)
returns (o0: int16;)
;
""",
            ),
        ],
    )
    def test_markup_signature(self, body, expected):
        swan_obj = parser.module_body(SwanString(SwanString.gen_version() + "\n" + body))
        res = swan_to_str(swan_obj)
        assert res == expected
