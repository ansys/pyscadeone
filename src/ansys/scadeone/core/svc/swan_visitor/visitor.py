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

# pylint: disable=too-many-lines, pointless-statement, invalid-name
from abc import ABC
from typing import Any, Union

from ansys.scadeone.core import swan


class SwanVisitor(ABC):
    """Visitor for Swan classes. This class must be derived."""

    @staticmethod
    def _is_builtin(obj):
        """Return True is name is a simple builtin-type
        that can be found in swan modules"""
        return type(obj).__name__ in ("str", "int", "bool", "float")

    def visit(self, swan_obj) -> None:
        """Entry point. After creation of an instance of
        a SwanVisitor, this method must be called on a Swan object instance."""
        self._visit(swan_obj, None, None)

    def _visit(
        self, swan_obj: Any, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Dispatch function."""
        try:
            class_name = swan_obj.__class__.__name__
            fn = getattr(self, f"visit_{class_name}")
            fn(swan_obj, owner, swan_property)
        except AttributeError:
            raise AttributeError(f"No visitor for {type(swan_obj)}")

    # Following methods must be overridden

    def visit_builtin(self, object, owner, swan_property) -> None:
        """Override this method."""
        pass

    def visit_SwanItem(self, swan_obj, owner, swan_property) -> None:
        """Override this method."""
        pass

    # Class visitors
    def visit_ActivateClock(
        self, swan_obj: swan.ActivateClock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ActivateClock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.clock, swan_obj, "clock")

    def visit_ActivateEvery(
        self, swan_obj: swan.ActivateEvery, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ActivateEvery visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.condition, swan_obj, "condition")
        self.visit_builtin(swan_obj.is_last, swan_obj, "is_last")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_ActivateIf(
        self, swan_obj: swan.ActivateIf, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ActivateIf visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.if_activation, swan_obj, "if_activation")

    def visit_ActivateIfBlock(
        self,
        swan_obj: swan.ActivateIfBlock,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ActivateIfBlock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DefByCaseBlockBase(swan_obj, owner, swan_property)

    def visit_ActivateWhen(
        self, swan_obj: swan.ActivateWhen, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ActivateWhen visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.condition, swan_obj, "condition")
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")

    def visit_ActivateWhenBlock(
        self,
        swan_obj: swan.ActivateWhenBlock,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ActivateWhenBlock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DefByCaseBlockBase(swan_obj, owner, swan_property)

    def visit_ActivateWhenBranch(
        self,
        swan_obj: swan.ActivateWhenBranch,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ActivateWhenBranch visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        if isinstance(swan_obj.data_def, swan.Equation):
            self._visit(swan_obj.data_def, swan_obj, "data_def")
        elif isinstance(swan_obj.data_def, swan.Scope):
            self._visit(swan_obj.data_def, swan_obj, "data_def")

    def visit_AnonymousOperatorWithDataDefinition(
        self,
        swan_obj: swan.AnonymousOperatorWithDataDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """AnonymousOperatorWithDataDefinition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.is_node, swan_obj, "is_node")
        for item in swan_obj.inputs:
            self._visit(item, swan_obj, "inputs")
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
        if isinstance(swan_obj.data_def, swan.Equation):
            self._visit(swan_obj.data_def, swan_obj, "data_def")
        elif isinstance(swan_obj.data_def, swan.Scope):
            self._visit(swan_obj.data_def, swan_obj, "data_def")

    def visit_AnonymousOperatorWithExpression(
        self,
        swan_obj: swan.AnonymousOperatorWithExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """AnonymousOperatorWithExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.is_node, swan_obj, "is_node")
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")
        for item in swan_obj.sections:
            self._visit(item, swan_obj, "sections")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_ArrayConstructor(
        self,
        swan_obj: swan.ArrayConstructor,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ArrayConstructor visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")

    def visit_ArrayProjection(
        self,
        swan_obj: swan.ArrayProjection,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ArrayProjection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.index, swan_obj, "index")

    def visit_ArrayRepetition(
        self,
        swan_obj: swan.ArrayRepetition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ArrayRepetition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.size, swan_obj, "size")

    def visit_ArrayTypeExpression(
        self,
        swan_obj: swan.ArrayTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ArrayTypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        self._visit(swan_obj.size, swan_obj, "size")

    def visit_Arrow(
        self, swan_obj: swan.Arrow, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Arrow visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.guard is not None:
            self._visit(swan_obj.guard, swan_obj, "guard")
        if swan_obj.action is not None:
            self._visit(swan_obj.action, swan_obj, "action")
        if swan_obj.target is not None:
            self._visit(swan_obj.target, swan_obj, "target")
        if swan_obj.fork is not None:
            self._visit(swan_obj.fork, swan_obj, "fork")

    def visit_AssertSection(
        self, swan_obj: swan.AssertSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """AssertSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.assertions:
            self._visit(item, swan_obj, "assertions")

    def visit_AssumeSection(
        self, swan_obj: swan.AssumeSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """AssumeSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.hypotheses:
            self._visit(item, swan_obj, "hypotheses")

    def visit_Bar(
        self, swan_obj: swan.Bar, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Bar visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.operation is not None:
            self._visit(swan_obj.operation, swan_obj, "operation")

    def visit_BinaryExpr(
        self, swan_obj: swan.BinaryExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """BinaryExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.left, swan_obj, "left")
        self._visit(swan_obj.right, swan_obj, "right")

    def visit_BinaryOp(
        self, swan_obj: swan.BinaryOp, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """BinaryOp visitor function. Should be overridden."""
        pass

    def visit_Block(
        self, swan_obj: swan.Block, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Block visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.instance, swan.OperatorBase):
            self._visit(swan_obj.instance, swan_obj, "instance")
        elif isinstance(swan_obj.instance, swan.OperatorExpression):
            self._visit(swan_obj.instance, swan_obj, "instance")
        elif isinstance(swan_obj.instance, swan.ProtectedItem):
            self._visit(swan_obj.instance, swan_obj, "instance")

    def visit_BoolPattern(
        self, swan_obj: swan.BoolPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """BoolPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")

    def visit_BoolType(
        self, swan_obj: swan.BoolType, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """BoolType visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_CaseBranch(
        self, swan_obj: swan.CaseBranch, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """CaseBranch visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_CaseExpr(
        self, swan_obj: swan.CaseExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """CaseExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")

    def visit_CharPattern(
        self, swan_obj: swan.CharPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """CharPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")

    def visit_CharType(
        self, swan_obj: swan.CharType, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """CharType visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_ClockExpr(
        self, swan_obj: swan.ClockExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ClockExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        if swan_obj.is_not is not None:
            self.visit_builtin(swan_obj.is_not, swan_obj, "is_not")
        if swan_obj.pattern is not None:
            self._visit(swan_obj.pattern, swan_obj, "pattern")

    def visit_Connection(
        self, swan_obj: swan.Connection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Connection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.port is not None:
            self._visit(swan_obj.port, swan_obj, "port")
        if swan_obj.adaptation is not None:
            self._visit(swan_obj.adaptation, swan_obj, "adaptation")

    def visit_ConstDecl(
        self, swan_obj: swan.ConstDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ConstDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.type is not None:
            self._visit(swan_obj.type, swan_obj, "type")
        if swan_obj.value is not None:
            self._visit(swan_obj.value, swan_obj, "value")

    def visit_ConstDeclarations(
        self,
        swan_obj: swan.ConstDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ConstDeclarations visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.constants:
            self._visit(item, swan_obj, "constants")

    def visit_Declaration(
        self, swan_obj: swan.Declaration, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Declaration visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")

    def visit_DefBlock(
        self, swan_obj: swan.DefBlock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """DefBlock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.lhs, swan.EquationLHS):
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        elif isinstance(swan_obj.lhs, swan.ProtectedItem):
            self._visit(swan_obj.lhs, swan_obj, "lhs")

    def visit_DefByCase(
        self, swan_obj: swan.DefByCase, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """DefByCase visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Equation(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.lhs is not None:
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        if swan_obj.name is not None:
            self._visit(swan_obj.name, swan_obj, "name")
        self.visit_builtin(swan_obj.is_equation, swan_obj, "is_equation")

    def visit_DefByCaseBlockBase(
        self,
        swan_obj: swan.DefByCaseBlockBase,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """DefByCaseBlockBase visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.def_by_case, swan_obj, "def_by_case")

    def visit_DefaultPattern(
        self,
        swan_obj: swan.DefaultPattern,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """DefaultPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)

    def visit_Diagram(
        self, swan_obj: swan.Diagram, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Diagram visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.objects:
            self._visit(item, swan_obj, "objects")

    def visit_DiagramObject(
        self, swan_obj: swan.DiagramObject, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """DiagramObject visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.lunum is not None:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")
        if swan_obj.locals is not None:
            for item in swan_obj.locals:
                self._visit(item, swan_obj, "locals")

    def visit_EmissionBody(
        self, swan_obj: swan.EmissionBody, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """EmissionBody visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.flows:
            self._visit(item, swan_obj, "flows")
        if swan_obj.condition is not None:
            self._visit(swan_obj.condition, swan_obj, "condition")
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")

    def visit_EmitSection(
        self, swan_obj: swan.EmitSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """EmitSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.emissions:
            self._visit(item, swan_obj, "emissions")

    def visit_EnumTypeDefinition(
        self,
        swan_obj: swan.EnumTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """EnumTypeDefinition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeDefinition(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.tags:
            self._visit(item, swan_obj, "tags")

    def visit_Equation(
        self, swan_obj: swan.Equation, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Equation visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_EquationLHS(
        self, swan_obj: swan.EquationLHS, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """EquationLHS visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.lhs_items:
            self._visit(item, swan_obj, "lhs_items")
        if swan_obj.is_partial_lhs is not None:
            self.visit_builtin(swan_obj.is_partial_lhs, swan_obj, "is_partial_lhs")

    def visit_ExprBlock(
        self, swan_obj: swan.ExprBlock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ExprBlock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_ExprEquation(
        self, swan_obj: swan.ExprEquation, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ExprEquation visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Equation(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")

    def visit_ExprTypeDefinition(
        self,
        swan_obj: swan.ExprTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ExprTypeDefinition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeDefinition(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_Expression(
        self, swan_obj: swan.Expression, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Expression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_Float32Type(
        self, swan_obj: swan.Float32Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Float32Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Float64Type(
        self, swan_obj: swan.Float64Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Float64Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Fork(
        self, swan_obj: swan.Fork, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Fork visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_ForkPriorityList(
        self,
        swan_obj: swan.ForkPriorityList,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForkPriorityList visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Fork(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.prio_forks:
            self._visit(item, swan_obj, "prio_forks")

    def visit_ForkTree(
        self, swan_obj: swan.ForkTree, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ForkTree visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Fork(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.if_arrow, swan_obj, "if_arrow")
        if swan_obj.elsif_arrows is not None:
            for item in swan_obj.elsif_arrows:
                self._visit(item, swan_obj, "elsif_arrows")
        if swan_obj.else_arrow is not None:
            self._visit(swan_obj.else_arrow, swan_obj, "else_arrow")

    def visit_ForkWithPriority(
        self,
        swan_obj: swan.ForkWithPriority,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForkWithPriority visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.priority is not None:
            self._visit(swan_obj.priority, swan_obj, "priority")
        self._visit(swan_obj.arrow, swan_obj, "arrow")
        self.visit_builtin(swan_obj.is_if_arrow, swan_obj, "is_if_arrow")

    def visit_FormalProperty(
        self,
        swan_obj: swan.FormalProperty,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """FormalProperty visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.luid, swan_obj, "luid")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_Forward(
        self, swan_obj: swan.Forward, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Forward visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.state, swan_obj, "state")
        for item in swan_obj.dimensions:
            self._visit(item, swan_obj, "dimensions")
        self._visit(swan_obj.body, swan_obj, "body")
        for item in swan_obj.returns:
            self._visit(item, swan_obj, "returns")
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")

    def visit_ForwardArrayClause(
        self,
        swan_obj: swan.ForwardArrayClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardArrayClause visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.return_clause, swan.ForwardItemClause):
            self._visit(swan_obj.return_clause, swan_obj, "return_clause")
        elif isinstance(swan_obj.return_clause, swan.ForwardArrayClause):
            self._visit(swan_obj.return_clause, swan_obj, "return_clause")

    def visit_ForwardBody(
        self, swan_obj: swan.ForwardBody, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ForwardBody visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.body:
            self._visit(item, swan_obj, "body")
        if swan_obj.unless_expr is not None:
            self._visit(swan_obj.unless_expr, swan_obj, "unless_expr")
        if swan_obj.until_expr is not None:
            self._visit(swan_obj.until_expr, swan_obj, "until_expr")

    def visit_ForwardDim(
        self, swan_obj: swan.ForwardDim, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ForwardDim visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.expr is not None:
            self._visit(swan_obj.expr, swan_obj, "expr")
        if swan_obj.dim_id is not None:
            self._visit(swan_obj.dim_id, swan_obj, "dim_id")
        if swan_obj.elems is not None:
            for item in swan_obj.elems:
                self._visit(item, swan_obj, "elems")
        if swan_obj.protected is not None:
            self.visit_builtin(swan_obj.protected, swan_obj, "protected")

    def visit_ForwardElement(
        self,
        swan_obj: swan.ForwardElement,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardElement visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_ForwardItemClause(
        self,
        swan_obj: swan.ForwardItemClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardItemClause visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        if swan_obj.last_default is not None:
            self._visit(swan_obj.last_default, swan_obj, "last_default")

    def visit_ForwardLHS(
        self, swan_obj: swan.ForwardLHS, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ForwardLHS visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.lhs, swan.Identifier):
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        elif isinstance(swan_obj.lhs, swan.ForwardLHS):
            self._visit(swan_obj.lhs, swan_obj, "lhs")

    def visit_ForwardLastDefault(
        self,
        swan_obj: swan.ForwardLastDefault,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardLastDefault visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.last is not None:
            self._visit(swan_obj.last, swan_obj, "last")
        if swan_obj.default is not None:
            self._visit(swan_obj.default, swan_obj, "default")
        if swan_obj.shared is not None:
            self._visit(swan_obj.shared, swan_obj, "shared")

    def visit_ForwardReturnArrayClause(
        self,
        swan_obj: swan.ForwardReturnArrayClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardReturnArrayClause visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ForwardReturnItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.array_clause, swan_obj, "array_clause")
        if swan_obj.return_id is not None:
            self._visit(swan_obj.return_id, swan_obj, "return_id")

    def visit_ForwardReturnItem(
        self,
        swan_obj: swan.ForwardReturnItem,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardReturnItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_ForwardReturnItemClause(
        self,
        swan_obj: swan.ForwardReturnItemClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ForwardReturnItemClause visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ForwardReturnItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.item_clause, swan_obj, "item_clause")

    def visit_ForwardState(
        self, swan_obj: swan.ForwardState, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """ForwardState visitor function. Should be overridden."""
        pass

    def visit_FunctionalUpdate(
        self,
        swan_obj: swan.FunctionalUpdate,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """FunctionalUpdate visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.modifiers:
            self._visit(item, swan_obj, "modifiers")

    def visit_GlobalDeclaration(
        self,
        swan_obj: swan.GlobalDeclaration,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GlobalDeclaration visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ModuleItem(swan_obj, owner, swan_property)

    def visit_Group(
        self, swan_obj: swan.Group, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Group visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.items:
            self._visit(item, swan_obj, "items")

    def visit_GroupAdaptation(
        self,
        swan_obj: swan.GroupAdaptation,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GroupAdaptation visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.renamings:
            self._visit(item, swan_obj, "renamings")

    def visit_GroupConstructor(
        self,
        swan_obj: swan.GroupConstructor,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GroupConstructor visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")

    def visit_GroupDecl(
        self, swan_obj: swan.GroupDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """GroupDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_GroupDeclarations(
        self,
        swan_obj: swan.GroupDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GroupDeclarations visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.groups:
            self._visit(item, swan_obj, "groups")

    def visit_GroupItem(
        self, swan_obj: swan.GroupItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """GroupItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        if swan_obj.label is not None:
            self._visit(swan_obj.label, swan_obj, "label")

    def visit_GroupOperation(
        self,
        swan_obj: swan.GroupOperation,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ):
        """GroupOperation visitor function. Should be overridden."""
        pass

    def visit_GroupProjection(
        self,
        swan_obj: swan.GroupProjection,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GroupProjection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.adaptation, swan_obj, "adaptation")

    def visit_GroupRenaming(
        self, swan_obj: swan.GroupRenaming, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """GroupRenaming visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.source, swan.Identifier):
            self._visit(swan_obj.source, swan_obj, "source")
        elif isinstance(swan_obj.source, swan.Literal):
            self._visit(swan_obj.source, swan_obj, "source")

        if swan_obj.renaming is not None:
            self._visit(swan_obj.renaming, swan_obj, "renaming")
        if swan_obj.is_shortcut is not None:
            self.visit_builtin(swan_obj.is_shortcut, swan_obj, "is_shortcut")

    def visit_GroupTypeExpression(
        self,
        swan_obj: swan.GroupTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GroupTypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_GroupTypeExpressionList(
        self,
        swan_obj: swan.GroupTypeExpressionList,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GroupTypeExpressionList visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.positional:
            self._visit(item, swan_obj, "positional")
        for item in swan_obj.named:
            self._visit(item, swan_obj, "named")

    def visit_GuaranteeSection(
        self,
        swan_obj: swan.GuaranteeSection,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """GuaranteeSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.guarantees:
            self._visit(item, swan_obj, "guarantees")

    def visit_Identifier(
        self, swan_obj: swan.Identifier, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Identifier visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")
        if swan_obj.comment is not None:
            self.visit_builtin(swan_obj.comment, swan_obj, "comment")
        if swan_obj.is_name is not None:
            self.visit_builtin(swan_obj.is_name, swan_obj, "is_name")

    def visit_IfActivation(
        self, swan_obj: swan.IfActivation, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """IfActivation visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")

    def visit_IfActivationBranch(
        self,
        swan_obj: swan.IfActivationBranch,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """IfActivationBranch visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.condition is not None:
            self._visit(swan_obj.condition, swan_obj, "condition")
        self._visit(swan_obj.branch, swan_obj, "branch")

    def visit_IfteBranch(
        self, swan_obj: swan.IfteBranch, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """IfteBranch visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_IfteDataDef(
        self, swan_obj: swan.IfteDataDef, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """IfteDataDef visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_IfteBranch(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.data_def, swan.Equation):
            self._visit(swan_obj.data_def, swan_obj, "data_def")
        elif isinstance(swan_obj.data_def, swan.Scope):
            self._visit(swan_obj.data_def, swan_obj, "data_def")

    def visit_IfteExpr(
        self, swan_obj: swan.IfteExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """IfteExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.cond_expr, swan_obj, "cond_expr")
        self._visit(swan_obj.then_expr, swan_obj, "then_expr")
        self._visit(swan_obj.else_expr, swan_obj, "else_expr")

    def visit_IfteIfActivation(
        self,
        swan_obj: swan.IfteIfActivation,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """IfteIfActivation visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_IfteBranch(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.if_activation, swan_obj, "if_activation")

    def visit_Int16Type(
        self, swan_obj: swan.Int16Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Int16Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Int32Type(
        self, swan_obj: swan.Int32Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Int32Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Int64Type(
        self, swan_obj: swan.Int64Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Int64Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Int8Type(
        self, swan_obj: swan.Int8Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Int8Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_IntPattern(
        self, swan_obj: swan.IntPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """IntPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")
        if swan_obj.is_minus is not None:
            self.visit_builtin(swan_obj.is_minus, swan_obj, "is_minus")

    def visit_Iterator(
        self, swan_obj: swan.Iterator, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Iterator visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")
        self._visit(swan_obj.operator, swan_obj, "operator")

    def visit_IteratorKind(
        self, swan_obj: swan.IteratorKind, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """IteratorKind visitor function. Should be overridden."""
        pass

    def visit_LHSItem(
        self, swan_obj: swan.LHSItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """LHSItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.id, swan.Identifier):
            self._visit(swan_obj.id, swan_obj, "id")
        elif SwanVisitor._is_builtin(swan_obj.id):
            self.visit_builtin(swan_obj.id, swan_obj, "id")

    def visit_LabelOrIndex(
        self, swan_obj: swan.LabelOrIndex, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """LabelOrIndex visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.value, swan.Identifier):
            self._visit(swan_obj.value, swan_obj, "value")
        elif isinstance(swan_obj.value, swan.Expression):
            self._visit(swan_obj.value, swan_obj, "value")

    def visit_LastExpr(
        self, swan_obj: swan.LastExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """LastExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")

    def visit_LetSection(
        self, swan_obj: swan.LetSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """LetSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.equations:
            self._visit(item, swan_obj, "equations")

    def visit_Literal(
        self, swan_obj: swan.Literal, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Literal visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")

    def visit_LiteralKind(
        self, swan_obj: swan.LiteralKind, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """LiteralKind visitor function. Should be overridden."""
        pass

    def visit_Luid(
        self, swan_obj: swan.Luid, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Luid visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")

    def visit_Lunum(
        self, swan_obj: swan.Lunum, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Lunum visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.value, swan_obj, "value")

    def visit_Markup(
        self, swan_obj: swan.Markup, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Markup visitor function. Should be overridden."""
        pass

    def visit_Merge(
        self, swan_obj: swan.Merge, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Merge visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")

    def visit_Modifier(
        self, swan_obj: swan.Modifier, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Modifier visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.modifier, list):
            for item in swan_obj.modifier:
                self._visit(item, swan_obj, "modifier")
        elif SwanVisitor._is_builtin(swan_obj.modifier):
            self.visit_builtin(swan_obj.modifier, swan_obj, "modifier")

        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_Module(
        self, swan_obj: swan.Module, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Module visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ModuleBase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.name, swan_obj, "name")
        if swan_obj.use_directives is not None:
            for item in swan_obj.use_directives:
                self._visit(item, swan_obj, "use_directives")
        if swan_obj.declarations is not None:
            for item in swan_obj.declarations:
                self._visit(item, swan_obj, "declarations")

    def visit_ModuleBase(
        self, swan_obj: swan.ModuleBase, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ModuleBase visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_ModuleBody(
        self, swan_obj: swan.ModuleBody, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ModuleBody visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Module(swan_obj, owner, swan_property)

    def visit_ModuleInterface(
        self,
        swan_obj: swan.ModuleInterface,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ModuleInterface visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Module(swan_obj, owner, swan_property)

    def visit_ModuleItem(
        self, swan_obj: swan.ModuleItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ModuleItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_NAryOperator(
        self, swan_obj: swan.NAryOperator, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """NAryOperator visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")

    def visit_NamedGroupTypeExpression(
        self,
        swan_obj: swan.NamedGroupTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """NamedGroupTypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.label, swan_obj, "label")
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_NaryOp(
        self, swan_obj: swan.NaryOp, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """NaryOp visitor function. Should be overridden."""
        pass

    def visit_NumericCast(
        self, swan_obj: swan.NumericCast, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """NumericCast visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_NumericKind(
        self, swan_obj: swan.NumericKind, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """NumericKind visitor function. Should be overridden."""
        pass

    def visit_Operator(
        self, swan_obj: swan.Operator, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Operator visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Signature(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.body, swan.Scope):
            self._visit(swan_obj.body, swan_obj, "body")
        elif isinstance(swan_obj.body, swan.Equation):
            self._visit(swan_obj.body, swan_obj, "body")

    def visit_OperatorBase(
        self, swan_obj: swan.OperatorBase, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """OperatorBase visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.sizes:
            self._visit(item, swan_obj, "sizes")

    def visit_OperatorExpression(
        self,
        swan_obj: swan.OperatorExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """OperatorExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_OperatorInstance(
        self,
        swan_obj: swan.OperatorInstance,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """OperatorInstance visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.params, swan_obj, "params")
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")

    def visit_OptGroupItem(
        self, swan_obj: swan.OptGroupItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """OptGroupItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.item is not None:
            self._visit(swan_obj.item, swan_obj, "item")

    def visit_Oracle(
        self, swan_obj: swan.Oracle, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Oracle visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")

    def visit_Partial(
        self, swan_obj: swan.Partial, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Partial visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        for item in swan_obj.partial_group:
            self._visit(item, swan_obj, "partial_group")

    def visit_PathIdExpr(
        self, swan_obj: swan.PathIdExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """PathIdExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")

    def visit_PathIdOpCall(
        self, swan_obj: swan.PathIdOpCall, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """PathIdOpCall visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")

    def visit_PathIdPattern(
        self, swan_obj: swan.PathIdPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """PathIdPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")

    def visit_PathIdentifier(
        self,
        swan_obj: swan.PathIdentifier,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """PathIdentifier visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.path_id, list):
            for item in swan_obj.path_id:
                self._visit(item, swan_obj, "path_id")
        elif SwanVisitor._is_builtin(swan_obj.path_id):
            self.visit_builtin(swan_obj.path_id, swan_obj, "path_id")

    def visit_Pattern(
        self, swan_obj: swan.Pattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Pattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_PortExpr(
        self, swan_obj: swan.PortExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """PortExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.lunum is not None:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")
        if swan_obj.is_self is not None:
            self.visit_builtin(swan_obj.is_self, swan_obj, "is_self")

    def visit_Pragma(
        self, swan_obj: swan.Pragma, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Pragma visitor function. Should be overridden."""
        # Visit properties
        self.visit_builtin(swan_obj.pragma, swan_obj, "pragma")

    def visit_PragmaBase(
        self, swan_obj: swan.PragmaBase, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """PragmaBase visitor function. Should be overridden."""
        # Visit properties
        if swan_obj.pragmas is not None:
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")

    def visit_PredefinedType(
        self,
        swan_obj: swan.PredefinedType,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """PredefinedType visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeExpression(swan_obj, owner, swan_property)

    def visit_PrefixOperatorExpression(
        self,
        swan_obj: swan.PrefixOperatorExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """PrefixOperatorExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.op_expr, swan_obj, "op_expr")

    def visit_PrefixPrimitive(
        self,
        swan_obj: swan.PrefixPrimitive,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """PrefixPrimitive visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")

    def visit_PrefixPrimitiveKind(
        self,
        swan_obj: swan.PrefixPrimitiveKind,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ):
        """PrefixPrimitiveKind visitor function. Should be overridden."""
        pass

    def visit_ProjectionWithDefault(
        self,
        swan_obj: swan.ProjectionWithDefault,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProjectionWithDefault visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.indices:
            self._visit(item, swan_obj, "indices")
        self._visit(swan_obj.default, swan_obj, "default")

    def visit_ProtectedDecl(
        self, swan_obj: swan.ProtectedDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ProtectedDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)
        self.visit_GlobalDeclaration(swan_obj, owner, swan_property)

    def visit_ProtectedExpr(
        self, swan_obj: swan.ProtectedExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ProtectedExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedForwardReturnItem(
        self,
        swan_obj: swan.ProtectedForwardReturnItem,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedForwardReturnItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)
        self.visit_ForwardReturnItem(swan_obj, owner, swan_property)

    def visit_ProtectedGroupRenaming(
        self,
        swan_obj: swan.ProtectedGroupRenaming,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedGroupRenaming visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GroupRenaming(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedItem(
        self, swan_obj: swan.ProtectedItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ProtectedItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.data, swan_obj, "data")
        if swan_obj.markup is not None:
            self.visit_builtin(swan_obj.markup, swan_obj, "markup")

    def visit_ProtectedOpExpr(
        self,
        swan_obj: swan.ProtectedOpExpr,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedOpExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedPattern(
        self,
        swan_obj: swan.ProtectedPattern,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedSection(
        self,
        swan_obj: swan.ProtectedSection,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedTypeExpr(
        self,
        swan_obj: swan.ProtectedTypeExpr,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedTypeExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeExpression(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedVariable(
        self,
        swan_obj: swan.ProtectedVariable,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """ProtectedVariable visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Variable(swan_obj, owner, swan_property)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_Restart(
        self, swan_obj: swan.Restart, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Restart visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_OperatorExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.condition, swan_obj, "condition")

    def visit_Scope(
        self, swan_obj: swan.Scope, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Scope visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.sections:
            self._visit(item, swan_obj, "sections")

    def visit_ScopeSection(
        self, swan_obj: swan.ScopeSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """ScopeSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_SectionBlock(
        self, swan_obj: swan.SectionBlock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """SectionBlock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.section, swan_obj, "section")

    def visit_SensorDecl(
        self, swan_obj: swan.SensorDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """SensorDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_SensorDeclarations(
        self,
        swan_obj: swan.SensorDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """SensorDeclarations visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.sensors:
            self._visit(item, swan_obj, "sensors")

    def visit_SetSensorEquation(
        self,
        swan_obj: swan.SetSensorEquation,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """SetSensorEquation visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Equation(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.sensor, swan_obj, "sensor")
        self._visit(swan_obj.value, swan_obj, "value")

    def visit_Signature(
        self, swan_obj: swan.Signature, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Signature visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        self.visit_ModuleItem(swan_obj, owner, swan_property)
        # Visit properties
        self.visit_builtin(swan_obj.has_inline, swan_obj, "has_inline")
        self.visit_builtin(swan_obj.is_node, swan_obj, "is_node")
        for item in swan_obj.inputs:
            self._visit(item, swan_obj, "inputs")
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
        if swan_obj.sizes is not None:
            for item in swan_obj.sizes:
                self._visit(item, swan_obj, "sizes")
        if swan_obj.constraints is not None:
            for item in swan_obj.constraints:
                self._visit(item, swan_obj, "constraints")
        if swan_obj.specialization is not None:
            self._visit(swan_obj.specialization, swan_obj, "specialization")
        if swan_obj.pragmas is not None:
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")

    def visit_SizedTypeExpression(
        self,
        swan_obj: swan.SizedTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """SizedTypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        self.visit_builtin(swan_obj.is_signed, swan_obj, "is_signed")

    def visit_Slice(
        self, swan_obj: swan.Slice, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Slice visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.start, swan_obj, "start")
        self._visit(swan_obj.end, swan_obj, "end")

    def visit_Source(
        self, swan_obj: swan.Source, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Source visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")

    def visit_State(
        self, swan_obj: swan.State, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """State visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_StateMachineItem(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.id is not None:
            self._visit(swan_obj.id, swan_obj, "id")
        if swan_obj.lunum is not None:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
        if swan_obj.strong_transitions is not None:
            for item in swan_obj.strong_transitions:
                self._visit(item, swan_obj, "strong_transitions")
        if swan_obj.sections is not None:
            for item in swan_obj.sections:
                self._visit(item, swan_obj, "sections")
        if swan_obj.weak_transitions is not None:
            for item in swan_obj.weak_transitions:
                self._visit(item, swan_obj, "weak_transitions")
        if swan_obj.is_initial is not None:
            self.visit_builtin(swan_obj.is_initial, swan_obj, "is_initial")

    def visit_StateMachine(
        self, swan_obj: swan.StateMachine, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """StateMachine visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.items is not None:
            for item in swan_obj.items:
                self._visit(item, swan_obj, "items")

    def visit_StateMachineBlock(
        self,
        swan_obj: swan.StateMachineBlock,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """StateMachineBlock visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DefByCaseBlockBase(swan_obj, owner, swan_property)

    def visit_StateMachineItem(
        self,
        swan_obj: swan.StateMachineItem,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """StateMachineItem visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_StateRef(
        self, swan_obj: swan.StateRef, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """StateRef visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.lunum is not None:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
        if swan_obj.id is not None:
            self._visit(swan_obj.id, swan_obj, "id")

    def visit_StructConstructor(
        self,
        swan_obj: swan.StructConstructor,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """StructConstructor visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        if swan_obj.type is not None:
            self._visit(swan_obj.type, swan_obj, "type")

    def visit_StructDestructor(
        self,
        swan_obj: swan.StructDestructor,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """StructDestructor visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_StructField(
        self, swan_obj: swan.StructField, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """StructField visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_StructProjection(
        self,
        swan_obj: swan.StructProjection,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """StructProjection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.label, swan_obj, "label")

    def visit_StructTypeDefinition(
        self,
        swan_obj: swan.StructTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """StructTypeDefinition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeDefinition(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.fields:
            self._visit(item, swan_obj, "fields")

    def visit_SwanRE(
        self, swan_obj: swan.SwanRE, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """SwanRE visitor function. Should be overridden."""
        pass

    def visit_Target(
        self, swan_obj: swan.Target, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Target visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.target, swan_obj, "target")
        if swan_obj.is_resume is not None:
            self.visit_builtin(swan_obj.is_resume, swan_obj, "is_resume")

    def visit_TestHarness(
        self, swan_obj: swan.TestHarness, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """TestHarness visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        self.visit_ModuleItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.body, swan.Scope):
            self._visit(swan_obj.body, swan_obj, "body")
        elif isinstance(swan_obj.body, swan.Equation):
            self._visit(swan_obj.body, swan_obj, "body")

    def visit_TestModule(
        self, swan_obj: swan.TestModule, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """TestModule visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ModuleBody(swan_obj, owner, swan_property)

    def visit_Transition(
        self, swan_obj: swan.Transition, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Transition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        self.visit_PragmaBase(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.arrow, swan_obj, "arrow")

    def visit_TransitionDecl(
        self,
        swan_obj: swan.TransitionDecl,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TransitionDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_StateMachineItem(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.priority is not None:
            self._visit(swan_obj.priority, swan_obj, "priority")
        self._visit(swan_obj.transition, swan_obj, "transition")
        self.visit_builtin(swan_obj.is_strong, swan_obj, "is_strong")
        self._visit(swan_obj.state_ref, swan_obj, "state_ref")

    def visit_Transpose(
        self, swan_obj: swan.Transpose, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Transpose visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PrefixPrimitive(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.params, list):
            for item in swan_obj.params:
                self.visit_builtin(item, swan_obj, "params")
        elif SwanVisitor._is_builtin(swan_obj.params):
            self.visit_builtin(swan_obj.params, swan_obj, "params")

    def visit_TypeConstraint(
        self,
        swan_obj: swan.TypeConstraint,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TypeConstraint visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        if isinstance(swan_obj.type_vars, list):
            for item in swan_obj.type_vars:
                self._visit(item, swan_obj, "type_vars")
        elif SwanVisitor._is_builtin(swan_obj.type_vars):
            self.visit_builtin(swan_obj.type_vars, swan_obj, "type_vars")

        self._visit(swan_obj.kind, swan_obj, "kind")

    def visit_TypeDecl(
        self, swan_obj: swan.TypeDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """TypeDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.definition is not None:
            self._visit(swan_obj.definition, swan_obj, "definition")

    def visit_TypeDeclarations(
        self,
        swan_obj: swan.TypeDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TypeDeclarations visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GlobalDeclaration(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.types:
            self._visit(item, swan_obj, "types")

    def visit_TypeDefinition(
        self,
        swan_obj: swan.TypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TypeDefinition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_TypeExpression(
        self,
        swan_obj: swan.TypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_TypeGroupTypeExpression(
        self,
        swan_obj: swan.TypeGroupTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TypeGroupTypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_TypeReferenceExpression(
        self,
        swan_obj: swan.TypeReferenceExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """TypeReferenceExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.alias, swan_obj, "alias")

    def visit_Uint16Type(
        self, swan_obj: swan.Uint16Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Uint16Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Uint32Type(
        self, swan_obj: swan.Uint32Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Uint32Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Uint64Type(
        self, swan_obj: swan.Uint64Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Uint64Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Uint8Type(
        self, swan_obj: swan.Uint8Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Uint8Type visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_UnaryExpr(
        self, swan_obj: swan.UnaryExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """UnaryExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.expr, swan_obj, "expr")

    def visit_UnaryOp(
        self, swan_obj: swan.UnaryOp, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """UnaryOp visitor function. Should be overridden."""
        pass

    def visit_UnderscorePattern(
        self,
        swan_obj: swan.UnderscorePattern,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """UnderscorePattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)

    def visit_UseDirective(
        self, swan_obj: swan.UseDirective, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """UseDirective visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ModuleItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.path, swan_obj, "path")
        if swan_obj.alias is not None:
            self._visit(swan_obj.alias, swan_obj, "alias")

    def visit_VarDecl(
        self, swan_obj: swan.VarDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """VarDecl visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Declaration(swan_obj, owner, swan_property)
        self.visit_Variable(swan_obj, owner, swan_property)
        # Visit properties
        if swan_obj.is_clock is not None:
            self.visit_builtin(swan_obj.is_clock, swan_obj, "is_clock")
        if swan_obj.is_probe is not None:
            self.visit_builtin(swan_obj.is_probe, swan_obj, "is_probe")
        if swan_obj.type is not None:
            self._visit(swan_obj.type, swan_obj, "type")
        if swan_obj.when is not None:
            self._visit(swan_obj.when, swan_obj, "when")
        if swan_obj.default is not None:
            self._visit(swan_obj.default, swan_obj, "default")
        if swan_obj.last is not None:
            self._visit(swan_obj.last, swan_obj, "last")

    def visit_VarSection(
        self, swan_obj: swan.VarSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """VarSection visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_ScopeSection(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.var_decls:
            self._visit(item, swan_obj, "var_decls")

    def visit_Variable(
        self, swan_obj: swan.Variable, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Variable visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)

    def visit_VariableTypeExpression(
        self,
        swan_obj: swan.VariableTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """VariableTypeExpression visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.name, swan_obj, "name")

    def visit_VariantComponent(
        self,
        swan_obj: swan.VariantComponent,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """VariantComponent visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_SwanItem(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.tag, swan_obj, "tag")

    def visit_VariantPattern(
        self,
        swan_obj: swan.VariantPattern,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """VariantPattern visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Pattern(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        if swan_obj.captured is not None:
            self._visit(swan_obj.captured, swan_obj, "captured")
        if swan_obj.underscore is not None:
            self.visit_builtin(swan_obj.underscore, swan_obj, "underscore")

    def visit_VariantSimple(
        self, swan_obj: swan.VariantSimple, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """VariantSimple visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_VariantComponent(swan_obj, owner, swan_property)

    def visit_VariantStruct(
        self, swan_obj: swan.VariantStruct, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """VariantStruct visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_VariantComponent(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.fields:
            self._visit(item, swan_obj, "fields")

    def visit_VariantTypeDefinition(
        self,
        swan_obj: swan.VariantTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """VariantTypeDefinition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_TypeDefinition(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.tags:
            self._visit(item, swan_obj, "tags")

    def visit_VariantTypeExpr(
        self,
        swan_obj: swan.VariantTypeExpr,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """VariantTypeExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_VariantComponent(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")

    def visit_VariantValue(
        self, swan_obj: swan.VariantValue, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """VariantValue visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.tag, swan_obj, "tag")
        self._visit(swan_obj.group, swan_obj, "group")

    def visit_WhenClockExpr(
        self, swan_obj: swan.WhenClockExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """WhenClockExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.clock, swan_obj, "clock")

    def visit_WhenMatchExpr(
        self, swan_obj: swan.WhenMatchExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """WhenMatchExpr visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.when, swan_obj, "when")

    def visit_Window(
        self, swan_obj: swan.Window, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Window visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        self._visit(swan_obj.init, swan_obj, "init")
        self._visit(swan_obj.params, swan_obj, "params")

    def visit_Wire(
        self, swan_obj: swan.Wire, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """Wire visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.source, swan_obj, "source")
        for item in swan_obj.targets:
            self._visit(item, swan_obj, "targets")
