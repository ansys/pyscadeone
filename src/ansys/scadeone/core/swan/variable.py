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
This module contains the classes for variable declarations:
- VarDecl
- ProtectedVariable, for syntactically incorrect variable definition
"""

from enum import Enum, auto
from typing import Optional, Union, List

import ansys.scadeone.core.swan.common as common
from ansys.scadeone.core.swan.pragmas import CGPragma, CGPragmaKind


class VarInitDelay(Enum):
    """Enum for variable initialization information."""

    #: No initialization.
    DelayNone = auto()

    #: Variable must be initialized for the first cycle.
    Delay0 = auto()

    #: Variable does not need to be initialized for the first cycle.
    Delay1 = auto()

    def __str__(self) -> str:
        return self.name.lower()


class VarDecl(common.Declaration, common.Variable):  # numpydoc ignore=PR01
    """Class for variable declaration.

    Parameters
    ----------
    id: common.Identifier
        Variable identifier.
    is_starred: bool, optional
        True if variable is starred. Default is False.
    at: Optional[common.Identifier], optional
        Memory constrained output. Name of the memory place. Note: *is_output* must be True. Default is None.
    type: Optional[common.GroupTypeExpression], optional
        Variable type. Default is None.
    init_type: VarInitDelay, optional
        Variable initialization delay. Default is VarInitDelay.DelayNone.
    causality_type: Optional[List[common.Identifier]], optional
        Variable causality_type attributes. Default is None.
    default: Optional[common.Expression], optional
        Variable default expression. Default is None.
    last: Optional[common.Expression], optional
        Variable last expression. Default is None.
    pragmas: Optional[list[common.Pragma]], optional
        List of pragmas. Default is None.

    """

    def __init__(
        self,
        id: common.Identifier,
        is_starred: bool = False,
        at: Optional[common.Identifier] = None,
        type: Optional[common.GroupTypeExpression] = None,
        init_type: VarInitDelay = VarInitDelay.DelayNone,
        causality_type: Optional[List[common.Identifier]] = None,
        default: Optional[common.Expression] = None,
        last: Optional[common.Expression] = None,
        pragmas: Optional[list[common.Pragma]] = None,
    ) -> None:
        common.Declaration.__init__(self, id, pragmas)
        self._is_starred = is_starred
        self._at = at
        self._type = type
        self._init_type = init_type
        self._causality_type = causality_type or []
        self._default = default
        self._last = last
        self._is_input = False
        self._is_output = False
        common.SwanItem.set_owner(self, self._type)
        common.SwanItem.set_owner(self, self._default)
        common.SwanItem.set_owner(self, self._last)
        common.SwanItem.set_owner(self, self._at)

    @property
    def init_type(self) -> VarInitDelay:
        """Variable initialization delay."""
        return self._init_type

    @property
    def causality_type(self) -> List[common.Identifier]:
        """Variable causality_type attributes."""
        return self._causality_type

    @property
    def is_starred(self) -> bool:
        """True when consumption is allowed for the input variable. Note: *is_input* must be True."""
        return self._is_starred

    @property
    def at(self) -> Optional[common.Identifier]:
        """Memory constrained output. Name of the memory place. Note: *is_output* must be True."""
        return self._at

    @property
    def is_probe(self) -> bool:
        """True when variable is a probe."""
        # probe pragma can be added or removed at any time, so we always check pragmas
        return any(isinstance(p, CGPragma) and p.kind == CGPragmaKind.PROBE for p in self.pragmas)

    @property
    def type(self) -> Union[common.GroupTypeExpression, None]:
        """Variable type."""
        return self._type

    @property
    def default(self) -> Union[common.Expression, None]:
        """Variable default expression."""
        return self._default

    @property
    def last(self) -> Union[common.Expression, None]:
        """Variable last expression."""
        return self._last

    @property
    def is_input(self) -> bool:
        """True when variable is an input."""
        return self._is_input

    @is_input.setter
    def is_input(self, value: bool) -> None:
        self._is_input = value

    @property
    def is_output(self) -> bool:
        """True when variable is an output."""
        return self._is_output

    @is_output.setter
    def is_output(self, value: bool) -> None:
        self._is_output = value

    @property
    def is_local(self) -> bool:
        """True when variable is local."""
        return not self.is_input and not self.is_output


class ProtectedVariable(
    common.Variable, common.ProtectedItem, common.HasPragma
):  # numpydoc ignore=PR01
    """Protected variable definition as a string."""

    def __init__(self, data: str, pragmas: Optional[List[common.Pragma]] = None) -> None:
        common.ProtectedItem.__init__(self, data, common.Markup.Var)
        common.HasPragma.__init__(self, pragmas)
