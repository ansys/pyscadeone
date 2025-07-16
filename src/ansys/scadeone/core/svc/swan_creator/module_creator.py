# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2024 ANSYS, Inc.
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

from abc import ABC
from typing import TYPE_CHECKING, List, Union, cast

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.common.versioning import gen_swan_version

if TYPE_CHECKING:
    from ansys.scadeone.core import swan
    import ansys.scadeone.core.swan.common as common
    from ansys.scadeone.core.model import Model


class UseDirectiveFactory:
    _instance = None

    def __init__(self) -> None:
        from ansys.scadeone.core.model.loader import SwanParser

        self._parser = SwanParser(LOGGER)

    def __new__(cls, *args, **kwargs) -> "UseDirectiveFactory":
        if not cls._instance:
            cls._instance = super(UseDirectiveFactory, cls).__new__(cls)
        return cls._instance

    def create_use_directive(
        self, module: Union["swan.Module", str], alias: str = None
    ) -> "swan.UseDirective":
        from ansys.scadeone.core.swan import Module, PathIdentifier

        if isinstance(module, str):
            module = Module(PathIdentifier.from_string(module))
        module_name = module.name.as_string
        if not module.name.is_valid:
            raise ScadeOneException(f"Invalid module name: {module_name}")
        code_str = "%s \nuse %s" % (gen_swan_version(), module_name)
        if alias:
            code_str += f" as {alias}"
        code_str += ";"
        use_dir_str = SwanString(code_str, "new_use")
        use_dir = self._parser.module_body(use_dir_str)
        return use_dir.use_directives[0]


class DeclarationFactory:
    _instance = None

    def __init__(self) -> None:
        from ansys.scadeone.core.model.loader import SwanParser

        self._parser = SwanParser(LOGGER)

    def __new__(cls, *args, **kwargs) -> "DeclarationFactory":
        if not cls._instance:
            cls._instance = super(DeclarationFactory, cls).__new__(cls)
        return cls._instance

    def create_declaration(self, decl: str) -> "swan.Declaration":
        """Create a declaration from an expression."""
        if decl[-1] != ";":
            decl += ";"
        decl_str = SwanString(decl, "new_decl")
        declaration = self._parser.declaration(decl_str)
        from ansys.scadeone.core.swan import (
            ConstDeclarations,
            GlobalDeclaration,
            GroupDeclarations,
            SensorDeclarations,
            TypeDeclarations,
        )

        if not isinstance(declaration, GlobalDeclaration):
            raise ScadeOneException(f"Invalid declaration: {decl}")
        if isinstance(declaration, ConstDeclarations):
            return declaration.constants[0]
        elif isinstance(declaration, TypeDeclarations):
            return declaration.types[0]
        elif isinstance(declaration, SensorDeclarations):
            return declaration.sensors[0]
        elif isinstance(declaration, GroupDeclarations):
            return declaration.groups[0]
        raise ScadeOneException(f"Declaration not supported: {decl}")

    @staticmethod
    def create_operator(
        name: Union[List["swan.Identifier"], str],
        is_node: bool = True,
        is_inlined: bool = False,
    ) -> "swan.Operator":
        """Create an operator."""
        from ansys.scadeone.core.swan import Identifier, Operator, Scope

        id = Identifier(name)  # noqa
        if not id.is_valid:
            raise ScadeOneException(f"Invalid module name: {name}")
        return Operator(id, is_inlined, is_node, [], [], Scope())

    @staticmethod
    def create_signature(
        name: Union[List["swan.Identifier"], str],
        is_node: bool = True,
        is_inlined: bool = False,
    ) -> "swan.Signature":
        """Create a signature."""
        from ansys.scadeone.core.swan import Identifier, Signature

        id = Identifier(name)  # noqa
        if not id.is_valid:
            raise ScadeOneException(f"Invalid module name: {name}")
        return Signature(id, is_inlined, is_node, [], [])

    def create_textual_operator(self, operator_str: str) -> "swan.Operator":
        """Create a textual operator."""
        from ansys.scadeone.core.swan import Operator

        operator = self._parser.operator_decl(SwanString(operator_str, "new_op"))
        if not isinstance(operator, Operator):
            raise ScadeOneException(f"Invalid operator: {operator_str}")
        operator.is_text = True
        return operator

    def create_textual_signature(self, operator_str: str) -> "swan.Operator":
        """Create a textual operator signature."""
        from ansys.scadeone.core.swan import Signature

        operator = self._parser.operator_decl(SwanString(operator_str, "new_op"))
        if isinstance(operator, Signature):
            operator.is_text = True
            return operator
        raise ScadeOneException(f"Invalid operator: {operator_str}")


