# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2022 - 2024 ANSYS, Inc.
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
This module contains the classes for operator and signature (operator
without body)
"""

from typing import Callable, Generator, List, Optional, Union

import ansys.scadeone.core.swan.common as common

from .diagram import Diagram
from .scopes import Scope
from .typedecl import VariableTypeExpression


class TypeConstraint(common.SwanItem):  # numpydoc ignore=PR01
    """Type constraint for operator. A constraint is:

    *where_decl* ::= **where** *typevar* {{ , *typevar* }} *numeric_kind*

    The *typevar* list can be protected and represented with string.
    """

    def __init__(
        self, type_vars: Union[List[VariableTypeExpression], str], kind: common.NumericKind
    ) -> None:
        super().__init__()
        self._is_protected = isinstance(type_vars, str)
        self._type_vars = type_vars
        self._kind = kind

    @property
    def is_protected(self) -> bool:
        """True when types are protected."""
        return self._is_protected

    @property
    def type_vars(self) -> Union[List[VariableTypeExpression], str]:
        """Returns type variable names of constraints.

        Returns
        -------
        Union[List[VariableTypeExpression], str]
            Returns the list of type names, if not protected, or
            the constraint names as a string.
        """
        return self._type_vars

    @property
    def kind(self) -> common.NumericKind:
        """Constraint numeric kind."""
        return self._kind

    def __str__(self) -> str:
        type_vars = (
            common.Markup.to_str(self.type_vars)
            if self.is_protected
            else ", ".join([str(tv) for tv in self.type_vars])
        )
        return f"where {type_vars} {common.NumericKind.to_str(self.kind)}"


class Signature(common.Declaration, common.ModuleItem):  # numpydoc ignore=PR01
    """Operator signature, without a body.

    Used in interfaces."""

    def __init__(
        self,
        id: common.Identifier,
        has_inline: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        sizes: Optional[List[common.Identifier]] = None,
        constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        common.Declaration.__init__(self, id)
        self._is_node = is_node
        self._has_inline = has_inline
        self._inputs = inputs
        self._outputs = outputs
        self._sizes = sizes if sizes else []
        self._constraints = constraints if constraints else []
        self._specialization = specialization
        self._pragmas = pragmas if pragmas else []
        for children in (self._inputs, self._outputs, self._sizes, self._constraints):
            self.set_owner(self, children)

    @property
    def is_node(self) -> bool:
        """True when operator is a node."""
        return self._is_node

    @property
    def has_inline(self) -> bool:
        """True when operator is marked for inlining."""
        return self._has_inline

    @property
    def inputs(self) -> Generator[common.Variable, None, None]:
        """Returns inputs as a generator."""
        for input in self._inputs:
            yield input

    @property
    def outputs(self) -> Generator[common.Variable, None, None]:
        """Return outputs as a generator."""
        for output in self._outputs:
            yield output

    @property
    def sizes(self) -> Generator[common.Identifier, None, None]:
        """Return sizes as a generator."""
        for size in self._sizes:
            yield size

    @property
    def constraints(self) -> Generator[TypeConstraint, None, None]:
        """Return constraints as a generator."""
        for constraint in self._constraints:
            yield constraint

    @property
    def specialization(self) -> Union[common.PathIdentifier, None]:
        """Return specialization path_id or None."""
        return self._specialization

    @property
    def pragmas(self) -> Generator[common.Pragma, None, None]:
        """Return pragmas as a generator."""
        for pragma in self._pragmas:
            yield pragma

    def to_str(self) -> str:
        """Interface declaration, without trailing semicolon."""
        inline = "inline " if self.has_inline else ""
        kind = "node" if self.is_node else "function"
        id = str(self.id)
        # Inputs/Outputs
        signals = {}
        for sig_kind, sig_list in (("in", self.inputs), ("out", self.outputs)):
            signals[sig_kind] = "; ".join([str(sig) for sig in sig_list])
            if signals[sig_kind]:
                signals[sig_kind] = f"(\n  {signals[sig_kind]}\n)"
            else:
                signals[sig_kind] = "()"
        # Sizes
        sizes = (
            " <<"
            + ", ".join([common.Markup.to_str(str(sz), sz.is_protected) for sz in self.sizes])
            + ">>"
        )
        if sizes == " <<>>":
            sizes = ""
        # Constraints
        constraints = " " + " ".join([str(ct) for ct in self.constraints])
        if constraints == " ":
            constraints = ""
        # Specialization
        if self.specialization:
            specialization = f" specialize {self.specialization}"
        else:
            specialization = ""
        # Pragmas
        pragmas = " " + " ".join([str(pg) for pg in self.pragmas])
        if pragmas == " ":
            pragmas = ""
        # Declaration
        return "{inline}{kd}{pragmas} {id}{sz} {ins} returns {outs}{cst}{spz}".format(
            inline=inline,
            kd=kind,
            pragmas=pragmas,
            id=id,
            sz=sizes,
            ins=signals["in"],
            outs=signals["out"],
            cst=constraints,
            spz=specialization,
        )

    def __str__(self) -> str:
        return f"{self.to_str()};"


class Operator(Signature):  # numpydoc ignore=PR01
    """Operator definition, with a body.

    Used in modules. The body may not bet yet defined."""

    def __init__(
        self,
        id: common.Identifier,
        has_inline: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        body: Union[Scope, common.Equation, None, Callable],
        sizes: Optional[List[common.Identifier]] = None,
        constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(
            id, has_inline, is_node, inputs, outputs, sizes, constraints, specialization, pragmas
        )
        self._body = body
        self._is_text = False

    @property
    def body(self) -> Union[Scope, common.Equation, None]:
        """Operator body: a scope, an equation, or None."""
        if isinstance(self._body, Callable):
            body = self._body(self)
            self._body = body
            self.set_owner(self, self._body)
        return self._body

    @property
    def is_text(self) -> bool:
        """True when operator is given from {text%...%text} markup."""
        return self._is_text

    @is_text.setter
    def is_text(self, text_flag: bool):
        self._is_text = text_flag

    @property
    def has_body(self) -> bool:
        """True when operator has a body."""
        return self._body is not None

    @property
    def is_equation_body(self) -> bool:
        """True when body is reduced to a single equation."""
        return isinstance(self.body, common.Equation)

    @property
    def signature(self) -> Signature:
        """Return operator signature."""
        return Signature(
            self.id,
            self.has_inline,
            self.is_node,
            list(self.inputs),
            list(self.outputs),
            list(self.sizes),
            list(self.constraints),
            self.specialization,
            list(self.pragmas),
        )

    @property
    def diagrams(self) -> Generator[Diagram, None, None]:
        """Return a generator on diagram declarations."""
        if not self.has_body or self.is_equation_body:
            return []
        for decl in filter(lambda x: isinstance(x, Diagram), self.body.sections):
            yield decl

    def __str__(self) -> str:
        decl = self.to_str()
        if isinstance(self.body, common.Equation):
            body = f"\n  {self.body}"
        elif isinstance(self.body, Scope):
            body = f"\n{self.body}"
        else:
            body = ";"
        return f"{decl}{body}"
