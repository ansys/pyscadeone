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
This module contains the classes for operator declarations and definitions.
"""

from typing import Callable, List, Optional, Union, cast

from ansys.scadeone.core.svc.swan_creator.operator_creator import (
    OperatorDeclarationCreator,
    OperatorCreator,
)
import ansys.scadeone.core.swan.common as common
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER

from .diagram import Diagram
from .scopes import Scope
from .typedecl import VariableTypeExpression
from .common import Variable


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
        if not isinstance(self._type_vars, str):
            common.SwanItem.set_owner(self, self._type_vars)

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


class SizeParameter(common.Declaration):  # numpydoc ignore=PR01
    """Size parameter declaration, used in operator declarations and definitions."""

    def __init__(
        self, id: common.Identifier, pragmas: Optional[List[common.Pragma]] = None
    ) -> None:
        common.Declaration.__init__(self, id, pragmas)
        self._id = id
        self.set_owner(self, self._id)


class OperatorDeclarationDefinitionBase(
    common.Declaration, common.ModuleItem
):  # numpydoc ignore=PR01
    """Base class for OperatorDeclaration and OperatorDefinition, gathering all interface details."""

    def __init__(
        self,
        id: common.Identifier,
        is_inlined: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        size_parameters: Optional[List[SizeParameter]] = None,
        type_constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        common.Declaration.__init__(self, id, pragmas)
        self._is_node = is_node
        self._is_inlined = is_inlined
        self._inputs = inputs
        self._outputs = outputs
        self._size_parameters = size_parameters if size_parameters else []
        self._type_constraints = type_constraints if type_constraints else []
        self._specialization = specialization
        for children in (
            self._inputs,
            self._outputs,
            self._size_parameters,
            self._type_constraints,
        ):
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
    def size_parameters(self) -> List[SizeParameter]:
        """Return size parameters as a list."""
        return self._size_parameters

    @property
    def type_constraints(self) -> List[TypeConstraint]:
        """Return type constraints as a list."""
        return self._type_constraints

    @property
    def specialization(self) -> Union[common.PathIdentifier, None]:
        """Return specialization path_id or None."""
        return self._specialization

    @property
    def is_text(self) -> bool:
        """True when operator is given from {text%...%text} markup,
        or an interface is given from {text%...%text} markup (body)
        or {signature%...%signature} markup (interface).
        """
        return self._is_text

    @is_text.setter
    def is_text(self, text_flag: bool) -> None:
        self._is_text = text_flag


class OperatorDeclaration(OperatorDeclarationDefinitionBase, OperatorDeclarationCreator):
    """Operator declaration definition.

    Used in module body or interface.
    """

    def __init__(
        self,
        id: common.Identifier,
        is_inlined: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        size_parameters: Optional[List[SizeParameter]] = None,
        type_constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        OperatorDeclarationDefinitionBase.__init__(
            self,
            id,
            is_inlined,
            is_node,
            inputs,
            outputs,
            size_parameters,
            type_constraints,
            specialization,
            pragmas,
        )

    def get_definition(self) -> Optional["OperatorDefinition"]:
        """Return the definition of this operator, if any.

        An operator declaration in a module body is always external.

        If the operator declaration is in a module interface, one looks for any definition in body."""
        if (module := self.module) is None:
            raise ScadeOneException(f"No module for operator declaration {self.id.value}")
        # An operator declaration may appear in a body or in an interface.
        if module.is_body:
            return (
                None  # operator declaration in body is always external, so no definition in body.
            )
        # in an interface, look for definition in body
        if (
            (mod := module.body())  # type: ignore
            and (decl := mod.get_declaration(self.id.value, local_only=True))
            and isinstance(decl, OperatorDefinition)
        ):
            return decl
        return None

    @property
    def is_external(self) -> bool:
        """True when operator has no definition."""
        if (module := self.module) is None:
            raise ScadeOneException(f"No module for operator declaration {self.id.value}")
        # An operator declaration may appear in a body or in an interface.
        if module.is_body:
            # In a body, operator declaration is always external
            # Check of alternative declaration in body
            if (
                (mod := module.body())  # type: ignore
                and (decl := mod.get_declaration(self.id.value, local_only=True))
                and isinstance(decl, OperatorDeclaration)
            ):
                LOGGER.warning(
                    f"Declaration {self.id.value} is declared in interface and body of module {module.get_full_path()}."
                )
                # No check for definition inside the body.
                return True
        # In an interface, look for definition in body, if any.
        # Interface declaration is external if there is no definition in the body.
        if (self.get_definition()) is not None:
            # found a definition in body, so not external.
            return False
        # Check of alternative declaration in body
        if (
            (mod := module.body())  # type: ignore
            and (decl := mod.get_declaration(self.id.value, local_only=True))
            and isinstance(decl, OperatorDeclaration)
        ):
            LOGGER.warning(
                f"Declaration {self.id.value} is declared in interface and body of module {module.get_full_path()}."
            )
        return True


class OperatorDefinition(OperatorDeclarationDefinitionBase, OperatorCreator):
    """Operator definition, with a body.

    Used in module body. The body may be empty.
    """

    def __init__(
        self,
        id: common.Identifier,
        is_inlined: bool,
        is_node: bool,
        inputs: List[common.Variable],
        outputs: List[common.Variable],
        body: Optional[Union[Scope, common.Equation, Callable]] = None,
        size_parameters: Optional[List[SizeParameter]] = None,
        type_constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[common.PathIdentifier] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        OperatorDeclarationDefinitionBase.__init__(
            self,
            id,
            is_inlined,
            is_node,
            inputs,
            outputs,
            size_parameters,
            type_constraints,
            specialization,
            pragmas,
        )
        self._body = body  # type: ignore
        self._lunum_manager = common.LunumManager()

    @property
    def body(self) -> Optional[Union[Scope, common.Equation]]:
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
    def is_public(self) -> bool:
        """True when operator is public.

        An operator is public when:
        - it is declared in a module interface,
        - or it is defined in a module body, but the module has no interface.
        """
        # Proceed with simple checks.
        # Other cases, like multiple declarations of same object
        # or another object kind with same name is not handled.
        if (module := self.module) is None:
            raise ScadeOneException(f"No module for operator {self.id.value}")
        # An operator definition can only be in a body.
        if (interface := module.interface()) is None:  # type: ignore
            # no interface, so all declarations are public.
            return True
        # module has an interface
        if (decl := interface.get_declaration(self.id.value, local_only=True)) and isinstance(
            decl, OperatorDeclaration
        ):
            return True
        else:
            # declaration is not in interface, so it is private.
            return False

    def get_declaration(self) -> Optional[OperatorDeclaration]:
        """Return the declaration of this operator, if any.

        Look for declaration in interface, if any."""
        if (module := self.module) is None:
            raise ScadeOneException(f"No module for operator {self.id.value}")
        # An operator definition can only be in a body, by construction
        # Look for declaration in interface, if any.
        if (interface := module.interface()) is None:  # type: ignore
            # no interface, so no declaration.
            return None
        # look for declaration in interface
        if (decl := interface.get_declaration(self.id.value, local_only=True)) and isinstance(
            decl, OperatorDeclaration
        ):
            return decl
        return None

    @property
    def is_external(self) -> bool:
        """Always False.

        Note that a body cannot be None in a final model."""
        return False

    @property
    def diagrams(self) -> List[Diagram]:
        """Return a list of diagram declarations."""
        if not self.has_body or self.is_equation_body:
            return []
        body = cast(Scope, self.body)
        return [
            cast(Diagram, diag)
            for diag in filter(lambda x: isinstance(x, Diagram), body.sections)
            if diag
        ]

    def get_local_variables(self) -> List[Variable]:
        """Return the list of all local variables declared for this operator definition.
        Local variables are collected from :py:class:`Scope` and recursively from all :py:class:`Diagram` sections of the
        operator. The returned list aggregates :py:attr:`Scope.local_variables` and :py:attr:`Diagram.local_variables`
        properties.

        Returns
        -------
        List[Variable]
            List of Variables found from the current operator definition.
        """
        if not self.has_body or self.is_equation_body:
            return []
        local_variables = []
        body = cast(Scope, self.body)
        local_variables.extend(body.local_variables)
        for diagram in [section for section in body.sections if isinstance(section, Diagram)]:
            OperatorDefinition._get_diagram_local_variables(diagram, local_variables)
        return local_variables

    @staticmethod
    def _get_diagram_local_variables(diagram: Diagram, local_variables: list[Variable]) -> None:
        """Recursive method for visiting all local variables of each diagram including subdiagrams. Exploration in
        depth relies on property :py:attr:`Diagram.diagrams`.

        Parameters
        ----------
        diagram : Diagram
            Diagram to visit.

        local_variables : list[Variable]
            List of local variables collected during the exploration.
        """
        local_variables.extend(diagram.local_variables)
        for subdiagram in diagram.diagrams:
            OperatorDefinition._get_diagram_local_variables(subdiagram, local_variables)
