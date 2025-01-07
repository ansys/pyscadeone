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

# cSpell: ignore Aroba elems OPEXPR Predef prio Verif
# pylint: disable=invalid-name, too-many-lines, no-else-return, too-many-branches,
# pylint: disable=inconsistent-return-statements, too-many-return-statements
# pylint: disable=singleton-comparison, too-many-locals, too-many-statements

"""
The PyOfAst module transforms F# AST into Python ansys.scadeone.core.swan classes.
"""

from typing import cast

# pylint: disable-next=import-error
from ANSYS.SONE.Infrastructure.Services.Serialization.BNF.Parsing import Ast, Raw  # type:ignore

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanString
import ansys.scadeone.core.swan as S

from .parser import Parser


def getValueOf(option):
    """Help to get value from 't option"""
    return option.Value if option else None


def getMarkup(raw):
    return Raw.getMarkup(raw)


def getProtectedString(raw):
    return Raw.getIndentedRawString(raw)


def protectedItemOfAst(raw):
    return S.ProtectedItem(getProtectedString(raw), getMarkup(raw))


def getPragmas(ast_pragmas):
    return [S.Pragma(p) for p in ast_pragmas]


# Identifiers
# ============================================================
def identifierOfAst(ast):
    id = Ast.idName(ast)
    pragmas = getPragmas(Ast.idPragmas(ast))
    return S.Identifier(id, pragmas)


def pathIdentifierOfAst(pathId):
    ids = [identifierOfAst(id) for id in pathId]
    return S.PathIdentifier(ids)


def pathIdentifierOrRawOfAst(pathId):
    if pathId.IsPIOfId:
        return pathIdentifierOfAst(pathId.Item1)
    return S.PathIdentifier(getProtectedString(pathId.Item))


def stringOfStringWithSP(ast):
    return ast.StringData


def instanceIdOfAst(ast) -> str:
    if ast.IsInstanceIdSelf:
        return "self"
    return stringOfStringWithSP(ast.Item)


def nameOfAst(ast) -> str:
    # skip '
    return stringOfStringWithSP(ast)[1:]


def luidOfAst(ast):
    return S.Luid(stringOfStringWithSP(ast))


def lunumOfAst(ast):
    return S.Lunum(stringOfStringWithSP(ast))


# Expressions
# ============================================================


# arithmetic & logical operators
# ------------------------------
def unaryOfOfAst(ast):
    if ast.IsUMinus:
        return S.UnaryOp.Minus
    elif ast.IsUPlus:
        return S.UnaryOp.Plus
    elif ast.IsULnot:
        return S.UnaryOp.Lnot
    elif ast.IsUNot:
        return S.UnaryOp.Not
    elif ast.IsUPre:
        return S.UnaryOp.Pre


def binaryOpOfAst(ast):
    if ast.IsBPlus:
        return S.BinaryOp.Plus
    elif ast.IsBMinus:
        return S.BinaryOp.Minus
    elif ast.IsBMult:
        return S.BinaryOp.Mult
    elif ast.IsBSlash:
        return S.BinaryOp.Slash
    elif ast.IsBMod:
        return S.BinaryOp.Mod
    elif ast.IsBLand:
        return S.BinaryOp.Land
    elif ast.IsBLor:
        return S.BinaryOp.Lor
    elif ast.IsBLxor:
        return S.BinaryOp.Lxor
    elif ast.IsBLsl:
        return S.BinaryOp.Lsl
    elif ast.IsBLsr:
        return S.BinaryOp.Lsr
    elif ast.IsBEqual:
        return S.BinaryOp.Equal
    elif ast.IsBDiff:
        return S.BinaryOp.Diff
    elif ast.IsBLt:
        return S.BinaryOp.Lt
    elif ast.IsBGt:
        return S.BinaryOp.Gt
    elif ast.IsBLeq:
        return S.BinaryOp.Leq
    elif ast.IsBGeq:
        return S.BinaryOp.Geq
    elif ast.IsBAnd:
        return S.BinaryOp.And
    elif ast.IsBOr:
        return S.BinaryOp.Or
    elif ast.IsBXor:
        return S.BinaryOp.Xor
    elif ast.IsBArrow:
        return S.BinaryOp.Arrow
    elif ast.IsBPre:
        return S.BinaryOp.Pre
    elif ast.IsBAroba:
        return S.BinaryOp.Concat


# label, group item
# -----------------
def labelOrIndexOfAst(ast):
    if ast.IsIndex:
        expr = exprOrRawOfAst(ast.Item)
        return S.LabelOrIndex(expr)
    id = identifierOfAst(ast.Item)
    return S.LabelOrIndex(id)


def groupItemOfAst(ast):
    expr = exprOrRawOfAst(ast.Item) if ast.IsGroupItemExpr else exprOrRawOfAst(ast.Item2)
    label = identifierOfAst(ast.Item1) if ast.IsGroupItemLabelExpr else None
    return S.GroupItem(expr, label)


def groupOfAst(ast):
    items = [groupItemOfAst(item) for item in ast]
    return S.Group(items)


# modifiers, patterns
# -------------------
def modifierOfAst(ast):
    new_value = exprOrRawOfAst(ast.Item2)
    if ast.IsModifierRaw:
        return S.Modifier(getProtectedString(ast.Item1), new_value)
    indices = [labelOrIndexOfAst(item) for item in ast.Item1]
    return S.Modifier(indices, new_value)


def casePatternsOfAst(cases):
    def caseOfAst(pattern, expr):
        p_obj = patternOrRawOfAst(pattern)
        e_obj = exprOrRawOfAst(expr)
        return S.CaseBranch(p_obj, e_obj)

    patterns = [caseOfAst(c.Item1, c.Item2) for c in cases]
    return patterns


def patternOrRawOfAst(pattern):
    if pattern.IsPRaw:
        return S.ProtectedPattern(getProtectedString(pattern.Item))

    pattern = pattern.Item1
    if pattern.IsPId:
        tag = pathIdentifierOfAst(pattern.Item)
        return S.PathIdPattern(tag)

    if pattern.IsPVariant:
        tag = pathIdentifierOfAst(pattern.Item)
        return S.VariantPattern(tag, underscore=True)

    if pattern.IsPVariantCapture:
        tag = pathIdentifierOfAst(pattern.Item1)
        if id := getValueOf(pattern.Item2):
            return S.VariantPattern(tag, identifierOfAst(id))
        return S.VariantPattern(tag)

    if pattern.IsPChar:
        return S.CharPattern(pattern.Item)

    if pattern.IsPInt:
        return S.IntPattern(pattern.Item2, pattern.Item1)

    if pattern.IsPBool:
        return S.BoolPattern(pattern.Item)

    if pattern.IsPUscore:
        return S.UnderscorePattern()

    if pattern.IsPDefault:
        return S.DefaultPattern()


