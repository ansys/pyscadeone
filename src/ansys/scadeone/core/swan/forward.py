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

"""
This module contains the classes for forward expression

"""

from typing import List, Optional, Union

import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes


# Forward Expression
# ======================================================================
class ForwardLHS(common.SwanItem):  # numpydoc ignore=PR01
    """**forward** construct:

    *current_lhs* ::= *id* | [ *current_lhs* ]"""

    def __init__(self, lhs: Union[common.Identifier, "ForwardLHS"]) -> None:
        super().__init__()
        self._lhs = lhs
        common.SwanItem.set_owner(self, self._lhs)

    @property
    def lhs(self) -> Union[common.Identifier, "ForwardLHS"]:
        """Returns current lhs as an Identifier or a ForwardLHS."""
        return self._lhs

    @property
    def is_id(self) -> bool:
        """True when current lhs is an ID."""
        return isinstance(self.lhs, common.Identifier)


class ForwardCurrentElement(common.SwanItem):  # numpydoc ignore=PR01
    """Forward current element:

    *current_elt* ::= *current_lhs* = *expr* ;"""

    def __init__(self, lhs: ForwardLHS, expr: common.Expression) -> None:
        super().__init__()
        self._lhs = lhs
        self._expr = expr
        common.SwanItem.set_owner(self, self._lhs)
        common.SwanItem.set_owner(self, self._expr)

    @property
    def lhs(self) -> ForwardLHS:
        """Current element."""
        return self._lhs

    @property
    def expr(self) -> common.Expression:
        """Current element expression."""
        return self._expr


