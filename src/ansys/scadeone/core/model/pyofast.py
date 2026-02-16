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

# cSpell: ignore Aroba elems OPEXPR Predef prio Verif
# pylint: disable=invalid-name, too-many-lines, no-else-return, too-many-branches,
# pylint: disable=inconsistent-return-statements, too-many-return-statements
# pylint: disable=singleton-comparison, too-many-locals, too-many-statements
# pyright: ignore-all
# pyre-ignore-all-errors
# type: ignore

"""
The PyOfAst module transforms F# AST into Python ansys.scadeone.core.swan classes.
"""

from typing import Optional, Union, List, Any

# pylint: disable-next=import-error
from ANSYS.SONE.Infrastructure.Services.Serialization.BNF.Parsing import Ast, Raw

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanString
import ansys.scadeone.core.swan as Swan
from ansys.scadeone.core.swan.pragmas import PragmaParser

from .parser import Parser


def getValueOf(option) -> Optional[Any]:
    """Help to get value from 't option"""
    return option.Value if option else None


def getMarkup(raw) -> str:
    return Raw.getMarkup(raw)


def getProtectedString(raw) -> str:
    return Raw.getIndentedRawString(raw)


def protectedItemOfAst(raw) -> Swan.ProtectedItem:
    return Swan.ProtectedItem(getProtectedString(raw), getMarkup(raw))


def getPragmas(ast_pragmas) -> List[Swan.Pragma]:
    sources = [p.reindentedSource() for p in ast_pragmas]
    pragmas = [PragmaParser().parse(src) for src in sources]
    if None in pragmas:
        raise ScadeOneException(
            "Invalid pragma found in the AST. Please check the syntax of your pragmas."
        )
    return pragmas


def getPragmasFromIdentifier(ast_id):
    return getPragmas(Ast.idPragmas(ast_id))


# Identifiers
# ============================================================
def identifierOfAst(ast) -> Swan.Identifier:
    id = Ast.idName(ast)
    return Swan.Identifier(id)


def pathIdentifierOfAst(pathId) -> Swan.PathIdentifier:
    ids = [identifierOfAst(id) for id in pathId]
    return Swan.PathIdentifier(ids)


def pathIdentifierOrRawOfAst(pathId) -> Swan.PathIdentifier:
    if pathId.IsPIOfId:
        return pathIdentifierOfAst(pathId.Item1)
    return Swan.PathIdentifier(getProtectedString(pathId.Item))


def stringOfStringWithSP(ast) -> str:
    return ast.StringData


def instanceIdOfAst(ast) -> str:
    if ast.IsInstanceIdSelf:
        return "self"
    return stringOfStringWithSP(ast.Item)


def nameOfAst(ast) -> str:
    # skip '
    return stringOfStringWithSP(ast)[1:]


def luidOfAst(ast) -> Swan.Luid:
    return Swan.Luid(stringOfStringWithSP(ast))


def lunumOfAst(ast) -> Swan.Lunum:
    return Swan.Lunum(stringOfStringWithSP(ast))


# Expressions
# ============================================================


# arithmetic & logical operators
# ------------------------------
def unaryOfOfAst(ast) -> Swan.UnaryOp:
    if ast.IsUMinus:
        return Swan.UnaryOp.Minus
    elif ast.IsUPlus:
        return Swan.UnaryOp.Plus
    elif ast.IsULnot:
        return Swan.UnaryOp.Lnot
    elif ast.IsUNot:
        return Swan.UnaryOp.Not
    elif ast.IsUPre:
        return Swan.UnaryOp.Pre
    elif ast.IsUBang:
        return Swan.UnaryOp.Bang


def binaryOpOfAst(ast) -> Swan.BinaryOp:
    if ast.IsBPlus:
        return Swan.BinaryOp.Plus
    elif ast.IsBMinus:
        return Swan.BinaryOp.Minus
    elif ast.IsBMult:
        return Swan.BinaryOp.Mult
    elif ast.IsBSlash:
        return Swan.BinaryOp.Slash
    elif ast.IsBMod:
        return Swan.BinaryOp.Mod
    elif ast.IsBLand:
        return Swan.BinaryOp.Land
    elif ast.IsBLor:
        return Swan.BinaryOp.Lor
    elif ast.IsBLxor:
        return Swan.BinaryOp.Lxor
    elif ast.IsBLsl:
        return Swan.BinaryOp.Lsl
    elif ast.IsBLsr:
        return Swan.BinaryOp.Lsr
    elif ast.IsBEqual:
        return Swan.BinaryOp.Equal
    elif ast.IsBDiff:
        return Swan.BinaryOp.Diff
    elif ast.IsBLt:
        return Swan.BinaryOp.Lt
    elif ast.IsBGt:
        return Swan.BinaryOp.Gt
    elif ast.IsBLeq:
        return Swan.BinaryOp.Leq
    elif ast.IsBGeq:
        return Swan.BinaryOp.Geq
    elif ast.IsBAnd:
        return Swan.BinaryOp.And
    elif ast.IsBOr:
        return Swan.BinaryOp.Or
    elif ast.IsBXor:
        return Swan.BinaryOp.Xor
    elif ast.IsBArrow:
        return Swan.BinaryOp.Arrow
    elif ast.IsBPre:
        return Swan.BinaryOp.Pre
    elif ast.IsBAroba:
        return Swan.BinaryOp.Concat


# label, group item
# -----------------
def labelOrIndexOfAst(ast) -> Swan.LabelOrIndex:
    if ast.IsIndex:
        expr = exprOrRawOfAst(ast.Item)
        return Swan.LabelOrIndex(expr)
    id = identifierOfAst(ast.Item)
    return Swan.LabelOrIndex(id)


def groupItemOfAst(ast) -> Swan.GroupItem:
    expr = exprOrRawOfAst(ast.Item) if ast.IsGroupItemExpr else exprOrRawOfAst(ast.Item2)
    label = identifierOfAst(ast.Item1) if ast.IsGroupItemLabelExpr else None
    return Swan.GroupItem(expr, label)


def groupOfAst(ast) -> Swan.Group:
    items = [groupItemOfAst(item) for item in ast]
    return Swan.Group(items)


# modifiers, patterns
# -------------------
def modifierOfAst(ast) -> Swan.Modifier:
    new_value = exprOrRawOfAst(ast.Item2)
    if ast.IsModifierRaw:
        return Swan.Modifier(getProtectedString(ast.Item1), new_value)
    indices = [labelOrIndexOfAst(item) for item in ast.Item1]
    return Swan.Modifier(indices, new_value)


def casePatternsOfAst(cases) -> List[Swan.CaseBranch]:
    def caseOfAst(pattern, expr):
        p_obj = patternOrRawOfAst(pattern)
        e_obj = exprOrRawOfAst(expr)
        return Swan.CaseBranch(p_obj, e_obj)

    patterns = [caseOfAst(c.Item1, c.Item2) for c in cases]
    return patterns


def patternOrRawOfAst(pattern) -> Swan.Pattern:
    if pattern.IsPRaw:
        return Swan.ProtectedPattern(getProtectedString(pattern.Item))

    pattern = pattern.Item1
    if pattern.IsPId:
        tag = pathIdentifierOfAst(pattern.Item)
        return Swan.PathIdPattern(tag)

    if pattern.IsPVariant:
        tag = pathIdentifierOfAst(pattern.Item)
        return Swan.VariantPattern(tag, is_underscore=True)

    if pattern.IsPVariantCapture:
        tag = pathIdentifierOfAst(pattern.Item1)
        if id := getValueOf(pattern.Item2):
            return Swan.VariantPattern(tag, identifierOfAst(id))
        return Swan.VariantPattern(tag)

    if pattern.IsPChar:
        return Swan.CharPattern(pattern.Item)

    if pattern.IsPInt:
        return Swan.IntPattern(pattern.Item2, pattern.Item1)

    if pattern.IsPBool:
        return Swan.BoolPattern(pattern.Item)

    if pattern.IsPUscore:
        return Swan.UnderscorePattern()

    if pattern.IsPDefault:
        return Swan.DefaultPattern()