# Renamings
# ---------
def renamingOfAst(ast):
    if ast.IsRenamingByPos:  # of string * bool * Id option
        index = S.Literal(ast.Item1)
        is_shortcut = ast.Item2
        if renaming := getValueOf(ast.Item3):
            renaming = identifierOfAst(renaming)
        return S.GroupRenaming(index, renaming, is_shortcut)

    if ast.IsRenamingByName:  #  of Id * bool * Id option
        index = identifierOfAst(ast.Item1)
        is_shortcut = ast.Item2
        if renaming := getValueOf(ast.Item3):
            renaming = identifierOfAst(renaming)
            is_shortcut = index.value == renaming.value
        return S.GroupRenaming(index, renaming, is_shortcut)

    if ast.IsRenamingRaw:  # of SourcePosition.t
        markup = getMarkup(ast.Item)
        content = getProtectedString(ast.Item)
        return S.ProtectedGroupRenaming(content, markup)


def groupAdaptationOfAst(ast):
    renamings = [renamingOfAst(ren) for ren in ast.GRenaming]
    return S.GroupAdaptation(renamings)


# Clock expression
# ----------------
def clockExprOfAst(ast):
    if ast.IsClockId:  # of Id
        return S.ClockExpr(identifierOfAst(ast.Item))
    if ast.IsClockNotId:  # of Id
        return S.ClockExpr(identifierOfAst(ast.Item), is_not=True)
    if ast.IsClockMatch:  # of Id * PatternOrRaw
        pattern = patternOrRawOfAst(ast.Item2)
        return S.ClockExpr(identifierOfAst(ast.Item1), pattern=pattern)


# Forward expression
# ~~~~~~~~~~~~~~~~~~~
def forwardLHSofAst(ast):
    if ast.IsFId:  # of Id
        return S.ForwardLHS(identifierOfAst(ast.Item))
    # FLhsArray of ForwardLhs
    return S.ForwardLHS(forwardLHSofAst(ast.Item))


def forwardElement(ast):
    lhs = forwardLHSofAst(ast.Item1)
    expr = expressionOfAst(ast.Item2)
    return S.ForwardElement(lhs, expr)


def forwardDimOfAst(ast):
    if ast.IsFDim:  # of Expr * SourcePosition.t
        return S.ForwardDim(expressionOfAst(ast.Item1))

    if ast.IsFDimWith:  # of Expr * Id option * (ForwardLhs * Expr) list * SourcePosition.t
        expr = expressionOfAst(ast.Item1)
        if id := getValueOf(ast.Item2):
            id = identifierOfAst(id)
        elems = [forwardElement(elem) for elem in ast.Item3]
        return S.ForwardDim(expr, id, elems)

    # FRaw of Raw.t
    data = getProtectedString(ast.Item1)
    return S.ForwardDim(protected=data)


def forwardBodyOfAst(ast):
    sections = [scopeSectionOfAst(sec) for sec in ast.FScopeSections]
    if until := getValueOf(ast.FUntilCondition):
        until = exprOrRawOfAst(until)
    if unless := getValueOf(ast.FUnlessCondition):
        unless = exprOrRawOfAst(unless)

    return S.ForwardBody(sections, unless, until)


def forwardLastDefaultOfAst(ast):
    if ast.IsFLast:  # of Expr
        return S.ForwardLastDefault(last=expressionOfAst(ast.Item))

    if ast.IsFDefault:  # of Expr
        return S.ForwardLastDefault(default=expressionOfAst(ast.Item))

    if ast.IsFLastPlusDefault:  # of Expr * Expr
        return S.ForwardLastDefault(
            last=expressionOfAst(ast.Item1), default=expressionOfAst(ast.Item2)
        )
    # ast.IsFLastAndDefault: # of Expr
    return S.ForwardLastDefault(shared=expressionOfAst(ast.Item))


def forwardItemClauseOfAst(ast):
    id = identifierOfAst(ast.Item1)
    if last_default := getValueOf(ast.Item2):
        last_default = forwardLastDefaultOfAst(last_default)
    return S.ForwardItemClause(id, last_default)


def forwardArrayClauseOfAst(ast):
    if ast.IsFItemClause:  # of ForwardItemClause
        clause = forwardItemClauseOfAst(ast.Item)
    else:  # ast.IsFArrayClause  of ForwardArrayClause
        clause = forwardArrayClauseOfAst(ast.Item)
    return S.ForwardArrayClause(clause)


def forwardReturnOfAst(ast):
    if ast.IsFRetItemClause:  # of ForwardItemClause * SourcePosition.t
        clause = forwardItemClauseOfAst(ast.Item1)
        return S.ForwardReturnItemClause(clause)
    if ast.IsFRetArrayClause:  # of Id option * ForwardArrayClause * SourcePosition.t
        if id := getValueOf(ast.Item1):
            id = identifierOfAst(id)
        clause = forwardArrayClauseOfAst(ast.Item2)
        return S.ForwardReturnArrayClause(clause, id)
    if ast.IsFRetRaw:  # of Raw.t
        return S.ProtectedForwardReturnItem(getProtectedString(ast.Item))


def forwardOfAst(ast):
    # Luid option * ForwardState * ForwardDim list * ForwardBody * ForwardReturnsItem list
    if luid := getValueOf(ast.Item1):
        luid = luidOfAst(luid)

    if ast.Item2.IsFNone:
        state = S.ForwardState.Nothing
    elif ast.Item2.IsFRestart:
        state = S.ForwardState.Restart
    else:  # IsFResume
        state = S.ForwardState.Resume

    dims = [forwardDimOfAst(dim) for dim in ast.Item3]
    body = forwardBodyOfAst(ast.Item4)
    returns = [forwardReturnOfAst(ret) for ret in ast.Item5]

    return S.Forward(state, dims, body, returns, luid)