class ForwardDim(common.SwanItem):  # numpydoc ignore=PR01
    """**forward** construct dimension:

    *dim* ::= << *size* >> [[ **with** (( << *id* >> | *current_elt* )) {{ *current_elt* }} ]]

    Note that:

    - there may be no **with** part,
    - or it is an ID followed by a possible empty list,
    - or if no ID, at least one *current_element*.

    The *is_valid()* method checks for that property.

    Parameters
    ----------
    size: common.Expression
       Dimension size.

    id: common.Identifier (optional)
       **with** ID.

    elems: List[ForwardCurrentElement] (optional)
       **with** elements part.

    protected: str (optional)
        Content of the dimension if it syntactically incorrect.
        In that case, all other parameters are None.

    """

    def __init__(
        self,
        size: Optional[common.Expression] = None,
        dim_id: Optional[common.Identifier] = None,
        elems: Optional[List[ForwardCurrentElement]] = None,
        protected: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._size = size
        self._dim_id = dim_id
        self._elems = elems
        self._is_protected = protected is not None
        self._protected = protected
        common.SwanItem.set_owner(self, self._size)
        common.SwanItem.set_owner(self, self._dim_id)
        common.SwanItem.set_owner(self, self._elems)

    @property
    def is_protected(self) -> bool:
        """True when dimension is syntactically incorrect and protected."""
        return self._is_protected

    @property
    def size(self) -> Union[common.Expression, None]:
        """**forward** dimension size."""
        return self._size

    @property
    def dim_id(self) -> Union[common.Identifier, None]:
        """**forward** dimension ID, or None."""
        return self._dim_id

    @property
    def elems(self) -> Union[List[ForwardCurrentElement], None]:
        """**forward** dimension elements or None."""
        return self._elems

    @property
    def is_valid(self) -> bool:
        """Returns True when ID is given, or list of elements is not empty."""
        if self.is_protected:
            return False
        if self.dim_id:
            return True
        if (self.elems is None) or (len(self.elems) > 0):
            return True
        return False

    @property
    def protected(self) -> Optional[str]:
        """Returns protected form as a string if dimension is syntactically invalid."""
        return self._protected


class ForwardReturnItem(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for *returns_item*."""

    def __init__(self) -> None:
        super().__init__()


# Accu clause
# ======================================================================


class ForwardAccuClause(ForwardReturnItem):  # numpydoc ignore=PR01
    """**forward** accumulator construct:

    *accu_clause* ::= *id* : **last** = *expr*"""

    def __init__(self, id: common.Identifier, last_expr: common.Expression) -> None:
        super().__init__()
        self._id = id
        self._last_expr = last_expr
        common.SwanItem.set_owner(self, self._id)
        common.SwanItem.set_owner(self, self._last_expr)

    @property
    def id(self) -> common.Identifier:
        """Item_clause identifier."""
        return self._id

    @property
    def last_expr(self) -> common.Expression:
        """Item_clause last expression."""
        return self._last_expr


# Array clauses
# ======================================================================


class ForwardArrayClause(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for forward *array_clause*."""

    def __init__(self) -> None:
        super().__init__()


class ForwardArrayClauseExpr(ForwardArrayClause):  # numpydoc ignore=PR01
    """**forward** construct:

    *array_clause* ::=  *expr_no_bracket* [[ **default** *expr* ]]"""

    def __init__(
        self,
        expr_no_bracket: common.Expression,
        default_expr: Optional[common.Expression] = None,
    ) -> None:
        super().__init__()
        self._expr_no_bracket = expr_no_bracket
        self._default_expr = default_expr
        common.SwanItem.set_owner(self, self._expr_no_bracket)
        common.SwanItem.set_owner(self, self._default_expr)

    @property
    def expr_no_bracket(self) -> common.Expression:
        """Expression without brackets."""
        return self._expr_no_bracket

    @property
    def default_expr(self) -> Union[common.Expression, None]:
        """Default expression, or None."""
        return self._default_expr


class ForwardArrayClauseElement(ForwardArrayClause):  # numpydoc ignore=PR01
    """**forward** construct:

    *array_clause* ::= [ *array_clause* ]]"""

    def __init__(
        self,
        array_clause: ForwardArrayClause,
    ) -> None:
        super().__init__()
        self._array_clause = array_clause
        common.SwanItem.set_owner(self, self._array_clause)

    @property
    def array_clause(self) -> ForwardArrayClause:
        """Array clause."""
        return self._array_clause


class ForwardReturnArrayClause(ForwardReturnItem):  # numpydoc ignore=PR01
    """**forward** construct:

    *returns_item* ::= [[ *id* : ]] *array_clause*"""

    def __init__(
        self,
        array_clause: ForwardArrayClause,
        id: Optional[common.Identifier] = None,
    ) -> None:
        super().__init__()
        self._array_clause = array_clause
        self._id = id
        common.SwanItem.set_owner(self, self._array_clause)
        common.SwanItem.set_owner(self, self._id)

    @property
    def array_clause(self) -> ForwardArrayClause:
        """Array clause."""
        return self._array_clause

    @property
    def id(self) -> Union[common.Identifier, None]:
        """Identifier of clause, or None."""
        return self._id


# Protected items
# =====================================================================
class ProtectedForwardReturnItem(common.ProtectedItem, ForwardReturnItem):  # numpydoc ignore=PR01
    """**forward** construct: protected *returns_item* with {syntax% ... %syntax} markup."""

    def __init__(self, data: str) -> None:
        super().__init__(data)


# Forward body
# =====================================================================
class ForwardBody(common.SwanItem):  # numpydoc ignore=PR01
    """
    **forward** construct:

    fwd_body ::= [[ unless expr ]] scope_sections [[ until expr ]]
    """

    def __init__(
        self,
        sections: List[scopes.ScopeSection],
        unless_expr: Optional[common.Expression] = None,
        until_expr: Optional[common.Expression] = None,
    ) -> None:
        super().__init__()
        self._sections = sections
        self._unless_expr = unless_expr
        self._until_expr = until_expr
        common.SwanItem.set_owner(self, self._sections)
        common.SwanItem.set_owner(self, self._unless_expr)
        common.SwanItem.set_owner(self, self._until_expr)

    @property
    def sections(self) -> List[scopes.ScopeSection]:
        return self._sections

    @property
    def unless_expr(self) -> Optional[common.Expression]:
        return self._unless_expr

    @property
    def until_expr(self) -> Optional[common.Expression]:
        return self._until_expr


class Forward(common.Expression):  # numpydoc ignore=PR01
    """Forward expression:

    | *fwd_expr* ::= **forward** [[ *luid*]] [[ (( **restart** | **resume** )) ]] {{ *dim* }}+
    |                *fwd_body* **returns** ( *returns_group* )
    | *returns_group* ::= [[ *returns_item* {{ , *returns_item* }} ]]
    """

    def __init__(
        self,
        restart: Optional[bool],
        dimensions: List[ForwardDim],
        body: ForwardBody,
        returns: List[ForwardReturnItem],
        luid: Optional[common.Luid] = None,
    ) -> None:
        super().__init__()
        self._restart = restart
        self._dimensions = dimensions
        self._body = body
        self._returns = returns
        self._luid = luid
        common.SwanItem.set_owner(self, self._dimensions)
        common.SwanItem.set_owner(self, self._body)
        common.SwanItem.set_owner(self, self._returns)
        common.SwanItem.set_owner(self, self._luid)

    @property
    def restart(self) -> Optional[bool]:
        return self._restart

    @property
    def is_restart(self) -> bool:
        """True if restart mode, else resume mode.
        Note: default mode for a forward is restart,
        which is indicated by the restart property being None."""
        return self._restart is None or self._restart

    @property
    def dimensions(self) -> List[ForwardDim]:
        return self._dimensions

    @property
    def body(self) -> ForwardBody:
        return self._body

    @property
    def returns(self) -> List[ForwardReturnItem]:
        return self._returns

    @property
    def luid(self) -> Union[common.Luid, None]:
        return self._luid