# Renamings
# ---------
def renamingOfAst(ast) -> Swan.GroupRenamingBase:
    if ast.IsRenamingByPos:  # of string * bool * Id option
        index = Swan.Literal(ast.Item1)
        is_shortcut = ast.Item2
        if renaming := getValueOf(ast.Item3):
            renaming = identifierOfAst(renaming)
        return Swan.GroupRenaming(index, renaming, is_shortcut)

    if ast.IsRenamingByName:  # of Id * bool * Id option
        index = identifierOfAst(ast.Item1)
        is_shortcut = ast.Item2
        if renaming := getValueOf(ast.Item3):
            renaming = identifierOfAst(renaming)
        return Swan.GroupRenaming(index, renaming, is_shortcut)

    if ast.IsRenamingRaw:  # of SourcePosition.t
        markup = getMarkup(ast.Item)
        content = getProtectedString(ast.Item)
        return Swan.ProtectedGroupRenaming(content, markup)


def groupAdaptationOfAst(ast) -> Swan.GroupAdaptation:
    renamings = [renamingOfAst(ren) for ren in ast.GRenaming]
    return Swan.GroupAdaptation(renamings)


# Clock expression
# ----------------
def clockExprOfAst(ast) -> Swan.ClockExpr:
    if ast.IsClockId:  # of Id
        return Swan.ClockExpr(identifierOfAst(ast.Item))
    if ast.IsClockNotId:  # of Id
        return Swan.ClockExpr(identifierOfAst(ast.Item), is_not=True)
    if ast.IsClockMatch:  # of Id * PatternOrRaw
        pattern = patternOrRawOfAst(ast.Item2)
        return Swan.ClockExpr(identifierOfAst(ast.Item1), pattern=pattern)


# Forward expression
# ~~~~~~~~~~~~~~~~~~~
def forwardLHSofAst(ast) -> Swan.ForwardLHS:
    if ast.IsFId:  # of Id
        return Swan.ForwardLHS(identifierOfAst(ast.Item))
    # FLhsArray of ForwardLhs
    return Swan.ForwardLHS(forwardLHSofAst(ast.Item))


def forwardElement(ast) -> Swan.ForwardElement:
    lhs = forwardLHSofAst(ast.Item1)
    expr = expressionOfAst(ast.Item2)
    return Swan.ForwardElement(lhs, expr)


def forwardDimOfAst(ast) -> Swan.ForwardDim:
    if ast.IsFDim:  # of Expr * SourcePosition.t
        return Swan.ForwardDim(expressionOfAst(ast.Item1))

    if ast.IsFDimWith:  # of Expr * Id option * (ForwardLhs * Expr) list * SourcePosition.t
        expr = expressionOfAst(ast.Item1)
        if id := getValueOf(ast.Item2):
            id = identifierOfAst(id)
        elems = [forwardElement(elem) for elem in ast.Item3]
        return Swan.ForwardDim(expr, id, elems)

    # FRaw of Raw.t
    data = getProtectedString(ast.Item)
    return Swan.ForwardDim(protected=data)


def forwardBodyOfAst(ast) -> Swan.ForwardBody:
    sections = [scopeSectionOfAst(sec) for sec in ast.FScopeSections]
    if until := getValueOf(ast.FUntilCondition):
        until = exprOrRawOfAst(until)
    if unless := getValueOf(ast.FUnlessCondition):
        unless = exprOrRawOfAst(unless)

    return Swan.ForwardBody(sections, unless, until)


def forwardLastDefaultOfAst(ast) -> Swan.ForwardLastDefault:
    if ast.IsFLast:  # of Expr
        return Swan.ForwardLastDefault(last=expressionOfAst(ast.Item))

    if ast.IsFDefault:  # of Expr
        return Swan.ForwardLastDefault(default=expressionOfAst(ast.Item))

    if ast.IsFLastPlusDefault:  # of Expr * Expr
        return Swan.ForwardLastDefault(
            last=expressionOfAst(ast.Item1), default=expressionOfAst(ast.Item2)
        )
    # ast.IsFLastAndDefault: # of Expr
    return Swan.ForwardLastDefault(shared=expressionOfAst(ast.Item))


def forwardItemClauseOfAst(ast) -> Swan.ForwardItemClause:
    id = identifierOfAst(ast.Item1)
    if last_default := getValueOf(ast.Item2):
        last_default = forwardLastDefaultOfAst(last_default)
    return Swan.ForwardItemClause(id, last_default)


def forwardArrayClauseOfAst(ast) -> Swan.ForwardArrayClause:
    if ast.IsFItemClause:  # of ForwardItemClause
        clause = forwardItemClauseOfAst(ast.Item)
    else:  # ast.IsFArrayClause  of ForwardArrayClause
        clause = forwardArrayClauseOfAst(ast.Item)
    return Swan.ForwardArrayClause(clause)


def forwardReturnOfAst(ast) -> Swan.ForwardReturnItem:
    if ast.IsFRetItemClause:  # of ForwardItemClause * SourcePosition.t
        clause = forwardItemClauseOfAst(ast.Item1)
        return Swan.ForwardReturnItemClause(clause)
    if ast.IsFRetArrayClause:  # of Id option * ForwardArrayClause * SourcePosition.t
        if id := getValueOf(ast.Item1):
            id = identifierOfAst(id)
        clause = forwardArrayClauseOfAst(ast.Item2)
        return Swan.ForwardReturnArrayClause(clause, id)
    if ast.IsFRetRaw:  # of Raw.t
        return Swan.ProtectedForwardReturnItem(getProtectedString(ast.Item))


def forwardOfAst(ast) -> Swan.Forward:
    # Luid option * RestartState * ForwardDim list * ForwardBody * ForwardReturnsItem list
    if luid := getValueOf(ast.Item1):
        luid = luidOfAst(luid)

    if ast.Item2.IsFNone:
        restart = None
    else:
        restart = ast.Item2.IsFRestart

    dims = [forwardDimOfAst(dim) for dim in ast.Item3]
    body = forwardBodyOfAst(ast.Item4)
    returns = [forwardReturnOfAst(ret) for ret in ast.Item5]

    return Swan.Forward(restart, dims, body, returns, luid)


# Operator instance & expressions
# -------------------------------
def iteratorOfAst(ast, operator) -> Swan.Iterator:
    # pylint: disable=possibly-used-before-assignment

    if ast.IsIMap:
        kind = Swan.IteratorKind.Map
    elif ast.IsIFold:
        kind = Swan.IteratorKind.Fold
    elif ast.IsIMapi:
        kind = Swan.IteratorKind.Mapi
    elif ast.IsIFoldi:
        kind = Swan.IteratorKind.Foldi
    elif ast.IsIMapfold:  # of int
        kind = Swan.IteratorKind.Mapfold
    elif ast.IsIMapfoldi:  # of int
        kind = Swan.IteratorKind.Mapfoldi

    return Swan.Iterator(kind, operator)


def optGroupItemOfAst(ast) -> Swan.OptGroupItem:
    group_item = groupItemOfAst(ast.Item) if ast.IsOGroupItem else None
    return Swan.OptGroupItem(group_item)


def operatorExprWithSPOfAst(ast) -> Swan.OperatorExpression:
    return operatorExprOfAst(ast.OEOpExpr)


