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

"""
This module contains the classes for expressions
"""

from enum import Enum, auto
from typing import List, Optional, Union

from typing_extensions import Self

from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.swan.common as common


class UnaryOp(Enum):
    # pylint: disable=invalid-name
    """Unary operators:

    - arithmetic operators
    - logical operators
    - Unit delay operator
    """

    #: (**-**) Unary minus.
    Minus = auto()
    #: (**+**) Unary plus.
    Plus = auto()
    #: (**lnot**) Bitwise not.
    Lnot = auto()
    #: (**not**) Logical not.
    Not = auto()
    #: (**pre**) Unit delay.
    Pre = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        if value == UnaryOp.Minus:
            return "-"
        elif value == UnaryOp.Plus:
            return "+"
        elif value == UnaryOp.Lnot:
            return "lnot"
        elif value == UnaryOp.Not:
            return "not"
        elif value == UnaryOp.Pre:
            return "pre"


class BinaryOp(Enum):
    """Binary operators:

    - arithmetic operators
    - relational operators
    - logical operators
    - bitwise operators
    - Initial value, initialed unit delay
    - Concat
    """

    # pylint: disable=invalid-name

    #: (+) Addition.
    Plus = auto()
    #: (-) Subtraction.
    Minus = auto()
    #: (*) Multiplication.
    Mult = auto()
    #: (/) Division.
    Slash = auto()
    #: (**mod**) Modulo.
    Mod = auto()
    #  Relational Expressions
    #: (=) Equal.
    Equal = auto()
    #: (<>) Different.
    Diff = auto()
    #: (<) Less than.
    Lt = auto()
    #: (>) Greater than.
    Gt = auto()
    #: (<=) Less than or equal to.
    Leq = auto()
    #: (>=) Greater than or equal to.
    Geq = auto()
    #  Boolean Expressions
    #: (**and**) Logical and.
    And = auto()
    #: (**or**) Logical or.
    Or = auto()
    #: (**xor**) Logical exclusive or.
    Xor = auto()
    # Bitwise Arithmetic
    #: (**land**) Bitwise and.
    Land = auto()
    #: (**lor**) Bitwise or.
    Lor = auto()
    #: (**lxor**) Bitwise exclusive or.
    Lxor = auto()
    #: (**lsl**) Logical shift left.
    Lsl = auto()
    #: (**lsr**) Logical shift right.
    Lsr = auto()
    # Other Binary
    # (**->**) Initial value.
    Arrow = auto()
    # (**->**) Initial value.
    Pre = auto()
    # (**@**) Array concat.
    Concat = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        # pylint disable=too-many-return-statements,no-else-return
        if value == BinaryOp.Plus:
            return "+"
        elif value == BinaryOp.Minus:
            return "-"
        elif value == BinaryOp.Mult:
            return "*"
        elif value == BinaryOp.Slash:
            return "/"
        elif value == BinaryOp.Mod:
            return "mod"
        # Bitwise Arithmetic
        elif value == BinaryOp.Land:
            return "land"
        elif value == BinaryOp.Lor:
            return "lor"
        elif value == BinaryOp.Lxor:
            return "lxor"
        elif value == BinaryOp.Lsl:
            return "lsl"
        elif value == BinaryOp.Lsr:
            return "lsr"
        #  Relational Expressions
        elif value == BinaryOp.Equal:
            return "="
        elif value == BinaryOp.Diff:
            return "<>"
        elif value == BinaryOp.Lt:
            return "<"
        elif value == BinaryOp.Gt:
            return ">"
        elif value == BinaryOp.Leq:
            return "<="
        elif value == BinaryOp.Geq:
            return ">="
        #  Boolean Expressions
        elif value == BinaryOp.And:
            return "and"
        elif value == BinaryOp.Or:
            return "or"
        elif value == BinaryOp.Xor:
            return "xor"
        # Other Binary
        elif value == BinaryOp.Arrow:
            return "->"
        elif value == BinaryOp.Pre:
            return "pre"
        elif value == BinaryOp.Concat:
            return "@"