# Operator instance & expressions
# -------------------------------
def iteratorOfAst(ast, operator):
    # pylint: disable=possibly-used-before-assignment

    if ast.IsIMap:
        kind = S.IteratorKind.Map
    elif ast.IsIFold:
        kind = S.IteratorKind.Fold
    elif ast.IsIMapi:
        kind = S.IteratorKind.Mapi
    elif ast.IsIFoldi:
        kind = S.IteratorKind.Foldi
    elif ast.IsIMapfold:  # of int
        kind = S.IteratorKind.Mapfold
    elif ast.IsIMapfoldi:  # of int
        kind = S.IteratorKind.Mapfoldi

    return S.Iterator(kind, operator)


def optGroupItemOfAst(ast):
    group_item = groupItemOfAst(ast.Item) if ast.IsOGroupItem else None
    return S.OptGroupItem(group_item)


def operatorExprWithSPOfAst(ast):
    return operatorExprOfAst(ast.OEOpExpr)


def operatorExprOfAst(ast):
    if ast.IsOIterator:  # Iterator * Operator
        operator = operatorBaseOfAst(ast.Item2)
        return iteratorOfAst(ast.Item1, operator)

    if ast.IsOActivateClock:  # Operator * ClockExpr
        operator = operatorBaseOfAst(ast.Item1)
        clock = clockExprOfAst(ast.Item2)
        return S.ActivateClock(operator, clock)

    if ast.IsOActivateCondition:  # Operator * ExprOrRaw * bool * ExprOrRaw
        operator = operatorBaseOfAst(ast.Item1)
        cond = exprOrRawOfAst(ast.Item2)
        is_last = ast.Item3
        default = exprOrRawOfAst(ast.Item4)
        return S.ActivateEvery(operator, cond, is_last, default)

    if ast.IsORestart:  # Operator * ExprOrRaw
        operator = operatorBaseOfAst(ast.Item1)
        condition = exprOrRawOfAst(ast.Item2)
        return S.Restart(operator, condition)

    if ast.IsOLambdaDataDef:  # bool * VarOrRaw list * VarOrRaw list * ScopeDefinition
        is_node = ast.Item1
        inputs = [varDeclOfAst(sig) for sig in ast.Item2]
        outputs = [varDeclOfAst(sig) for sig in ast.Item3]
        data_def = scopeOfAst(ast.Item4)
        return S.AnonymousOperatorWithDataDefinition(is_node, inputs, outputs, data_def)

    if ast.IsOLambdaScopes:  # bool * Id list * ScopeSection list * ExprOrRaw
        is_node = ast.Item1
        params = [identifierOfAst(id) for id in ast.Item2]
        sections = [scopeSectionOfAst(scope) for scope in ast.Item3]
        expr = exprOrRawOfAst(ast.Item4)
        return S.AnonymousOperatorWithExpression(is_node, params, sections, expr)

    if ast.IsOPartial:  # Operator * OptGroupItem list
        operator = operatorBaseOfAst(ast.Item1)
        partial_group = [optGroupItemOfAst(item) for item in ast.Item2]
        return S.Partial(operator, partial_group)

    if ast.IsONary:  # BinaryOp // ONary is a subset of BinaryOp
        nary = ast.Item
        if nary.IsBPlus:
            return S.NAryOperator(S.NaryOp.Plus)
        if nary.IsBMult:
            return S.NAryOperator(S.NaryOp.Mult)
        if nary.IsBLand:
            return S.NAryOperator(S.NaryOp.Land)
        if nary.IsBLor:
            return S.NAryOperator(S.NaryOp.Lor)
        if nary.IsBAnd:
            return S.NAryOperator(S.NaryOp.And)
        if nary.IsBOr:
            return S.NAryOperator(S.NaryOp.Or)
        if nary.IsBXor:
            return S.NAryOperator(S.NaryOp.Xor)
        if nary.IsBAroba:
            return S.NAryOperator(S.NaryOp.Concat)
    if ast.IsOSource:
        return S.Source(ast.Item)
    if ast.IsOOracle:
        return S.Oracle(ast.Item)


def operatorPrefixOfAst(ast, sizes, pragmas):
    if ast.IsOPathId:  # PathId
        id = pathIdentifierOfAst(ast.Item)
        return S.PathIdOpCall(id, sizes, pragmas)

    if ast.IsOPrefixPrimitive:  # PrefixPrimitive
        prefix = ast.Item
        if prefix.IsFlatten:
            kind = S.PrefixPrimitiveKind.Flatten
        elif prefix.IsPack:
            kind = S.PrefixPrimitiveKind.Pack
        elif prefix.IsReverse:
            kind = S.PrefixPrimitiveKind.Reverse
        else:  # ast.IsTranspose
            kind = S.PrefixPrimitiveKind.Transpose

        if kind != S.PrefixPrimitiveKind.Transpose:
            return S.PrefixPrimitive(kind, sizes)
        # Transpose
        index = prefix.Item
        if index.IsTSList:
            params = [int(index) for index in index.Item1]
        else:
            params = getProtectedString(index.Item)
        return S.Transpose(params, sizes)

    if ast.IsORawPrefix or ast.IsORawOpExpr:
        # Protected content, find what it is.
        markup = getMarkup(ast.Item)
        source = getProtectedString(ast.Item)
        if markup == "text":
            origin = Parser.get_source().name
            swan = SwanString(f"{source}", origin)
            op_block = Parser.get_current_parser().operator_block(swan)
            return op_block

        if markup == "op_expr":
            # ORawPrefix is returned for: LP RAW_OPEXPR RP
            origin = Parser.get_source().name
            swan = SwanString(f"{source}", origin)
            op_expr = Parser.get_current_parser().op_expr(swan)
            return S.PrefixOperatorExpression(op_expr, sizes)

        return S.ProtectedOpExpr(source, markup)

    # op_expr OOperatorExpr
    op_expr = operatorExprWithSPOfAst(ast.Item)
    return S.PrefixOperatorExpression(op_expr, sizes)


def operatorBaseOfAst(ast):
    sizes = [exprOrRawOfAst(sz) for sz in ast.CallSize]
    pragmas = getPragmas(ast.CallPragmas)
    return operatorPrefixOfAst(ast.CallOp, sizes, pragmas)


# Expressions or raw
# ------------------
def exprOrRawOfAst(ast):
    if ast.IsExprWithSP:  # of Expr * SourcePosition.t
        return expressionOfAst(ast.Item1)
    return S.ProtectedExpr(getProtectedString(ast.Item), getMarkup(ast.Item))


