# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Code module for Swan Code Generator mapping data.

This module implements classes representing C code elements generated from Swan language.
Each code item has a unique integer ID and can reference other code items
or model items by their IDs.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, cast
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .model import ModelElement

from .mapping import MappingDataBase, MappingRole, require_cgmapping
from .model import ModelVariable, ModelGroupVariableProjection, ModelMonoVariable


@dataclass
class CodeElement:
    """Base class for all C code elements.

    This class provides common functionality for all code elements,
    including access to their corresponding model elements through the mapping system.

    All code elements that inherit from this class must have an 'id' attribute.
    """

    cgmapping: MappingDataBase | None = field(default=None, init=False)

    @require_cgmapping
    def get_model_element(self) -> ModelElement | None:
        """Get the model element for this code element.

        Returns
        -------
        ModelElement | None
            The model element mapped to this code element, or None if not found.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        AttributeError
            If the class does not have an 'id' attribute.
        """
        # Ensure the class has an 'id' attribute
        if not hasattr(self, "id"):
            raise AttributeError(
                f"{type(self).__name__} must have an 'id' attribute to inherit from CodeElement"
            )

        elements = self.cgmapping._get_model_for_code(self.id)  # type: ignore[missing-attribute]
        return elements[0] if elements else None


@dataclass
class CodeTypeBase(CodeElement):
    """Base class for code elements that represent types."""

    @require_cgmapping
    def get_copy_function_name(self) -> str | None:
        """Get copy function name if it exists.

        Returns
        -------
        str | None
            The name of the copy function, None if not found.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        if hasattr(self, "copy"):
            # Get the model elements mapped to this type ID
            copy_function = self.cgmapping._get_code_by_id(self.copy)  # type: ignore[missing-attribute]
            if isinstance(copy_function, CFunction | CMacro):
                return copy_function.name

        return None

    @require_cgmapping
    def get_equality_function(self) -> CFunction | None:
        """Get the equality function for this type if it exists.

        Returns
        -------
        CFunction | None
            The equality CFunction, or None if not found.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        if hasattr(self, "equality") and self.equality is not None:
            code_item = self.cgmapping._get_code_by_id(self.equality)  # type: ignore[missing-attribute]
            return cast(CFunction, code_item) if code_item else None

        return None

    def get_equality_use_macro(self) -> str | None:
        """Get the equality use macro string for this type if it exists.
        It is the name of the C macro that conditionates equality function compilation.
        `CArray`, `CStruct, and `CUnion` types can have an equality use macro.
        `CExternalType` and `CTypedef` don't have equality use macro thus always return None.

        Returns
        -------
        str | None
            The equality use macro string if it exists.
        """
        if hasattr(self, "equality_use"):
            return self.equality_use

        return None


@dataclass
class CParameter(CodeElement):
    """C function parameter.

    Parameters
    ----------
    id : int
        Unique identifier for this parameter.
    name : str
        Name of the parameter.
    type : int
        Reference ID to the type of the parameter.
    pointer : bool | None
        Whether this parameter is a pointer.
    const : bool | None
        Whether this parameter is const.
    """

    id: int
    name: str
    type: int
    pointer: bool | None = None
    const: bool | None = None


@dataclass
class CFunction(CodeElement):
    """C function declaration.

    Parameters
    ----------
    id : int
        Unique identifier for this function.
    name : str
        Name of the function.
    return_type : int | None
        Reference ID to the return type (None for void).
    parameters : list[CParameter]
        List of function parameters.
    """

    id: int
    name: str
    parameters: list[CParameter]
    return_type: int | None = None


@dataclass
class CGlobal(CodeElement):
    """C global variable.

    Parameters
    ----------
    id : int
        Unique identifier for this global variable.
    name : str
        Name of the global variable.
    type : int
        Reference ID to the type of the variable.
    """

    id: int
    name: str
    type: int


@dataclass
class CMacro(CodeElement):
    """C macro definition.

    Parameters
    ----------
    id : int
        Unique identifier for this macro.
    name : str
        Name of the macro.
    """

    id: int
    name: str


@dataclass
class CPredefinedType(CodeElement):
    """C predefined type.

    Parameters
    ----------
    id : int
        Unique identifier for this type.
    name : str
        Name of the predefined type (e.g., int, float, double).
    """

    id: int
    name: str


@dataclass
class CArray(CodeTypeBase):
    """C array type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this array type.
    name : str
        Name of the array type.
    base_type : int
        Reference ID to the base type of the array.
    size : int
        Size of the array.
    copy : int | None
        Reference ID to copy function (if any).
    equality : int | None
        Reference ID to equality function (if any).
    equality_use : str | None
        Usage string for equality function.
    """

    id: int
    name: str
    base_type: int
    size: int
    copy: int | None = None
    equality: int | None = None
    equality_use: str | None = None


