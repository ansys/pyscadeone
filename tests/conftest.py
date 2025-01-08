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

import logging

import pytest

import ansys.scadeone.core.swan as S


# Unit test logger => './unit_tests.log'
@pytest.fixture(scope="session")
def unit_test_logger():
    logger = logging.getLogger("test_logger")
    fh = logging.FileHandler("unit_tests.log", mode="w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


# CC model path
@pytest.fixture(scope="session")
def cc_project():
    return "examples/models/CC/CruiseControl/CruiseControl.sproj"


# scadeone "installation" path for tests
@pytest.fixture(scope="session")
def installation():
    return "src/ansys/scadeone"


#######################################
# pyofast fixtures
#


# Identifier creation: ID1, ID2, ....
# ex:
# test(make_identifier):
#   id1 = make_identifier()
#   id2 = make_identifier()
# Use make_identifier(True) to reset counter.
@pytest.fixture
def make_identifier():
    count = {"ctr": 0}

    def _make_identifier(reset=False):
        if reset:
            count["ctr"] = 0
        count["ctr"] += 1
        return S.Identifier(f"ID{count['ctr']}")

    return _make_identifier


# Create a path_identifier ID<x>::ID<x+1>::ID<x+2>
# Ex:
# test(make_path_identifier)
#   p = make_path_identifier()
# use make_path_identifier(True) to reset counter.
@pytest.fixture
def make_path_identifier(make_identifier):
    def _make_path_identifier(reset=False):
        return S.PathIdentifier([make_identifier(reset), make_identifier(), make_identifier()])

    return _make_path_identifier


# Create a simple type expression.
# Ex:
# text(make_simple_type)
# ex: typ = make_simple_type('int'|'float'|'bool').
# Any other parameters leads to "bool" type.
@pytest.fixture
def make_simple_type():
    def _make_simple_type(type_name):
        if type_name == "int":
            return S.Int32Type()
        elif type_name == "float":
            return S.Float32Type()
        return S.BoolType()

    return _make_simple_type


# Create the type expression: {a: int8}
@pytest.fixture
def make_boxed_int8():
    f = S.StructField(S.Identifier("a"), S.Int8Type())
    return S.StructTypeDefinition([f])


# Create a type variable 'T1, 'T2, ...
@pytest.fixture
def make_type_var():
    count = {"ctr": 0}

    def _make_type_var():
        count["ctr"] += 1

        return S.VariableTypeExpression(S.Identifier(f"T{count['ctr']}", is_name=True))

    return _make_type_var


# Create a var declaration: IDx : {a: int8}
# Ex:
# test(make_var_decl):
#   var = make_var_decl()       => var is bool
#   var = make_var_decl(False)  => var is {a: int8}
@pytest.fixture
def make_var_decl(make_identifier, make_boxed_int8, make_simple_type):
    def _make_var_decl(as_bool=True):
        return S.VarDecl(
            make_identifier(),
            type=S.TypeGroupTypeExpression(
                make_simple_type("bool") if as_bool else make_boxed_int8
            ),
        )

    return _make_var_decl


# Create a list of lhs items
@pytest.fixture
def make_lhs(make_identifier):
    def _make_lhs(count, reset=False):
        lhs = []
        for i in range(0, count):
            lhs.append(S.LHSItem(make_identifier(reset)))
            reset = False
        return S.EquationLHS(lhs)

    return _make_lhs


@pytest.fixture
def make_let(make_lhs, make_path_identifier):
    def _make_let(reset=False):
        expr = S.PathIdExpr(make_path_identifier())
        eq1 = S.ExprEquation(make_lhs(1, reset=reset), expr)
        eq2 = S.ExprEquation(make_lhs(1), expr)
        return S.LetSection([eq1, eq2])

    return _make_let
