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
This module contains classes for package and interface.
"""

from typing import List, Optional, Union, cast
from pathlib import Path

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.svc.swan_creator.module_creator import ModuleCreator
import ansys.scadeone.core.swan.common as common


from .globals import ConstDecl, SensorDecl
from .groupdecl import GroupDecl
from .operators import Operator, Signature
from .typedecl import TypeDecl


class GlobalDeclaration(common.ModuleItem):  # numpydoc ignore=PR01
    """Abstract class for global declarations:

    - type declaration list
    - constant declaration list
    - sensor declaration list
    - group declarations
    - user operator declaration (without body, in interface)
    - user operator definition (with body)
    """

    def __init__(self) -> None:
        super().__init__()

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        if self.owner is None:
            raise ScadeOneException("No owner")
        return f"{self.owner.get_full_path()}"


class TypeDeclarations(GlobalDeclaration):  # numpydoc ignore=PR01
    """Type declarations: **type** {{ *type_decl* ; }}."""

    def __init__(self, types: List[TypeDecl]) -> None:
        super().__init__()
        self._types = types
        common.SwanItem.set_owner(self, types)

    @property
    def types(self) -> List[TypeDecl]:
        """Declared types."""
        return self._types


class ConstDeclarations(GlobalDeclaration):  # numpydoc ignore=PR01
    """Constant declarations: **constant** {{ *constant_decl* ; }}."""

    def __init__(self, constants: List[ConstDecl]) -> None:
        super().__init__()
        self._constants = constants
        common.SwanItem.set_owner(self, constants)

    @property
    def constants(self) -> List[ConstDecl]:
        """Declared constants."""
        return self._constants


class SensorDeclarations(GlobalDeclaration):  # numpydoc ignore=PR01
    """Sensor declarations: **sensor** {{ *sensor_decl* ; }}."""

    def __init__(self, sensors: List[SensorDecl]) -> None:
        super().__init__()
        self._sensors = sensors
        common.SwanItem.set_owner(self, sensors)

    @property
    def sensors(self) -> List[SensorDecl]:
        """Declared sensors."""
        return self._sensors


class GroupDeclarations(GlobalDeclaration):  # numpydoc ignore=PR01
    """Group declarations: **group** {{ *group_decl* ; }}."""

    def __init__(self, groups: List[GroupDecl]) -> None:
        super().__init__()
        self._groups = groups
        common.SwanItem.set_owner(self, groups)

    @property
    def groups(self) -> List[GroupDecl]:
        """Declared groups."""
        return self._groups


class UseDirective(common.ModuleItem):  # numpydoc ignore=PR01
    """Class for **use** directive."""

    def __init__(
        self, path: common.PathIdentifier, alias: Optional[common.Identifier] = None
    ) -> None:
        super().__init__()
        self._path = path
        self._alias = alias

    @property
    def path(self) -> common.PathIdentifier:
        """Used module path."""
        return self._path

    @property
    def alias(self) -> Union[common.Identifier, None]:
        """Renaming of module."""
        return self._alias


class ProtectedDecl(common.ProtectedItem, GlobalDeclaration):  # numpydoc ignore=PR01
    """Protected declaration."""

    def __init__(self, markup: str, data: str) -> None:
        super().__init__(data, markup)

    @property
    def is_type(self) -> bool:
        """Protected type declaration."""
        return self.markup == "type"

    @property
    def is_const(self) -> bool:
        """Protected const declaration."""
        return self.markup == "const"

    @property
    def is_group(self) -> bool:
        """Protected group declaration."""
        return self.markup == "group"

    @property
    def is_sensor(self) -> bool:
        """Protected sensor declaration."""
        return self.markup == "sensor"

    @property
    def is_user_operator(self) -> bool:
        """Protected operator declaration.

        Note: operator declaration within {text% ... %text} is parsed."""
        return self.markup == "syntax_text"

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        if self.owner is None:
            raise ScadeOneException("No owner")
        return f"{self.owner.get_full_path()}::<protected>"


class Module(common.ModuleBase, ModuleCreator):  # numpydoc ignore=PR01
    """Module base class.

    Parameters
    ----------
    name : common.PathIdentifier
        module name
    use_directives : Union[List[UseDirective], None]
        **use** directives
    declarations : Union[List[common.ModuleItem], None]
        module declarations
    """

    def __init__(
        self,
        name: common.PathIdentifier,
        use_directives: List[UseDirective] = None,
        declarations: List[common.ModuleItem] = None,
    ) -> None:
        super().__init__()
        self._name = name
        self._uses = use_directives if use_directives else []
        self._declarations = declarations if declarations else []
        self._source = None
        common.SwanItem.set_owner(self, self._uses)
        common.SwanItem.set_owner(self, self._declarations)

    @property
    def name(self) -> common.PathIdentifier:
        """Module or Interface name."""
        return self._name

    @property
    def source(self) -> Union[str, None]:
        "Source of the module, as a string (file name)."
        return self._source

    @source.setter
    def source(self, path: str):
        "Set source of the module"
        self._source = path

    @property
    def declarations(self) -> List[common.ModuleItem]:
        """Module's declarations"""
        return self._declarations

    @property
    def use_directives(self) -> List[UseDirective]:
        """Module's **use** directives as a list."""
        return self._uses

    @property
    def extension(self) -> str:
        """Return module extension, with . included."""
        return ""

    @property
    def file_name(self) -> str:
        """Return a file name based on module name and namespaces."""
        return self.name.as_string.replace("::", "-") + self.extension

    @staticmethod
    def module_name_from_path(path: Path) -> str:
        """Returns a module name from a path.

        Parameters
        ----------
        path : Path
            Path to the module, e.g. */path/to/namespace-module.swan*

        Returns
        -------
        str
            Module name, e.g. *namespace::module*
        """
        module_name = path.stem.replace("-", "::")
        if common.PathIdentifier.is_valid_path(module_name):
            return module_name
        raise ScadeOneException(f"Invalid module path name: {path}")

    def filter_declarations(self, filter_fn) -> List[GlobalDeclaration]:
        """Return declarations matched by a filter.

        Parameters
        ----------
        filter_fn : function
            A function of one argument of type GlobalDeclaration, returning True or False.

        Returns
        -------
        List[GlobalDeclaration]
            List of matching declarations.
        """
        return list(filter(filter_fn, self.declarations))

    @property
    def types(self) -> List[TypeDecl]:
        """Return a list of type declarations."""
        types = []
        for decl in self.filter_declarations(lambda x: isinstance(x, TypeDeclarations)):
            for typ in cast(TypeDeclarations, decl).types:
                types.append(typ)
        return types

    @property
    def sensors(self) -> List[SensorDecl]:
        """Return a list of sensor declarations."""
        sensors = []
        for decl in self.filter_declarations(lambda x: isinstance(x, SensorDeclarations)):
            for sensor in cast(SensorDeclarations, decl).sensors:
                sensors.append(sensor)
        return sensors

    @property
    def constants(self) -> List[ConstDecl]:
        """Return a list of constant declarations."""
        constants = []
        for decl in self.filter_declarations(lambda x: isinstance(x, ConstDeclarations)):
            for constant in cast(ConstDeclarations, decl).constants:
                constants.append(constant)
        return constants

    @property
    def groups(self) -> List[GroupDecl]:
        """Return a list of group declarations."""
        groups = []
        for decl in self.filter_declarations(lambda x: isinstance(x, GroupDeclarations)):
            for grp in cast(GroupDeclarations, decl).groups:
                groups.append(grp)
        return groups

    @property
    def signatures(self) -> List[Signature]:
        """Return a list of signatures."""
        return [
            cast(Signature, signature)
            for signature in self.filter_declarations(lambda x: isinstance(x, Signature))
            if signature
        ]

    def get_full_path(self) -> str:
        """Full Swan path of module."""
        return self.name.as_string

    def get_declaration(self, name: str) -> GlobalDeclaration:
        """Return the type, global, or operator declaration searching by namespace."""
        from .namespace import ModuleNamespace

        m_ns = ModuleNamespace(self)
        decl = m_ns.get_declaration(name)
        return cast(GlobalDeclaration, decl) if decl else None

    def get_use_directive(self, module_name: str) -> Union[UseDirective, None]:
        """Return the use directive searching by module name or alias name.

        Aliases are searched first, the module name is searched if no alias is found.
        When a module name is searched, use directive with first occurrence is returned.

        Parameters
        ----------
            module_name : str
                Name of the module (last part of a path) or alias.

        Returns
        -------
            Found UseDirective or None
        """
        for use in self.use_directives:
            if use.alias:
                key = use.alias.value
            else:
                if not isinstance(use.path.path_id, list):
                    raise ScadeOneException(f"{use.path.as_string} is invalid.")
                key = use.path.path_id[-1].value
            if key == module_name:
                return use
        return None

    def interface(self) -> "ModuleInterface":
        """Return the module interface for a module body if it exists."""
        return None

    def body(self) -> "ModuleBody":
        """Return the module body for a module interface if it exists."""
        return None

    def harness(self):
        """Return the test harness if it exists."""
        return None