@dataclass
class CStructField(CodeElement):
    """C structure field.

    Parameters
    ----------
    id : int
        Unique identifier for this field.
    name : str
        Name of the field.
    type : int
        Reference ID to the type of the field.
    pointer : bool | None
        Whether this field is a pointer.
    size : list[int] | None
        Array dimensions if this field is an array.
    """

    id: int
    name: str
    type: int
    pointer: bool | None = None
    size: list[int] | None = None

    @require_cgmapping
    def get_model_element(self) -> ModelElement | None:
        if not hasattr(self, "id"):
            raise AttributeError(
                f"{type(self).__name__} must have an 'id' attribute to inherit from CodeElement"
            )

        # Struct fields are potentially Probes counterparts, thus may have multiple model elements mapped.
        # If this code element has an association with an OBS_STRUCT_FIELD role, then it shall
        # return the Probe model element.
        if self.cgmapping._has_code_mapping_role(self.id, MappingRole.OBS_STRUCT_FIELD):  # type: ignore[missing-attribute]
            elements = self.cgmapping._get_model_for_code(self.id)  # type: ignore[missing-attribute]
            if not elements:
                return None
            if isinstance(
                elements[0], ModelVariable | ModelMonoVariable | ModelGroupVariableProjection
            ):
                probe = elements[0].get_associated_probe()
                if probe:
                    return probe
            return elements[0]
        else:
            return super().get_model_element()


@dataclass
class CStruct(CodeTypeBase):
    """C structure type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this struct type.
    name : str
        Name of the struct type.
    fields : list[CStructField]
        List of fields in the structure.
    copy : int | None
        Reference ID to copy function (if any).
    equality : int | None
        Reference ID to equality function (if any).
    equality_use : str | None
        Usage string for equality function.
    """

    id: int
    name: str
    fields: list[CStructField]
    copy: int | None = None
    equality: int | None = None
    equality_use: str | None = None


@dataclass
class CEnumValue(CodeElement):
    """C enum type value.

    Parameters
    ----------
    id : int
        Unique identifier for this enum value.
    name : str
        Name of the enum value.
    user_value : str | None
        User-defined constant expression for the enum value.
    """

    id: int
    name: str
    user_value: str | None = None


@dataclass
class CEnum(CodeElement):
    """C enum type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this enum type.
    name : str
        Name of the enum type.
    values : list[CEnumValue]
        List of enum values.
    """

    id: int
    name: str
    values: list[CEnumValue]


@dataclass
class CUnionVariant(CodeElement):
    """C union type variant.

    Parameters
    ----------
    id : int
        Unique identifier for this variant.
    name : str
        Name of the variant.
    enum_value : int
        Reference ID to the corresponding enum value.
    type : int
        Reference ID to the type of this variant.
    """

    id: int
    name: str
    enum_value: int
    type: int


@dataclass
class CUnion(CodeTypeBase):
    """C union type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this union type.
    name : str
        Name of the union type.
    variants : list[CUnionVariant]
        List of union variants.
    copy : int | None
        Reference ID to copy function (if any).
    equality : int | None
        Reference ID to equality function (if any).
    equality_use : str | None
        Usage string for equality function.
    """

    id: int
    name: str
    variants: list[CUnionVariant]
    copy: int | None = None
    equality: int | None = None
    equality_use: str | None = None


@dataclass
class CTypedef(CodeTypeBase):
    """C typedef definition.

    Parameters
    ----------
    id : int
        Unique identifier for this typedef.
    name : str
        Name of the typedef.
    type : int
        Reference ID to the underlying type.
    copy : int | None
        Reference ID to copy function (if any).
    equality : int | None
        Reference ID to equality function (if any).
    """

    id: int
    name: str
    type: int
    copy: int | None = None
    equality: int | None = None


@dataclass
class CExternalType(CodeTypeBase):
    """C external type.

    Parameters
    ----------
    id : int
        Unique identifier for this external type.
    name : str
        Name of the external type.
    scalar : bool | None
        Whether this is a scalar type.
    init : int | None
        Reference ID to initialization function (if any).
    copy : int | None
        Reference ID to copy function (if any).
    equality : int | None
        Reference ID to equality function (if any).
    """

    id: int
    name: str
    scalar: bool | None = None
    init: int | None = None
    copy: int | None = None
    equality: int | None = None


type CDeclaration = tuple[
    str,
    CFunction
    | CGlobal
    | CMacro
    | CPredefinedType
    | CStruct
    | CArray
    | CEnum
    | CUnion
    | CTypedef
    | CExternalType,
]
"""Type alias for C declarations (discriminated union)"""


