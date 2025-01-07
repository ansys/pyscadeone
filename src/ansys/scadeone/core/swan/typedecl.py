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
This module contains classes to manipulate types and types expressions.
"""

from typing import List, Optional, Union

import ansys.scadeone.core.swan.common as common


class TypeDefinition(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for type definition classes."""

    pass


class TypeDecl(common.Declaration):  # numpydoc ignore=PR01
    """Type declaration with its name and optional definition:
    *type_decl* ::= id [[ = *type_def* ]]."""

    def __init__(self, id: common.Identifier, definition: Optional[TypeDefinition] = None) -> None:
        super().__init__(id)
        self._definition = definition

    @property
    def definition(self) -> Union[TypeDefinition, None]:
        return self._definition

    def __str__(self) -> str:
        decl = f"{self.id}"
        return f"{decl} = {self.definition}" if self.definition else f"{decl}"


# Type definitions
# ----------------


class ExprTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as a type expression: *type_def* ::= *type_expr*."""

    def __init__(self, type: common.TypeExpression) -> None:
        super().__init__()
        self._type = type

    @property
    def type(self):
        return self._type

    def __str__(self) -> str:
        return str(self.type)


class EnumTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as an enumeration: *type_def* ::= **enum** { id {{ , id }} }."""

    def __init__(self, tags: List[common.Identifier]) -> None:
        super().__init__()
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    def __str__(self):
        tags_str = [str(t) for t in self.tags]
        return f"enum {{{', '.join(tags_str)}}}"


class PredefinedType(common.TypeExpression):  # numpydoc ignore=PR01
    """Predefined types."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def is_predefined(self) -> bool:
        "True if type is predefined"
        return True

    @property
    def name(self) -> str:
        """Name of a predefined type from its class."""
        return self.__class__.__name__[:-4].lower()

    def __str__(self) -> str:
        return self.name


class BoolType(PredefinedType):  # numpydoc ignore=PR01
    """**bool** type."""


class CharType(PredefinedType):  # numpydoc ignore=PR01
    """**char** type."""


class Int8Type(PredefinedType):  # numpydoc ignore=PR01
    """**int8** type."""


class Int16Type(PredefinedType):  # numpydoc ignore=PR01
    """**int16** type."""


class Int32Type(PredefinedType):  # numpydoc ignore=PR01
    """**int32** type."""


class Int64Type(PredefinedType):  # numpydoc ignore=PR01
    """**int64** type."""


class Uint8Type(PredefinedType):  # numpydoc ignore=PR01
    """**uint8** type."""


class Uint16Type(PredefinedType):  # numpydoc ignore=PR01
    """**uin16** type."""


class Uint32Type(PredefinedType):  # numpydoc ignore=PR01
    """**uint32** type."""


class Uint64Type(PredefinedType):  # numpydoc ignore=PR01
    """**uint64** type."""


class Float32Type(PredefinedType):  # numpydoc ignore=PR01
    """**float32** type."""


class Float64Type(PredefinedType):  # numpydoc ignore=PR01
    """**float64** type."""


class SizedTypeExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Type with a size expression:

    | *type_expr* ::= **signed** << *expr* >>
    |   | **unsigned** << *expr* >>

    """

    def __init__(self, size: common.Expression, is_signed: bool) -> None:
        super().__init__()
        self._expr = size
        self._is_signed = is_signed

    @property
    def is_signed(self):
        return self._is_signed

    @property
    def size(self):
        return self._expr

    def __str__(self) -> str:
        if self.is_signed:
            return f"signed <<{self.size}>>"
        else:
            return f"unsigned <<{self.size}>>"


class TypeReferenceExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Type reference to another type: *type_expr* ::= *path_id*."""

    def __init__(self, alias: common.PathIdentifier) -> None:
        super().__init__()
        self._alias = alias

    @property
    def alias(self) -> common.PathIdentifier:
        """Returns aliased type name."""
        return self._alias

    def __str__(self) -> str:
        return str(self.alias)


class VariableTypeExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Type variable expression:
    *type_expr* ::= 'Id
    """

    def __init__(self, name: common.Identifier) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> common.Identifier:
        """Name of variable."""
        return self._name

    def __str__(self) -> str:
        return f"{self.name}"