class ModuleInterface(Module):  # numpydoc ignore=PR01
    """Module interface definition."""

    def __init__(
        self,
        name: common.PathIdentifier,
        use_directives: Optional[List[UseDirective]] = None,
        declarations: Optional[List[common.ModuleItem]] = None,
    ) -> None:
        super().__init__(name, use_directives, declarations)

    @property
    def extension(self) -> str:
        """Return module extension, with . included."""
        return ".swani"

    def body(self) -> "ModuleBody":
        """Return the module body for a module interface if it exists."""
        return self.model.get_module_body(self.name.as_string)


class ModuleBody(Module):  # numpydoc ignore=PR01
    """Module body definition."""

    def __init__(
        self,
        name: common.PathIdentifier,
        use_directives: Optional[List[UseDirective]] = None,
        declarations: Optional[List[GlobalDeclaration]] = None,
    ) -> None:
        super().__init__(name, use_directives, declarations)

        from ansys.scadeone.core.model.loader import SwanParser

        self._parser = SwanParser(LOGGER)

    @property
    def extension(self) -> str:
        """Return module extension, with '.' included."""
        return ".swan"

    @property
    def operators(self) -> List[Operator]:
        """Return a list of operators."""
        return [
            cast(Operator, decl)
            for decl in self.filter_declarations(lambda x: isinstance(x, Operator))
            if decl
        ]

    def interface(self) -> "ModuleInterface":
        """Return the module interface for a module body if it exists."""
        return self.model.get_module_interface(self.name.as_string)