class ModuleFactory:
    @staticmethod
    def create_module(name: Union[List["swan.PathIdentifier"], str]) -> "swan.Module":
        """Create a module."""
        from ansys.scadeone.core.swan import ModuleBody

        id_path = ModuleFactory._get_path_identifier(name)
        return ModuleBody(id_path)

    @staticmethod
    def create_module_interface(
        name: Union[List["swan.PathIdentifier"], str],
    ) -> "swan.ModuleInterface":
        """Create a module interface."""
        from ansys.scadeone.core.swan import ModuleInterface

        id_path = ModuleFactory._get_path_identifier(name)
        return ModuleInterface(id_path)

    @staticmethod
    def _get_path_identifier(name: str) -> "swan.PathIdentifier":
        """Get a path identifier from a module name."""
        from ansys.scadeone.core.swan import Identifier, PathIdentifier

        if isinstance(name, str):
            if name.find("::") == -1:
                path_id = PathIdentifier([Identifier(name)])
            else:
                path = name.split("::")
                path_id = PathIdentifier([Identifier(p) for p in path])
        elif isinstance(name, PathIdentifier):
            path_id = name
        else:
            raise ScadeOneException(f"Invalid module name: {name}")
        if not path_id.is_valid:
            raise ScadeOneException(f"Invalid module name: {name}")
        return path_id


class UseDirectiveAdder:
    @staticmethod
    def add_use_directive(module: "swan.Module", use_directive: "swan.UseDirective") -> None:
        """Add a use directive to the module."""
        module.use_directives.append(use_directive)
        use_directive._owner = module


class DeclarationAdder:
    @staticmethod
    def add_declaration(module: "swan.Module", declaration: "swan.Declaration") -> None:
        """Add a declaration to the module."""
        from ansys.scadeone.core.swan import (
            ConstDecl,
            ConstDeclarations,
            GroupDecl,
            GroupDeclarations,
            ModuleItem,
            Operator,
            SensorDecl,
            SensorDeclarations,
            Signature,
            TypeDecl,
            TypeDeclarations,
        )

        if isinstance(declaration, ConstDecl):
            const_decl = ConstDeclarations([declaration])
            module.declarations.append(cast(ModuleItem, const_decl))
        elif isinstance(declaration, TypeDecl):
            type_decl = TypeDeclarations([declaration])
            module.declarations.append(cast(ModuleItem, type_decl))
        elif isinstance(declaration, SensorDecl):
            sensor_decl = SensorDeclarations([declaration])
            module.declarations.append(cast(ModuleItem, sensor_decl))
        elif isinstance(declaration, GroupDecl):
            group_decl = GroupDeclarations([declaration])
            module.declarations.append(cast(ModuleItem, group_decl))
        elif isinstance(declaration, Operator):
            module.declarations.append(declaration)
        elif isinstance(declaration, Signature):
            module.declarations.append(declaration)
        else:
            raise ScadeOneException(f"Declaration not supported: {declaration}")
        declaration._owner = module


