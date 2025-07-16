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

from typing import Callable, List, Optional, Union, cast

from ansys.scadeone.core.svc.swan_creator.operator_creator import (
    SignatureCreator,
    OperatorCreator,
)
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
        self,
        type_vars: Union[List[VariableTypeExpression], str],
        kind: common.NumericKind,
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
        """Return type variable names of constraints.

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


class OperatorSignatureBase(common.Declaration, common.ModuleItem):  # numpydoc ignore=PR01
    """Base class for Operator and Signature, gathering all interface details."""

    def __init__(
        self,
        id: common.Identifier,
        is_inlined: bool,
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
        self._is_inlined = is_inlined
        self._inputs = inputs
        self._outputs = outputs
        self._sizes = sizes if sizes else []
        self._constraints = constraints if constraints else []
        self._specialization = specialization
        self._pragmas = pragmas if pragmas else []
        for children in (self._inputs, self._outputs, self._sizes, self._constraints):
            self.set_owner(self, children)
        self._is_text = False

    @property
    def is_node(self) -> bool:
        """True when operator is a node."""
        return self._is_node

    @property
    def is_inlined(self) -> bool:
        """True when operator is marked for inlining."""
        return self._is_inlined

    @property
    def inputs(self) -> List[common.Variable]:
        """Return inputs as a list."""
        return self._inputs

    @property
    def outputs(self) -> List[common.Variable]:
        """Return outputs as a list."""
        return self._outputs

    @property
    def sizes(self) -> List[common.Identifier]:
        """Return sizes as a list."""
        return self._sizes

    @property
    def constraints(self) -> List[TypeConstraint]:
        """Return constraints as a list."""
        return self._constraints

    @property
    def specialization(self) -> Union[common.PathIdentifier, None]:
        """Return specialization path_id or None."""
        return self._specialization

    @property
    def pragmas(self) -> List[common.Pragma]:
        """Return pragmas as a list."""
        return self._pragmas

    @property
    def is_text(self) -> bool:
        """True when operator is given from {text%...%text} markup,
        or an interface is given from {text%...%text} markup (body)
        or {signature%...%signature} markup (interface).
        """
        return self._is_text

    @is_text.setter
    def is_text(self, text_flag: bool):
        self._is_text = text_flag


class Signature(OperatorSignatureBase, SignatureCreator):
    """Operator interface definition.

    Used in module body or interface.
    """

    def __init__(
        self,
        id: common.Identifier,
        is_inlined: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        sizes: Optional[List[common.Identifier]] = None,
        constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        OperatorSignatureBase.__init__(
            self,
            id,
            is_inlined,
            is_node,
            inputs,
            outputs,
            sizes,
            constraints,
            specialization,
            pragmas,
        )


class Operator(OperatorSignatureBase, OperatorCreator):
    """Operator definition, with a body.

    Used in modules. The body may be empty.
    """

    def __init__(
        self,
        id: common.Identifier,
        is_inlined: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        body: Union[Scope, common.Equation, Callable] = None,
        sizes: Optional[List[common.Identifier]] = None,
        constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        OperatorSignatureBase.__init__(
            self,
            id,
            is_inlined,
            is_node,
            inputs,
            outputs,
            sizes,
            constraints,
            specialization,
            pragmas,
        )
        self._body = body

    @property
    def body(self) -> Union[Scope, common.Equation, None]:
        """Operator body: a scope, an equation, or None."""
        if isinstance(self._body, Callable):
            body = self._body(self)
            self._body = body
            self.set_owner(self, self._body)
        return self._body

    @property
    def has_body(self) -> bool:
        """True when operator has a body."""
        return self._body is not None

    @property
    def is_equation_body(self) -> bool:
        """True when body is reduced to a single equation."""
        return isinstance(self.body, common.Equation)

    @property
    def diagrams(self) -> List[Diagram]:
        """Return a list of diagram declarations."""
        if not self.has_body or self.is_equation_body:
            return []
        return [
            cast(Diagram, diag)
            for diag in filter(lambda x: isinstance(x, Diagram), self.body.sections)
            if diag
        ]
