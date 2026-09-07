# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

from typing import cast

import pytest

from ansys.scadeone.core import swan
from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.common.storage import SwanString


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(gen_swan_version() + "\n" + swan, module)


class TestScopeVariables:
    """Class focused on access of property **local_variables** of a **Scope** object"""

    @pytest.fixture
    def scope(self, parser):
        code = gen_code(
            """
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  var x1: int32; x2: int32;
                  let o0 = i0;
                  var x3: int32;
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        return cast(swan.Scope, body.operator_definitions[0].body)

    @staticmethod
    def test_variables(scope):
        scope_variables = scope.local_variables
        assert len(scope_variables) == 3
        assert scope_variables[0].id.value == "x1"
        assert scope_variables[1].id.value == "x2"
        assert scope_variables[2].id.value == "x3"