def operatorExprOfAst(ast) -> Swan.OperatorExpression:
    if ast.IsOIterator:  # Iterator * Operator
        operator = operatorBaseOfAst(ast.Item2)
        return iteratorOfAst(ast.Item1, operator)

    if ast.IsOActivateClock:  # Operator * ClockExpr
        operator = operatorBaseOfAst(ast.Item1)
        clock = clockExprOfAst(ast.Item2)
        return Swan.ActivateClock(operator, clock)

    if ast.IsOActivateCondition:  # Operator * ExprOrRaw * bool * ExprOrRaw
        operator = operatorBaseOfAst(ast.Item1)
        cond = exprOrRawOfAst(ast.Item2)
        is_last = ast.Item3
        default = exprOrRawOfAst(ast.Item4)
        return Swan.ActivateEvery(operator, cond, is_last, default)

    if ast.IsORestart:  # Operator * ExprOrRaw
        operator = operatorBaseOfAst(ast.Item1)
        condition = exprOrRawOfAst(ast.Item2)
        return Swan.RestartOperator(operator, condition)

    if ast.IsOLambdaDataDef:  # bool * VarOrRaw list * VarOrRaw list * ScopeDefinition
        is_node = ast.Item1
        inputs = [varDeclOfAst(sig) for sig in ast.Item2]
        outputs = [varDeclOfAst(sig) for sig in ast.Item3]
        data_def = scopeOfAst(ast.Item4)
        return Swan.AnonymousOperatorWithDataDefinition(is_node, inputs, outputs, data_def)

    if ast.IsOLambdaScopes:  # bool * Id list * ScopeSection list * ExprOrRaw
        is_node = ast.Item1
        params = [identifierOfAst(id) for id in ast.Item2]
        sections = [scopeSectionOfAst(scope) for scope in ast.Item3]
        expr = exprOrRawOfAst(ast.Item4)
        return Swan.AnonymousOperatorWithExpression(is_node, params, sections, expr)

    if ast.IsOPartial:  # Operator * OptGroupItem list
        operator = operatorBaseOfAst(ast.Item1)
        partial_group = [optGroupItemOfAst(item) for item in ast.Item2]
        return Swan.PartialOperator(operator, partial_group)

    if ast.IsONary:  # BinaryOp // ONary is a subset of BinaryOp
        nary = ast.Item
        if nary.IsBPlus:
            return Swan.NAryOperator(Swan.NaryOp.Plus)
        if nary.IsBMult:
            return Swan.NAryOperator(Swan.NaryOp.Mult)
        if nary.IsBLand:
            return Swan.NAryOperator(Swan.NaryOp.Land)
        if nary.IsBLor:
            return Swan.NAryOperator(Swan.NaryOp.Lor)
        if nary.IsBAnd:
            return Swan.NAryOperator(Swan.NaryOp.And)
        if nary.IsBOr:
            return Swan.NAryOperator(Swan.NaryOp.Or)
        if nary.IsBXor:
            return Swan.NAryOperator(Swan.NaryOp.Xor)
        if nary.IsBLxor:
            return Swan.NAryOperator(Swan.NaryOp.Lxor)
        if nary.IsBAroba:
            return Swan.NAryOperator(Swan.NaryOp.Concat)
    if ast.IsOSource:
        id = identifierOfAst(ast.Item)
        return Swan.DataSource(id)
    if ast.IsOOracle:
        id = identifierOfAst(ast.Item)
        return Swan.Oracle(id)


def operatorPrefixOfAst(ast, sizes):
    if ast.IsOPathId:  # PathId
        id = pathIdentifierOfAst(ast.Item)
        return Swan.NamedInstance(id, sizes)

    if ast.IsOPrefixPrimitive:  # PrefixPrimitive
        prefix = ast.Item
        if prefix.IsFlatten:
            return Swan.FlattenOperator(sizes)
        elif prefix.IsPack:
            return Swan.PackOperator(sizes)
        elif prefix.IsReverse:
            return Swan.ReverseOperator(sizes)
        else:  # ast.IsTranspose
            index = prefix.Item
            if index.IsTSList:
                params = [index for index in index.Item1]
            else:
                params = getProtectedString(index.Item)
            return Swan.TransposeOperator(params, sizes)

    if ast.IsORawPrefix or ast.IsORawOpExpr:
        # Protected content, find what it is.
        markup = getMarkup(ast.Item)
        source = getProtectedString(ast.Item)
        if markup == "text":
            # text markup is used for an operator expression
            # which is not between parentheses and not an operator instance.
            origin = Parser.get_source().name
            swan = SwanString(f"{source}", origin)
            op_block = Parser.get_current_parser().operator_block(swan)
            op_block.is_text = True
            # sizes may be defined outside of the operator block (form)
            # Note: having both sizes in text and in the operator block is not allowed
            # and SLS raises an error => we don't check it here, as it is a syntax error
            if sizes:
                op_block._sizes = sizes
            return op_block

        if markup == "op_expr":
            # ORawPrefix is returned for: LP RAW_OPEXPR RP
            # which is an operator expression between parentheses.
            origin = Parser.get_source().name
            swan = SwanString(f"{source}", origin)
            op_expr = Parser.get_current_parser().op_expr(swan)
            op_expr.is_op_expr = True
            return Swan.OperatorExpressionInstance(op_expr, sizes)

        return Swan.ProtectedOpExpr(source, markup)

    # op_expr OOperatorExpr
    op_expr = operatorExprWithSPOfAst(ast.Item)
    return Swan.OperatorExpressionInstance(op_expr, sizes)


def operatorBaseOfAst(ast):
    sizes = [exprOrRawOfAst(sz) for sz in ast.CallSize]
    return operatorPrefixOfAst(ast.CallOp, sizes)


# Expressions or raw
# ------------------
def exprOrRawOfAst(ast):
    if ast.IsExprWithSP:  # of Expr * SourcePosition.t
        return expressionOfAst(ast.Item1)
    return Swan.ProtectedExpr(getProtectedString(ast.Item), getMarkup(ast.Item))


