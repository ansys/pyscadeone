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
This module contains classes to manipulate group declarations
and group expressions.
"""

from typing import List

import ansys.scadeone.core.swan.common as common


class TypeGroupTypeExpression(common.GroupTypeExpression):  # numpydoc ignore=PR01
    """Group type expression: *group_type_expr* ::= *type_expr*."""

    def __init__(self, type: common.TypeExpression) -> None:
        super().__init__()
        self._type = type

    @property
    def type(self) -> common.TypeExpression:
        """Type expression of group item"""
        return self._type


class NamedGroupTypeExpression(common.GroupTypeExpression):  # numpydoc ignore=PR01
    """A named group type expression, used in GroupTypeExpressionList as id : *group_type_expr*."""

    def __init__(self, label: common.Identifier, type: common.GroupTypeExpression) -> None:
        super().__init__()
        self._label = label
        self._type = type

    @property
    def label(self) -> common.Identifier:
        """Label of named group item."""
        return self._label

    @property
    def type(self) -> common.GroupTypeExpression:
        """Type of named group item."""
        return self._type


class GroupTypeExpressionList(common.GroupTypeExpression):  # numpydoc ignore=PR01
    """Group list made of positional items followed by named items.
    Each item is a group type expression.

    | *group_type_expr* ::= ( *group_type_expr* {{ , *group_type_expr* }}
    |                        {{ , id : *group_type_expr* }} )
    | | ( id : *group_type_expr* {{ , id : *group_type_expr* }} )
    """

    def __init__(
        self,
        positional: List[common.GroupTypeExpression],
        named: List[NamedGroupTypeExpression],
    ) -> None:
        super().__init__()
        self._positional = positional
        self._named = named

    @property
    def positional(self) -> List[common.GroupTypeExpression]:
        """Return positional group items"""
        return [p for p in self._positional]

    @property
    def named(self) -> List[NamedGroupTypeExpression]:
        """Return named group items"""
        return [p for p in self._named]

    @property
    def items(self) -> List[common.GroupTypeExpression]:
        """Returns all items"""
        items = []
        for pos in self.positional:
            items.append(pos)
        for named in self.named:
            items.append(named)
        return items


class GroupDecl(common.Declaration):  # numpydoc ignore=PR01
    """Group declaration with an id and a type."""

    def __init__(self, id: common.Identifier, type: common.GroupTypeExpression) -> None:
        super().__init__(id)
        self._type = type

    @property
    def type(self) -> common.GroupTypeExpression:
        """Group type expression."""
        return self._type
