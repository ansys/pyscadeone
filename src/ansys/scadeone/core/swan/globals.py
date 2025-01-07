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
This module contains the classes for global definitions:
constants (const) and sensors.
"""

from typing import Optional, Union

import ansys.scadeone.core.swan.common as common


class ConstDecl(common.Declaration):  # numpydoc ignore=PR01
    """Constant declaration, with an id, a type, and an optional expression."""

    def __init__(
        self,
        id: common.Identifier,
        type: Optional[common.TypeExpression],
        value: Optional[common.Expression] = None,
    ) -> None:
        super().__init__(id)
        self._type_expr = type
        self._value = value

    @property
    def type(self) -> Union[common.TypeExpression, None]:
        """Type of constant."""
        return self._type_expr

    @property
    def value(self) -> Union[common.Expression, None]:
        """Constant optional value. None if undefined."""
        return self._value

    def __str__(self) -> str:
        type = f": {self.type}" if self.type else ""
        decl = self.id
        init = f" = {self.value}" if self.value else ""
        return f"{decl}{type}{init}"


class SensorDecl(common.Declaration):  # numpydoc ignore=PR01
    """Sensor declaration with an id and a type."""

    def __init__(self, id: common.Identifier, type: common.TypeExpression) -> None:
        super().__init__(id)
        self._type = type

    @property
    def type(self) -> common.TypeExpression:
        """Sensor type."""
        return self._type

    def __str__(self) -> str:
        return f"{self.id}: {self.type}"