def expressionOfAst(ast):
    if ast.IsEId:  # of PathId
        path_id = pathIdentifierOfAst(ast.Item)
        return Swan.PathIdExpr(path_id)

    elif ast.IsELast:  # of Name
        return Swan.LastExpr(Swan.Identifier(nameOfAst(ast.Item), is_name=True))

    elif ast.IsEBoolLiteral:  # of bool
        return Swan.BooleanLiteral("true" if ast.Item else "false")

    elif ast.IsECharLiteral:  # of string
        return Swan.CharLiteral(ast.Item)

    elif ast.IsENumLiteral:  # of string
        if Swan.SwanRE.is_integer(ast.Item):
            return Swan.IntegerLiteral(ast.Item)
        elif Swan.SwanRE.is_float(ast.Item):
            return Swan.FloatLiteral(ast.Item)
        else:
            raise ScadeOneException(
                f"Invalid numeric literal: {ast.Item}. Expected an integer or a float."
            )

    elif ast.IsEUnaryOp:  # of UnaryOp * ExprOrRaw
        unary_op = unaryOfOfAst(ast.Item1)
        expr = exprOrRawOfAst(ast.Item2)
        if unary_op == Swan.UnaryOp.Pre:
            # Pre operator is a special case we want to extract
            return Swan.PreExpr(expr)
        return Swan.UnaryExpr(unary_op, expr)

    elif ast.IsEBinaryOp:  # of BinaryOp * ExprOrRaw * ExprOrRaw
        binary_op = binaryOpOfAst(ast.Item1)
        left = exprOrRawOfAst(ast.Item2)
        right = exprOrRawOfAst(ast.Item3)

        if binary_op == Swan.BinaryOp.Pre:
            return Swan.PreWithInitialValueExpr(left, right)
        if binary_op == Swan.BinaryOp.Arrow:
            return Swan.InitialValueExpr(left, right)
        if binary_op == Swan.BinaryOp.Concat:
            return Swan.ArrayConcatExpr(left, right)

        return Swan.BinaryExpr(binary_op, left, right)

    elif ast.IsEAt:  # ExprOrRaw * Id
        expr = exprOrRawOfAst(ast.Item1)
        id_ = identifierOfAst(ast.Item2)
        expr.at = id_
        return expr

    elif ast.IsEWhenClock:  # of ExprOrRaw * ClockExpr
        expr = exprOrRawOfAst(ast.Item1)
        ck = clockExprOfAst(ast.Item2)
        return Swan.WhenClockExpr(expr, ck)

    elif ast.IsEWhenMatch:  # of ExprOrRaw * PathId
        expr = exprOrRawOfAst(ast.Item1)
        match = pathIdentifierOfAst(ast.Item2)
        return Swan.WhenMatchExpr(expr, match)

    elif ast.IsECast:  # of ExprOrRaw * TypeExprOrRaw
        expr = exprOrRawOfAst(ast.Item1)
        type = typeOrRawOfAst(ast.Item2)
        return Swan.NumericCast(expr, type)

    elif ast.IsEGroup:  # of Group
        items = [groupItemOfAst(item) for item in ast.Item]
        return Swan.GroupConstructor(Swan.Group(items))

    elif ast.IsEGroupAdapt:  # of ExprOrRaw * GroupAdaptation
        expr = exprOrRawOfAst(ast.Item1)
        adaptation = groupAdaptationOfAst(ast.Item2)
        return Swan.GroupProjection(expr, adaptation)

    ## Composite
    elif ast.IsEStaticProj:  # of ExprOrRaw * LabelOrIndex
        expr = exprOrRawOfAst(ast.Item1)
        labelOrIndex = labelOrIndexOfAst(ast.Item2)
        if labelOrIndex.is_label:
            return Swan.StructProjection(expr, labelOrIndex)
        else:
            return Swan.ArrayProjection(expr, labelOrIndex)

    elif ast.IsEMkGroup:  # of PathIdOrRaw * ExprOrRaw
        name = pathIdentifierOrRawOfAst(ast.Item1)
        expr = exprOrRawOfAst(ast.Item2)
        return Swan.StructDestructor(name, expr)

    elif ast.IsESlice:  # of ExprOrRaw * ExprOrRaw * ExprOrRaw
        expr = exprOrRawOfAst(ast.Item1)
        start = exprOrRawOfAst(ast.Item2)
        end = exprOrRawOfAst(ast.Item3)
        return Swan.Slice(expr, start, end)

    elif ast.IsEDynProj:  # of ExprOrRaw * LabelOrIndex list * ExprOrRaw (* default *)
        expr = exprOrRawOfAst(ast.Item1)
        indices = [labelOrIndexOfAst(item) for item in ast.Item2]
        default = exprOrRawOfAst(ast.Item3)
        return Swan.ProjectionWithDefault(expr, indices, default)

    elif ast.IsEMkArray:  # of ExprOrRaw * ExprOrRaw
        expr = exprOrRawOfAst(ast.Item1)
        size = exprOrRawOfAst(ast.Item2)
        return Swan.ArrayRepetition(expr, size)

    elif ast.IsEMkArrayGroup:  # of Group
        return Swan.ArrayConstructor(groupOfAst(ast.Item))

    elif ast.IsEMkStruct:  # of Group * PathIdOrRaw option
        group = groupOfAst(ast.Item1)
        if id := getValueOf(ast.Item2):
            id = pathIdentifierOrRawOfAst(id)
        return Swan.StructConstructor(group, id)

    elif ast.IsEVariant:  # of PathIdOrRaw * Group
        tag = pathIdentifierOrRawOfAst(ast.Item1)
        group = groupOfAst(ast.Item2)
        return Swan.VariantValue(tag, group)

    elif ast.IsEMkCopy:  # of ExprOrRaw * Modifier list
        expr = exprOrRawOfAst(ast.Item1)
        modifiers = [modifierOfAst(item) for item in ast.Item3]
        return Swan.FunctionalUpdate(expr, ast.Item2, modifiers)

    ## Switch
    elif ast.IsEIfte:  # of ExprOrRaw * ExprOrRaw * ExprOrRaw
        cond_expr = exprOrRawOfAst(ast.Item1)
        then_expr = exprOrRawOfAst(ast.Item2)
        else_expr = exprOrRawOfAst(ast.Item3)
        return Swan.IfteExpr(cond_expr, then_expr, else_expr)

    elif ast.IsECase:  # of ExprOrRaw * (PatternOrRaw * ExprOrRaw) list
        expr = exprOrRawOfAst(ast.Item1)
        patterns = casePatternsOfAst(ast.Item2)
        return Swan.CaseExpr(expr, patterns)

    ## OpCalls & Ports
    elif ast.IsEOpCall:  # of OperatorInstance * Group
        params = groupOfAst(ast.Item2)
        if luid := getValueOf(ast.Item1.OIInstance):
            luid = luidOfAst(luid)
        operator = operatorBaseOfAst(ast.Item1.OIOperator)
        return Swan.OperatorInstanceApplication(operator, params, luid)

    elif ast.IsEPort:  # of Port
        return portOfAst(ast.Item)

    ## Forward loops
    elif ast.IsEForward:
        #  of Luid option * RestartState * ForwardDim list
        # * ForwardBody * ForwardReturnsItem list
        return forwardOfAst(ast)

    elif ast.IsEWindow:  # of ExprOrRaw * Group * Group
        expr = exprOrRawOfAst(ast.Item1)
        params = groupOfAst(ast.Item2)
        init = groupOfAst(ast.Item3)
        return Swan.Window(expr, params, init)

    elif ast.IsEMerge:  # of Group list
        params = [groupOfAst(group) for group in ast.Item]
        return Swan.Merge(params)


def portOfAst(ast):
    if ast.IsInstanceIdLunum:
        lunum = lunumOfAst(ast.Item)
        return Swan.PortExpr(lunum=lunum)
    if ast.IsInstanceIdLuid:
        luid = luidOfAst(ast.Item)
        return Swan.PortExpr(luid=luid)
    elif ast.IsInstanceIdSelf:
        return Swan.PortExpr(is_self=True)
    else:
        raise ScadeOneException("internal error, unexpected instance id")


# Type Expressions
# ============================================================
def predefinedTypeOfAst(ast):
    if ast.IsBool:
        return Swan.BoolType()
    elif ast.IsChar:
        return Swan.CharType()
    elif ast.IsInt8:
        return Swan.Int8Type()
    elif ast.IsInt16:
        return Swan.Int16Type()
    elif ast.IsInt32:
        return Swan.Int32Type()
    elif ast.IsInt64:
        return Swan.Int64Type()
    elif ast.IsUint8:
        return Swan.Uint8Type()
    elif ast.IsUint16:
        return Swan.Uint16Type()
    elif ast.IsUint32:
        return Swan.Uint32Type()
    elif ast.IsUint64:
        return Swan.Uint64Type()
    elif ast.IsFloat32:
        return Swan.Float32Type()
    elif ast.IsFloat64:
        return Swan.Float64Type()