def expressionOfAst(ast):
    if ast.IsEId:  #  of PathId
        path_id = pathIdentifierOfAst(ast.Item)
        return S.PathIdExpr(path_id)

    elif ast.IsELast:  #  of Name
        return S.LastExpr(S.Identifier(nameOfAst(ast.Item), is_name=True))

    elif ast.IsEBoolLiteral:  #  of bool
        return S.Literal("true" if ast.Item else "false")

    elif ast.IsECharLiteral:  #  of string
        return S.Literal(ast.Item)

    elif ast.IsENumLiteral:  #  of string
        return S.Literal(ast.Item)

    elif ast.IsEUnaryOp:  #  of UnaryOp * ExprOrRaw
        return S.UnaryExpr(unaryOfOfAst(ast.Item1), exprOrRawOfAst(ast.Item2))

    elif ast.IsEBinaryOp:  #  of BinaryOp * ExprOrRaw * ExprOrRaw
        return S.BinaryExpr(
            binaryOpOfAst(ast.Item1), exprOrRawOfAst(ast.Item2), exprOrRawOfAst(ast.Item3)
        )

    elif ast.IsEWhenClock:  #  of ExprOrRaw * ClockExpr
        expr = exprOrRawOfAst(ast.Item1)
        ck = clockExprOfAst(ast.Item2)
        return S.WhenClockExpr(expr, ck)

    elif ast.IsEWhenMatch:  #  of ExprOrRaw * PathId
        expr = exprOrRawOfAst(ast.Item1)
        match = pathIdentifierOfAst(ast.Item2)
        return S.WhenMatchExpr(expr, match)

    elif ast.IsECast:  #  of ExprOrRaw * TypeExprOrRaw
        expr = exprOrRawOfAst(ast.Item1)
        type = typeOrRawOfAst(ast.Item2)
        return S.NumericCast(expr, type)

    elif ast.IsEGroup:  #  of Group
        items = [groupItemOfAst(item) for item in ast.Item]
        return S.GroupConstructor(S.Group(items))

    elif ast.IsEGroupAdapt:  #  of ExprOrRaw * GroupAdaptation
        expr = exprOrRawOfAst(ast.Item1)
        adaptation = groupAdaptationOfAst(ast.Item2)
        return S.GroupProjection(expr, adaptation)

    ## Composite
    elif ast.IsEStaticProj:  #  of ExprOrRaw * LabelOrIndex
        expr = exprOrRawOfAst(ast.Item1)
        labelOrIndex = labelOrIndexOfAst(ast.Item2)
        if labelOrIndex.is_label:
            return S.StructProjection(expr, labelOrIndex)
        else:
            return S.ArrayProjection(expr, labelOrIndex)

    elif ast.IsEMkGroup:  #  of PathIdOrRaw * ExprOrRaw
        name = pathIdentifierOrRawOfAst(ast.Item1)
        expr = exprOrRawOfAst(ast.Item2)
        return S.StructDestructor(name, expr)

    elif ast.IsESlice:  #  of ExprOrRaw * ExprOrRaw * ExprOrRaw
        expr = exprOrRawOfAst(ast.Item1)
        start = exprOrRawOfAst(ast.Item2)
        end = exprOrRawOfAst(ast.Item3)
        return S.Slice(expr, start, end)

    elif ast.IsEDynProj:  #  of ExprOrRaw * LabelOrIndex list * ExprOrRaw (* default *)
        expr = exprOrRawOfAst(ast.Item1)
        indices = [labelOrIndexOfAst(item) for item in ast.Item2]
        default = exprOrRawOfAst(ast.Item3)
        return S.ProjectionWithDefault(expr, indices, default)

    elif ast.IsEMkArray:  #  of ExprOrRaw * ExprOrRaw
        expr = exprOrRawOfAst(ast.Item1)
        size = exprOrRawOfAst(ast.Item2)
        return S.ArrayRepetition(expr, size)

    elif ast.IsEMkArrayGroup:  #  of Group
        return S.ArrayConstructor(groupOfAst(ast.Item))

    elif ast.IsEMkStruct:  #  of Group * PathIdOrRaw option
        group = groupOfAst(ast.Item1)
        if id := getValueOf(ast.Item2):
            id = pathIdentifierOrRawOfAst(id)
        return S.StructConstructor(group, id)

    elif ast.IsEVariant:  #  of PathIdOrRaw * Group
        tag = pathIdentifierOrRawOfAst(ast.Item1)
        group = groupOfAst(ast.Item2)
        return S.VariantValue(tag, group)

    elif ast.IsEMkCopy:  #  of ExprOrRaw * Modifier list
        expr = exprOrRawOfAst(ast.Item1)
        modifiers = [modifierOfAst(item) for item in ast.Item2]
        return S.FunctionalUpdate(expr, modifiers)

    ## Switch
    elif ast.IsEIfte:  #  of ExprOrRaw * ExprOrRaw * ExprOrRaw
        cond_expr = exprOrRawOfAst(ast.Item1)
        then_expr = exprOrRawOfAst(ast.Item2)
        else_expr = exprOrRawOfAst(ast.Item3)
        return S.IfteExpr(cond_expr, then_expr, else_expr)

    elif ast.IsECase:  #  of ExprOrRaw * (PatternOrRaw * ExprOrRaw) list
        expr = exprOrRawOfAst(ast.Item1)
        patterns = casePatternsOfAst(ast.Item2)
        return S.CaseExpr(expr, patterns)

    ## OpCalls & Ports
    elif ast.IsEOpCall:  #  of OperatorInstance * Group
        params = groupOfAst(ast.Item2)
        if luid := getValueOf(ast.Item1.OIInstance):
            luid = luidOfAst(luid)
        operator = operatorBaseOfAst(ast.Item1.OIOperator)
        return S.OperatorInstance(operator, params, luid)

    elif ast.IsEPort:  #  of Port
        return portOfAst(ast.Item)

    ## Forward loops
    elif ast.IsEForward:
        #  of Luid option * ForwardState * ForwardDim list
        # * ForwardBody * ForwardReturnsItem list
        return forwardOfAst(ast)

    elif ast.IsEWindow:  #  of ExprOrRaw * Group * Group
        expr = exprOrRawOfAst(ast.Item1)
        params = groupOfAst(ast.Item2)
        init = groupOfAst(ast.Item3)
        return S.Window(expr, params, init)

    elif ast.IsEMerge:  #  of Group list
        params = [groupOfAst(group) for group in ast.Item]
        return S.Merge(params)


