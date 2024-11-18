# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for variable declarations:
- VarDecl
- ProtectedVariable, for syntactically incorrect variable definition
"""
from typing import Optional, Union

import ansys.scadeone.core.swan.common as common
from ansys.scadeone.core.swan.expressions import ClockExpr


class VarDecl(common.Declaration, common.Variable):
    """Class for variable declaration."""

    def __init__(
        self,
        id: common.Identifier,
        is_clock: Optional[bool] = False,
        is_probe: Optional[bool] = False,
        type: Optional[common.GroupTypeExpression] = None,
        when: Optional[ClockExpr] = None,
        default: Optional[common.Expression] = None,
        last: Optional[common.Expression] = None,
    ) -> None:
        common.Declaration.__init__(self, id)
        self._is_clock = is_clock
        self._is_probe = is_probe
        self._type = type
        self._when = when
        self._default = default
        self._last = last
        self._is_input = False
        self._is_output = False

    @property
    def is_clock(self) -> bool:
        """True when variable is a clock."""
        return self._is_clock

    @property
    def is_probe(self) -> bool:
        """True when variable is a probe."""
        return self._is_probe

    @property
    def type(self) -> Union[common.GroupTypeExpression, None]:
        """Variable type."""
        return self._type

    @property
    def when(self) -> Union[ClockExpr, None]:
        """Variable clock."""
        return self._when

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

    def __str__(self) -> str:
        buffer = ""
        if self.is_clock:
            buffer += "clock "
        if self.is_probe:
            buffer += "#pragma cg probe #end "
        buffer += str(self.id)
        if self.type:
            buffer += f": {self.type}"
        if self.when:
            buffer += f" when {self.when}"
        if self.default:
            buffer += f" default = {self.default}"
        if self.last:
            buffer += f" last = {self.last}"
        return buffer

    def var_decl(self) -> str:
        """Return variable declaration string."""
        return f"var {self};\n"


class ProtectedVariable(common.Variable, common.ProtectedItem):
    """Protected variable definition as a string."""

    def __init__(self, data: str) -> None:
        common.ProtectedItem.__init__(self, data, common.Markup.Var)