@dataclass
class CodeContainer:
    """Generated code item with interface file, optional implementation file, and declarations."""

    """Path to the interface/header file.

    Parameters
    ----------
    interface_file : str
        Path to the interface/header file.
    implementation_file : str | None
        Path to the implementation file (if any).
    declarations : list[CDeclaration]
        List of C declarations in this container.
    user_provided : bool | None
        Whether this code is user-provided (not generated)."""

    interface_file: str
    declarations: list[CDeclaration]
    implementation_file: str | None = None
    user_provided: bool | None = None


class _CodeRegistry:
    """Registry to manage all code items and resolve ID references.

    This class stores all code items indexed by their unique IDs and provides
    methods to load from JSON and resolve references between items.

    Attributes
    ----------
    items : dict[int, CodeElement]
        Dictionary mapping item IDs to their corresponding objects.
    containers : list[CodeContainer]
        List of all code containers.
    """

    def __init__(self):
        """Initialize an empty code registry."""
        self.items: dict[int, CodeElement] = {}
        self.containers: list[CodeContainer] = []

    def register(self, item: CodeElement) -> None:
        """Register a code item in the registry.

        Parameters
        ----------
        item : CodeElement
            The code item to register. Must have an 'id' attribute.

        Raises
        ------
        ValueError
            If an item with the same ID is already registered or the ID is missing.
        """
        if not hasattr(item, "id"):
            raise ValueError(f"Item {item} does not have an 'id' attribute")

        if item.id in self.items:
            raise ValueError(f"Item with ID {item.id} is already registered")

        self.items[item.id] = item

    def add_container(self, container: CodeContainer) -> None:
        """Add a code container to the registry.

        Parameters
        ----------
        container : CodeContainer
            The code container to add.
        """
        self.containers.append(container)

    def get(self, item_id: int) -> CodeElement | None:
        """Get a code item by its ID.

        Parameters
        ----------
        item_id : int
            The unique ID of the item to retrieve.

        Returns
        -------
        CodeElement | None
            The code item if found, None otherwise.
        """
        return self.items.get(item_id)

    def get_by_type(self, item_type: type) -> list[CodeElement]:
        """Get all code items of a specific code type.

        Parameters
        ----------
        item_type : type
            The type of items to retrieve.

        Returns
        -------
        list[CodeElement]
            List of all items matching the specified type.
        """
        return [item for item in self.items.values() if isinstance(item, item_type)]

    def get_by_name(self, name: str) -> list[CodeElement]:
        """Get all code items with a specific name.

        Parameters
        ----------
        name : str
            The name to search for.

        Returns
        -------
        list[CodeElement]
            List of all items with the specified name.
        """
        return [item for item in self.items.values() if hasattr(item, "name") and item.name == name]

    def get_containers(self) -> list[CodeContainer]:
        """Get all code containers.

        Returns
        -------
        list[CodeContainer]
            List of all code containers.
        """
        return self.containers

    def get_container_by_interface(self, interface_file: str) -> CodeContainer | None:
        """Get a code container by its interface file path.

        Parameters
        ----------
        interface_file : str
            The interface file path to search for.

        Returns
        -------
        CodeContainer | None
            The code container if found, None otherwise.
        """
        for container in self.containers:
            if container.interface_file == interface_file:
                return container
        return None

    def clear(self) -> None:
        """Clear all items and containers from the registry."""
        self.items.clear()
        self.containers.clear()

    def __len__(self) -> int:
        """Return the number of items in the registry."""
        return len(self.items)

    def __contains__(self, item_id: int) -> bool:
        """Check if an item ID is in the registry."""
        return item_id in self.items

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f"CodeRegistry({len(self.items)} items, {len(self.containers)} containers)"


def parse_c_parameter(data: dict) -> CParameter:
    """Parse a CParameter from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the parameter.

    Returns
    -------
    CParameter
        Parsed parameter object.
    """
    return CParameter(
        id=data["id"],
        name=data["name"],
        type=data["type"],
        pointer=data.get("pointer"),
        const=data.get("const"),
    )


def parse_c_struct_field(data: dict) -> CStructField:
    """Parse a CStructField from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the struct field.

    Returns
    -------
    CStructField
        Parsed struct field object.
    """
    return CStructField(
        id=data["id"],
        name=data["name"],
        type=data["type"],
        pointer=data.get("pointer"),
        size=data.get("size"),
    )


def parse_c_enum_value(data: dict) -> CEnumValue:
    """Parse a CEnumValue from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the enum value.

    Returns
    -------
    CEnumValue
        Parsed enum value object.
    """
    return CEnumValue(id=data["id"], name=data["name"], user_value=data.get("user_value"))