def portOfAst(ast):
    if ast.IsInstanceIdLunum:
        lunum = lunumOfAst(ast.Item)
        return S.PortExpr(lunum=lunum)
    if ast.IsInstanceIdLuid:
        luid = luidOfAst(ast.Item)
        return S.PortExpr(luid=luid)
    elif ast.IsInstanceIdSelf:
        return S.PortExpr(is_self=True)
    else:
        raise ScadeOneException("internal error, unexpected instance id")


# Type Expressions
# ============================================================
def predefinedTypeOfAst(ast):
    if ast.IsBool:
        return S.BoolType()
    elif ast.IsChar:
        return S.CharType()
    elif ast.IsInt8:
        return S.Int8Type()
    elif ast.IsInt16:
        return S.Int16Type()
    elif ast.IsInt32:
        return S.Int32Type()
    elif ast.IsInt64:
        return S.Int64Type()
    elif ast.IsUint8:
        return S.Uint8Type()
    elif ast.IsUint16:
        return S.Uint16Type()
    elif ast.IsUint32:
        return S.Uint32Type()
    elif ast.IsUint64:
        return S.Uint64Type()
    elif ast.IsFloat32:
        return S.Float32Type()
    elif ast.IsFloat64:
        return S.Float64Type()


def typeExpressionOfAst(ast):
    if ast.IsTPredefinedType:  # of PredefType
        return predefinedTypeOfAst(ast.Item)

    elif ast.IsTSizedSigned:  # of Expr
        expr = expressionOfAst(ast.Item)
        return S.SizedTypeExpression(expr, True)

    elif ast.IsTSizedUnsigned:  # of Expr
        expr = expressionOfAst(ast.Item)
        return S.SizedTypeExpression(expr, False)

    elif ast.IsTAlias:  # of PathId
        path_id = pathIdentifierOfAst(ast.Item)
        return S.TypeReferenceExpression(path_id)

    elif ast.IsTVar:  # of StringWithSourcePosition
        var = S.Identifier(nameOfAst(ast.Item), is_name=True)
        return S.VariableTypeExpression(var)

    elif ast.IsTArray:  # of TypeExpr * Expr
        type = typeExpressionOfAst(ast.Item1)
        size = expressionOfAst(ast.Item2)
        return S.ArrayTypeExpression(type, size)


def typeOrRawOfAst(ast):
    if ast.IsRawTypeExpr:
        return S.ProtectedTypeExpr(getProtectedString(ast.Item))
    return typeExpressionOfAst(ast.Item1)


# Declarations
# ============================================================


# Global declarations
# ------------------------------------------------------------
def constDecl(ast):
    id = identifierOfAst(ast.ConstId)
    if value := getValueOf(ast.ConstDefinition):
        value = expressionOfAst(value)
    if type := getValueOf(ast.ConstType):
        type = typeExpressionOfAst(type)
    return S.ConstDecl(id, type, value)


def sensorDecl(ast):
    id = identifierOfAst(ast.SensorId)
    type = typeExpressionOfAst(ast.SensorType)
    return S.SensorDecl(id, type)


def structFieldsOfAst(ast):
    def field(ast):
        id = identifierOfAst(ast.Item1)
        type = typeExpressionOfAst(ast.Item2)
        return S.StructField(id, type)

    fields = [field(f) for f in ast]
    return fields


def typeDecl(ast):
    id = identifierOfAst(ast.TypeId)
    if ast.TypeDef.IsTDefNone:
        return S.TypeDecl(id)

    elif ast.TypeDef.IsTDefExpr:  # of TypeExpr
        type_expr = typeExpressionOfAst(ast.TypeDef.Item)
        type_def = S.ExprTypeDefinition(type_expr)
        return S.TypeDecl(id, type_def)

    elif ast.TypeDef.IsTDefEnum:  # of Id list
        tags = [identifierOfAst(t) for t in ast.TypeDef.Item]
        enum_decl = S.EnumTypeDefinition(tags)
        return S.TypeDecl(id, enum_decl)

    elif ast.TypeDef.IsTDefVariant:  # of TypeVariant list

        def variantOfAst(ast):
            tag = identifierOfAst(ast.Item1)
            if ast.Item2.IsVTSimple:
                return S.VariantSimple(tag)
            elif ast.Item2.IsVTTypeExpr:
                type_expr = typeExpressionOfAst(ast.Item2.Item)
                return S.VariantTypeExpr(tag, type_expr)
            fields = structFieldsOfAst(ast.Item2.Item)
            return S.VariantStruct(tag, fields)

        tags = [variantOfAst(v) for v in ast.TypeDef.Item]
        variant_decl = S.VariantTypeDefinition(tags)
        return S.TypeDecl(id, variant_decl)

    elif ast.TypeDef.IsTDefStruct:  # of StructField list
        # StructField = Id * TypeExpr
        fields = structFieldsOfAst(ast.TypeDef.Item)
        struct_decl = S.StructTypeDefinition(fields)
        return S.TypeDecl(id, struct_decl)


def useDecl(ast) -> S.UseDirective:
    path_id = pathIdentifierOfAst(ast.UPath)
    if alias := getValueOf(ast.UAs):
        alias = identifierOfAst(alias)
    return S.UseDirective(path_id, alias)


def groupDecl(ast):
    id = identifierOfAst(ast.GroupId)
    type = groupTypeExprOfAst(ast.GroupType)
    return S.GroupDecl(id, type)


def groupTypeExprOfAst(ast) -> S.GroupTypeExpression:
    if ast.IsGTypeExpr:
        type = typeExpressionOfAst(ast.Item)
        return S.TypeGroupTypeExpression(type)
    positional = [groupTypeExprOfAst(pos) for pos in ast.Item1]

    def namedGroupExprOfAst(ast):
        id = identifierOfAst(ast.Item1)
        type = groupTypeExprOfAst(ast.Item2)
        return S.NamedGroupTypeExpression(id, type)

    named = [namedGroupExprOfAst(named) for named in ast.Item2]
    return S.GroupTypeExpressionList(positional, named)


# Operator & Signature declarations
# ------------------------------------------------------------
def numericKindOfAst(ast):
    if ast.IsNumeric:
        return S.NumericKind.Numeric
    if ast.IsInteger:
        return S.NumericKind.Integer
    if ast.IsSigned:
        return S.NumericKind.Signed
    if ast.IsUnsigned:
        return S.NumericKind.Unsigned
    if ast.IsFloat:
        return S.NumericKind.Float


