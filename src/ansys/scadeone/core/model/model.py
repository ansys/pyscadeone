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

from pathlib import Path
from typing import List, Union, cast

from ansys.scadeone.core import project  # noqa: F401
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanFile
import ansys.scadeone.core.swan as swan

from .loader import SwanParser


class Model:
    """Model handling class.
    A model contains module and interface declarations.

    Loading of Swan sources is lazy.
    """

    def __init__(self) -> None:
        self._project = None
        self._parser = None
        self._bodies = {}  # _bodies["N1::N2::M"] = ModuleBody | SwanFile
        self._interfaces = {}
        self._harnesses = {}

    def add_body(self, swan_path: Path, swan_elt: Union[swan.SwanFile, swan.ModuleBody]) -> None:
        self._bodies[Model._get_swan_name(swan_path)] = swan_elt

    def add_interface(
        self, swan_path: Path, swan_elt: Union[swan.SwanFile, swan.ModuleInterface]
    ) -> None:
        self._interfaces[Model._get_swan_name(swan_path)] = swan_elt

    def add_harness(self, swan_path: Path, swan_elt: Union[swan.SwanFile, swan.TestModule]) -> None:
        self._harnesses[Model._get_swan_name(swan_path)] = swan_elt

    def module_exists(self, module_file: SwanFile) -> bool:
        return (
            (module_file.is_module and module_file.name in self._bodies.keys())
            or (module_file.is_interface and module_file.name in self._interfaces.keys())
            or (module_file.is_test and module_file.name in self._harnesses.keys())
        )

    @staticmethod
    def _get_swan_name(swan_path: Path) -> str:
        return swan_path.stem.replace("-", "::")

    def add_asset(
        self, module: Union[swan.ModuleBody, swan.ModuleInterface, swan.TestModule]
    ) -> None:
        """Adds an asset to the model, respectively to its type and name

        Parameters
        ----------
        module : Union[swan.ModuleBody, swan.ModuleInterface, swan.TestModule]
            Asset to add
        """
        if isinstance(module, swan.ModuleBody):
            self.add_body(module.name, module)
        elif isinstance(module, swan.ModuleInterface):
            self.add_interface(module.name, module)
        elif isinstance(module, swan.TestModule):
            self.add_harness(module.name, module)

    def module_dicts(self) -> List[dict]:
        """Returns all modules dicts in one list"""
        return [self._bodies, self._interfaces, self._harnesses]

    def configure(self, project_instance: "project.IProject"):
        """Configures model for a given project. The configuration
        associates the project and the model and prepares internal data to
        store module bodies and interfaces.

        It is called by :py:attr:`ansys.scadeone.core.project.Project.model`."""

        if project_instance.storage.exists():
            for swan_file in project_instance.swan_sources(all=True):
                if swan_file.is_module:
                    self._bodies[Model._get_swan_name(swan_file.path)] = swan_file
                elif swan_file.is_interface:
                    self._interfaces[Model._get_swan_name(swan_file.path)] = swan_file
                # TODO use this once test harness visitor and creator are implemented
                # elif swan_file.is_test:
                #     self._harnesses[Model._get_swan_name(swan_path)] = swan_file

        self._project = project_instance
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

    def _load_source(
        self,
        swan_f: Union[SwanFile, swan.ModuleBody, swan.ModuleInterface, swan.TestModule],
        project: "project.IProject" = None,
    ) -> swan.Module:
        """Read a Swan file (.swan or .swani or .swant)

        Parameters
        ----------
        swan_f : Union[SwanFile, swan.ModuleBody, swan.ModuleInterface, swan.TestModule]
            Swan source code or module

        Returns
        -------
        Module
            Swan Module, either a ModuleBody, a ModuleInterface or a TestModule.

        Raises
        ------
        ScadeOneException
            - Error when file has not the proper suffix
            - Parse error
        """
        if (
            isinstance(swan_f, swan.ModuleBody)
            or isinstance(swan_f, swan.ModuleInterface)
            or isinstance(swan_f, swan.TestModule)
        ):
            return swan_f
        elif swan_f.is_module:
            ast = self.parser.module_body(swan_f)
            ast.source = str(swan_f.path)
        elif swan_f.is_interface:
            ast = self.parser.module_interface(swan_f)
            ast.source = str(swan_f.path)
        elif swan_f.is_test:
            ast = self.parser.test_harness(swan_f)
        else:
            raise ScadeOneException(f"Model.load_source: unexpected file kind {swan_f.path}.")
        ast.owner = project
        return ast

    @property
    def all_modules_loaded(self) -> bool:
        """Returns True when all Swan modules have been loaded."""
        for module_dict in self.module_dicts():
            for module in module_dict.values():
                if not (
                    isinstance(module, swan.ModuleBody)
                    or isinstance(module, swan.ModuleInterface)
                    or isinstance(module, swan.TestModule)
                ):
                    return False
        return True

    @property
    def modules(self) -> List[swan.Module]:
        """Returns all model modules (module body, interface, test harness) as a list."""
        modules_list = [value for d in self.module_dicts() for value in d.values()]
        return modules_list

    def get_module_body(self, name: str) -> Union[swan.ModuleBody, None]:
        """Returns module body of name 'name'"""
        if name not in self._bodies:
            return None
        if isinstance(self._bodies.get(name), SwanFile):
            self._bodies[name] = self._load_source(self._bodies[name], self._project)
        return self._bodies[name]

    def get_module_interface(self, name: str) -> Union[swan.ModuleInterface, None]:
        """Returns module interface of name 'name'"""
        if name not in self._interfaces:
            return None
        if isinstance(self._interfaces.get(name), SwanFile):
            self._interfaces[name] = self._load_source(self._interfaces[name], self._project)
        return self._interfaces[name]

    def get_test_harness(self, name: str) -> Union[swan.TestModule, None]:
        """Returns module test harness of name 'name'"""
        if name not in self._harnesses:
            return None
        if isinstance(self._harnesses.get(name), SwanFile):
            self._harnesses[name] = self._load_source(self._harnesses[name], self._project)
        return self._harnesses[name]

    def get_module_from_pathid(self, pathid: str, module: swan.Module) -> Union[swan.Module, None]:
        """Return the :py:class:`Module` instance for a given *pathid*
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
            module_path = cast(swan.UseDirective, use).path.as_string
        else:
            module_path = "::".join(ids[0:-1])
        m = model.get_module_body(module_path)
        if m is None:
            m = model.get_module_interface(module_path)
        return m

    @property
    def types(self) -> List[swan.TypeDecl]:
        """Returns a list of type declarations."""
        types = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.TypeDeclarations)):
            for type in cast(swan.TypeDeclarations, decls).types:
                types.append(type)
        return types

    @property
    def sensors(self) -> List[swan.SensorDecl]:
        """Returns a list of sensor declarations."""
        sensors = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.SensorDeclarations)):
            for sensor in cast(swan.SensorDeclarations, decls).sensors:
                sensors.append(sensor)
        return sensors

    @property
    def constants(self) -> List[swan.ConstDecl]:
        """Returns a list of constant declarations."""
        consts = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.ConstDeclarations)):
            for const in cast(swan.ConstDeclarations, decls).constants:
                consts.append(const)
        return consts

    @property
    def groups(self) -> List[swan.GroupDecl]:
        """Returns a list of group declarations."""
        groups = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.GroupDeclarations)):
            for group in cast(swan.GroupDeclarations, decls).groups:
                groups.append(group)
        return groups

    @property
    def operators(self) -> List[swan.Operator]:
        """Returns a list of operator declarations."""
        return [
            cast(swan.Operator, operator)
            for operator in self.filter_declarations(lambda x: isinstance(x, swan.Operator))
        ]

    @property
    def signatures(self) -> List[swan.Signature]:
        """Returns a list of operator signature declarations."""
        return [
            cast(swan.Signature, signature)
            for signature in self.filter_declarations(
                lambda x: isinstance(x, swan.Signature) and not isinstance(x, swan.Operator)
            )
        ]

    def _load_module(self, name: str, mod_dict: dict) -> None:
        swan_file = mod_dict.get(name)
        if swan_file and isinstance(swan_file, SwanFile):
            mod_dict[name] = self._load_source(swan_file, self._project)

    def load_module_body(self, name: str) -> None:
        self._load_module(name, self._bodies)

    def load_module_interface(self, name: str) -> None:
        self._load_module(name, self._interfaces)

    def load_test_harness(self, name: str) -> None:
        self._load_module(name, self._harnesses)

    def load_all_modules(
        self, bodies: bool = True, interfaces: bool = True, harnesses: bool = True
    ) -> None:
        """Loads systematically all modules.

        Parameters
        ----------
        bodies : bool, optional
            Includes module bodies
        interfaces : bool, optional
            Includes module interfaces
        harnesses : bool, optional
            Includes test harnesses
        """
        for cond, data, load_fn in [
            (bodies, self._bodies, self.load_module_body),
            (interfaces, self._interfaces, self.load_module_interface),
            (harnesses, self._harnesses, self.load_test_harness),
        ]:
            if cond:
                for name in data.keys():
                    load_fn(name)

    @property
    def declarations(self) -> List[swan.GlobalDeclaration]:
        """Declarations found in all modules/interfaces as a list.

        The Swan code of a module/interface is loaded if not yet loaded.
        """

        declarations = []
        for data, load_fn in [
            (self._interfaces, self.load_module_interface),
            (self._bodies, self.load_module_body),
            (self._harnesses, self.load_test_harness),
        ]:
            for swan_code, swan_object in data.items():
                if isinstance(swan_object, SwanFile):
                    swan_object = self._load_source(swan_object, self.project)
                    data[swan_code] = swan_object
                elif swan_object is None:
                    swan_object = load_fn(swan_code)
                    data[swan_code] = swan_object
                for decl in swan_object.declarations:
                    declarations.append(cast(swan.GlobalDeclaration, decl))
        return declarations

    def filter_declarations(self, filter_fn) -> List[swan.GlobalDeclaration]:
        """Returns declarations matched by a filter.

        Parameters
        ----------
        filter_fn : function
            A function of one argument of type S.GlobalDeclaration, returning True or False.

        Returns
        -------
        List[S.GlobalDeclaration]
            List of matching declarations.
        """
        return list(filter(filter_fn, self.declarations))

    def find_declaration(self, predicate_fn) -> Union[swan.GlobalDeclaration, None]:
        """Finds a declaration for which predicate_fn returns True.

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
