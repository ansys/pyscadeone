# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for:

- var section
- let section
- emit section
- assume section
- guaranteed section
"""

from typing import List, Optional, Union

import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes

from .variable import VarDecl


class LetSection(scopes.ScopeSection):
    """Implements:

    **let** {{*equation* ;}} section.
    """

    def __init__(self, equations: List[common.Equation]) -> None:
        super().__init__()
        self._equations = equations
        common.SwanItem.set_owner(self, equations)

    @property
    def equations(self) -> List[common.Equation]:
        """List of equation in **let**."""
        return self._equations

    def __str__(self) -> str:
        content = self.to_str("let", self.equations, end="")
        return common.Markup.to_str(content, self.is_text, common.Markup.Text)


class VarSection(scopes.ScopeSection):
    """Implements:

    **var** {{*var_decl* ;}} section."""

    def __init__(self, var_decls: List[VarDecl]) -> None:
        super().__init__()
        self._var_decls = var_decls
        common.SwanItem.set_owner(self, var_decls)

    @property
    def var_decls(self) -> List[VarDecl]:
        """Declared variables."""
        return self._var_decls

    def __str__(self) -> str:
        return self.to_str("var", self.var_decls)


class EmissionBody(common.SwanItem):
    """Implements an emission:

    | *emission_body* ::= *flow_names* [[ **if** *expr* ]]
    | *flow_names* ::= NAME {{ , NAME }}
    """

    def __init__(
        self,
        flows: List[common.Identifier],
        condition: Optional[common.Expression] = None,
        luid: Optional[common.Luid] = None,
    ) -> None:
        super().__init__()
        self._flows = flows
        self._condition = condition
        self._luid = luid

    @property
    def flows(self) -> List[common.Identifier]:
        """Emitted flows."""
        return self._flows

    @property
    def condition(self) -> Union[common.Expression, None]:
        """Emission condition if exists, else None."""
        return self._condition

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Emission identifier if exists, else None."""
        return self._luid

    def __str__(self) -> str:
        emission = ", ".join([str(flow) for flow in self.flows])
        if self.condition:
            emission += f" if {self.condition}"
        return emission


class EmitSection(scopes.ScopeSection):
    """Implements an Emit section:

    **emit** {{*emission_body* ;}}"""

    def __init__(self, emissions: List[EmissionBody]) -> None:
        super().__init__()
        self._emissions = emissions
        common.SwanItem.set_owner(self, emissions)

    @property
    def emissions(self) -> List[EmissionBody]:
        """List of emissions."""
        return self._emissions

    def __str__(self) -> str:
        return self.to_str("emit", self.emissions)


class FormalProperty(common.SwanItem):
    """Assume or Guarantee expression."""

    def __init__(self, luid: common.Luid, expr: common.Expression) -> None:
        super().__init__()
        self._luid = luid
        self._expr = expr

    @property
    def luid(self) -> common.Luid:
        """Property identifier."""
        return self._luid

    @property
    def expr(self) -> common.Expression:
        """Property expression."""
        return self._expr

    def __str__(self) -> str:
        return f"{self.luid}: {self.expr}"


class AssertSection(scopes.ScopeSection):
    """Implements Assert section:

    **assert** {{LUID: *expr* ;}}"""

    def __init__(self, assertions: List[FormalProperty]) -> None:
        super().__init__()
        self._assertions = assertions
        common.SwanItem.set_owner(self, assertions)

    @property
    def assertions(self) -> List[FormalProperty]:
        """Hypotheses of Assert."""
        return self._assertions

    def __str__(self) -> str:
        return self.to_str("assert", self.assertions)


class AssumeSection(scopes.ScopeSection):
    """Implements Assume section:

    **assume** {{LUID: *expr* ;}}"""

    def __init__(self, hypotheses: List[FormalProperty]) -> None:
        super().__init__()
        self._hypotheses = hypotheses
        common.SwanItem.set_owner(self, hypotheses)

    @property
    def hypotheses(self) -> List[FormalProperty]:
        """Hypotheses of Assume."""
        return self._hypotheses

    def __str__(self) -> str:
        return self.to_str("assume", self.hypotheses)


class GuaranteeSection(scopes.ScopeSection):
    """Implements Guarantee section:

    **guarantee** {{LUID: *expr* ;}}"""

    def __init__(self, guarantees: List[FormalProperty]) -> None:
        super().__init__()
        self._guarantees = guarantees
        common.SwanItem.set_owner(self, guarantees)

    @property
    def guarantees(self) -> List[FormalProperty]:
        """Guarantees of Guarantee."""
        return self._guarantees

    def __str__(self) -> str:
        return self.to_str("guarantee", self.guarantees)


class ProtectedSection(scopes.ScopeSection, common.ProtectedItem):
    """Protected section, meaning a syntactically incorrect section construct."""

    def __init__(self, data: str) -> None:
        common.ProtectedItem.__init__(self, data)


# Diagram section is in diagram.py
