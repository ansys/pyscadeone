# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as swan
from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.swan.typedecl import (
    EnumTypeDefinition,
    ExprTypeDefinition,
    StructTypeDefinition,
)


def gen_code(swan_code: str, module: str) -> SwanString:
    return SwanString(gen_swan_version() + "\n" + swan_code, module)


@pytest.fixture(scope="session")
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


@pytest.fixture(scope="session")
def model(parser):
    app_ = ScadeOne()
    model_ = app_.model

    code_M0_body = gen_code(
        """
            use M1;
            use M2 as M3;
            use N1::N2::M4 as M5;
            type T1 = int32;
            const C1: T1 = 10;
            const C2: T2;
            const C3: M1::T3 = true;
            const C4: M3::T4;
            const C5: M5::T5;
        """,
        "M0",
    )
    code_M0_interface = gen_code(
        """
            type T2 = float64;
        """,
        "M0",
    )
    code_M1_body = gen_code(
        """
            type T3 = bool;
        """,
        "M1",
    )
    code_M2_interface = gen_code(
        """
            type T4 = {a: int8, b: int16};
        """,
        "M2",
    )
    code_M3_body = gen_code(
        """
            type T5 = enum {ONE, TWO, THREE};
        """,
        "N1::N2::M4",
    )

    M0_body = parser.module_body(code_M0_body)
    M0_interface = parser.module_interface(code_M0_interface)
    M1_body = parser.module_body(code_M1_body)
    M2_interface = parser.module_interface(code_M2_interface)
    M3_body = parser.module_body(code_M3_body)

    model_.add_body(M0_body)
    model_.add_interface(M0_interface)
    model_.add_body(M1_body)
    model_.add_interface(M2_interface)
    model_.add_body(M3_body)

    yield model_


class TestGetTypeDecl:
    @pytest.mark.parametrize(
        ("constant", "expected_type_definition", "expected_type_str"),
        [
            ("C1", ExprTypeDefinition, "T1 = int32"),
            ("C2", ExprTypeDefinition, "T2 = float64"),
            ("C3", ExprTypeDefinition, "T3 = bool"),
            ("C4", StructTypeDefinition, "T4 = {a: int8, b: int16}"),
            ("C5", EnumTypeDefinition, "T5 = enum {ONE, TWO, THREE}"),
        ],
    )
    def test_constant_decl(self, model, constant, expected_type_definition, expected_type_str):
        decl = model.get_module_body("M0").get_declaration(constant).type.type_decl
        assert isinstance(decl, swan.TypeDecl)
        type_definition = decl.definition
        assert isinstance(type_definition, expected_type_definition)
        decl_str = swan.swan_to_str(decl)
        assert decl_str == expected_type_str