def constraintOfAst(ast) -> S.TypeConstraint:
    num_kind = numericKindOfAst(ast.Item2)
    if ast.IsTCRaw:
        return S.TypeConstraint(getProtectedString(ast.Item1), num_kind)
    type_vars = [typeExpressionOfAst(tv) for tv in ast.Item1]
    return S.TypeConstraint(type_vars, num_kind)


def isProbePragma(p: S.Pragma):
    d = p.extract()
    return d == ("cg", "probe")


def varDeclOfAst(ast) -> S.Variable:
    if ast.IsRawVar:
        return S.ProtectedVariable(getProtectedString(ast.Item))
    var_decl = ast.Item1
    id = identifierOfAst(var_decl.VarId)
    is_clock = var_decl.VarIsClock
    is_probe = var_decl.VarIsProbe
    if is_probe:
        id._pragmas = [p for p in id.pragmas if not isProbePragma(p)]
    if type := getValueOf(var_decl.VarType):
        type = groupTypeExprOfAst(type)
    if when := getValueOf(var_decl.VarWhen):
        when = clockExprOfAst(when)
    if default := getValueOf(var_decl.VarDefault):
        default = expressionOfAst(default)
    if last := getValueOf(var_decl.VarLast):
        last = expressionOfAst(last)

    return S.VarDecl(id, is_clock, is_probe, type, when, default, last)


def signatureElementsOfAst(ast):
    inline = ast.OpInline
    kind = ast.OpNode
    name = S.Identifier(stringOfStringWithSP(ast.OpId))
    inputs = [varDeclOfAst(sig) for sig in ast.OpInputs]
    for sig in inputs:
        sig.is_input = True
    outputs = [varDeclOfAst(sig) for sig in ast.OpOutputs]
    for sig in outputs:
        sig.is_output = True
    sizes = [identifierOfAst(id) for id in ast.OpSizes]
    constraints = [constraintOfAst(ct) for ct in ast.OpConstraints]
    if specialization := getValueOf(ast.OpSpecialization):
        specialization = pathIdentifierOrRawOfAst(specialization)
    pragmas = getPragmas(ast.OpPragmas)
    return (inline, kind, name, inputs, outputs, sizes, constraints, specialization, pragmas)


def signatureOfAst(ast):
    (inline, kind, name, inputs, outputs, sizes, constraints, specialization, pragmas) = (
        signatureElementsOfAst(ast)
    )

    return S.Signature(
        id=name,
        has_inline=inline,
        is_node=kind,
        inputs=inputs,
        outputs=outputs,
        sizes=sizes,
        constraints=constraints,
        specialization=specialization,
        pragmas=pragmas,
    )


def emissionBodyOfAst(ast):
    flows = [S.Identifier(nameOfAst(sig), is_name=True) for sig in ast.ESignals]
    if condition := getValueOf(ast.EExpr):
        condition = expressionOfAst(condition)
    if luid := getValueOf(ast.ELuid):
        luid = luidOfAst(luid)
    return S.EmissionBody(flows, condition, luid)


# Equations
# ------------------------------------------------------------


def lhsOfAst(ast):
    if ast.IsLhsId:
        return S.LHSItem(identifierOfAst(ast.Item))
    return S.LHSItem()


def equationLhsOfAst(ast):
    if ast.IsLhsEmpty:
        return S.EquationLHS([])
    lhs_items = [lhsOfAst(lhs) for lhs in ast.Item]
    return S.EquationLHS(lhs_items, ast.IsLhsWithRest)


def equationOfAst(ast):
    if ast.IsEquation:  # of Luid option * Lhs * Expr * SourcePosition.t
        if luid := getValueOf(ast.Item1):
            luid = luidOfAst(luid)
        lhs = equationLhsOfAst(ast.Item2)
        expr = expressionOfAst(ast.Item3)
        return S.ExprEquation(lhs, expr, luid)
    if ast.IsSetSensorEquation:
        return S.SetSensorEquation(pathIdentifierOfAst(ast.Item1), expressionOfAst(ast.Item2))
    # def_by_case = automaton or activate
    return defByCaseOfAst(ast.Item, True)


def defByCaseOfAst(ast, is_equation=False):
    if ast.IsDAutomaton:  # of Lhs option * StateMachine * SourcePosition.t
        if lhs := getValueOf(ast.Item1):
            lhs = equationLhsOfAst(lhs)
        return stateMachineOfAst(lhs, ast.Item2, is_equation)

    if ast.DActivate:  # of Lhs option * Activate * SourcePosition.t
        if lhs := getValueOf(ast.Item1):
            lhs = equationLhsOfAst(lhs)
        if ast.Item2.IsActivateIf:
            return activateIfOfAst(lhs, ast.Item2, is_equation)
        # ast.Item2.IsActivateWhen
        return activateWhenOfAst(lhs, ast.Item2, is_equation)


# Activate
# ~~~~~~~~


# Activate if
def activateIfOfAst(lhs, ast, is_equation):
    # ActivateIf of luid option * IfActivation
    if name := getValueOf(ast.Item1):
        name = luidOfAst(name)
    activation = ifActivationOfAst(ast.Item2)
    return S.ActivateIf(activation, lhs, name, is_equation)


def ifActivationOfAst(ast):
    branches = [activationBranchOfAst(branch) for branch in ast.IfThenElif]
    else_branch = ifteBranchOfAst(ast.Else)
    branches.append(S.IfActivationBranch(None, else_branch))
    return S.IfActivation(branches)


def ifteBranchOfAst(ast):
    if ast.IsIfteDataDef:  # of ScopeDefinition
        data_def = scopeOfAst(ast.Item)
        return S.IfteDataDef(data_def)
    # ast.IfteBlock of IfActivation
    activation = ifActivationOfAst(ast.Item)
    return S.IfteIfActivation(activation)


def activationBranchOfAst(ast):
    expr = exprOrRawOfAst(ast.Item1)
    ifte_branch = ifteBranchOfAst(ast.Item2)
    return S.IfActivationBranch(expr, ifte_branch)


# Activate when
def activateWhenOfAst(lhs, ast, is_equation):
    # ActivateWhen of luid option * WhenActivation
    if name := getValueOf(ast.Item1):
        name = luidOfAst(name)
    condition = exprOrRawOfAst(ast.Item2.AWExpr)
    branches = [activateWhenBranchOfAst(branch) for branch in ast.Item2.AWMatches]
    return S.ActivateWhen(condition, branches, lhs, name, is_equation)