def typeExpressionOfAst(ast):
    if ast.IsTPredefinedType:  # of PredefType
        return predefinedTypeOfAst(ast.Item)

    elif ast.IsTSizedSigned:  # of Expr
        expr = expressionOfAst(ast.Item)
        return Swan.SizedTypeExpression(expr, True)

    elif ast.IsTSizedUnsigned:  # of Expr
        expr = expressionOfAst(ast.Item)
        return Swan.SizedTypeExpression(expr, False)

    elif ast.IsTAlias:  # of PathId
        path_id = pathIdentifierOfAst(ast.Item)
        return Swan.TypeReferenceExpression(path_id)

    elif ast.IsTVar:  # of StringWithSourcePosition
        var = Swan.Identifier(nameOfAst(ast.Item), is_name=True)
        return Swan.VariableTypeExpression(var)

    elif ast.IsTArray:  # of TypeExpr * Expr
        type = typeExpressionOfAst(ast.Item1)
        size = expressionOfAst(ast.Item2)
        return Swan.ArrayTypeExpression(type, size)


def typeOrRawOfAst(ast):
    if ast.IsRawTypeExpr:
        return Swan.ProtectedTypeExpression(getProtectedString(ast.Item))
    return typeExpressionOfAst(ast.Item1)


# Declarations
# ============================================================


# Global declarations
# ------------------------------------------------------------
def constDecl(ast):
    id = identifierOfAst(ast.ConstId)
    pragmas = getPragmasFromIdentifier(ast.ConstId)
    if value := getValueOf(ast.ConstDefinition):
        value = expressionOfAst(value)
    if type := getValueOf(ast.ConstType):
        type = typeExpressionOfAst(type)
    return Swan.ConstDecl(id, type, value, pragmas)


def sensorDecl(ast):
    id = identifierOfAst(ast.SensorId)
    type = typeExpressionOfAst(ast.SensorType)
    pragmas = getPragmasFromIdentifier(ast.SensorId)
    return Swan.SensorDecl(id, type, pragmas)


def structFieldsOfAst(ast):
    def field(ast):
        id = identifierOfAst(ast.Item1)
        pragmas = getPragmasFromIdentifier(ast.Item1)
        type = typeExpressionOfAst(ast.Item2)
        return Swan.StructField(id, type, pragmas)

    fields = [field(f) for f in ast]
    return fields


def typeDecl(ast):
    id = identifierOfAst(ast.TypeId)
    pragmas = getPragmasFromIdentifier(ast.TypeId)
    type_def = None
    if ast.TypeDef.IsTDefNone:
        type_def = None

    elif ast.TypeDef.IsTDefExpr:  # of TypeExpr
        type_expr = typeExpressionOfAst(ast.TypeDef.Item)
        type_def = Swan.ExprTypeDefinition(type_expr)

    elif ast.TypeDef.IsTDefEnum:  # of Id list
        tags = [
            Swan.EnumTag(identifierOfAst(t), getPragmasFromIdentifier(t)) for t in ast.TypeDef.Item
        ]
        type_def = Swan.EnumTypeDefinition(tags)

    elif ast.TypeDef.IsTDefVariant:  # of TypeVariant list

        def variantOfAst(ast):
            tag = identifierOfAst(ast.Item1)
            pragmas = getPragmasFromIdentifier(ast.Item1)
            if ast.Item2.IsVTSimple:
                return Swan.VariantSimple(tag, pragmas)
            elif ast.Item2.IsVTTypeExpr:
                type_expr = typeExpressionOfAst(ast.Item2.Item)
                return Swan.VariantTypeExpression(tag, type_expr, pragmas)
            fields = structFieldsOfAst(ast.Item2.Item)
            struct_decl = Swan.StructTypeDefinition(fields)
            return Swan.VariantStruct(tag, struct_decl, pragmas)

        tags = [variantOfAst(v) for v in ast.TypeDef.Item]
        type_def = Swan.VariantTypeDefinition(tags)

    elif ast.TypeDef.IsTDefStruct:  # of StructField list
        # StructField = Id * TypeExpr
        fields = structFieldsOfAst(ast.TypeDef.Item)
        type_def = Swan.StructTypeDefinition(fields)

    return Swan.TypeDecl(id, type_def, pragmas)


def useDecl(ast) -> Swan.UseDirective:
    path_id = pathIdentifierOfAst(ast.UPath)
    pragmas = getPragmas(ast.UPragmas)
    if alias := getValueOf(ast.UAs):
        alias = identifierOfAst(alias)
    return Swan.UseDirective(path_id, alias, pragmas)


def groupDecl(ast):
    id = identifierOfAst(ast.GroupId)
    pragmas = getPragmasFromIdentifier(ast.GroupId)

    type = groupTypeExprOfAst(ast.GroupType)
    return Swan.GroupDecl(id, type, pragmas)


def groupTypeExprOfAst(ast) -> Swan.GroupTypeExpression:
    if ast.IsGTypeExpr:
        type = typeExpressionOfAst(ast.Item)
        return Swan.TypeGroupTypeExpression(type)
    positional = [groupTypeExprOfAst(pos) for pos in ast.Item1]

    def namedGroupExprOfAst(ast):
        id = identifierOfAst(ast.Item1)
        type = groupTypeExprOfAst(ast.Item2)
        return Swan.NamedGroupTypeExpression(id, type)

    named = [namedGroupExprOfAst(named) for named in ast.Item2]
    return Swan.GroupTypeExpressionList(positional, named)


# Operator declarations and definitions
# ------------------------------------------------------------
def numericKindOfAst(ast):
    if ast.IsNumeric:
        return Swan.NumericKind.Numeric
    if ast.IsInteger:
        return Swan.NumericKind.Integer
    if ast.IsSigned:
        return Swan.NumericKind.Signed
    if ast.IsUnsigned:
        return Swan.NumericKind.Unsigned
    if ast.IsFloat:
        return Swan.NumericKind.Float


def constraintOfAst(ast) -> Swan.TypeConstraint:
    num_kind = numericKindOfAst(ast.Item2)
    if ast.IsTCRaw:
        return Swan.TypeConstraint(getProtectedString(ast.Item1), num_kind)
    type_vars = [typeExpressionOfAst(tv) for tv in ast.Item1]
    return Swan.TypeConstraint(type_vars, num_kind)


def varDeclOfAst(ast) -> Swan.Variable:
    if ast.IsRawVar:
        pragmas = getPragmas(ast.Item2)
        return Swan.ProtectedVariable(getProtectedString(ast.Item1), pragmas)
    var_decl = ast.Item1
    id = identifierOfAst(var_decl.VarId)
    is_clock = var_decl.VarIsClock
    is_modified = var_decl.VarIsStar
    if place := getValueOf(var_decl.VarAt):
        place = identifierOfAst(place)
    pragmas = [p for p in getPragmasFromIdentifier(var_decl.VarId)]
    if type := getValueOf(var_decl.VarType):
        type = groupTypeExprOfAst(type)
    if when := getValueOf(var_decl.VarWhen):
        when = clockExprOfAst(when)
    if default := getValueOf(var_decl.VarDefault):
        default = expressionOfAst(default)
    if last := getValueOf(var_decl.VarLast):
        last = expressionOfAst(last)

    return Swan.VarDecl(id, is_clock, is_modified, place, type, when, default, last, pragmas)


def sizeParameterOfAst(ast) -> Swan.SizeParameter:
    id = identifierOfAst(ast)
    pragmas = getPragmasFromIdentifier(ast)
    return Swan.SizeParameter(id, pragmas)


def operatorInterfaceElementsOfAst(ast):
    inline = ast.OpInline
    kind = ast.OpNode
    name = Swan.Identifier(stringOfStringWithSP(ast.OpId))
    inputs = [varDeclOfAst(sig) for sig in ast.OpInputs]
    for sig in inputs:
        sig.is_input = True
    outputs = [varDeclOfAst(sig) for sig in ast.OpOutputs]
    for sig in outputs:
        sig.is_output = True
    size_parameters = [sizeParameterOfAst(id) for id in ast.OpSizes]
    type_constraints = [constraintOfAst(ct) for ct in ast.OpConstraints]
    if specialization := getValueOf(ast.OpSpecialization):
        specialization = pathIdentifierOrRawOfAst(specialization)
    pragmas = getPragmas(ast.OpPragmas)
    return (
        inline,
        kind,
        name,
        inputs,
        outputs,
        size_parameters,
        type_constraints,
        specialization,
        pragmas,
    )


