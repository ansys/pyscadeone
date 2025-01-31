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

from typing import Generator, Union, cast

from ansys.scadeone.core import project  # noqa: F401
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanFile
import ansys.scadeone.core.swan as S

from .loader import SwanParser


class Model:
    """Model handling class.
    A model contains module and interface declarations.

    Loading of Swan sources is lazy.
    """

    def __init__(self):
        self._modules = {}
        self._project = None
        self._parser = None

    def configure(self, project: "project.IProject"):
        """Configure model with project as owner. The configuration
        associate the project and the model and prepare internal data to
        store module bodies and interfaces.

        It is called by :py:attr:`ansys.scadeone.core.project.Project.model`."""
        self._modules = {swan: None for swan in project.swan_sources(all=True)}
        self._project = project
        self._parser = SwanParser(self.project.app.logger)
        return self

    @property
    def project(self) -> "project.IProject":
        """Model project, as a Project object."""
        return self._project

    @property
    def parser(self) -> SwanParser:
        """Swan parser."""
        return self._parser

    def _load_source(self, swan: SwanFile) -> S.Module:
        """Read a Swan file (.swan or .swani)

        Parameters
        ----------
        swan : SwanFile
            Swan source code.

        Returns
        -------
        Module
            Swan Module, either a ModuleBody or a ModuleInterface.

        Raises
        ------
        ScadeOneException
            - Error when file has not the proper suffix
            - Parse error
        """
        if swan.is_module:
            ast = self.parser.module_body(swan)
        elif swan.is_interface:
            ast = self.parser.module_interface(swan)
        else:
            raise ScadeOneException("Model.load_source: unexpected file kind {swan.path}.")
        self._modules[swan] = ast
        ast.owner = self
        ast.source = str(swan.path)
        return ast

    @property
    def all_modules_loaded(self) -> True:
        """Return True when all Swan modules have been loaded."""
        return all(self._modules.values())

    @property
    def modules(self) -> Generator[S.Module, None, None]:
        """Loaded module (module body or interface) as a generator."""
        return (module for module in self._modules.values() if module)

    def _get_module(self, name: str, search_module_body: bool) -> Union[S.Module, None]:
        """Return module body of name 'name'"""
        for swan_code, swan_object in self._modules.items():
            if swan_object is None:
                swan_object = self._load_source(swan_code)
            if (
                swan_object.name.as_string == name
                and isinstance(swan_object, S.ModuleBody) == search_module_body
            ):
                return swan_object
        return None

    def get_module_body(self, name: str) -> Union[S.ModuleBody, None]:
        """Return module body of name 'name'"""
        if body := self._get_module(name, True):
            return cast(S.ModuleBody, body)
        return None

    def get_module_interface(self, name: str) -> Union[S.ModuleInterface, None]:
        """Return module interface of name 'name'"""
        if interface := self._get_module(name, False):
            return cast(S.ModuleInterface, interface)
        return None

    def get_module_from_pathid(self, pathid: str, module: S.Module) -> Union[S.Module, None]:
        """Return the :py:class:`Module` instance for a given *pathid*.
        A *path* is of the form *[ID ::]+ ID*, where the last ID is the object
        name, and the "ID::ID...::" is the module path.

        If the *pathid* has no path part (reduced to ID), return *module*.

        Parameters
        ----------
        pathid : str
            object full path

        module : Module
            Context module where the search occurs.

        Returns
        -------
        Union[S.Module, None]
            Module of the object, or None if not module found
        """
        ids = pathid.split("::")

        if len(ids) == 1:
            return module

        model = cast(Model, module.model)
        if len(ids) == 2:
            # case M::ID
            if module.name.as_string == ids[0]:
                # case M::ID inside M (can happen from a search).
                # No use directives in that case
                return module
            use = module.get_use_directive(ids[0])
            if not use:
                # if not in module, try in interface.
                # not: module can be an interface already, its interface is None
                interface = module.interface()
                if not interface:
                    return None
                use = interface.get_use_directive(ids[0])
                if not use:
                    return None
            module_path = cast(S.UseDirective, use).path.as_string
        else:
            module_path = "::".join(ids[0:-1])
        m = model.get_module_body(module_path)
        if m is None:
            m = model.get_module_interface(module_path)
        return m

    @property
    def types(self) -> Generator[S.TypeDecl, None, None]:
        """Return a generator on type declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.TypeDeclarations)):
            for decl in cast(S.TypeDeclarations, decls).types:
                yield decl

    @property
    def sensors(self) -> Generator[S.SensorDecl, None, None]:
        """Return a generator on sensor declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.SensorDeclarations)):
            for decl in cast(S.SensorDeclarations, decls).sensors:
                yield decl

    @property
    def constants(self) -> Generator[S.ConstDecl, None, None]:
        """Return a generator on constant declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.ConstDeclarations)):
            for decl in cast(S.ConstDeclarations, decls).constants:
                yield decl

    @property
    def groups(self) -> Generator[S.GroupDecl, None, None]:
        """Return a generator on group declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.GroupDeclarations)):
            for decl in cast(S.GroupDeclarations, decls).groups:
                yield decl

    @property
    def operators(self) -> Generator[S.Operator, None, None]:
        """Return a generator on operator declarations."""
        for decl in self.filter_declarations(lambda x: isinstance(x, S.Operator)):
            yield decl

    @property
    def signatures(self) -> Generator[S.Signature, None, None]:
        """Return a generator on operator signature declarations."""
        for decl in self.filter_declarations(
            lambda x: isinstance(x, S.Signature) and not isinstance(x, S.Operator)
        ):
            yield decl

    def load_module(self, name: str):
        """Load module by name

        Parameters
        ----------
        name : str
            Module name.

        Returns
        -------
        Module
            Swan Module, either a ModuleBody or a ModuleInterface.

        """
        for swan in self._modules.keys():
            if swan.name.lower() == name.lower():
                self._load_source(swan)

    def load_all_modules(self):
        """Load systematically all modules."""
        for swan in self._modules.keys():
            self._load_source(swan)

    @property
    def declarations(self) -> Generator[S.GlobalDeclaration, None, None]:
        """Declarations found in all modules/interfaces as a generator.

        The Swan code of a module/interface is loaded if not yet loaded.
        """

        # Need to use self._modules here, as self.modules is not a direct access to it
        for swan_code, swan_object in self._modules.items():
            if swan_object is None:
                swan_object = self._load_source(swan_code)
            for decl in swan_object.declarations:
                yield decl

    def filter_declarations(self, filter_fn) -> Generator[S.GlobalDeclaration, None, None]:
        """Return declarations matched by a filter.

        Parameters
        ----------
        filter_fn : function
            A function of one argument of type S.GlobalDeclaration, returning True or False.

        Yields
        ------
        Generator[S.GlobalDeclaration, None, None]
            Generator on matching declarations.
        """
        return filter(filter_fn, self.declarations)

    def find_declaration(self, predicate_fn) -> Union[S.GlobalDeclaration, None]:
        """Find a declaration for which predicate_fn returns True.

        Parameters
        ----------
        predicate_fn : function
            Function taking one S.GlobalDeclaration as argument and
            returning True when some property holds, else False.

        Returns
        -------
        Union[S.GlobalDeclaration, None]
            Found declaration or None.
        """
        for decl in self.filter_declarations(predicate_fn):
            return decl
        return None