def parse_c_union_variant(data: dict) -> CUnionVariant:
    """Parse a CUnionVariant from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the union variant.

    Returns
    -------
    CUnionVariant
        Parsed union variant object.
    """
    return CUnionVariant(
        id=data["id"],
        name=data["name"],
        enum_value=data["enum_value"],
        type=data["type"],
    )


def parse_c_declaration(data: tuple) -> CDeclaration:
    """Parse a CDeclaration from JSON data.

    Parameters
    ----------
    data : tuple
        JSON data as a tuple [type_name, declaration_data].

    Returns
    -------
    CDeclaration
        Parsed declaration as a tuple (type_name, declaration_object).
    """
    decl_type, decl_data = data

    if decl_type == "function":
        obj = CFunction(
            id=decl_data["id"],
            name=decl_data["name"],
            return_type=decl_data.get("return_type"),
            parameters=[parse_c_parameter(p) for p in decl_data.get("parameters", [])],
        )

    elif decl_type == "global":
        obj = CGlobal(id=decl_data["id"], name=decl_data["name"], type=decl_data["type"])

    elif decl_type == "macro":
        obj = CMacro(id=decl_data["id"], name=decl_data["name"])

    elif decl_type == "predefined_type":
        obj = CPredefinedType(id=decl_data["id"], name=decl_data["name"])

    elif decl_type == "struct":
        obj = CStruct(
            id=decl_data["id"],
            name=decl_data["name"],
            fields=[parse_c_struct_field(f) for f in decl_data.get("fields", [])],
            copy=decl_data.get("copy"),
            equality=decl_data.get("equality"),
            equality_use=decl_data.get("equality_use"),
        )

    elif decl_type == "array":
        obj = CArray(
            id=decl_data["id"],
            name=decl_data["name"],
            base_type=decl_data["base_type"],
            size=decl_data["size"],
            copy=decl_data.get("copy"),
            equality=decl_data.get("equality"),
            equality_use=decl_data.get("equality_use"),
        )

    elif decl_type == "enum":
        obj = CEnum(
            id=decl_data["id"],
            name=decl_data["name"],
            values=[parse_c_enum_value(v) for v in decl_data.get("values", [])],
        )

    elif decl_type == "union":
        obj = CUnion(
            id=decl_data["id"],
            name=decl_data["name"],
            variants=[parse_c_union_variant(v) for v in decl_data.get("variants", [])],
            copy=decl_data.get("copy"),
            equality=decl_data.get("equality"),
            equality_use=decl_data.get("equality_use"),
        )

    elif decl_type == "typedef":
        obj = CTypedef(
            id=decl_data["id"],
            name=decl_data["name"],
            type=decl_data["type"],
            copy=decl_data.get("copy"),
            equality=decl_data.get("equality"),
        )

    elif decl_type == "external_type":
        obj = CExternalType(
            id=decl_data["id"],
            name=decl_data["name"],
            scalar=decl_data.get("scalar"),
            init=decl_data.get("init"),
            copy=decl_data.get("copy"),
            equality=decl_data.get("equality"),
        )

    else:
        raise ValueError(f"Unknown C declaration type: {decl_type}")

    return (decl_type, obj)


def parse_code_container(data: dict) -> CodeContainer:
    """Parse a CodeContainer from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the code container.

    Returns
    -------
    CodeContainer
        Parsed code container object.
    """
    return CodeContainer(
        interface_file=data["interface_file"],
        implementation_file=data.get("implementation_file"),
        declarations=[parse_c_declaration(d) for d in data.get("declarations", [])],
        user_provided=data.get("user_provided"),
    )


def load_code_from_json(
    code_data: list[dict], registry: _CodeRegistry | None = None
) -> _CodeRegistry:
    """Load code containers from JSON data into a registry.

    Parameters
    ----------
    code_data : list[dict]
        List of code containers from JSON.
    registry : CodeRegistry | None
        Existing registry to use, or None to create a new one.

    Returns
    -------
    CodeRegistry
        Registry containing all parsed code items.
    """
    if registry is None:
        registry = _CodeRegistry()

    for container_data in code_data:
        container = parse_code_container(container_data)
        registry.add_container(container)

        # Register all declarations and their nested items
        for decl_type, decl_obj in container.declarations:
            registry.register(decl_obj)

            # Register nested items
            if isinstance(decl_obj, CFunction):
                for param in decl_obj.parameters:
                    registry.register(param)
            elif isinstance(decl_obj, CStruct):
                for struct_field in decl_obj.fields:
                    registry.register(struct_field)
            elif isinstance(decl_obj, CEnum):
                for value in decl_obj.values:
                    registry.register(value)
            elif isinstance(decl_obj, CUnion):
                for variant in decl_obj.variants:
                    registry.register(variant)

    return registry