def operatorDeclarationOfAst(ast):
    (
        inline,
        kind,
        name,
        inputs,
        outputs,
        size_parameters,
        type_constraints,
        specialization,
        pragmas,
    ) = operatorInterfaceElementsOfAst(ast)

    return Swan.OperatorDeclaration(
        id=name,
        is_inlined=inline,
        is_node=kind,
        inputs=inputs,
        outputs=outputs,
        size_parameters=size_parameters,
        type_constraints=type_constraints,
        specialization=specialization,
        pragmas=pragmas,
    )


def emissionBodyOfAst(ast):
    flows = [Swan.Identifier(nameOfAst(sig), is_name=True) for sig in ast.ESignals]
    if condition := getValueOf(ast.EExpr):
        condition = expressionOfAst(condition)
    if luid := getValueOf(ast.ELuid):
        luid = luidOfAst(luid)
    return Swan.EmissionBody(flows, condition, luid)


# Equations
# ------------------------------------------------------------


def lhsOfAst(ast):
    if ast.IsLhsId:
        return Swan.LHSItem(identifierOfAst(ast.Item))
    return Swan.LHSItem()


def equationLhsOfAst(ast):
    if ast.IsLhsEmpty:
        return Swan.EquationLHS([])
    lhs_items = [lhsOfAst(lhs) for lhs in ast.Item]
    return Swan.EquationLHS(lhs_items, ast.IsLhsWithRest)


def equationOfAst(ast):
    if ast.IsEquation:  # of Luid option * Lhs * Expr * SourcePosition.t
        if luid := getValueOf(ast.Item1):
            luid = luidOfAst(luid)
        lhs = equationLhsOfAst(ast.Item2)
        expr = expressionOfAst(ast.Item3)
        return Swan.ExprEquation(lhs, expr, luid)
    if ast.IsSetSensorEquation:
        return Swan.SetSensorEquation(pathIdentifierOfAst(ast.Item1), expressionOfAst(ast.Item2))
    # def_by_case = automaton or activate
    return defByCaseOfAst(ast.Item)


def defByCaseOfAst(ast):
    if ast.IsDAutomaton:  # of Lhs option * StateMachine * SourcePosition.t
        if lhs := getValueOf(ast.Item1):
            lhs = equationLhsOfAst(lhs)
        return stateMachineOfAst(lhs, ast.Item2)

    if ast.DActivate:  # of Lhs option * Activate * SourcePosition.t
        if lhs := getValueOf(ast.Item1):
            lhs = equationLhsOfAst(lhs)
        if ast.Item2.IsActivateIf:
            return activateIfOfAst(lhs, ast.Item2)
        # ast.Item2.IsActivateWhen
        return activateWhenOfAst(lhs, ast.Item2)


# Activate
# ~~~~~~~~


# Activate if
def activateIfOfAst(lhs, ast):
    # ActivateIf of lunum option * luid option * IfActivation
    if lunum := getValueOf(ast.Item1):
        lunum = lunumOfAst(lunum)
    if name := getValueOf(ast.Item2):
        name = luidOfAst(name)
    activation = ifActivationOfAst(ast.Item3)
    return Swan.ActivateIf(activation, lhs, lunum, name)


def ifActivationOfAst(ast):
    branches = [activationBranchOfAst(branch) for branch in ast.IfThenElif]
    else_branch = ifteBranchOfAst(ast.Else)
    branches.append(Swan.IfActivationBranch(None, else_branch))
    return Swan.IfActivation(branches)


def ifteBranchOfAst(ast):
    if ast.IsIfteDataDef:  # of ScopeDefinition
        data_def = scopeOfAst(ast.Item)
        return Swan.IfteDataDef(data_def)
    # ast.IfteBlock of IfActivation
    activation = ifActivationOfAst(ast.Item)
    return Swan.IfteIfActivation(activation)


def activationBranchOfAst(ast):
    expr = exprOrRawOfAst(ast.Item1)
    ifte_branch = ifteBranchOfAst(ast.Item2)
    return Swan.IfActivationBranch(expr, ifte_branch)


# Activate when
def activateWhenOfAst(lhs, ast):
    # ActivateWhen of Lunum option * luid option * WhenActivation
    if lunum := getValueOf(ast.Item1):
        lunum = lunumOfAst(lunum)
    if name := getValueOf(ast.Item2):
        name = luidOfAst(name)
    condition = exprOrRawOfAst(ast.Item3.AWExpr)
    branches = [activateWhenBranchOfAst(branch) for branch in ast.Item3.AWMatches]
    return Swan.ActivateWhen(condition, branches, lhs, lunum, name)


def activateWhenBranchOfAst(ast):
    # ast: PatternOrRaw * ScopeDefinition
    pattern = patternOrRawOfAst(ast.Item1)
    data_def = scopeOfAst(ast.Item2)
    return Swan.ActivateWhenBranch(pattern, data_def)


# State-machine
# ~~~~~~~~~~~~~


# State machine: Intermediate structures and helpers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class InStateTransitionBuilder:
    # Helper to build transitions defined inside a state with automatic priority.

    def __init__(self):
        self.is_strong = None
        self.prio_counter = 0

    def build(self, arrow) -> Swan.Transition:
        """Build a transition from an arrow, giving it an automatic priority."""
        assert self.is_strong is not None, "is_strong must be set before build()"
        transition = transitionOfAst(arrow, self.is_strong)
        self.prio_counter += 1
        transition._priority = Swan.Literal(str(self.prio_counter))
        return transition

    def reset(self):
        self.prio_counter = 0


# State machine: StateMachine and its items
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def stateMachineOfAst(lhs, ast):
    # Lunum option * Luid option * StateMachineItem list
    if lunum := getValueOf(ast.Item1):
        lunum = lunumOfAst(lunum)
    if name := getValueOf(ast.Item2):
        name = luidOfAst(name)

    # Process all items (states and transition declarations)
    items = [stateMachineItemOfAst(item) for item in ast.Item3]
    machine = Swan.StateMachine(lhs, items, lunum, name)

    return machine


def stateMachineItemOfAst(ast) -> Union[Swan.State, Swan.Transition]:
    # StateMachineItem : StateItem | TransitionDecl
    if ast.IsStateItem:
        state = stateOfAst(ast.Item)
        return state

    # Transition declaration.
    # Build the transition and save the source state for later use.
    ast = ast.Item
    source = stateRefOfAst(ast.TSource)
    pragmas = getPragmas(ast.TPragmas)
    transition = transitionOfAst(ast.TArrow, is_strong=ast.TStrong, source=source, pragmas=pragmas)
    return transition


def stateRefOfAst(ast):
    if ast.IsStateRefId:
        return Swan.StateRef(id=identifierOfAst(ast.Item))
    return Swan.StateRef(lunum=lunumOfAst(ast.Item))


# State machine: State
# ~~~~~~~~~~~~~~~~~~~~