class PathIdExpr(common.Expression):  # numpydoc ignore=PR01
    """:py:class:`ansys.scadeone.core.swan.PathIdentifier` expression."""

    def __init__(self, path_id: common.PathIdentifier) -> None:
        super().__init__()
        self._path_id = path_id

    @property
    def path_id(self) -> common.PathIdentifier:
        """The identifier expression."""
        return self._path_id

    def __str__(self) -> str:
        return str(self.path_id)


class LastExpr(common.Expression):  # numpydoc ignore=PR01
    """Last expression."""

    def __init__(self, id: common.Identifier) -> None:
        super().__init__()
        self._id = id

    @property
    def id(self) -> common.Identifier:
        """Identifier."""
        return self._id

    def __str__(self) -> str:
        return f"last {self.id}"


class LiteralKind(Enum):
    """Literal kind enumeration."""

    # pylint: disable=invalid-name

    #: Boolean literal
    Bool = auto()
    #: Char literal
    Char = auto()
    #: Numeric literal (integer or float, with/without size)
    Numeric = auto()
    #: Erroneous literal
    Error = auto()


class Literal(common.Expression):  # numpydoc ignore=PR01
    """Class for char, numeric, and Boolean expression.

    Boolean value is stored as 'true' or 'false'.

    Char value is a ascii char with its value between simple quotes (ex: 'a')
    or an hexadecimal value.

    Numeric value is INTEGER, TYPED_INTEGER, FLOAT, TYPED_FLOAT
    (see language grammar definition and :py:class:`SwanRE` class).
    """

    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value
        if common.SwanRE.is_char(self._value):
            self._kind = LiteralKind.Char
        elif common.SwanRE.is_bool(self._value):
            self._kind = LiteralKind.Bool
        elif common.SwanRE.is_numeric(self._value):
            self._kind = LiteralKind.Numeric
        else:
            self._kind = LiteralKind.Error

    @property
    def value(self) -> str:
        """Literal expression."""
        return self._value

    @property
    def is_bool(self) -> bool:
        """Return true when LiteralExpr is a Boolean."""
        return self._kind == LiteralKind.Bool

    @property
    def is_true(self) -> bool:
        """Return true when LiteralExpr is true."""
        return self._kind == LiteralKind.Bool and self._value == "true"

    @property
    def is_char(self) -> bool:
        """Return true when LiteralExpr is a char."""
        return self._kind == LiteralKind.Char

    @property
    def is_numeric(self) -> bool:
        """Return true when LiteralExpr is a numeric."""
        return self._kind == LiteralKind.Numeric

    @property
    def is_integer(self):
        """Return true when LiteralExpr is an integer."""
        return self._kind == LiteralKind.Numeric and common.SwanRE.is_integer(self.value)

    @property
    def is_float(self):
        """Return true when LiteralExpr is a float."""
        return self._kind == LiteralKind.Numeric and common.SwanRE.is_float(self.value)

    def __str__(self) -> str:
        return str(self.value)


