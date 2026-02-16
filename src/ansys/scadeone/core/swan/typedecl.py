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

from typing import List, Optional, Union, cast

import ansys.scadeone.core.swan.common as common


class TypeDefinition(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for type definition classes."""

    pass


class TypeDecl(common.Declaration):  # numpydoc ignore=PR01
    """Type declaration with its name and optional definition:
    *type_decl* ::= id [[ = *type_def* ]]."""

    def __init__(
        self,
        id: common.Identifier,
        definition: Optional[TypeDefinition] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(id, pragmas)
        self._definition = definition
        common.SwanItem.set_owner(self, definition)

    @property
    def definition(self) -> Union[TypeDefinition, None]:
        """Definition of the type declaration."""
        return self._definition


# Type definitions
# ----------------


class ExprTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as a type expression: *type_def* ::= *type_expr*."""

    def __init__(self, type: common.TypeExpression) -> None:
        super().__init__()
        self._type = type
        common.SwanItem.set_owner(self, type)

    @property
    def type(self) -> common.TypeExpression:
        return self._type


class EnumTag(common.HasPragma):  # numpydoc ignore=PR01
    """Enumeration tag as: ID, with optional pragmas."""

    def __init__(self, id: common.Identifier, pragmas: Optional[List[common.Pragma]] = None):
        super().__init__(pragmas)
        self._id = id
        common.SwanItem.set_owner(self, id)

    @property
    def id(self) -> common.Identifier:
        """Field name."""
        return self._id


class EnumTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as an enumeration: *type_def* ::= **enum** { id {{ , id }} }."""

    def __init__(self, tags: List[EnumTag]) -> None:
        super().__init__()
        self._tags = tags
        common.SwanItem.set_owner(self, tags)

    @property
    def tags(self) -> List[EnumTag]:
        return self._tags


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
        common.SwanItem.set_owner(self, size)

    @property
    def is_signed(self) -> bool:
        return self._is_signed

    @property
    def size(self) -> common.Expression:
        return self._expr


class TypeReferenceExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Type reference to another type: *type_expr* ::= *path_id*."""

    def __init__(self, alias: common.PathIdentifier) -> None:
        super().__init__()
        self._alias = alias
        common.SwanItem.set_owner(self, alias)

    @property
    def alias(self) -> common.PathIdentifier:
        """Returns aliased type name."""
        return self._alias

    @property
    def type_decl(self) -> TypeDecl:
        """Returns the final type definition."""
        type_name = self._alias.as_string
        type_decl = cast(common.ModuleBase, self.module).get_declaration(type_name)
        return cast(TypeDecl, type_decl)


class VariableTypeExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Type variable expression:
    *type_expr* ::= 'Id
    """

    def __init__(self, name: common.Identifier) -> None:
        super().__init__()
        self._name = name
        common.SwanItem.set_owner(self, name)

    @property
    def name(self) -> common.Identifier:
        """Name of variable."""
        return self._name


class StructField(common.HasPragma):  # numpydoc ignore=PR01
    """Structure field as: ID **:** *type_expr*."""

    def __init__(
        self,
        id: common.Identifier,
        type: common.TypeExpression,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(pragmas)
        self._id = id
        self._type = type
        common.SwanItem.set_owner(self, id)
        common.SwanItem.set_owner(self, type)

    @property
    def id(self) -> common.Identifier:
        """Field name."""
        return self._id

    @property
    def type(self) -> common.TypeExpression:
        """Field type."""
        return self._type


class StructTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as a structure: *type_expr* ::= { *field_decl* {{, *field_decl*}}}."""

    def __init__(self, fields: List[StructField]) -> None:
        super().__init__()
        self._fields = fields
        common.SwanItem.set_owner(self, fields)

    @property
    def fields(self) -> List[StructField]:
        """List of fields."""
        return self._fields


class ArrayTypeExpression(common.TypeExpression):  # numpydoc ignore=PR01
    """Array type expression: *type_expr* := *type_expr* ^ *expr*."""

    def __init__(self, type: common.TypeExpression, size: common.Expression) -> None:
        super().__init__()
        self._type = type
        self._size = size
        common.SwanItem.set_owner(self, type)
        common.SwanItem.set_owner(self, size)

    @property
    def size(self) -> common.Expression:
        """Array size."""
        return self._size

    @property
    def type(self) -> common.TypeExpression:
        """Array cell type."""
        return self._type


class VariantConstructor(common.HasPragma):  # numpydoc ignore=PR01
    """Variant component: *variant* ::= id *variant_type_expr*."""

    def __init__(
        self, tag: common.Identifier, pragmas: Optional[List[common.Pragma]] = None
    ) -> None:
        super().__init__(pragmas)
        self._tag = tag
        common.SwanItem.set_owner(self, tag)

    @property
    def tag(self) -> common.Identifier:
        """Variant tag."""
        return self._tag


class VariantSimple(VariantConstructor):  # numpydoc ignore=PR01
    """Simple Variant

    *variant* ::= ID {}"""

    def __init__(
        self, tag: common.Identifier, pragmas: Optional[List[common.Pragma]] = None
    ) -> None:
        super().__init__(tag, pragmas=pragmas)


class VariantTypeExpression(VariantConstructor):  # numpydoc ignore=PR01
    """Variant type expression:

    *variant* ::= ID { *type_expr* }"""

    def __init__(
        self,
        tag: common.Identifier,
        type: common.TypeExpression,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(tag, pragmas=pragmas)
        self._type = type
        common.SwanItem.set_owner(self, type)

    @property
    def type(self) -> common.TypeExpression:
        """Variant type expression."""
        return self._type


class VariantStruct(VariantConstructor):  # numpydoc ignore=PR01
    """Variant structure type expression:

    *variant* ::= ID *struct_texpr*"""

    def __init__(
        self,
        tag: common.Identifier,
        structure_type: StructTypeDefinition,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(tag, pragmas=pragmas)
        self._structure_type = structure_type
        common.SwanItem.set_owner(self, structure_type)

    @property
    def structure_type(self) -> StructTypeDefinition:
        """Variant structure type."""
        return self._structure_type


class VariantTypeDefinition(TypeDefinition):  # numpydoc ignore=PR01
    """Type definition as a variant: *type_def* ::= *variant* {{ | *variant* }}."""

    def __init__(self, tags: List[VariantConstructor]) -> None:
        super().__init__()
        self._tags = tags
        common.SwanItem.set_owner(self, tags)

    @property
    def tags(self) -> List[VariantConstructor]:
        return self._tags


class ProtectedTypeExpression(common.TypeExpression, common.ProtectedItem):  # numpydoc ignore=PR01
    """Protected type expression, i.e., saved as string if
    syntactically incorrect."""

    def __init__(self, data: str) -> None:
        common.ProtectedItem.__init__(self, data)