def stateOfAst(ast) -> Swan.State:
    # Build a State from ast
    if id := getValueOf(ast.StateId):
        id = identifierOfAst(id)
    if lunum := getValueOf(ast.StateLunum):
        lunum = lunumOfAst(lunum)
    # Helper to give priorities to transitions without explicit priority
    # when transitions are defined in the state itself.
    builder = InStateTransitionBuilder()

    # Weak transitions (Until)
    builder.is_strong = False
    weak = [builder.build(arrow) for arrow in ast.UntilTransitions]
    # Strong transitions (Unless)
    builder.is_strong = True
    builder.reset()
    strong = [builder.build(arrow) for arrow in ast.UnlessTransitions]
    # Other parts of the state
    is_initial = ast.StateIsInitial
    body = stateBodyOfAst(ast.StateBody)
    pragmas = getPragmas(ast.StatePragmas)
    state = Swan.State(id, lunum, strong, body, weak, is_initial, pragmas)
    return state


def stateBodyOfAst(ast):
    # StateBody : actually stored as a Scope
    # even if grammar says StateBody of ScopeSection list
    sections = [scopeSectionOfAst(section) for section in ast.Item1]
    return Swan.Scope(sections)


# State machine: Transition and Fork
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def transitionOfAst(
    ast,
    is_strong: bool,
    source: Optional[Swan.StateRef] = None,
    pragmas: Optional[List[Swan.Pragma]] = None,
) -> Swan.Transition:
    prio = None if ast.APrio == "-1" else Swan.Literal(ast.APrio)
    # Guard may be absent for transition with no condition to avoid (true)
    # or on "else" transition for forks. Else-transition is optional.
    if guard := getValueOf(ast.AGuard):
        guard = exprOrRawOfAst(guard)
    # Action may be absent (None)
    action = scopeOfAst(ast.AAction)
    # End of transition: either a fork or a state
    if fork := getValueOf(ast.AFork):  # AFork: Fork option
        # arrow goes to a fork
        target = forkOfAst(fork, is_strong)
        is_resume = False
    else:
        # arrow goes to a state
        ref_target = getValueOf(ast.ATarget)
        assert ref_target is not None
        target = stateRefOfAst(ref_target)
        is_resume = ast.AIsResume

    transition = Swan.Transition(
        priority=prio,
        is_strong=is_strong,
        guard=guard,
        action=action,
        target=target,
        source=source,
        is_resume=is_resume,
        pragmas=pragmas,
    )
    return transition


def forkOfAst(ast, is_strong: bool) -> Swan.Fork:
    if ast.IsAForkTree:
        # AForkTree of Arrow * Arrow list * Arrow option
        #  if guarded {{elsif guarded}} [else guarded]
        builder = InStateTransitionBuilder()
        builder.is_strong = is_strong
        transitions = [builder.build(ast.Item1)]
        transitions.extend([builder.build(item) for item in ast.Item2])
        if else_arrow := getValueOf(ast.Item3):
            transitions.append(builder.build(else_arrow))
        return Swan.Fork(transitions)

    else:
        # AForkPrio of Arrow list
        # arrow list. All arrows must have a priority.
        transitions = [transitionOfAst(arrow, is_strong) for arrow in ast.Item]
        return Swan.Fork(transitions)


# Diagram
# ---------------------------------------------------------------


def diagramObjectOfAst(ast, is_local=False):
    if lunum := getValueOf(ast.ObjLunum):
        lunum = lunumOfAst(lunum)
    if luid := getValueOf(ast.ObjLuid):
        luid = luidOfAst(luid)

    locals = [diagramObjectOfAst(obj, True) for obj in ast.ObjLocals]
    pragmas = getPragmas(ast.ObjPragmas)

    description = ast.ObjDescription

    if description.IsBExpr:  # ExprOrRaw
        expr = exprOrRawOfAst(description.Item)
        if isinstance(expr, Swan.GroupConstructor):
            group = expr.group
            # todo : check if group is made of lunums
            is_concat = hasattr(group, "items") and all(
                hasattr(item, "expr")
                and isinstance(item.expr, Swan.PortExpr)
                and getattr(item.expr, "lunum", None) is not None
                for item in group.items
            )
            if is_concat:
                return Swan.Concat(group, lunum, luid, locals, pragmas)

        return Swan.ExprBlock(expr, lunum, luid, locals, pragmas)

    if description.IsBDef:  # Lhs * SourcePosition.t
        lhs = equationLhsOfAst(description.Item1)
        return Swan.DefBlock(lhs, lunum, luid, locals, pragmas)

    if description.IsBRawDef:  # Raw.t
        protected = protectedItemOfAst(description.Item)
        return Swan.DefBlock(protected, lunum, luid, locals, pragmas)

    if description.IsBBlock:  # OperatorBlock * SourcePosition.t
        op_block = operatorBlockOfAst(description.Item1)
        old_block_pragmas = getPragmas(description.Item1.OBPragmas)
        pragmas.extend(old_block_pragmas)
        return Swan.Block(op_block, lunum=lunum, luid=luid, locals=locals, pragmas=pragmas)

    if description.IsBWire:  # Connection * Connection list
        source = connectionOfAst(description.Item1)
        targets = [connectionOfAst(conn) for conn in description.Item2]
        return Swan.Wire(source, targets, lunum, luid, locals, pragmas)

    if description.IsBGroup:  # GroupOperation * SourcePosition.t
        ast_op = description.Item1
        if ast_op.IsGByName:
            return Swan.ByName(lunum, luid, locals, pragmas)
        elif ast_op.IsGByPos:
            return Swan.ByPos(lunum, luid, locals, pragmas)
        elif ast_op.IsGNoOp:
            return (
                Swan.Bar(lunum, luid, locals, pragmas)
                if not is_local
                else Swan.GroupBlock(lunum, luid, locals, pragmas)
            )
        elif ast_op.IsGNorm:
            return Swan.GroupNormalize(lunum, luid, locals, pragmas)

    if description.IsBDefByCase:
        def_by_case = defByCaseOfAst(description.Item)
        if isinstance(def_by_case, Swan.StateMachine):
            return Swan.StateMachineBlock(def_by_case, locals, pragmas)
        elif isinstance(def_by_case, Swan.ActivateIf):
            return Swan.ActivateIfBlock(def_by_case, locals, pragmas)
        else:
            return Swan.ActivateWhenBlock(def_by_case, locals, pragmas)

    if description.IsBScopeSection:  # ScopeSection
        section = scopeSectionOfAst(description.Item)
        return Swan.SectionObject(section, locals, pragmas)

    # BSensorLhs of PathId * SourcePosition.t
    # BRawSensorLhs of Raw.t
    if description.IsBSensorLhs:
        path_id = pathIdentifierOfAst(description.Item1)
        return Swan.SetSensorBlock(path_id, lunum, luid, locals, pragmas)

    # BRawSensorLhs of Raw.t
    elif description.IsBRawSensorLhs:
        protected = protectedItemOfAst(description.Item)
        return Swan.SetSensorBlock(protected, lunum, luid, locals, pragmas)

    assert False, "Unexpected diagram object"


def connectionOfAst(ast):
    if ast.IsConnEmpty:
        return Swan.Connection()

    # ConnPort of Port * GroupAdaptation option
    port = portOfAst(ast.Item1)
    if adaptation := getValueOf(ast.Item2):
        adaptation = groupAdaptationOfAst(adaptation)
    return Swan.Connection(port, adaptation)


def operatorBlockOfAst(ast):
    called = ast.OBCalled
    if called.IsCallOperator:  # Operator
        op_block = operatorBaseOfAst(called.Item)
    else:  # CallOperatorExpr of OperatorExprWithSP
        op_block = operatorExprWithSPOfAst(called.Item)
    return op_block


# Scope & sections
# ~~~~~~~~~~~~~~~~
def assertionsOfAst(ast):
    return [
        Swan.Assertion(luidOfAst(prop.VTag), expressionOfAst(prop.VExpr), getPragmas(prop.VPragmas))
        for prop in ast
    ]