class ModuleAdder:
    @staticmethod
    def add_module(model: "Model", module: "swan.Module") -> None:
        """Add a module to the model."""
        from ansys.scadeone.core.swan import ModuleBody, ModuleInterface, TestHarness

        if model.module_exists(module):
            raise ScadeOneException(f"Module '{module.name}' already exists.")
        if isinstance(module, ModuleBody):
            model.add_body(module)
        elif isinstance(module, ModuleInterface):
            model.add_interface(module)
        elif isinstance(module, TestHarness):
            model.add_harness(module)
        else:
            assert False, f"Module type not supported: {type(module)}"


class ModuleCreator(ABC):
    def use(self, module: Union["swan.Module", str], alias: str = None) -> "swan.UseDirective":
        """Add a use directive to the module.

        Parameters
        ----------
        module: Module
            Module name.
        alias: Str
            Module alias.

        Returns
        -------
        UseDirective
            UseDirective object.
        """
        from ansys.scadeone.core.swan import Module

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add use directive to {type(self)}")
        use_directive = UseDirectiveFactory().create_use_directive(module, alias)
        UseDirectiveAdder.add_use_directive(self, use_directive)
        return use_directive

    def add_declaration(self, decl_expr: str) -> "common.Declaration":
        """Add a declaration to the module.

        Parameters
        ----------
        decl_expr: str
            Declaration expression.

        Returns
        -------
        Declaration
            Declaration object.
        """
        from ansys.scadeone.core.swan import Module

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add sensor to {type(self)}")
        declaration = DeclarationFactory().create_declaration(decl_expr)
        DeclarationAdder.add_declaration(self, declaration)
        return declaration

    def add_constant(self, name: str, type_str: str, value: str) -> "swan.ConstDecl":
        """Add a constant to the module.

        Parameters
        ----------
        name: str
            Constant name.
        type_str: Str
            Constant type.
        value: Str
            Constant value.

        Returns
        -------
        ConstDecl
            Constant object.
        """
        from ansys.scadeone.core.swan import ConstDecl, Module

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add constant to {type(self)}")
        const = DeclarationFactory().create_declaration(f"const {name}: {type_str} = {value}")
        DeclarationAdder.add_declaration(self, const)
        return cast(ConstDecl, const)

    def add_type(self, name: str, type_str: str) -> "swan.TypeDecl":
        """Add a type to the module.

        Parameters
        ----------
        name: str
            Type name.
        type_str: str
            Type definition as a string.

        Returns
        -------
        TypeDecl
            Type object.
        """
        from ansys.scadeone.core.swan import Module, TypeDecl

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add sensor to {type(self)}")
        type_decl = DeclarationFactory().create_declaration(f"type {name} = {type_str}")
        DeclarationAdder.add_declaration(self, type_decl)
        return cast(TypeDecl, type_decl)

    def add_enum(self, name: str, values: List[str]) -> "swan.TypeDecl":
        """Add an enum to the module.

        Parameters
        ----------
        name: str
            Enum name.
        values: List[Str]
            Enum values.

        Returns
        -------
        TypeDecl
            Type object.
        """
        from ansys.scadeone.core.swan import Module, TypeDecl

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add enum to {type(self)}")
        type_decl = DeclarationFactory().create_declaration(
            f"type {name} = enum {{{', '.join(values)}}}"
        )
        DeclarationAdder.add_declaration(self, type_decl)
        return cast(TypeDecl, type_decl)

    def add_struct(self, name: str, fields: dict[str, str]) -> "swan.TypeDecl":
        """Add a struct to the module.

        Parameters
        ----------
        name: str
            Struct name.
        fields: dict[str, str]
            Struct fields (name, type).

        Returns
        -------
        TypeDecl
            Type object.
        """
        from ansys.scadeone.core.swan import Module, TypeDecl

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add struct to {type(self)}")
        decl_str = f"type {name} = {{{', '.join(f'{k}: {v}' for k, v in fields.items())}}}"
        type_decl = DeclarationFactory().create_declaration(decl_str)
        DeclarationAdder.add_declaration(self, type_decl)
        return cast(TypeDecl, type_decl)

    def add_sensor(self, name: str, type_str: str) -> "swan.SensorDecl":
        """Add a sensor to the module.

        Parameters
        ----------
        name: str
            Sensor name.
        type_str: Str
            Sensor type.

        Returns
        -------
        SensorDecl
            Sensor object.
        """
        from ansys.scadeone.core.swan import Module, SensorDecl

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add sensor to {type(self)}")
        sensor = DeclarationFactory().create_declaration(f"sensor {name}: {type_str}")
        DeclarationAdder.add_declaration(self, sensor)
        return cast(SensorDecl, sensor)

    def add_group(
        self, name: str, types: Union[str, List[str], dict[str, str]]
    ) -> "swan.GroupDecl":
        """Add a group to the module.

        Parameters
        ----------
        name: str
            Group name.
        types: Union[str, List[str], dict[str, str]]
            List of types (type or {name: type}).

        Returns
        -------
        GroupDecl
            Group object.
        """
        from ansys.scadeone.core.swan import GroupDecl, Module

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add group to {type(self)}")
        if isinstance(types, str):
            type_list = [types]
        elif isinstance(types, list):
            type_list = types
        elif isinstance(types, dict):
            type_list = [f"{k}: {v}" for k, v in types.items()]
        else:
            raise ScadeOneException(f"Invalid types: {types}")
        group = DeclarationFactory().create_declaration(f"group {name} = ({', '.join(type_list)})")
        DeclarationAdder.add_declaration(self, group)
        return cast(GroupDecl, group)

    def add_operator(
        self,
        name: str,
        is_node: bool = True,
        is_inlined: bool = False,
    ) -> "swan.Operator":
        """Add an operator to the module body.

        Parameters
        ----------
        name: str
            Operator name.
        is_node: Bool
            True if Node, otherwise Function.
        is_inlined: Bool
            True if inline operator.

        Returns
        -------
        Operator
            Operator object.
        """
        from ansys.scadeone.core.swan import ModuleBody

        if not isinstance(self, ModuleBody):
            raise ScadeOneException(f"Cannot add operator to {type(self)}")
        operator = DeclarationFactory().create_operator(name, is_node, is_inlined)
        DeclarationAdder.add_declaration(self, operator)
        return operator

    def add_textual_operator(self, operator_str: str) -> "swan.Operator":
        """Add a textual operator to the module body.

        Parameters
        ----------
        operator_str: str
            Operator string.

        Returns
        -------
        Operator
            Operator object.
        """
        from ansys.scadeone.core.swan import ModuleBody, Operator

        if not isinstance(self, ModuleBody):
            raise ScadeOneException(f"Cannot add operator to {type(self)}")
        operator = DeclarationFactory().create_textual_operator(operator_str)
        DeclarationAdder.add_declaration(self, operator)
        return cast(Operator, operator)

    def add_signature(
        self,
        name: str,
        is_node: bool = True,
        is_inlined: bool = False,
    ) -> "swan.Signature":
        """Add an operator signature to the module.

        Parameters
        ----------
        name: str
            Operator name.
        is_inlined: Bool
            True if inline operator.
        is_node: Bool
            True if Node, otherwise Function.

        Returns
        -------
        Signature
            Signature object.
        """
        from ansys.scadeone.core.swan import Module

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add operator to {type(self)}")
        operator = DeclarationFactory().create_signature(name, is_node, is_inlined)
        DeclarationAdder.add_declaration(self, operator)
        return operator

    def add_textual_signature(self, operator_str: str) -> "swan.Signature":
        """Add a textual operator signature to the module.

        Parameters
        ----------
        operator_str: str
            Operator string.

        Returns
        -------
        Signature
            Signature object.
        """
        from ansys.scadeone.core.swan import Module, Signature

        if not isinstance(self, Module):
            raise ScadeOneException(f"Cannot add operator to {type(self)}")
        operator = DeclarationFactory().create_textual_signature(operator_str)
        DeclarationAdder.add_declaration(self, operator)
        return cast(Signature, operator)