def activateWhenBranchOfAst(ast):
    # ast: PatternOrRaw * ScopeDefinition
    pattern = patternOrRawOfAst(ast.Item1)
    data_def = scopeOfAst(ast.Item2)
    return S.ActivateWhenBranch(pattern, data_def)


# State-machine
# ~~~~~~~~~~~~~


def stateMachineOfAst(lhs, ast, is_equation):
    if name := getValueOf(ast.Item1):
        name = luidOfAst(name)
    items = [stateMachineItemOfAst(item) for item in ast.Item2]
    machine = S.StateMachine(lhs, items, name, is_equation)
    return machine


def stateRefOfAst(ast):
    if ast.IsStateRefId:
        return S.StateRef(id=identifierOfAst(ast.Item))
    return S.StateRef(lunum=lunumOfAst(ast.Item))


def stateMachineItemOfAst(ast):
    if ast.IsStateItem:
        ast = ast.Item
        if id := getValueOf(ast.StateId):
            id = identifierOfAst(id)
        if lunum := getValueOf(ast.StateLunum):
            lunum = lunumOfAst(lunum)
        weak = [S.Transition(arrowOfAst(arrow)) for arrow in ast.UntilTransitions]
        strong = [S.Transition(arrowOfAst(arrow)) for arrow in ast.UnlessTransitions]
        is_initial = ast.StateIsInitial
        sections = stateBodyOfAst(ast.StateBody)
        pragmas = getPragmas(ast.StatePragmas)
        state = S.State(id, lunum, strong, sections, weak, is_initial, pragmas)
        return state

    # Transition declaration
    ast = ast.Item
    source = stateRefOfAst(ast.TSource)
    is_strong = ast.TStrong
    spec = arrowSpecOfAst(ast.TArrow)
    pragmas = getPragmas(ast.TPragmas)

    return S.TransitionDecl(spec["prio"], S.Transition(spec["arrow"], pragmas), is_strong, source)


def arrowOfAst(ast):
    spec = arrowSpecOfAst(ast)
    return spec["arrow"]


def arrowSpecOfAst(ast):
    prio = None if ast.APrio == "-1" else S.Literal(ast.APrio)

    if guard := getValueOf(ast.AGuard):
        guard = exprOrRawOfAst(guard)
    action = scopeOfAst(ast.AAction)

    arrow_target = None
    arrow_fork = None

    if fork := getValueOf(ast.AFork):  # AFork: Fork option
        if fork.IsAForkTree:
            # AForkTree of Arrow * Arrow list * Arrow option
            #  if guarded {{elsif guarded}} [else guarded]
            if_arrow = arrowOfAst(fork.Item1)
            elsif_arrows = [arrowOfAst(item) for item in fork.Item2]
            if else_arrow := getValueOf(fork.Item3):
                else_arrow = arrowOfAst(else_arrow)
            arrow_fork = S.ForkTree(if_arrow, elsif_arrows, else_arrow)

        else:
            # AForkPrio of Arrow list
            forks = [forkWithPrioFromAst(arrow) for arrow in fork.Item]
            arrow_fork = S.ForkPriorityList(forks)

    else:  # state
        target = getValueOf(ast.ATarget)
        assert target is not None
        target = stateRefOfAst(target)
        is_resume = ast.AIsResume
        arrow_target = S.Target(target, is_resume)

    # For Fork with priority: priority if guarded_arrow | priority else arrow
    is_if = ast.AIf

    return {"arrow": S.Arrow(guard, action, arrow_target, arrow_fork), "is_if": is_if, "prio": prio}


def forkWithPrioFromAst(ast):
    arrow_spec = arrowSpecOfAst(ast)
    return S.ForkWithPriority(arrow_spec["prio"], arrow_spec["arrow"], arrow_spec["is_if"])


def stateBodyOfAst(ast):
    # StateBody : ScopeDefinition
    # but ScadeDefinition is as SDSections
    sections = [scopeSectionOfAst(section) for section in ast.Item1]
    return sections


# Diagram
# ---------------------------------------------------------------


def diagramObjectOfAst(ast):
    if lunum := getValueOf(ast.ObjLunum):
        lunum = lunumOfAst(lunum)
    if luid := getValueOf(ast.ObjLuid):
        luid = luidOfAst(luid)

    locals = [diagramObjectOfAst(obj) for obj in ast.ObjLocals]
    pragmas = getPragmas(ast.ObjPragmas)

    description = ast.ObjDescription

    if description.IsBExpr:  # ExprOrRaw
        expr = exprOrRawOfAst(description.Item)
        return S.ExprBlock(expr, lunum, luid, locals, pragmas)

    if description.IsBDef:  # Lhs * SourcePosition.t
        lhs = equationLhsOfAst(description.Item1)
        return S.DefBlock(lhs, lunum, luid, locals, pragmas)

    if description.IsBRawDef:  # Raw.t
        protected = protectedItemOfAst(description.Item)
        return S.DefBlock(protected, lunum, luid, locals, pragmas)

    if description.IsBBlock:  # OperatorBlock * SourcePosition.t
        op_block = operatorBlockOfAst(description.Item1)
        return S.Block(op_block, lunum=lunum, luid=luid, locals=locals, pragmas=pragmas)

    if description.IsBWire:  # Connection * Connection list
        source = connectionOfAst(description.Item1)
        targets = [connectionOfAst(conn) for conn in description.Item2]
        return S.Wire(source, targets, lunum, locals, pragmas)

    if description.IsBGroup:  # GroupOperation * SourcePosition.t
        ast_op = description.Item1
        if ast_op.IsGByName:
            operation = S.GroupOperation.ByName
        elif ast_op.IsGByPos:
            operation = S.GroupOperation.ByPos
        elif ast_op.IsGNoOp:
            operation = S.GroupOperation.NoOp
        else:  # IsGNorm
            operation = S.GroupOperation.Normalize

        return S.Bar(operation, lunum, locals, pragmas)

    if description.IsBDefByCase:
        def_by_case = defByCaseOfAst(description.Item)
        if isinstance(def_by_case, S.StateMachine):
            return S.StateMachineBlock(def_by_case, locals, pragmas)
        elif isinstance(def_by_case, S.ActivateIf):
            return S.ActivateIfBlock(def_by_case, locals, pragmas)
        else:
            return S.ActivateWhenBlock(def_by_case, locals, pragmas)

    if description.IsBScopeSection:  # ScopeSection
        section = scopeSectionOfAst(description.Item)
        return S.SectionBlock(section, locals, pragmas)

    # TODO BSensorLhs, BSensorLhs