def scopeSectionOfAst(ast):
    if ast.IsSEmission:  # EmissionBody list * SourcePosition.t
        emissions = [emissionBodyOfAst(emit) for emit in ast.Item1]
        section = Swan.EmitSection(emissions)
        return section

    if ast.IsSAssume:  # VerifExpr list * SourcePosition.t
        hypotheses = assertionsOfAst(ast.Item1)
        section = Swan.AssumeSection(hypotheses)
        return section

    if ast.IsSAssert:  # VerifExpr list * SourcePosition.t
        assertions = assertionsOfAst(ast.Item1)
        section = Swan.AssertSection(assertions)
        return section

    if ast.IsSGuarantee:  # VerifExpr list * SourcePosition.t
        guarantees = assertionsOfAst(ast.Item1)
        section = Swan.GuaranteeSection(guarantees)
        return section

    if ast.IsSVarList:  # VarOrRaw list
        var_decls = [varDeclOfAst(var) for var in ast.Item]
        section = Swan.VarSection(var_decls)
        return section

    if ast.IsSLet:  # SourcePosition.t * Equation list * SourcePosition.t
        equations = [equationOfAst(eq) for eq in ast.Item2]
        section = Swan.LetSection(equations)
        return section

    if ast.IsSDiagram:  # Diagram
        objects = [diagramObjectOfAst(obj) for obj in ast.Item.DObjects]
        if luid := getValueOf(ast.Item.DLuid):
            luid = luidOfAst(luid)
        section = Swan.Diagram(luid, objects)
        return section

    if ast.IsSRaw:  # Raw.t
        markup = getMarkup(ast.Item)
        content = getProtectedString(ast.Item)
        if markup == "text":
            origin = Parser.get_source().name
            swan = SwanString(f"{content}", origin)
            section = Parser.get_current_parser().scope_section(swan)
            section.is_text = True
            return section
        return Swan.ProtectedSection(getProtectedString(ast.Item))


def scopeOfAst(ast):
    if ast.IsSDEmpty:
        return None

    if ast.IsSDEquation:
        return equationOfAst(ast.Item)

    if ast.IsSDSections:
        sections = [scopeSectionOfAst(section) for section in ast.Item1]
        # diagram context
        pragmas = getPragmas(ast.Item3)
        scope = Swan.Scope(sections, pragmas)
        return scope


def operatorOfAst(ast):
    (
        inline,
        kind,
        name,
        inputs,
        outputs,
        size_parameters,
        type_constraints,
        specialization,
        pragmas,
    ) = operatorInterfaceElementsOfAst(ast)

    def delayed_body(owner: Swan.SwanItem):
        if body := scopeOfAst(ast.OpBody):
            # body can be None
            body.owner = owner
        return body

    return Swan.OperatorDefinition(
        id=name,
        is_inlined=inline,
        is_node=kind,
        inputs=inputs,
        outputs=outputs,
        body=delayed_body,
        size_parameters=size_parameters,
        type_constraints=type_constraints,
        specialization=specialization,
        pragmas=pragmas,
    )


def harnessOfAst(ast):
    name = Swan.Identifier(stringOfStringWithSP(ast.HId))

    def delayed_body(owner: Swan.SwanItem):
        if body := scopeOfAst(ast.HBody):
            # body can be None
            body.owner = owner
        return body

    pragmas = getPragmas(ast.HPragmas)
    return Swan.TestHarness(
        id=name,  # path_id
        body=delayed_body,
        pragmas=pragmas,
    )


# Declaration factory
# ===================


def declarationOfAst(ast):
    """Build a ansys.scadeone.swan construct from an F# ast item

    Parameters
    ----------
    ast : F# object
        Object representing a declaration

    Returns
    -------
    GlobalDeclaration
        GlobalDeclaration derived object

    Raises
    ------
    ScadeOneException
        raise an exception when an invalid object is given
    """
    if ast.IsDConst:
        decls = [constDecl(item) for item in ast.Item1]
        return Swan.ConstDeclarations(decls)

    if ast.IsDGroup:
        decls = [groupDecl(item) for item in ast.Item1]
        return Swan.GroupDeclarations(decls)

    if ast.IsDOperator:
        return operatorOfAst(ast.Item)

    if ast.IsDSignature:
        return operatorDeclarationOfAst(ast.Item)

    if ast.IsDSensor:
        decls = [sensorDecl(item) for item in ast.Item1]
        return Swan.SensorDeclarations(decls)

    if ast.IsDType:
        decls = [typeDecl(item) for item in ast.Item1]
        return Swan.TypeDeclarations(decls)

    if ast.IsDUse:
        return useDecl(ast.Item1)

    if ast.IsDRaw:
        markup = getMarkup(ast.Item1)
        content = getProtectedString(ast.Item1)
        if markup in ("text", "signature"):
            # - text denotes a *textual* operator declaration
            # (full operator or interface) in a module body.
            # It must be syntactically correct (else syntax_text apply)
            # - "signature" denotes a *textual* operator declaration in an interface:
            # It can either syntactically correct or not
            origin = Parser.get_source().name
            swan = SwanString(content, origin)
            # decl is OperatorDefinition or OperatorDeclaration or None
            if decl := Parser.get_current_parser().operator_decl_or_def(swan):
                decl.is_text = True
                return decl
            # parser error => declaration is not correct (definition should be correct by construction)
            if markup == "text":
                raise ScadeOneException(f"invalid text operator declaration: {content}")
            # syntactically incorrect operator declaration, default behavior

        # other protected: const, type, group, sensor, operator declaration.
        pragmas = getPragmas(ast.Item2)
        return Swan.ProtectedDecl(markup, content, pragmas)

    if ast.IsDTestHarness:
        return harnessOfAst(ast.Item)

    raise ScadeOneException(f"unexpected ast class: {type(ast)}")


def allDeclsOfAst(ast):
    use_list = []
    decl_list = []

    for decl in ast.MDecls:
        py_obj = declarationOfAst(decl)
        if isinstance(py_obj, Swan.UseDirective):
            use_list.append(py_obj)
        else:
            decl_list.append(py_obj)
    return (use_list, decl_list)


def pathIdOfString(name: str) -> Swan.PathIdentifier:
    """Create a path identifier from a string

    Parameters
    ----------
    name : str
        Path name with '-' separating namespaces and module/interface
        name

    Returns
    -------
    S.PathIdentifier
         PathIdentifier object from name
    """
    if Swan.PathIdentifier.is_valid_file_path(name):
        id_list = [Swan.Identifier(id) for id in name.split("-")]
        return Swan.PathIdentifier(id_list)
    if Swan.PathIdentifier.is_valid_path(name):
        id_list = [Swan.Identifier(id.strip()) for id in name.split("::")]
        return Swan.PathIdentifier(id_list)
    return Swan.PathIdentifier(name)


def moduleOfAst(name: str, ast):
    path_id = pathIdOfString(name)
    (use_list, decl_list) = allDeclsOfAst(ast)
    pragmas = getPragmas(ast.MPragmas)
    body = Swan.ModuleBody(path_id, use_list, decl_list, pragmas)
    return body


def interfaceOfAst(name, ast):
    path_id = pathIdOfString(name)
    (use_list, decl_list) = allDeclsOfAst(ast)
    pragmas = getPragmas(ast.MPragmas)
    interface = Swan.ModuleInterface(path_id, use_list, decl_list, pragmas)
    return interface


def testOfAst(name: str, ast):
    path_id = pathIdOfString(name)
    (use_list, decl_list) = allDeclsOfAst(ast)
    pragmas = getPragmas(ast.MPragmas)
    test = Swan.TestModule(path_id, use_list, decl_list, pragmas)
    return test
