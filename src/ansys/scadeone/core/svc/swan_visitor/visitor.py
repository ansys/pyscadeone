# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
# AUTOMATICALLY GENERATED FILE DO NOT EDIT OR MAKE A COPY OF IT

# pylint: disable=too-many-lines, pointless-statement, invalid-name
from abc import ABC
from typing import Any, Optional, Union
from enum import Enum

from ansys.scadeone.core import swan

__all__ = ["SwanVisitor", "Owner", "OwnerProperty"]

Owner = Optional[swan.SwanItem]
OwnerProperty = Optional[str]


class SwanVisitor(ABC):
    """Base class for visiting Swan elements

    Provides a generic ``_visit`` method that delegates to
    type-specific ``visit_<ElementType>`` methods.

    Subclass this visitor and override the relevant ``visit_<ElementType>`` methods
    to customize the behavior for specific elements."""

    @staticmethod
    def _is_builtin(obj: Any) -> bool:
        """Return True if name is a simple builtin-type
        that can be found in swan modules"""
        return type(obj).__name__ in ("str", "int", "bool", "float")

    def visit(self, swan_obj: swan.SwanItem) -> None:
        """Default visitor main method. After creation of an instance of
        a SwanVisitor, this method must be called on a Swan object instance."""
        self._visit(swan_obj, None, None)

    def _visit(
        self,
        swan_obj: Union[swan.SwanItem, Enum],
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Dispatch function. Visit a Swan object and its properties recursively
        by calling `self.visit_<swan_obj class name>(swan_obj, owner, owner_property)`.

        Parameters
        ----------
        swan_obj : Union[swan.SwanItem, Enum]
            Visited Swan object.
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object.
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object.
        """
        try:
            class_name = swan_obj.__class__.__name__
            fn = getattr(self, f"visit_{class_name}")
        except AttributeError:
            msg = f"{self.__class__.__name__}: no visitor for {type(swan_obj)}"
            if owner:
                msg += f" owned by {type(owner)}"
            if owner_property:
                msg += f" in property '{owner_property}'"
            raise AttributeError(msg)
        fn(swan_obj, owner, owner_property)

    # Following methods should be overridden

    def visit_builtin(
        self,
        object: Any,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default visitor for builtin value of type `str`, `bool`, `int` or `float`."""
        pass

    def visit_SwanItem(
        self,
        swan_obj: swan.SwanItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default visitor method for every Swan construct."""
        pass

    def visit_HasPragma(
        self,
        swan_obj: swan.HasPragma,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default visitor method for classes with pragmas."""
        self.visit_SwanItem(swan_obj, owner, owner_property)
        for pragma in swan_obj.pragmas:
            self.visit_Pragma(pragma, swan_obj, "pragmas")

    def visit_Pragma(
        self,
        swan_obj: swan.Pragma,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Pragma visitor method."""
        pass

    # Classes visitors

    def visit_ActivateClock(
        self,
        swan_obj: swan.ActivateClock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateClock visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        self._visit(
            swan_obj.clock,
            swan_obj,
            "clock",
        )

    def visit_ActivateEvery(
        self,
        swan_obj: swan.ActivateEvery,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateEvery visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        self._visit(
            swan_obj.condition,
            swan_obj,
            "condition",
        )
        self.visit_builtin(
            swan_obj.is_last,
            swan_obj,
            "is_last",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_ActivateIf(
        self,
        swan_obj: swan.ActivateIf,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateIf visitor method."""
        # Visit base class(es)
        self.visit_DefByCase(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.if_activation,
            swan_obj,
            "if_activation",
        )

    def visit_ActivateIfBlock(
        self,
        swan_obj: swan.ActivateIfBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateIfBlock visitor method."""
        # Visit base class(es)
        self.visit_DefByCaseBlockBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ActivateWhen(
        self,
        swan_obj: swan.ActivateWhen,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateWhen visitor method."""
        # Visit base class(es)
        self.visit_DefByCase(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.condition,
            swan_obj,
            "condition",
        )
        for item in swan_obj.branches:
            self._visit(
                item,
                swan_obj,
                "branches",
            )

    def visit_ActivateWhenBlock(
        self,
        swan_obj: swan.ActivateWhenBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateWhenBlock visitor method."""
        # Visit base class(es)
        self.visit_DefByCaseBlockBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ActivateWhenBranch(
        self,
        swan_obj: swan.ActivateWhenBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ActivateWhenBranch visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.pattern,
            swan_obj,
            "pattern",
        )
        self._visit(
            swan_obj.data_def,
            swan_obj,
            "data_def",
        )  # isinstance(swan_obj.data_def, [swan.Equation, swan.Scope])

    def visit_AnonymousOperatorWithDataDefinition(
        self,
        swan_obj: swan.AnonymousOperatorWithDataDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default AnonymousOperatorWithDataDefinition visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.is_node,
            swan_obj,
            "is_node",
        )
        for item in swan_obj.inputs:
            self._visit(
                item,
                swan_obj,
                "inputs",
            )
        for item in swan_obj.outputs:
            self._visit(
                item,
                swan_obj,
                "outputs",
            )
        self._visit(
            swan_obj.data_def,
            swan_obj,
            "data_def",
        )  # isinstance(swan_obj.data_def, [swan.Equation, swan.Scope])

    def visit_AnonymousOperatorWithExpression(
        self,
        swan_obj: swan.AnonymousOperatorWithExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default AnonymousOperatorWithExpression visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.is_node,
            swan_obj,
            "is_node",
        )
        for item in swan_obj.params:
            self._visit(
                item,
                swan_obj,
                "params",
            )
        for item in swan_obj.sections:
            self._visit(
                item,
                swan_obj,
                "sections",
            )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_ArrayConcatExpr(
        self,
        swan_obj: swan.ArrayConcatExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ArrayConcatExpr visitor method."""
        # Visit base class(es)
        self.visit_BinaryExpr(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ArrayConstructor(
        self,
        swan_obj: swan.ArrayConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ArrayConstructor visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.group,
            swan_obj,
            "group",
        )

    def visit_ArrayProjection(
        self,
        swan_obj: swan.ArrayProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ArrayProjection visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.index,
            swan_obj,
            "index",
        )

    def visit_ArrayRepetition(
        self,
        swan_obj: swan.ArrayRepetition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ArrayRepetition visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.size,
            swan_obj,
            "size",
        )

    def visit_ArrayTypeExpression(
        self,
        swan_obj: swan.ArrayTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ArrayTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_TypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )
        self._visit(
            swan_obj.size,
            swan_obj,
            "size",
        )

    def visit_AssertSection(
        self,
        swan_obj: swan.AssertSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default AssertSection visitor method."""
        # Visit base class(es)
        self.visit_AssertionBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Assertion(
        self,
        swan_obj: swan.Assertion,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Assertion visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.luid,
            swan_obj,
            "luid",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_AssertionBase(
        self,
        swan_obj: swan.AssertionBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default AssertionBase visitor method."""
        # Visit base class(es)
        self.visit_ScopeSection(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.assertions:
            self._visit(
                item,
                swan_obj,
                "assertions",
            )

    def visit_AssumeSection(
        self,
        swan_obj: swan.AssumeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default AssumeSection visitor method."""
        # Visit base class(es)
        self.visit_AssertionBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Bar(
        self,
        swan_obj: swan.Bar,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Bar visitor method."""
        # Visit base class(es)
        self.visit_GroupBlock(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_BinaryExpr(
        self,
        swan_obj: swan.BinaryExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default BinaryExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        self._visit(
            swan_obj.left,
            swan_obj,
            "left",
        )
        self._visit(
            swan_obj.right,
            swan_obj,
            "right",
        )

    def visit_BinaryOp(
        self,
        swan_obj: swan.BinaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """BinaryOp visitor function. Should be overridden."""
        # Enum values:
        # Plus
        # Minus
        # Mult
        # Slash
        # Mod
        # Equal
        # Diff
        # Lt
        # Gt
        # Leq
        # Geq
        # And
        # Or
        # Xor
        # Land
        # Lor
        # Lxor
        # Lsl
        # Lsr
        # Arrow
        # Pre
        # Concat
        pass

    def visit_Block(
        self,
        swan_obj: swan.Block,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Block visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.instance,
            swan_obj,
            "instance",
        )  # isinstance(swan_obj.instance, [swan.OperatorInstance, swan.OperatorExpression, swan.ProtectedItem])

    def visit_BoolPattern(
        self,
        swan_obj: swan.BoolPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default BoolPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )

    def visit_BoolType(
        self,
        swan_obj: swan.BoolType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default BoolType visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_BooleanLiteral(
        self,
        swan_obj: swan.BooleanLiteral,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default BooleanLiteral visitor method."""
        # Visit base class(es)
        self.visit_Literal(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ByName(
        self,
        swan_obj: swan.ByName,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ByName visitor method."""
        # Visit base class(es)
        self.visit_GroupBlock(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ByPos(
        self,
        swan_obj: swan.ByPos,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ByPos visitor method."""
        # Visit base class(es)
        self.visit_GroupBlock(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_CaseBranch(
        self,
        swan_obj: swan.CaseBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default CaseBranch visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.pattern,
            swan_obj,
            "pattern",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_CaseExpr(
        self,
        swan_obj: swan.CaseExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default CaseExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        for item in swan_obj.branches:
            self._visit(
                item,
                swan_obj,
                "branches",
            )

    def visit_CharLiteral(
        self,
        swan_obj: swan.CharLiteral,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default CharLiteral visitor method."""
        # Visit base class(es)
        self.visit_Literal(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_CharPattern(
        self,
        swan_obj: swan.CharPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default CharPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )

    def visit_CharType(
        self,
        swan_obj: swan.CharType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default CharType visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ClockExpr(
        self,
        swan_obj: swan.ClockExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ClockExpr visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )
        self.visit_builtin(
            swan_obj.is_not,
            swan_obj,
            "is_not",
        )
        if swan_obj.pattern is not None:
            self._visit(
                swan_obj.pattern,
                swan_obj,
                "pattern",
            )

    def visit_Concat(
        self,
        swan_obj: swan.Concat,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Concat visitor method."""
        # Visit base class(es)
        self.visit_GroupBlock(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.group,
            swan_obj,
            "group",
        )

    def visit_Connection(
        self,
        swan_obj: swan.Connection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Connection visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.port is not None:
            self._visit(
                swan_obj.port,
                swan_obj,
                "port",
            )
        if swan_obj.adaptation is not None:
            self._visit(
                swan_obj.adaptation,
                swan_obj,
                "adaptation",
            )

    def visit_ConstDecl(
        self,
        swan_obj: swan.ConstDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ConstDecl visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.type is not None:
            self._visit(
                swan_obj.type,
                swan_obj,
                "type",
            )
        if swan_obj.value is not None:
            self._visit(
                swan_obj.value,
                swan_obj,
                "value",
            )

    def visit_ConstDeclarations(
        self,
        swan_obj: swan.ConstDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ConstDeclarations visitor method."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.constants:
            self._visit(
                item,
                swan_obj,
                "constants",
            )

    def visit_DataSource(
        self,
        swan_obj: swan.DataSource,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default DataSource visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )

    def visit_Declaration(
        self,
        swan_obj: swan.Declaration,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Declaration visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )

    def visit_DefBlock(
        self,
        swan_obj: swan.DefBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default DefBlock visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.lhs,
            swan_obj,
            "lhs",
        )  # isinstance(swan_obj.lhs, [swan.EquationLHS, swan.ProtectedItem])

    def visit_DefByCase(
        self,
        swan_obj: swan.DefByCase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default DefByCase visitor method."""
        # Visit base class(es)
        self.visit_Equation(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.lhs is not None:
            self._visit(
                swan_obj.lhs,
                swan_obj,
                "lhs",
            )
        if swan_obj.lunum is not None:
            self._visit(
                swan_obj.lunum,
                swan_obj,
                "lunum",
            )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )

    def visit_DefByCaseBlockBase(
        self,
        swan_obj: swan.DefByCaseBlockBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default DefByCaseBlockBase visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.def_by_case,
            swan_obj,
            "def_by_case",
        )

    def visit_DefaultPattern(
        self,
        swan_obj: swan.DefaultPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default DefaultPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Diagram(
        self,
        swan_obj: swan.Diagram,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Diagram visitor method."""
        # Visit base class(es)
        self.visit_ScopeSection(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )
        for item in swan_obj.objects:
            self._visit(
                item,
                swan_obj,
                "objects",
            )

    def visit_DiagramObject(
        self,
        swan_obj: swan.DiagramObject,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default DiagramObject visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.lunum is not None:
            self._visit(
                swan_obj.lunum,
                swan_obj,
                "lunum",
            )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )
        if swan_obj.locals is not None:
            for item in swan_obj.locals:
                self._visit(
                    item,
                    swan_obj,
                    "locals",
                )

    def visit_EmissionBody(
        self,
        swan_obj: swan.EmissionBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default EmissionBody visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.flows:
            self._visit(
                item,
                swan_obj,
                "flows",
            )
        if swan_obj.condition is not None:
            self._visit(
                swan_obj.condition,
                swan_obj,
                "condition",
            )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )

    def visit_EmitSection(
        self,
        swan_obj: swan.EmitSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default EmitSection visitor method."""
        # Visit base class(es)
        self.visit_ScopeSection(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.emissions:
            self._visit(
                item,
                swan_obj,
                "emissions",
            )

    def visit_EnumTag(
        self,
        swan_obj: swan.EnumTag,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default EnumTag visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )

    def visit_EnumTypeDefinition(
        self,
        swan_obj: swan.EnumTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default EnumTypeDefinition visitor method."""
        # Visit base class(es)
        self.visit_TypeDefinition(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.tags:
            self._visit(
                item,
                swan_obj,
                "tags",
            )

    def visit_Equation(
        self,
        swan_obj: swan.Equation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Equation visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_EquationLHS(
        self,
        swan_obj: swan.EquationLHS,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default EquationLHS visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.lhs_items:
            self._visit(
                item,
                swan_obj,
                "lhs_items",
            )
        self.visit_builtin(
            swan_obj.is_partial_lhs,
            swan_obj,
            "is_partial_lhs",
        )

    def visit_ExprBlock(
        self,
        swan_obj: swan.ExprBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ExprBlock visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_ExprEquation(
        self,
        swan_obj: swan.ExprEquation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ExprEquation visitor method."""
        # Visit base class(es)
        self.visit_Equation(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.lhs,
            swan_obj,
            "lhs",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )

    def visit_ExprTypeDefinition(
        self,
        swan_obj: swan.ExprTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ExprTypeDefinition visitor method."""
        # Visit base class(es)
        self.visit_TypeDefinition(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_Expression(
        self,
        swan_obj: swan.Expression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Expression visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_FlattenOperator(
        self,
        swan_obj: swan.FlattenOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default FlattenOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorInstance(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Float32Type(
        self,
        swan_obj: swan.Float32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Float32Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Float64Type(
        self,
        swan_obj: swan.Float64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Float64Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_FloatLiteral(
        self,
        swan_obj: swan.FloatLiteral,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default FloatLiteral visitor method."""
        # Visit base class(es)
        self.visit_Literal(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Fork(
        self,
        swan_obj: swan.Fork,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Fork visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.transitions:
            self._visit(
                item,
                swan_obj,
                "transitions",
            )

    def visit_Forward(
        self,
        swan_obj: swan.Forward,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Forward visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.restart is not None:
            self.visit_builtin(
                swan_obj.restart,
                swan_obj,
                "restart",
            )
        for item in swan_obj.dimensions:
            self._visit(
                item,
                swan_obj,
                "dimensions",
            )
        self._visit(
            swan_obj.body,
            swan_obj,
            "body",
        )
        for item in swan_obj.returns:
            self._visit(
                item,
                swan_obj,
                "returns",
            )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )

    def visit_ForwardArrayClause(
        self,
        swan_obj: swan.ForwardArrayClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardArrayClause visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.return_clause,
            swan_obj,
            "return_clause",
        )  # isinstance(swan_obj.return_clause, [swan.ForwardItemClause, swan.ForwardArrayClause])

    def visit_ForwardBody(
        self,
        swan_obj: swan.ForwardBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardBody visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.body:
            self._visit(
                item,
                swan_obj,
                "body",
            )
        if swan_obj.unless_expr is not None:
            self._visit(
                swan_obj.unless_expr,
                swan_obj,
                "unless_expr",
            )
        if swan_obj.until_expr is not None:
            self._visit(
                swan_obj.until_expr,
                swan_obj,
                "until_expr",
            )

    def visit_ForwardDim(
        self,
        swan_obj: swan.ForwardDim,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardDim visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.expr is not None:
            self._visit(
                swan_obj.expr,
                swan_obj,
                "expr",
            )
        if swan_obj.dim_id is not None:
            self._visit(
                swan_obj.dim_id,
                swan_obj,
                "dim_id",
            )
        if swan_obj.elems is not None:
            for item in swan_obj.elems:
                self._visit(
                    item,
                    swan_obj,
                    "elems",
                )
        if swan_obj.protected is not None:
            self.visit_builtin(
                swan_obj.protected,
                swan_obj,
                "protected",
            )

    def visit_ForwardElement(
        self,
        swan_obj: swan.ForwardElement,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardElement visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.lhs,
            swan_obj,
            "lhs",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_ForwardItemClause(
        self,
        swan_obj: swan.ForwardItemClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardItemClause visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )
        if swan_obj.last_default is not None:
            self._visit(
                swan_obj.last_default,
                swan_obj,
                "last_default",
            )

    def visit_ForwardLHS(
        self,
        swan_obj: swan.ForwardLHS,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardLHS visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.lhs,
            swan_obj,
            "lhs",
        )  # isinstance(swan_obj.lhs, [swan.Identifier, swan.ForwardLHS])

    def visit_ForwardLastDefault(
        self,
        swan_obj: swan.ForwardLastDefault,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardLastDefault visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.last is not None:
            self._visit(
                swan_obj.last,
                swan_obj,
                "last",
            )
        if swan_obj.default is not None:
            self._visit(
                swan_obj.default,
                swan_obj,
                "default",
            )
        if swan_obj.shared is not None:
            self._visit(
                swan_obj.shared,
                swan_obj,
                "shared",
            )

    def visit_ForwardReturnArrayClause(
        self,
        swan_obj: swan.ForwardReturnArrayClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardReturnArrayClause visitor method."""
        # Visit base class(es)
        self.visit_ForwardReturnItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.array_clause,
            swan_obj,
            "array_clause",
        )
        if swan_obj.return_id is not None:
            self._visit(
                swan_obj.return_id,
                swan_obj,
                "return_id",
            )

    def visit_ForwardReturnItem(
        self,
        swan_obj: swan.ForwardReturnItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardReturnItem visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ForwardReturnItemClause(
        self,
        swan_obj: swan.ForwardReturnItemClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ForwardReturnItemClause visitor method."""
        # Visit base class(es)
        self.visit_ForwardReturnItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.item_clause,
            swan_obj,
            "item_clause",
        )

    def visit_FunctionalUpdate(
        self,
        swan_obj: swan.FunctionalUpdate,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default FunctionalUpdate visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self.visit_builtin(
            swan_obj.is_starred,
            swan_obj,
            "is_starred",
        )
        for item in swan_obj.modifiers:
            self._visit(
                item,
                swan_obj,
                "modifiers",
            )

    def visit_GlobalDeclaration(
        self,
        swan_obj: swan.GlobalDeclaration,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GlobalDeclaration visitor method."""
        # Visit base class(es)
        self.visit_ModuleItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Group(
        self,
        swan_obj: swan.Group,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Group visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.items:
            self._visit(
                item,
                swan_obj,
                "items",
            )

    def visit_GroupAdaptation(
        self,
        swan_obj: swan.GroupAdaptation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupAdaptation visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.renamings:
            self._visit(
                item,
                swan_obj,
                "renamings",
            )

    def visit_GroupBlock(
        self,
        swan_obj: swan.GroupBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupBlock visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_GroupConstructor(
        self,
        swan_obj: swan.GroupConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupConstructor visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.group,
            swan_obj,
            "group",
        )

    def visit_GroupDecl(
        self,
        swan_obj: swan.GroupDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupDecl visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_GroupDeclarations(
        self,
        swan_obj: swan.GroupDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupDeclarations visitor method."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.groups:
            self._visit(
                item,
                swan_obj,
                "groups",
            )

    def visit_GroupItem(
        self,
        swan_obj: swan.GroupItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupItem visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        if swan_obj.label is not None:
            self._visit(
                swan_obj.label,
                swan_obj,
                "label",
            )

    def visit_GroupNormalize(
        self,
        swan_obj: swan.GroupNormalize,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupNormalize visitor method."""
        # Visit base class(es)
        self.visit_GroupBlock(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_GroupOperation(
        self,
        swan_obj: swan.GroupOperation,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """GroupOperation visitor function. Should be overridden."""
        # Enum values:
        # NoOp
        # ByName
        # ByPos
        # Normalize
        pass

    def visit_GroupProjection(
        self,
        swan_obj: swan.GroupProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupProjection visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.adaptation,
            swan_obj,
            "adaptation",
        )

    def visit_GroupRenaming(
        self,
        swan_obj: swan.GroupRenaming,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupRenaming visitor method."""
        # Visit base class(es)
        self.visit_GroupRenamingBase(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.source,
            swan_obj,
            "source",
        )  # isinstance(swan_obj.source, [swan.Identifier, swan.Literal])
        if swan_obj.renaming is not None:
            self._visit(
                swan_obj.renaming,
                swan_obj,
                "renaming",
            )
        self.visit_builtin(
            swan_obj.is_shortcut,
            swan_obj,
            "is_shortcut",
        )

    def visit_GroupRenamingBase(
        self,
        swan_obj: swan.GroupRenamingBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupRenamingBase visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_GroupTypeExpression(
        self,
        swan_obj: swan.GroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_GroupTypeExpressionList(
        self,
        swan_obj: swan.GroupTypeExpressionList,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GroupTypeExpressionList visitor method."""
        # Visit base class(es)
        self.visit_GroupTypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.positional:
            self._visit(
                item,
                swan_obj,
                "positional",
            )
        for item in swan_obj.named:
            self._visit(
                item,
                swan_obj,
                "named",
            )

    def visit_GuaranteeSection(
        self,
        swan_obj: swan.GuaranteeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default GuaranteeSection visitor method."""
        # Visit base class(es)
        self.visit_AssertionBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Identifier(
        self,
        swan_obj: swan.Identifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Identifier visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )
        self.visit_builtin(
            swan_obj.comment,
            swan_obj,
            "comment",
        )
        self.visit_builtin(
            swan_obj.is_name,
            swan_obj,
            "is_name",
        )

    def visit_IfActivation(
        self,
        swan_obj: swan.IfActivation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IfActivation visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.branches:
            self._visit(
                item,
                swan_obj,
                "branches",
            )

    def visit_IfActivationBranch(
        self,
        swan_obj: swan.IfActivationBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IfActivationBranch visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.condition is not None:
            self._visit(
                swan_obj.condition,
                swan_obj,
                "condition",
            )
        self._visit(
            swan_obj.branch,
            swan_obj,
            "branch",
        )

    def visit_IfteBranch(
        self,
        swan_obj: swan.IfteBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IfteBranch visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_IfteDataDef(
        self,
        swan_obj: swan.IfteDataDef,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IfteDataDef visitor method."""
        # Visit base class(es)
        self.visit_IfteBranch(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.data_def,
            swan_obj,
            "data_def",
        )  # isinstance(swan_obj.data_def, [swan.Equation, swan.Scope])

    def visit_IfteExpr(
        self,
        swan_obj: swan.IfteExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IfteExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.cond_expr,
            swan_obj,
            "cond_expr",
        )
        self._visit(
            swan_obj.then_expr,
            swan_obj,
            "then_expr",
        )
        self._visit(
            swan_obj.else_expr,
            swan_obj,
            "else_expr",
        )

    def visit_IfteIfActivation(
        self,
        swan_obj: swan.IfteIfActivation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IfteIfActivation visitor method."""
        # Visit base class(es)
        self.visit_IfteBranch(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.if_activation,
            swan_obj,
            "if_activation",
        )

    def visit_InitialValueExpr(
        self,
        swan_obj: swan.InitialValueExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default InitialValueExpr visitor method."""
        # Visit base class(es)
        self.visit_BinaryExpr(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Int16Type(
        self,
        swan_obj: swan.Int16Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Int16Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Int32Type(
        self,
        swan_obj: swan.Int32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Int32Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Int64Type(
        self,
        swan_obj: swan.Int64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Int64Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Int8Type(
        self,
        swan_obj: swan.Int8Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Int8Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_IntPattern(
        self,
        swan_obj: swan.IntPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IntPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )
        self.visit_builtin(
            swan_obj.is_minus,
            swan_obj,
            "is_minus",
        )

    def visit_IntegerLiteral(
        self,
        swan_obj: swan.IntegerLiteral,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default IntegerLiteral visitor method."""
        # Visit base class(es)
        self.visit_Literal(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Iterator(
        self,
        swan_obj: swan.Iterator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Iterator visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.kind,
            swan_obj,
            "kind",
        )
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )  # isinstance(swan_obj.operator, [swan.OperatorInstance, swan.ProtectedOpExpr])

    def visit_IteratorKind(
        self,
        swan_obj: swan.IteratorKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """IteratorKind visitor function. Should be overridden."""
        # Enum values:
        # Map
        # Fold
        # Mapfold
        # Mapi
        # Foldi
        # Mapfoldi
        pass

    def visit_LHSItem(
        self,
        swan_obj: swan.LHSItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default LHSItem visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.id is not None:
            self._visit(
                swan_obj.id,
                swan_obj,
                "id",
            )

    def visit_LabelOrIndex(
        self,
        swan_obj: swan.LabelOrIndex,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default LabelOrIndex visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.value,
            swan_obj,
            "value",
        )  # isinstance(swan_obj.value, [swan.Identifier, swan.Expression])

    def visit_LastExpr(
        self,
        swan_obj: swan.LastExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default LastExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )

    def visit_LetSection(
        self,
        swan_obj: swan.LetSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default LetSection visitor method."""
        # Visit base class(es)
        self.visit_ScopeSection(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.equations:
            self._visit(
                item,
                swan_obj,
                "equations",
            )

    def visit_Literal(
        self,
        swan_obj: swan.Literal,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Literal visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )

    def visit_Luid(
        self,
        swan_obj: swan.Luid,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Luid visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )

    def visit_Lunum(
        self,
        swan_obj: swan.Lunum,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Lunum visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.value,
            swan_obj,
            "value",
        )

    def visit_Merge(
        self,
        swan_obj: swan.Merge,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Merge visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.params:
            self._visit(
                item,
                swan_obj,
                "params",
            )

    def visit_Modifier(
        self,
        swan_obj: swan.Modifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Modifier visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if isinstance(swan_obj.modifier, list):
            for item in swan_obj.modifier:
                self._visit(
                    item,
                    swan_obj,
                    "modifier",
                )
        else:  # SwanVisitor._is_builtin(swan_obj.modifier)
            self.visit_builtin(
                swan_obj.modifier,
                swan_obj,
                "modifier",
            )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_Module(
        self,
        swan_obj: swan.Module,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Module visitor method."""
        # Visit base class(es)
        self.visit_ModuleBase(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.name,
            swan_obj,
            "name",
        )
        if swan_obj.use_directives is not None:
            for item in swan_obj.use_directives:
                self._visit(
                    item,
                    swan_obj,
                    "use_directives",
                )
        if swan_obj.declarations is not None:
            for item in swan_obj.declarations:
                self._visit(
                    item,
                    swan_obj,
                    "declarations",
                )

    def visit_ModuleBase(
        self,
        swan_obj: swan.ModuleBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ModuleBase visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ModuleBody(
        self,
        swan_obj: swan.ModuleBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ModuleBody visitor method."""
        # Visit base class(es)
        self.visit_Module(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ModuleInterface(
        self,
        swan_obj: swan.ModuleInterface,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ModuleInterface visitor method."""
        # Visit base class(es)
        self.visit_Module(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ModuleItem(
        self,
        swan_obj: swan.ModuleItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ModuleItem visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_NAryOperator(
        self,
        swan_obj: swan.NAryOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default NAryOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )

    def visit_NamedGroupTypeExpression(
        self,
        swan_obj: swan.NamedGroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default NamedGroupTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_GroupTypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.label,
            swan_obj,
            "label",
        )
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_NamedInstance(
        self,
        swan_obj: swan.NamedInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default NamedInstance visitor method."""
        # Visit base class(es)
        self.visit_OperatorInstance(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.path_id,
            swan_obj,
            "path_id",
        )

    def visit_NaryOp(
        self,
        swan_obj: swan.NaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """NaryOp visitor function. Should be overridden."""
        # Enum values:
        # Plus
        # Mult
        # Land
        # Lor
        # And
        # Or
        # Xor
        # Lxor
        # Concat
        pass

    def visit_NumericCast(
        self,
        swan_obj: swan.NumericCast,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default NumericCast visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_NumericKind(
        self,
        swan_obj: swan.NumericKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """NumericKind visitor function. Should be overridden."""
        # Enum values:
        # Numeric
        # Integer
        # Signed
        # Unsigned
        # Float
        pass

    def visit_OperatorDeclaration(
        self,
        swan_obj: swan.OperatorDeclaration,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorDeclaration visitor method."""
        # Visit base class(es)
        self.visit_OperatorDeclarationDefinitionBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_OperatorDeclarationDefinitionBase(
        self,
        swan_obj: swan.OperatorDeclarationDefinitionBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorDeclarationDefinitionBase visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ModuleItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.is_inlined,
            swan_obj,
            "is_inlined",
        )
        self.visit_builtin(
            swan_obj.is_node,
            swan_obj,
            "is_node",
        )
        for item in swan_obj.inputs:
            self._visit(
                item,
                swan_obj,
                "inputs",
            )
        for item in swan_obj.outputs:
            self._visit(
                item,
                swan_obj,
                "outputs",
            )
        if swan_obj.size_parameters is not None:
            for item in swan_obj.size_parameters:
                self._visit(
                    item,
                    swan_obj,
                    "size_parameters",
                )
        if swan_obj.type_constraints is not None:
            for item in swan_obj.type_constraints:
                self._visit(
                    item,
                    swan_obj,
                    "type_constraints",
                )
        if swan_obj.specialization is not None:
            self._visit(
                swan_obj.specialization,
                swan_obj,
                "specialization",
            )

    def visit_OperatorDefinition(
        self,
        swan_obj: swan.OperatorDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorDefinition visitor method."""
        # Visit base class(es)
        self.visit_OperatorDeclarationDefinitionBase(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.body is not None:
            self._visit(
                swan_obj.body,
                swan_obj,
                "body",
            )  # isinstance(swan_obj.body, [swan.Scope, swan.Equation])

    def visit_OperatorExpression(
        self,
        swan_obj: swan.OperatorExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorExpression visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_OperatorExpressionInstance(
        self,
        swan_obj: swan.OperatorExpressionInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorExpressionInstance visitor method."""
        # Visit base class(es)
        self.visit_OperatorInstance(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.op_expr,
            swan_obj,
            "op_expr",
        )

    def visit_OperatorInstance(
        self,
        swan_obj: swan.OperatorInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorInstance visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.sizes:
            self._visit(
                item,
                swan_obj,
                "sizes",
            )

    def visit_OperatorInstanceApplication(
        self,
        swan_obj: swan.OperatorInstanceApplication,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OperatorInstanceApplication visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        self._visit(
            swan_obj.params,
            swan_obj,
            "params",
        )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )

    def visit_OptGroupItem(
        self,
        swan_obj: swan.OptGroupItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default OptGroupItem visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.item is not None:
            self._visit(
                swan_obj.item,
                swan_obj,
                "item",
            )

    def visit_Oracle(
        self,
        swan_obj: swan.Oracle,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Oracle visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )

    def visit_PackOperator(
        self,
        swan_obj: swan.PackOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PackOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorInstance(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_PartialOperator(
        self,
        swan_obj: swan.PartialOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PartialOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        for item in swan_obj.partial_group:
            self._visit(
                item,
                swan_obj,
                "partial_group",
            )

    def visit_PathIdExpr(
        self,
        swan_obj: swan.PathIdExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PathIdExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.path_id,
            swan_obj,
            "path_id",
        )

    def visit_PathIdPattern(
        self,
        swan_obj: swan.PathIdPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PathIdPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.path_id,
            swan_obj,
            "path_id",
        )

    def visit_PathIdentifier(
        self,
        swan_obj: swan.PathIdentifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PathIdentifier visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if isinstance(swan_obj.path_id, list):
            for item in swan_obj.path_id:
                self._visit(
                    item,
                    swan_obj,
                    "path_id",
                )
        else:  # SwanVisitor._is_builtin(swan_obj.path_id)
            self.visit_builtin(
                swan_obj.path_id,
                swan_obj,
                "path_id",
            )

    def visit_Pattern(
        self,
        swan_obj: swan.Pattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Pattern visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_PortExpr(
        self,
        swan_obj: swan.PortExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PortExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.lunum is not None:
            self._visit(
                swan_obj.lunum,
                swan_obj,
                "lunum",
            )
        if swan_obj.luid is not None:
            self._visit(
                swan_obj.luid,
                swan_obj,
                "luid",
            )
        self.visit_builtin(
            swan_obj.is_self,
            swan_obj,
            "is_self",
        )

    def visit_PragmaKey(
        self,
        swan_obj: swan.PragmaKey,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """PragmaKey visitor function. Should be overridden."""
        # Enum values:
        # SWT
        # CG
        # DIAGRAM
        # REQUIREMENT
        # DOC
        pass

    def visit_PreExpr(
        self,
        swan_obj: swan.PreExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PreExpr visitor method."""
        # Visit base class(es)
        self.visit_UnaryExpr(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_PreWithInitialValueExpr(
        self,
        swan_obj: swan.PreWithInitialValueExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PreWithInitialValueExpr visitor method."""
        # Visit base class(es)
        self.visit_BinaryExpr(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_PredefinedType(
        self,
        swan_obj: swan.PredefinedType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default PredefinedType visitor method."""
        # Visit base class(es)
        self.visit_TypeExpression(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProjectionWithDefault(
        self,
        swan_obj: swan.ProjectionWithDefault,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProjectionWithDefault visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        for item in swan_obj.indices:
            self._visit(
                item,
                swan_obj,
                "indices",
            )
        self._visit(
            swan_obj.default,
            swan_obj,
            "default",
        )

    def visit_ProtectedDecl(
        self,
        swan_obj: swan.ProtectedDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedDecl visitor method."""
        # Visit base class(es)
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_GlobalDeclaration(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedExpr(
        self,
        swan_obj: swan.ProtectedExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedForwardReturnItem(
        self,
        swan_obj: swan.ProtectedForwardReturnItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedForwardReturnItem visitor method."""
        # Visit base class(es)
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ForwardReturnItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedGroupRenaming(
        self,
        swan_obj: swan.ProtectedGroupRenaming,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedGroupRenaming visitor method."""
        # Visit base class(es)
        self.visit_GroupRenamingBase(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedItem(
        self,
        swan_obj: swan.ProtectedItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedItem visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.data,
            swan_obj,
            "data",
        )
        self.visit_builtin(
            swan_obj.markup,
            swan_obj,
            "markup",
        )

    def visit_ProtectedOpExpr(
        self,
        swan_obj: swan.ProtectedOpExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedOpExpr visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedPattern(
        self,
        swan_obj: swan.ProtectedPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedSection(
        self,
        swan_obj: swan.ProtectedSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedSection visitor method."""
        # Visit base class(es)
        self.visit_ScopeSection(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedTypeExpression(
        self,
        swan_obj: swan.ProtectedTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_TypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_ProtectedVariable(
        self,
        swan_obj: swan.ProtectedVariable,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ProtectedVariable visitor method."""
        # Visit base class(es)
        self.visit_Variable(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ProtectedItem(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_RestartOperator(
        self,
        swan_obj: swan.RestartOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default RestartOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        self._visit(
            swan_obj.condition,
            swan_obj,
            "condition",
        )

    def visit_ReverseOperator(
        self,
        swan_obj: swan.ReverseOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ReverseOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorInstance(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Scope(
        self,
        swan_obj: swan.Scope,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Scope visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.sections is not None:
            for item in swan_obj.sections:
                self._visit(
                    item,
                    swan_obj,
                    "sections",
                )

    def visit_ScopeSection(
        self,
        swan_obj: swan.ScopeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default ScopeSection visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_SectionObject(
        self,
        swan_obj: swan.SectionObject,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SectionObject visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.section,
            swan_obj,
            "section",
        )

    def visit_SensorDecl(
        self,
        swan_obj: swan.SensorDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SensorDecl visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_SensorDeclarations(
        self,
        swan_obj: swan.SensorDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SensorDeclarations visitor method."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.sensors:
            self._visit(
                item,
                swan_obj,
                "sensors",
            )

    def visit_SetSensorBlock(
        self,
        swan_obj: swan.SetSensorBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SetSensorBlock visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.sensor,
            swan_obj,
            "sensor",
        )  # isinstance(swan_obj.sensor, [swan.PathIdentifier, swan.ProtectedItem])

    def visit_SetSensorEquation(
        self,
        swan_obj: swan.SetSensorEquation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SetSensorEquation visitor method."""
        # Visit base class(es)
        self.visit_Equation(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.sensor,
            swan_obj,
            "sensor",
        )
        self._visit(
            swan_obj.value,
            swan_obj,
            "value",
        )

    def visit_SizeParameter(
        self,
        swan_obj: swan.SizeParameter,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SizeParameter visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_SizedTypeExpression(
        self,
        swan_obj: swan.SizedTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default SizedTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_TypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.size,
            swan_obj,
            "size",
        )
        self.visit_builtin(
            swan_obj.is_signed,
            swan_obj,
            "is_signed",
        )

    def visit_Slice(
        self,
        swan_obj: swan.Slice,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Slice visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.start,
            swan_obj,
            "start",
        )
        self._visit(
            swan_obj.end,
            swan_obj,
            "end",
        )

    def visit_State(
        self,
        swan_obj: swan.State,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default State visitor method."""
        # Visit base class(es)
        self.visit_StateMachineItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.id is not None:
            self._visit(
                swan_obj.id,
                swan_obj,
                "id",
            )
        if swan_obj.lunum is not None:
            self._visit(
                swan_obj.lunum,
                swan_obj,
                "lunum",
            )
        if swan_obj.in_state_strong_transition_decls is not None:
            for item in swan_obj.in_state_strong_transition_decls:
                self._visit(
                    item,
                    swan_obj,
                    "in_state_strong_transition_decls",
                )
        if swan_obj.body is not None:
            self._visit(
                swan_obj.body,
                swan_obj,
                "body",
            )
        if swan_obj.in_state_weak_transition_decls is not None:
            for item in swan_obj.in_state_weak_transition_decls:
                self._visit(
                    item,
                    swan_obj,
                    "in_state_weak_transition_decls",
                )
        self.visit_builtin(
            swan_obj.is_initial,
            swan_obj,
            "is_initial",
        )

    def visit_StateMachine(
        self,
        swan_obj: swan.StateMachine,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StateMachine visitor method."""
        # Visit base class(es)
        self.visit_DefByCase(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.items is not None:
            for item in swan_obj.items:
                self._visit(
                    item,
                    swan_obj,
                    "items",
                )

    def visit_StateMachineBlock(
        self,
        swan_obj: swan.StateMachineBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StateMachineBlock visitor method."""
        # Visit base class(es)
        self.visit_DefByCaseBlockBase(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_StateMachineItem(
        self,
        swan_obj: swan.StateMachineItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StateMachineItem visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_StateRef(
        self,
        swan_obj: swan.StateRef,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StateRef visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.id is not None:
            self._visit(
                swan_obj.id,
                swan_obj,
                "id",
            )
        if swan_obj.lunum is not None:
            self._visit(
                swan_obj.lunum,
                swan_obj,
                "lunum",
            )

    def visit_StructConstructor(
        self,
        swan_obj: swan.StructConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StructConstructor visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.group,
            swan_obj,
            "group",
        )
        if swan_obj.type is not None:
            self._visit(
                swan_obj.type,
                swan_obj,
                "type",
            )

    def visit_StructDestructor(
        self,
        swan_obj: swan.StructDestructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StructDestructor visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.group_id,
            swan_obj,
            "group_id",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_StructField(
        self,
        swan_obj: swan.StructField,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StructField visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_StructProjection(
        self,
        swan_obj: swan.StructProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StructProjection visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.label,
            swan_obj,
            "label",
        )

    def visit_StructTypeDefinition(
        self,
        swan_obj: swan.StructTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default StructTypeDefinition visitor method."""
        # Visit base class(es)
        self.visit_TypeDefinition(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.fields:
            self._visit(
                item,
                swan_obj,
                "fields",
            )

    def visit_TestHarness(
        self,
        swan_obj: swan.TestHarness,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TestHarness visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ModuleItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.body is not None:
            self._visit(
                swan_obj.body,
                swan_obj,
                "body",
            )  # isinstance(swan_obj.body, [swan.Scope, swan.Equation])

    def visit_TestModule(
        self,
        swan_obj: swan.TestModule,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TestModule visitor method."""
        # Visit base class(es)
        self.visit_Module(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Transition(
        self,
        swan_obj: swan.Transition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Transition visitor method."""
        # Visit base class(es)
        self.visit_StateMachineItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.priority is not None:
            self._visit(
                swan_obj.priority,
                swan_obj,
                "priority",
            )
        self.visit_builtin(
            swan_obj.is_strong,
            swan_obj,
            "is_strong",
        )
        if swan_obj.guard is not None:
            self._visit(
                swan_obj.guard,
                swan_obj,
                "guard",
            )
        if swan_obj.action is not None:
            self._visit(
                swan_obj.action,
                swan_obj,
                "action",
            )
        self._visit(
            swan_obj.target,
            swan_obj,
            "target",
        )  # isinstance(swan_obj.target, [swan.StateRef, swan.Fork])
        if swan_obj.source is not None:
            self._visit(
                swan_obj.source,
                swan_obj,
                "source",
            )
        self.visit_builtin(
            swan_obj.is_resume,
            swan_obj,
            "is_resume",
        )

    def visit_TransposeOperator(
        self,
        swan_obj: swan.TransposeOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TransposeOperator visitor method."""
        # Visit base class(es)
        self.visit_OperatorInstance(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if isinstance(swan_obj.params, list):
            for item in swan_obj.params:
                self.visit_builtin(
                    item,
                    swan_obj,
                    "params",
                )
        else:  # SwanVisitor._is_builtin(swan_obj.params)
            self.visit_builtin(
                swan_obj.params,
                swan_obj,
                "params",
            )

    def visit_TypeConstraint(
        self,
        swan_obj: swan.TypeConstraint,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeConstraint visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if isinstance(swan_obj.type_vars, list):
            for item in swan_obj.type_vars:
                self._visit(
                    item,
                    swan_obj,
                    "type_vars",
                )
        else:  # SwanVisitor._is_builtin(swan_obj.type_vars)
            self.visit_builtin(
                swan_obj.type_vars,
                swan_obj,
                "type_vars",
            )
        self._visit(
            swan_obj.kind,
            swan_obj,
            "kind",
        )

    def visit_TypeDecl(
        self,
        swan_obj: swan.TypeDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeDecl visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        if swan_obj.definition is not None:
            self._visit(
                swan_obj.definition,
                swan_obj,
                "definition",
            )

    def visit_TypeDeclarations(
        self,
        swan_obj: swan.TypeDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeDeclarations visitor method."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.types:
            self._visit(
                item,
                swan_obj,
                "types",
            )

    def visit_TypeDefinition(
        self,
        swan_obj: swan.TypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeDefinition visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_TypeExpression(
        self,
        swan_obj: swan.TypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeExpression visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_TypeGroupTypeExpression(
        self,
        swan_obj: swan.TypeGroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeGroupTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_GroupTypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_TypeReferenceExpression(
        self,
        swan_obj: swan.TypeReferenceExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default TypeReferenceExpression visitor method."""
        # Visit base class(es)
        self.visit_TypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.alias,
            swan_obj,
            "alias",
        )

    def visit_Uint16Type(
        self,
        swan_obj: swan.Uint16Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Uint16Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Uint32Type(
        self,
        swan_obj: swan.Uint32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Uint32Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Uint64Type(
        self,
        swan_obj: swan.Uint64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Uint64Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_Uint8Type(
        self,
        swan_obj: swan.Uint8Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Uint8Type visitor method."""
        # Visit base class(es)
        self.visit_PredefinedType(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_UnaryExpr(
        self,
        swan_obj: swan.UnaryExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default UnaryExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.operator,
            swan_obj,
            "operator",
        )
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )

    def visit_UnaryOp(
        self,
        swan_obj: swan.UnaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """UnaryOp visitor function. Should be overridden."""
        # Enum values:
        # Minus
        # Plus
        # Lnot
        # Not
        # Pre
        # Bang
        pass

    def visit_UnderscorePattern(
        self,
        swan_obj: swan.UnderscorePattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default UnderscorePattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_UseDirective(
        self,
        swan_obj: swan.UseDirective,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default UseDirective visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_ModuleItem(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.path,
            swan_obj,
            "path",
        )
        if swan_obj.alias is not None:
            self._visit(
                swan_obj.alias,
                swan_obj,
                "alias",
            )

    def visit_VarDecl(
        self,
        swan_obj: swan.VarDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VarDecl visitor method."""
        # Visit base class(es)
        self.visit_Declaration(
            swan_obj,
            owner,
            owner_property,
        )
        self.visit_Variable(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self.visit_builtin(
            swan_obj.is_clock,
            swan_obj,
            "is_clock",
        )
        self.visit_builtin(
            swan_obj.is_starred,
            swan_obj,
            "is_starred",
        )
        if swan_obj.at is not None:
            self._visit(
                swan_obj.at,
                swan_obj,
                "at",
            )
        if swan_obj.type is not None:
            self._visit(
                swan_obj.type,
                swan_obj,
                "type",
            )
        if swan_obj.when is not None:
            self._visit(
                swan_obj.when,
                swan_obj,
                "when",
            )
        if swan_obj.default is not None:
            self._visit(
                swan_obj.default,
                swan_obj,
                "default",
            )
        if swan_obj.last is not None:
            self._visit(
                swan_obj.last,
                swan_obj,
                "last",
            )

    def visit_VarSection(
        self,
        swan_obj: swan.VarSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VarSection visitor method."""
        # Visit base class(es)
        self.visit_ScopeSection(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.var_decls:
            self._visit(
                item,
                swan_obj,
                "var_decls",
            )

    def visit_Variable(
        self,
        swan_obj: swan.Variable,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Variable visitor method."""
        # Visit base class(es)
        self.visit_SwanItem(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_VariableTypeExpression(
        self,
        swan_obj: swan.VariableTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariableTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_TypeExpression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.name,
            swan_obj,
            "name",
        )

    def visit_VariantConstructor(
        self,
        swan_obj: swan.VariantConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantConstructor visitor method."""
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.tag,
            swan_obj,
            "tag",
        )

    def visit_VariantPattern(
        self,
        swan_obj: swan.VariantPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantPattern visitor method."""
        # Visit base class(es)
        self.visit_Pattern(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.path_id,
            swan_obj,
            "path_id",
        )
        if swan_obj.captured is not None:
            self._visit(
                swan_obj.captured,
                swan_obj,
                "captured",
            )
        self.visit_builtin(
            swan_obj.is_underscore,
            swan_obj,
            "is_underscore",
        )

    def visit_VariantSimple(
        self,
        swan_obj: swan.VariantSimple,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantSimple visitor method."""
        # Visit base class(es)
        self.visit_VariantConstructor(
            swan_obj,
            owner,
            owner_property,
        )

    def visit_VariantStruct(
        self,
        swan_obj: swan.VariantStruct,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantStruct visitor method."""
        # Visit base class(es)
        self.visit_VariantConstructor(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.structure_type,
            swan_obj,
            "structure_type",
        )

    def visit_VariantTypeDefinition(
        self,
        swan_obj: swan.VariantTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantTypeDefinition visitor method."""
        # Visit base class(es)
        self.visit_TypeDefinition(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        for item in swan_obj.tags:
            self._visit(
                item,
                swan_obj,
                "tags",
            )

    def visit_VariantTypeExpression(
        self,
        swan_obj: swan.VariantTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantTypeExpression visitor method."""
        # Visit base class(es)
        self.visit_VariantConstructor(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.type,
            swan_obj,
            "type",
        )

    def visit_VariantValue(
        self,
        swan_obj: swan.VariantValue,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default VariantValue visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.tag,
            swan_obj,
            "tag",
        )
        self._visit(
            swan_obj.group,
            swan_obj,
            "group",
        )

    def visit_WhenClockExpr(
        self,
        swan_obj: swan.WhenClockExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default WhenClockExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.clock,
            swan_obj,
            "clock",
        )

    def visit_WhenMatchExpr(
        self,
        swan_obj: swan.WhenMatchExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default WhenMatchExpr visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.expr,
            swan_obj,
            "expr",
        )
        self._visit(
            swan_obj.when,
            swan_obj,
            "when",
        )

    def visit_Window(
        self,
        swan_obj: swan.Window,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Window visitor method."""
        # Visit base class(es)
        self.visit_Expression(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.size,
            swan_obj,
            "size",
        )
        self._visit(
            swan_obj.init,
            swan_obj,
            "init",
        )
        self._visit(
            swan_obj.params,
            swan_obj,
            "params",
        )

    def visit_Wire(
        self,
        swan_obj: swan.Wire,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Wire visitor method."""
        # Visit base class(es)
        self.visit_DiagramObject(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.source,
            swan_obj,
            "source",
        )
        for item in swan_obj.targets:
            self._visit(
                item,
                swan_obj,
                "targets",
            )