class StructField(common.SwanItem):  # numpydoc ignore=PR01
    """Structure field as: ID **:** *type_expr*."""

    def __init__(self, id: common.Identifier, type: common.TypeExpression) -> None:
        super().__init__()
        self._id = id
        self._type = type

    @property
    def id(self) -> common.Identifier:
        """Field name."""
        return self._id

    @property
    def type(self) -> common.TypeExpression:
        """Field type."""
        return self._type

    def __str__(self) -> str:
        return f"{self.id}: {self.type}"


class StructTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as a structure: *type_expr* ::= { *field_decl* {{, *field_decl*}}}."""

    def __init__(self, fields: List[StructField]) -> None:
        super().__init__()
        self._fields = fields

    @property
    def fields(self) -> List[StructField]:
        """List of fields."""
        return self._fields

    def __str__(self) -> str:
        f_str = [str(f) for f in self._fields]
        return f"{{{', '.join(f_str)}}}"


class ArrayTypeExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Array type expression: *type_expr* := *type_expr* ^ *expr*."""

    def __init__(self, type: common.TypeExpression, size: common.Expression) -> None:
        super().__init__()
        self._type = type
        self._size = size

    @property
    def size(self) -> common.Expression:
        """Array size."""
        return self._size

    @property
    def type(self) -> common.TypeExpression:
        """Array cell type."""
        return self._type

    def __str__(self) -> str:
        return f"{self.type} ^ {self.size}"


class VariantComponent(common.SwanItem):  # numpydoc ignore=PR01
    """Variant component: *variant* ::= id *variant_type_expr*."""

    def __init__(self, tag: common.Identifier) -> None:
        super().__init__()
        self._tag = tag

    @property
    def tag(self):
        """Variant tag."""
        return self._tag


class VariantSimple(VariantComponent):  # numpydoc ignore=PR01
    """Simple Variant

    *variant* ::= ID {}"""

    def __init__(self, tag: common.Identifier) -> None:
        super().__init__(tag)

    def __str__(self) -> str:
        return f"{self.tag} {{}}"


class VariantTypeExpr(VariantComponent):  # numpydoc ignore=PR01
    """Variant type expression:

    *variant* ::= ID { *type_expr* }"""

    def __init__(self, tag: common.Identifier, type: common.TypeExpression) -> None:
        super().__init__(tag)
        self._type = type

    @property
    def type(self) -> common.TypeExpression:
        """Variant type expression."""
        return self._type

    def __str__(self) -> str:
        if self.type:
            return f"{self.tag} {{ {self.type} }}"
        else:
            return f"{self.tag} {{ }}"


class VariantStruct(VariantComponent):  # numpydoc ignore=PR01
    """Variant structure expression:

    *variant* ::= ID *struct_texpr*"""

    def __init__(self, tag: common.Identifier, fields: list[StructField]) -> None:
        super().__init__(tag)
        self._fields = fields

    @property
    def fields(self) -> list[StructField]:
        """Variant structure fields."""
        return self._fields

    def __str__(self) -> str:
        f_str = [str(f) for f in self.fields]
        return f"{self.tag} {{{', '.join(f_str)}}}"


class VariantTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as a variant: *type_def* ::= *variant* {{ | *variant* }}."""

    def __init__(self, tags: List[VariantComponent]) -> None:
        super().__init__()
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    def __str__(self) -> str:
        v_str = [str(v) for v in self.tags]
        return " | ".join(v_str)


class ProtectedTypeExpr(common.TypeExpression, common.ProtectedItem):  # numpydoc ignore=PR01
    """Protected type expression, i.e., saved as string if
    syntactically incorrect."""

    def __init__(self, data: str) -> None:
        common.ProtectedItem.__init__(self, data)