def connectionOfAst(ast):
    if ast.IsConnEmpty:
        return S.Connection()

    # ConnPort of Port * GroupAdaptation option
    port = portOfAst(ast.Item1)
    if adaptation := getValueOf(ast.Item2):
        adaptation = groupAdaptationOfAst(adaptation)
    return S.Connection(port, adaptation)


def operatorBlockOfAst(ast):
    called = ast.OBCalled
    if called.IsCallOperator:  # Operator
        op_block = operatorBaseOfAst(called.Item)
        if isinstance(op_block, S.PathIdOpCall):
            cast(S.PathIdOpCall, op_block).pragmas.extend(getPragmas(ast.OBPragmas))
    else:  # CallOperatorExpr of OperatorExprWithSP
        op_block = operatorExprWithSPOfAst(called.Item)
    return op_block


# Scope & sections
# ~~~~~~~~~~~~~~~~
def scopeSectionOfAst(ast):
    if ast.IsSEmission:  # EmissionBody list * SourcePosition.t
        emissions = [emissionBodyOfAst(emit) for emit in ast.Item1]
        section = S.EmitSection(emissions)
        return section

    if ast.IsSAssume:  # VerifExpr list * SourcePosition.t
        hypotheses = [
            S.FormalProperty(luidOfAst(prop.VTag), expressionOfAst(prop.VExpr))
            for prop in ast.Item1
        ]
        section = S.AssumeSection(hypotheses)
        return section

    if ast.IsSAssert:  # VerifExpr list * SourcePosition.t
        assertions = [
            S.FormalProperty(luidOfAst(prop.VTag), expressionOfAst(prop.VExpr))
            for prop in ast.Item1
        ]
        section = S.AssertSection(assertions)
        return section

    if ast.IsSGuarantee:  # VerifExpr list * SourcePosition.t
        guarantees = [
            S.FormalProperty(luidOfAst(prop.VTag), expressionOfAst(prop.VExpr))
            for prop in ast.Item1
        ]
        section = S.GuaranteeSection(guarantees)
        return section

    if ast.IsSVarList:  # VarOrRaw list
        var_decls = [varDeclOfAst(var) for var in ast.Item]
        section = S.VarSection(var_decls)
        return section

    if ast.IsSLet:  # SourcePosition.t * Equation list * SourcePosition.t
        equations = [equationOfAst(eq) for eq in ast.Item2]
        section = S.LetSection(equations)
        return section

    if ast.IsSDiagram:  # Diagram
        objects = [diagramObjectOfAst(obj) for obj in ast.Item.DObjects]
        section = S.Diagram(objects)
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
        return S.ProtectedSection(getProtectedString(ast.Item))


def scopeOfAst(ast):
    if ast.IsSDEmpty:
        return None

    if ast.IsSDEquation:
        return equationOfAst(ast.Item)

    if ast.IsSDSections:
        sections = [scopeSectionOfAst(section) for section in ast.Item1]
        # diagram context
        pragmas = getPragmas(ast.Item3)
        scope = S.Scope(sections, pragmas)
        return scope


def operatorOfAst(ast):
    (inline, kind, name, inputs, outputs, sizes, constraints, specialization, pragmas) = (
        signatureElementsOfAst(ast)
    )

    def delayed_body(owner: S.SwanItem):
        if body := scopeOfAst(ast.OpBody):
            # body can be None
            body.owner = owner
        return body

    return S.Operator(
        id=name,
        has_inline=inline,
        is_node=kind,
        inputs=inputs,
        outputs=outputs,
        body=delayed_body,
        sizes=sizes,
        constraints=constraints,
        specialization=specialization,
        pragmas=pragmas,
    )


def harnessOfAst(ast):
    name = stringOfStringWithSP(ast.HId)

    def delayed_body(owner: S.SwanItem):
        if body := scopeOfAst(ast.HBody):
            # body can be None
            body.owner = owner
        return body

    pragmas = getPragmas(ast.HPragmas)
    return S.TestHarness(
        id=name,
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
        return S.ConstDeclarations(decls)

    if ast.IsDGroup:
        decls = [groupDecl(item) for item in ast.Item1]
        return S.GroupDeclarations(decls)

    if ast.IsDOperator:
        return operatorOfAst(ast.Item)

    if ast.IsDRaw:
        markup = getMarkup(ast.Item)
        content = getProtectedString(ast.Item)
        if markup == "text":
            origin = Parser.get_source().name
            swan = SwanString(f"{content}", origin)
            op = Parser.get_current_parser().operator(swan)
            op.is_text = True
            return op
        # other protected: const, type, group, sensor
        return S.ProtectedDecl(markup, content)

    if ast.IsDSensor:
        decls = [sensorDecl(item) for item in ast.Item1]
        return S.SensorDeclarations(decls)

    if ast.IsDSignature:
        return signatureOfAst(ast.Item)

    if ast.IsDType:
        decls = [typeDecl(item) for item in ast.Item1]
        return S.TypeDeclarations(decls)

    if ast.IsDUse:
        return useDecl(ast.Item1)

    if ast.IsDTestHarness:
        return harnessOfAst(ast.Item)

    raise ScadeOneException(f"unexpected ast class: {type(ast)}")


def allDeclsOfAst(ast):
    use_list = []
    decl_list = []
    for decl in ast.MDecls:
        py_obj = declarationOfAst(decl)
        if isinstance(py_obj, S.UseDirective):
            use_list.append(py_obj)
        else:
            decl_list.append(py_obj)
    return (use_list, decl_list)


def pathIdOfString(name: str) -> S.PathIdentifier:
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
    if S.PathIdentifier.is_valid_file_path(name):
        id_list = [S.Identifier(id) for id in name.split("-")]
        return S.PathIdentifier(id_list)
    if S.PathIdentifier.is_valid_path(name):
        id_list = [S.Identifier(id.strip()) for id in name.split("::")]
        return S.PathIdentifier(id_list)
    return S.PathIdentifier(name)


def moduleOfAst(name: str, ast):
    path_id = pathIdOfString(name)
    (use_list, decl_list) = allDeclsOfAst(ast)
    body = S.ModuleBody(path_id, use_list, decl_list)
    return body


def interfaceOfAst(name, ast):
    path_id = pathIdOfString(name)
    (use_list, decl_list) = allDeclsOfAst(ast)
    interface = S.ModuleInterface(path_id, use_list, decl_list)
    return interface