class Pattern(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for patterns."""

    def __init__(self) -> None:
        super().__init__()


class ProtectedPattern(Pattern, common.ProtectedItem):  # numpydoc ignore=PR01
    """Protected pattern expression, i.e., saved as string if
    syntactically incorrect."""

    def __init__(self, data: str) -> None:
        common.ProtectedItem.__init__(self, data)


class ClockExpr(common.SwanItem):  # numpydoc ignore=PR01
    """Clock expressions:

    - Id
    - **not** Id
    - ( Id **match** *pattern*)
    """

    def __init__(
        self,
        id: common.Identifier,
        is_not: Optional[bool] = False,
        pattern: Optional[Pattern] = None,
    ) -> None:
        super().__init__()
        self._id = id
        self._is_not = is_not
        self._pattern = pattern
        if is_not and pattern:
            raise ScadeOneException("ClockExpr: not and pattern together")

    @property
    def id(self) -> common.Identifier:
        """Clock identifier."""
        return self._id

    @property
    def is_not(self) -> bool:
        """**not** id clock expression."""
        return self._is_not

    @property
    def pattern(self) -> Union[Pattern, None]:
        """Matching pattern or None."""
        return self._pattern

    def __str__(self) -> str:
        if self.pattern:
            return f"({self.id} match {self.pattern})"
        if self.is_not:
            return f"not {self.id}"
        return str(self.id)


class UnaryExpr(common.Expression):  # numpydoc ignore=PR01
    """Expression with unary operators
    :py:class`ansys.scadeone.core.swan.expressions.UnaryOp`."""

    def __init__(self, operator: UnaryOp, expr: common.Expression) -> None:
        super().__init__()
        self._operator = operator
        self._expr = expr

    @property
    def operator(self) -> UnaryOp:
        """Unary operator."""
        return self._operator

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    def __str__(self) -> str:
        return f"{UnaryOp.to_str(self.operator)} {str(self.expr)}"


class BinaryExpr(common.Expression):  # numpydoc ignore=PR01
    """Expression with binary operators
    :py:class`ansys.scadeone.swan.expressions.BinaryOp`."""

    def __init__(
        self,
        operator: BinaryOp,
        left: common.Expression,
        right: common.Expression,
    ) -> None:
        super().__init__()
        self._operator = operator
        self._left = left
        self._right = right

    @property
    def operator(self) -> BinaryOp:
        """Binary operator."""
        return self._operator

    @property
    def left(self) -> common.Expression:
        """Left expression."""
        return self._left

    @property
    def right(self) -> common.Expression:
        """Right expression."""
        return self._right

    def __str__(self) -> str:
        return "{l} {o} {r}".format(
            l=str(self.left), o=BinaryOp.to_str(self.operator), r=str(self.right)
        )


class WhenClockExpr(common.Expression):  # numpydoc ignore=PR01
    """*expr* **when** *clock_expr* expression"""

    def __init__(self, expr: common.Expression, clock: ClockExpr) -> None:
        super().__init__()
        self._expr = expr
        self._clock = clock

    @property
    def expr(self) -> common.Expression:
        """Expression"""
        return self._expr

    @property
    def clock(self) -> ClockExpr:
        """Clock expression"""
        return self._clock

    def __str__(self) -> str:
        return f"{self.expr} when {self.clock}"


class WhenMatchExpr(common.Expression):  # numpydoc ignore=PR01
    """*expr* **when match** *path_id* expression"""

    def __init__(self, expr: common.Expression, when: common.PathIdentifier) -> None:
        super().__init__()
        self._expr = expr
        self._when = when

    @property
    def expr(self) -> common.Expression:
        """Expression"""
        return self._expr

    @property
    def when(self) -> ClockExpr:
        """When expression"""
        return self._when

    def __str__(self) -> str:
        return f"{self.expr} when match {self.when}"


class NumericCast(common.Expression):  # numpydoc ignore=PR01
    """Cast expression: ( *expr* :> *type_expr*)."""

    def __init__(self, expr: common.Expression, type: common.TypeExpression) -> None:
        super().__init__()

        self._expr = expr
        self._type = type

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def type(self) -> common.TypeExpression:
        """Type expression."""
        return self._type

    def __str__(self) -> str:
        return f"({self.expr} :> {self.type})"


class GroupItem(common.SwanItem):  # numpydoc ignore=PR01
    """Item of a group expression: *group_item* ::= [[ *label* : ]] *expr*."""

    def __init__(self, expr: common.Expression, label: Optional[common.Identifier] = None) -> None:
        super().__init__()
        self._expr = expr
        self._label = label

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def label(self) -> Union[common.Identifier, None]:
        """Group item label."""
        return self._label

    @property
    def has_label(self) -> bool:
        return self._label is not None

    def __str__(self) -> str:
        return f"{self.label}: {self.expr}" if self.has_label else str(self.expr)


class Group(common.SwanItem):  # numpydoc ignore=PR01
    """Group item as a list of GroupItem."""

    def __init__(self, items: List[GroupItem]) -> None:
        super().__init__()
        self._items = items

    @property
    def items(self) -> List[GroupItem]:
        """Group items."""
        return self._items

    def __str__(self) -> str:
        return ", ".join(str(i) for i in self._items)


class GroupConstructor(common.Expression):  # numpydoc ignore=PR01
    """A group expression:
    *group_expr ::= (*group*).
    """

    def __init__(self, group: Group) -> None:
        super().__init__()
        self._group = group

    @property
    def group(self):
        return self._group

    def __str__(self) -> str:
        return f"({self.group})"


class GroupRenaming(common.SwanItem):  # numpydoc ignore=PR01
    """Group renaming: (( Id | Integer)) [: [Id]].

    - Renaming source index as Id or Integer, either a name or a position. For example: *a* or 2.
    - Optional renaming target index:

      - No index
      - Renaming as **:** Id, for example: *a* **:** *b*, 2 **:** *b*
      - Shortcut, example *a* **:** means *a* **:** *a*

    Parameters
    ----------

    source: common.Identifier | LiteralExpr
       Source index.

    renaming: common.Identifier  (optional)
       Renaming as an Identifier.

    is_shortcut: bool (optional)
       Renaming is a shortcut of the form ID.
    """

    def __init__(
        self,
        source: Union[common.Identifier, Literal],
        renaming: Optional[common.Identifier] = None,
        is_shortcut: Optional[bool] = False,
    ) -> None:
        super().__init__()
        self._source = source
        self._renaming = renaming
        self._is_shortcut = is_shortcut

    @property
    def source(self) -> Union[common.Identifier, Literal]:
        """Source selection in group."""
        return self._source

    @property
    def is_shortcut(self) -> bool:
        """True when renaming is a shortcut."""
        return self._is_shortcut

    @property
    def is_valid(self) -> bool:
        """True when renaming is a shortcut with no renaming, or a renaming with no shortcut."""
        if self._renaming and self.is_shortcut:
            # check both id are the same
            return self._source.id == self._renaming.id
        return True

    @property
    def is_by_name(self) -> bool:
        """True when access by name."""
        return isinstance(self._source, common.Identifier)

    @property
    def renaming(self) -> Union[common.Identifier, None]:
        """Renaming in new group. None if no renaming."""
        return self._renaming

    def __str__(self) -> str:
        renaming = str(self.source)
        if self.renaming:
            renaming += f": {self.renaming}"
        elif self.is_shortcut:
            renaming += ":"
        return renaming


class ProtectedGroupRenaming(GroupRenaming, common.ProtectedItem):  # numpydoc ignore=PR01
    """Specific class when a renaming is protected for syntax error.

    Source is an adaptation such as: .( {syntax%renaming%syntax} ).
    """

    def __init__(self, data: str, markup: Optional[str] = common.Markup.Syntax) -> None:
        common.ProtectedItem.__init__(self, data, markup)

    @property
    def source(self) -> None:
        """Source selection in group."""
        return None

    @property
    def is_shortcut(self) -> bool:
        """True when renaming is a shortcut."""
        return False

    @property
    def is_valid(self) -> bool:
        """True when renaming is a shortcut with no renaming, or a renaming with no shortcut."""
        return False

    @property
    def is_by_name(self) -> bool:
        """True when access by name."""
        return False

    @property
    def renaming(self) -> Union[common.Identifier, None]:
        """Renaming in new group. None if no renaming."""
        return None

    def __str__(self) -> str:
        return common.ProtectedItem.__str__(self)


class GroupAdaptation(common.SwanItem):  # numpydoc ignore=PR01
    """Group adaptation: *group_adaptation* ::= . ( *group_renamings* )."""

    def __init__(self, renamings: List[GroupRenaming]) -> None:
        super().__init__()
        self._renamings = renamings

    @property
    def renamings(self) -> List[GroupRenaming]:
        """Renaming list of group adaptation."""
        return self._renamings

    def __str__(self) -> str:
        adaptation = ", ".join([str(r) for r in self.renamings])
        return f".({adaptation})"


class GroupProjection(common.Expression):  # numpydoc ignore=PR01
    """Group projection: *group_expr* ::= *expr* *group_adaptation*."""

    def __init__(self, expr: common.Expression, adaptation: GroupAdaptation) -> None:
        super().__init__()
        self._expr = expr
        self._adaptation = adaptation

    @property
    def expr(self) -> common.Expression:
        """Adapted expression."""
        return self._expr

    @property
    def adaptation(self) -> GroupAdaptation:
        """Expression group adaptation."""
        return self._adaptation

    def __str__(self) -> str:
        return f"{self.expr} {self.adaptation}"


# Composite


class ArrayProjection(common.Expression):  # numpydoc ignore=PR01
    """Static projection: *expr* [*index*], where index is a static expression."""

    def __init__(self, expr: common.Expression, index: common.Expression) -> None:
        super().__init__()
        self._expr = expr
        self._index = index

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def index(self) -> common.Expression:
        """Index expression."""
        return self._index

    def __str__(self) -> str:
        return f"{self.expr}{self.index}"


class StructProjection(common.Expression):  # numpydoc ignore=PR01
    """Static structure field access: *expr* . *label*."""

    def __init__(self, expr: common.Expression, label: common.Identifier) -> None:
        super().__init__()
        self._expr = expr
        self._label = label

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def label(self) -> common.Identifier:
        """Field name."""
        return self._label

    def __str__(self) -> str:
        return f"{self.expr}{self.label}"


class StructDestructor(common.Expression):  # numpydoc ignore=PR01
    """Group creation: *path_id* **group** (*expr*)."""

    def __init__(self, group: common.PathIdentifier, expr: common.Expression) -> None:
        super().__init__()
        self._group = group
        self._expr = expr

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def group(self) -> common.PathIdentifier:
        """Group type."""
        return self._group

    def __str__(self) -> str:
        return f"{self.group} group ({self.expr})"


class Slice(common.Expression):  # numpydoc ignore=PR01
    """Slice expression: *expr* [ *expr* .. *expr*]."""

    def __init__(
        self, expr: common.Expression, start: common.Expression, end: common.Expression
    ) -> None:
        super().__init__()
        self._expr = expr
        self._start = start
        self._end = end

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def start(self) -> common.Expression:
        """Start of slice expression."""
        return self._start

    @property
    def end(self) -> common.Expression:
        """End of slice expression."""
        return self._end

    def __str__(self) -> str:
        return f"{self.expr}[{self.start} .. {self.end}]"


class LabelOrIndex(common.Expression):  # numpydoc ignore=PR01
    """Stores an index as:

    - a label :py:class:`ansys.scadeone.swan.Identifier` or,
    - an expression :py:class:`ansys.scadeone.swan.Expression`.
    """

    def __init__(self, value: Union[common.Identifier, common.Expression]) -> None:
        super().__init__()
        self._value = value

    @property
    def is_label(self) -> bool:
        return isinstance(self.value, common.Identifier)

    @property
    def value(self) -> Union[common.Identifier, common.Expression]:
        """Return the index (expression or label)."""
        return self._value

    def __str__(self) -> str:
        fmt = ".{}" if self.is_label else "[{}]"
        return fmt.format(str(self.value))


class ProjectionWithDefault(common.Expression):  # numpydoc ignore=PR01
    """Dynamic projection: (*expr* . {{ *label_or_index* }}+ **default** *expr*)."""

    def __init__(
        self, expr: common.Expression, indices: List[LabelOrIndex], default: common.Expression
    ) -> None:
        super().__init__()
        self._expr = expr
        self._indices = indices
        self._default = default

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def default(self) -> common.Expression:
        """Default value."""
        return self._default

    @property
    def indices(self) -> List[LabelOrIndex]:
        """List of indices."""
        return self._indices

    def __str__(self) -> str:
        projections = "".join([str(i) for i in self.indices])

        return f"({self.expr} . {projections} default {self.default})"


class ArrayRepetition(common.Expression):  # numpydoc ignore=PR01
    """Array expression: *expr* ^ *expr*."""

    def __init__(self, expr: common.Expression, size: common.Expression):
        super().__init__()
        self._expr = expr
        self._size = size

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def size(self) -> common.Expression:
        """Array size."""
        return self._size

    def __str__(self) -> str:
        return f"{self.expr}^{self.size}"


class ArrayConstructor(common.Expression):  # numpydoc ignore=PR01
    """Array construction expression: [ *group* ]."""

    def __init__(self, group: Group):
        super().__init__()
        self._group = group

    @property
    def group(self) -> Group:
        """Group items as a Group."""
        return self._group

    def __str__(self) -> str:
        return f"[{self.group}]"


class StructConstructor(common.Expression):  # numpydoc ignore=PR01
    """Structure expression, with optional type for cast
    to structure from a group: { *group* } [[ : *path_id*]].

    """

    def __init__(self, group: Group, type: Optional[common.PathIdentifier] = None) -> None:
        super().__init__()
        self._group = group
        self._type = type

    @property
    def group(self) -> Group:
        """Group value"""
        return self._group

    @property
    def type(self) -> Union[common.PathIdentifier, None]:
        """Structure type."""
        return self._type

    def __str__(self) -> str:
        type_part = f" : {self.type}" if self.type else ""
        return f"{{{self.group}}}{type_part}"


class VariantValue(common.Expression):  # numpydoc ignore=PR01
    """Variant expression: *path_id* { *group* }."""

    def __init__(self, tag: common.PathIdentifier, group: Group) -> None:
        super().__init__()
        self._tag = tag
        self._group = group

    @property
    def group(self) -> Group:
        """Group value."""
        return self._group

    @property
    def tag(self) -> common.PathIdentifier:
        """Variant tag."""
        return self._tag

    def __str__(self) -> str:
        return f"{self.tag} {{{self.group}}}"


class Modifier(common.SwanItem):  # numpydoc ignore=PR01
    """Modifier expression: {{ *label_or_index* }}+ = *expr*.

    Label of index can be syntactically incorrect. In which case, _modifier_ is
    a string, and *is_protected* property is True.

    See :py:class:`FunctionalUpdate`.
    """

    def __init__(self, modifier: Union[List[LabelOrIndex], str], expr: common.Expression) -> None:
        super().__init__()
        self._modifier = modifier
        self._expr = expr
        self._is_protected = isinstance(modifier, str)

    @property
    def expr(self) -> common.Expression:
        """Modifier expression."""
        return self._expr

    @property
    def modifier(self) -> Union[List[LabelOrIndex], str]:
        """Modifier as label or index."""
        return self._modifier

    @property
    def is_protected(self):
        """Modifier has a syntax error and is protected."""
        return self._is_protected

    def __str__(self) -> str:
        m_str = (
            common.Markup.to_str(self.modifier)
            if self.is_protected
            else "".join([str(m) for m in self.modifier])
        )
        return f"{m_str} = {self.expr}"


class FunctionalUpdate(common.Expression):  # numpydoc ignore=PR01
    """Copy with modification: ( *expr*  **with** *modifier* {{ ; *modifier* }} [[ ; ]] )."""

    def __init__(self, expr: common.Expression, modifiers: List[Modifier]) -> None:
        super().__init__()
        self._expr = expr
        self._modifiers = modifiers

    @property
    def expr(self) -> common.Expression:
        """Expression."""
        return self._expr

    @property
    def modifiers(self) -> List[Modifier]:
        """Copy modifiers."""
        return self._modifiers

    def __str__(self) -> str:
        modifiers = "; ".join([str(m) for m in self.modifiers])
        return f"({self.expr} with {modifiers})"


# Switches


class IfteExpr(common.Expression):  # numpydoc ignore=PR01
    """Conditional if/then/else expression: **if** *expr* **then** *expr* **else** *expr*."""

    def __init__(
        self,
        cond_expr: common.Expression,
        then_expr: common.Expression,
        else_expr: common.Expression,
    ) -> None:
        super().__init__()
        self._cond = cond_expr
        self._then = then_expr
        self._else = else_expr

    @property
    def cond_expr(self) -> common.Expression:
        """Condition expression."""
        return self._cond

    @property
    def then_expr(self) -> common.Expression:
        """Then expression."""
        return self._then

    @property
    def else_expr(self) -> common.Expression:
        """Else expression."""
        return self._else

    def __str__(self) -> str:
        return f"if {self.cond_expr} then {self.then_expr} else {self.else_expr}"


class CaseBranch(common.SwanItem):  # numpydoc ignore=PR01
    """Case branch expression:  *pattern* : *expr*.

    See :py:class:`ansys.scadeone.swan.expressions.CaseExpr`."""

    def __init__(self, pattern: Pattern, expr: common.Expression) -> None:
        super().__init__()
        self._pattern = pattern
        self._expr = expr

    @property
    def pattern(self) -> Pattern:
        """Case branch pattern."""
        return self._pattern

    @property
    def expr(self) -> common.Expression:
        """Case branch expression."""
        return self._expr

    def __str__(self) -> str:
        return f"| {self.pattern}: {self.expr}"


class CaseExpr(common.Expression):  # numpydoc ignore=PR01
    """Case expression: **case** *expr* **of** {{ | *pattern* : *expr* }}+ )."""

    def __init__(self, expr: common.Expression, branches: List[CaseBranch]) -> None:
        super().__init__()
        self._expr = expr
        self._branches = branches

    @property
    def expr(self) -> common.Expression:
        """Case expression."""
        return self._expr

    @property
    def branches(self) -> List[CaseBranch]:
        """Case branches."""
        return self._branches

    def __str__(self) -> str:
        b_str = " ".join([str(b) for b in self.branches])
        return f"(case {self.expr} of {b_str})"


class PathIdPattern(Pattern):  # numpydoc ignore=PR01
    """Simple pattern: *pattern* ::= *path_id*."""

    def __init__(self, path_id: common.PathIdentifier) -> None:
        super().__init__()
        self._path_id = path_id

    @property
    def path_id(self) -> common.PathIdentifier:
        """The path_id of pattern."""
        return self._path_id

    def __str__(self) -> str:
        return str(self.path_id)


class VariantPattern(Pattern):  # numpydoc ignore=PR01
    """Variant pattern:

    *pattern* ::=

    - *path_id* **_**: has_underscore is True
    - *path_id* { } has_underscore is False, has_capture is False
    - *path_id* { Id } : has_capture is True

    """

    def __init__(
        self,
        path_id: common.PathIdentifier,
        captured: Optional[common.Identifier] = None,
        underscore: Optional[bool] = False,
    ) -> None:
        super().__init__()
        self._path_id = path_id
        self._captured = captured
        self._underscore = underscore

    @property
    def path_id(self) -> common.PathIdentifier:
        """The path_id of variant pattern."""
        return self._path_id

    @property
    def underscore(self) -> Union[bool, None]:
        """Underscore as bool or None."""
        return self._underscore

    @property
    def has_underscore(self) -> bool:
        """Variant part is '_'."""
        return self._underscore

    @property
    def has_capture(self) -> bool:
        """The variant pattern has a captured tag."""
        return self._captured is not None

    @property
    def empty_capture(self) -> bool:
        """The variant pattern as an empty {} capture."""
        return not (self.has_underscore or self.has_capture)

    @property
    def captured(self) -> Union[common.Identifier, None]:
        """The variant pattern captured tag."""
        return self._captured

    def __str__(self) -> str:
        if self.has_underscore:
            return f"{self.path_id} _"
        elif self.has_capture:
            return f"{self.path_id} {{ {self.captured} }}"
        return f"{self.path_id} {{ }}"


class CharPattern(Pattern):  # numpydoc ignore=PR01
    """Pattern: *pattern* ::= CHAR."""

    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self.value


class IntPattern(Pattern):  # numpydoc ignore=PR01
    """Pattern: *pattern* ::= [-] INTEGER | [-] TYPED_INTEGER."""

    def __init__(self, value: str, is_minus: Optional[bool] = False) -> None:
        super().__init__()
        self._value = value
        self._is_minus = is_minus

    @property
    def value(self) -> str:
        """Return value as a string, without sign."""
        return self._value

    @property
    def is_minus(self) -> bool:
        """Return True when has sign minus."""
        return self._is_minus

    @property
    def as_int(self) -> int:
        """Return value as an integer."""
        description = common.SwanRE.parse_integer(self.value, self.is_minus)
        return description.value

    def __str__(self) -> str:
        return f"-{self.value}" if self.is_minus else self.value


class BoolPattern(Pattern):  # numpydoc ignore=PR01
    """Pattern: *pattern* ::= **true** | **false**."""

    def __init__(self, value: bool) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> bool:
        """Return value as a bool value"""
        return self._value

    @property
    def is_true(self) -> bool:
        """Return True when pattern is **true**, else False."""
        return self._value

    def __str__(self) -> str:
        return "true" if self.is_true else "false"


class UnderscorePattern(Pattern):  # numpydoc ignore=PR01
    """Pattern: *pattern* ::= **_**."""

    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "_"


class DefaultPattern(Pattern):  # numpydoc ignore=PR01
    """Pattern: *pattern* ::= **default**."""

    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "default"


class PortExpr(common.Expression):  # numpydoc ignore=PR01
    """Port information."""

    def __init__(
        self,
        lunum: Optional[common.Luid] = None,
        luid: Optional[common.Luid] = None,
        is_self: Optional[bool] = False,
    ) -> None:
        super().__init__()
        self._lunum = lunum
        self._luid = luid
        self._is_self = is_self

    @property
    def lunum(self) -> common.Lunum:
        return self._lunum

    @property
    def luid(self) -> common.Luid:
        return self._luid

    @property
    def is_self(self) -> bool:
        return self._is_self

    def __str__(self) -> str:
        """Port identification, either a Luid or 'self'."""
        return "self" if self.is_self else str(self.luid) if self.luid else str(self.lunum)


class Window(common.Expression):  # numpydoc ignore=PR01
    """Temporal window: *expr* ::= **window** <<*expr*>> ( *group* ) ( *group* )."""

    def __init__(self, size: common.Expression, init: Group, params: Group) -> None:
        super().__init__()
        self._size = size
        self._params = params
        self._init = init

    @property
    def size(self) -> common.Expression:
        """Window size."""
        return self._size

    @property
    def params(self) -> Group:
        """Window parameters."""
        return self._params

    @property
    def init(self) -> Group:
        """Window initial values."""
        return self._init

    def __str__(self) -> str:
        return f"window <<{self.size}>> ({self.init}) ({self.params})"


class Merge(common.Expression):  # numpydoc ignore=PR01
    """**merge** ( *group* ) {{ ( *group* ) }}."""

    def __init__(self, params: List[Group]) -> None:
        super().__init__()
        self._params = params

    @property
    def params(self) -> List[Group]:
        return self._params

    def __str__(self) -> str:
        if self.params:
            p_str = " ".join([f"({str(p)})" for p in self.params])
            return f"merge {p_str}"
        else:
            # empty list is invalid
            return common.Markup.to_str("merge")


# =============================================
# Protected Items
# =============================================


class ProtectedExpr(common.Expression, common.ProtectedItem):  # numpydoc ignore=PR01
    """Protected expression, i.e., saved as string if syntactically incorrect."""

    def __init__(self, data: str, markup: Optional[str] = common.Markup.Syntax) -> None:
        common.ProtectedItem.__init__(self, data, markup)
