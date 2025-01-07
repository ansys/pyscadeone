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

from typing import Generator, Union, Optional, cast

from ..common.exception import ScadeOneException
from ..model import Model
from .common import Declaration, SwanItem
from .diagram import Diagram, SectionBlock
from .modules import (
    Module,
    GroupDeclarations,
    TypeDeclarations,
    ConstDeclarations,
    SensorDeclarations,
    ModuleInterface,
    ModuleBody,
)
from .operators import Operator, Signature
from .scopes import Scope, ScopeSection
from .scopesections import VarSection
from .variable import VarDecl


class ModuleNamespace:
    """Class to handle named objects defined in a module."""

    def __init__(self, module: Module):
        self._module = module

    def get_declaration(self, name: str) -> SwanItem:
        """Returns the declaration with the given name."""

        if not name:
            raise ScadeOneException("Name cannot be None or empty.")

        decl = ModuleNamespace._get_declaration(name, self._module)
        if decl is not None:
            return decl
        model = cast(Model, self._module.model)
        module_int = model.get_module_interface(self._module.name.as_string)
        if module_int is not None:
            ns = ModuleNamespace(module_int)
            return ns.get_declaration(name)

    @staticmethod
    def _get_declaration(name: str, module: Module) -> SwanItem:
        # Returns declaration searching by name
        if name.find("::") == -1:
            for decl in module.declarations:
                found_decl = None
                if isinstance(decl, GroupDeclarations):
                    found_decl = ModuleNamespace._find_declaration(name, decl.groups)
                if isinstance(decl, TypeDeclarations):
                    found_decl = ModuleNamespace._find_declaration(name, decl.types)
                if isinstance(decl, ConstDeclarations):
                    found_decl = ModuleNamespace._find_declaration(name, decl.constants)
                if isinstance(decl, SensorDeclarations):
                    found_decl = ModuleNamespace._find_declaration(name, decl.sensors)
                if isinstance(decl, Signature) and str(decl.id) == name:
                    found_decl = decl
                if found_decl is not None:
                    return found_decl
            return None
        else:
            # look for path_id
            module_from_name = cast(Model, module.model).get_module_from_pathid(name, module)
            if module_from_name is None:
                raise ScadeOneException(f"Module not found: {name}.")
            module_ns = ModuleNamespace(module_from_name)
            return module_ns.get_declaration(name.split("::")[-1])

    @staticmethod
    def _find_declaration(
        name: str, declarations: Generator[Declaration, None, None]
    ) -> Optional[Declaration]:
        """Look for a declaration searching by name"""
        if name is None:
            raise ScadeOneException("Declaration name is None.")
        for decl in declarations:
            if decl.id is None:
                continue
            if decl.id.value == name:
                return decl
        return None


class ScopeNamespace:
    """Class to handle named objects defined in a scope.

    As scope can contain other scopes, each scope maintains a reference
    to its enclosing scope.
    """

    def __init__(self, scope: Union[Scope, ScopeSection]):
        self._scope = scope

    def get_declaration(self, name: str) -> SwanItem:
        """Returns the declaration with the given name."""
        from .scopes import Scope, ScopeSection

        if not name:
            raise ScadeOneException("Name cannot be None or empty.")
        if isinstance(self._scope, ScopeSection):
            return ScopeNamespace._get_section_declaration(name, self._scope)
        elif isinstance(self._scope, Scope):
            for section in self._scope.sections:
                return ScopeNamespace._get_section_declaration(name, section)

    @staticmethod
    def _get_section_declaration(name: str, section: ScopeSection) -> SwanItem:
        """Returns the section declaration with the given namespace."""
        if name.find("::") == -1:
            return ScopeNamespace._find_declaration(name, section)

        # look for path_id
        module_from_name = cast(Model, section.model).get_module_from_pathid(name, section.module)
        if module_from_name is None:
            raise ScadeOneException(f"Module not found: {name}.")
        module_ns = ModuleNamespace(module_from_name)
        return module_ns.get_declaration(name.split("::")[-1])

    @staticmethod
    def _find_declaration(name: str, item: SwanItem) -> SwanItem:
        # Look for declaration with the given name.

        if isinstance(item, ModuleBody):
            module_ns = ModuleNamespace(item)
            return module_ns.get_declaration(name)
        if isinstance(item, ModuleInterface):
            module_ns = ModuleNamespace(item)
            return module_ns.get_declaration(name)
        if isinstance(item, Operator):
            for input in item.inputs:
                if not isinstance(input, VarDecl):
                    raise ScadeOneException("Input is not a variable.")
                if input.id.value == name:
                    return input
            for output in item.outputs:
                if not isinstance(output, VarDecl):
                    raise ScadeOneException("Output is not a variable.")
                if output.id.value == name:
                    return output
        if isinstance(item, Scope):
            for section in item.sections:
                decl = ScopeNamespace._find_section_obj(name, section)
                if decl is not None:
                    return decl
        if isinstance(item, ScopeSection):
            decl = ScopeNamespace._find_section_obj(name, item)
            if decl is not None:
                return decl
        if item.owner is None:
            raise ScadeOneException(f"Item without owner: {type(item)}")
        return ScopeNamespace._find_declaration(name, item.owner)

    @staticmethod
    def _find_section_obj(name: str, section: ScopeSection) -> Declaration:
        """Returns the section object with the given name."""
        if isinstance(section, VarSection):
            for var_decl in section.var_decls:
                if var_decl.id.value == name:
                    return var_decl
        if isinstance(section, Diagram):
            for obj in filter(lambda sec_obj: isinstance(sec_obj, SectionBlock), section.objects):
                if not isinstance(obj.section, VarSection):
                    continue
                var_sec = ScopeNamespace._find_section_obj(name, obj.section)
                if var_sec is not None:
                    return var_sec
        return None
