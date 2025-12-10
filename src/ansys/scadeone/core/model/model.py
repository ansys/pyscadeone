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

from typing import List, Union, Callable, cast

from ansys.scadeone.core import project  # noqa: F401
from ansys.scadeone.core.interfaces import IScadeOne, IModel
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanFile
import ansys.scadeone.core.swan as swan

from .loader import SwanParser


class Model(IModel):
    """Model handling class.
    A model contains module and interface declarations.

    Loading of Swan sources is lazy: when a module body or interface is needed,
    it is loaded from the Swan source file.

    The IModel base class is an empty interface implemented by the Model class.
    """

    def __init__(self, app: IScadeOne) -> None:
        # dictionaries of Swan module, interface and test module
        # Key is the Swan name of the module, interface or test module
        self._bodies = {}  # _bodies["N1::N2::M"] = ModuleBody | SwanFile
        self._interfaces = {}
        self._test_modules = {}
        self._app = app
        self._parser = SwanParser(self.app.logger)  # type: ignore # link Python / DOTNET

    @property
    def app(self) -> IScadeOne:
        """Scade One application instance."""
        return self._app

    def _add_module(self, swan_elt: Union[SwanFile, swan.Module], where: dict) -> None:
        """Add a SwanFile (content will be possible loaded later) or a Module to its
        proper dictionary *where* (bodies, interfaces, test modules). If Module is given, updates ownership."""
        where[Model._get_swan_name(swan_elt)] = swan_elt
        if isinstance(swan_elt, swan.Module):
            swan_elt.owner = self

    def add_body(self, swan_elt: swan.ModuleBody) -> None:
        """Add a module body to the model.

        Parameters
        ----------
        swan_elt : swan.ModuleBody
            Content of the module body
        """
        self._add_module(swan_elt, self._bodies)

    def add_interface(self, swan_elt: swan.ModuleInterface) -> None:
        """Add a module interface to the model.

        Parameters
        ----------
        swan_elt : swan.ModuleInterface
            Content of the module interface
        """
        self._add_module(swan_elt, self._interfaces)

    def module_exists(self, module: swan.Module) -> bool:
        """Check if a module exists by its path in the model.

        Parameters
        ----------
        module : swan.Module
            Module source or module object to check. In case of a source, it is not loaded.

        Returns
        -------
        bool
            True if the module exists, False otherwise.
        """
        where = None
        if isinstance(module, swan.Module):
            module_name = cast(swan.Module, module).name.as_string
            if isinstance(module, swan.ModuleBody):
                where = self._bodies
            elif isinstance(module, swan.ModuleInterface):
                where = self._interfaces
            elif isinstance(module, swan.TestModule):
                where = self._test_modules
        else:
            module_name = Model._get_swan_name(module)
            if cast(SwanFile, module).is_module:
                where = self._bodies
            elif cast(SwanFile, module).is_interface:
                where = self._interfaces
            elif cast(SwanFile, module).is_test:
                where = self._test_modules
        if where:
            return module_name in where.keys()
        return False

    @staticmethod
    def _get_swan_name(swan_elt: Union[SwanFile, swan.Module]) -> str:
        """Returns the name of a Swan element.

        Parameters
        ----------
        swan_elt : Union[swan.SwanFile, swan.TestModule]
            Swan element

        Returns
        -------
        str
            Name of the Swan element.
        """
        if isinstance(swan_elt, SwanFile):
            return swan.Module.module_name_from_path(swan_elt.path)
        return swan_elt.name.as_string.replace("-", "::")

    def load_project(self, project_instance: "project.IProject") -> "Model":
        """Add model information from a given project. It
        prepares internal data to store module bodies and interfaces.

        Parameters
        ----------
        project_instance : IProject
            Project instance to load.

        Returns
        -------
        Model
            Itself, for chaining.
        """

        if project_instance.storage and project_instance.storage.exists():
            for swan_file in project_instance.swan_sources(all=True):
                module_name = swan.Module.module_name_from_path(swan_file.path)
                if swan_file.is_module:
                    self._bodies[module_name] = swan_file
                elif swan_file.is_interface:
                    self._interfaces[module_name] = swan_file
                elif swan_file.is_test:
                    self._test_modules[module_name] = swan_file
        return self

    def configure(self, project_instance: "project.IProject") -> "Model":
        """Configure the model with a project instance.

        .. deprecated:: 0.7, use :py:meth:`load_project` instead."""
        self.load_project(project_instance)
        return self

    @property
    def parser(self) -> SwanParser:
        """Swan parser."""
        return self._parser

    def _load_source(
        self,
        swan_f: Union[SwanFile, swan.ModuleBody, swan.ModuleInterface, swan.TestModule],
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
            ast = self.parser.test_module(swan_f)
            ast.source = str(swan_f.path)
        else:
            raise ScadeOneException(f"Model.load_source: unexpected file kind {swan_f.path}.")
        ast.owner = self
        return ast

    @property
    def is_all_modules_loaded(self) -> bool:
        """Returns True when all Swan modules have been loaded."""
        for module in self.all_modules:
            if not (
                isinstance(module, swan.ModuleBody)
                or isinstance(module, swan.ModuleInterface)
                or isinstance(module, swan.TestModule)
            ):
                return False
        return True

    @property
    def modules(self) -> List[swan.Module]:
        """Returns all *loaded* Module objects (module body, module interface interface, test module) as a list."""
        modules_list = [mod for mod in self.all_modules if isinstance(mod, swan.Module)]
        return modules_list

    @property
    def all_modules(self) -> List[Union[swan.Module, SwanFile]]:
        """Returns *all* modules (loaded Module objects, or not-yet-loaded module files) as a list."""
        modules = (
            list(self._bodies.values())
            + list(self._interfaces.values())
            + list(self._test_modules.values())
        )
        return modules

    def get_module_body(self, name: str) -> Union[swan.ModuleBody, None]:
        """Returns module body of name 'name'"""
        if name not in self._bodies:
            return None
        if isinstance(self._bodies.get(name), SwanFile):
            self._bodies[name] = self._load_source(self._bodies[name])
        return self._bodies[name]

    def get_module_interface(self, name: str) -> Union[swan.ModuleInterface, None]:
        """Returns module interface of name 'name'"""
        if name not in self._interfaces:
            return None
        if isinstance(self._interfaces.get(name), SwanFile):
            self._interfaces[name] = self._load_source(self._interfaces[name])
        return self._interfaces[name]

    def get_module_from_pathid(self, pathid: str, module: swan.Module) -> Union[swan.Module, None]:
        """Return the :py:class:`Module` instance for a given *pathid*
        A *pathId* is of the form *[ID ::]+ ID*, where the last ID is the object
        name, and the previous IDs with "::" form the the module full name.

        If module's name is reduced to a single ID, search for the module from the
        **use** directive in *module*.

        If the *pathid* is reduced to a single ID, return *module*.

        Parameters
        ----------
        pathid : str
            object full path

        module : Module
            Context module where the search occurs.

        Returns
        -------
        Union[Module, None]
            Module of the object, or None if not module found
        """
        ids = pathid.split("::")

        if len(ids) == 1:
            return module

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
        m = self.get_module_body(module_path)
        if m is None:
            m = self.get_module_interface(module_path)
        return m

    @staticmethod
    def get_path_in_module(
        declaration: swan.Declaration, module: swan.Module
    ) -> swan.PathIdentifier:
        """Get the path of declaration in module. If the declaration is in module, return the identifier,
        else return the path of the declaration in the module based on the use directives.

        Parameters
        ----------
        item: SwanItem
            Declaration to get the path for.
        module: Module
            Module where the declaration is used.

        Returns
        -------
        PathIdentifier
            Path of the item in the module.

        Raises
        ------
        ScadeOneException
            - If the declaration does not have a module.
            - If the module does not exist.
            - If the module does not have a use directive for the declaration module.
        """

        if declaration.module is None:
            raise ScadeOneException(f"{declaration.get_full_path()} does not have a module.")
        if module is None:
            raise ScadeOneException("Module does not exist.")

        if cast(swan.Module, declaration.module).name == module.name:
            # The operator is in the same module as the instance
            return swan.PathIdentifier([declaration.id])

        # `declaration`` is in another module

        # Get the use directive of the operator module including body and/or interface
        module_uses = module.use_directives
        if module.model:
            # if model is defined (required by called functions), get the peer module from the model
            peer_module = (
                module.interface() if isinstance(module, swan.ModuleBody) else module.body()
            )
        else:
            peer_module = None
        peer_uses = cast(swan.Module, peer_module).use_directives if peer_module else []

        # Find use directive for the declaration module in all uses
        decl_module_path = cast(swan.Module, declaration.module).name.as_string

        uses = [
            use
            for use_list in [module_uses, peer_uses]
            for use in use_list
            if use.path.as_string == decl_module_path
        ]
        if not uses:
            raise ScadeOneException(
                f"Missing use directive in module {module.name.as_string} for item {declaration.get_full_path()}."
            )
        # Get the module part of the use directive
        # If the use directive has an alias, use it. Otherwise, use the last part of the path.
        mod_part = (
            uses[0].alias.value
            if uses[0].alias
            else swan.PathIdentifier.split(uses[0].path.as_string)[-1]
        )
        return swan.PathIdentifier.from_string(f"{mod_part}::{declaration.id}")

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
    def operator_definitions(self) -> List[swan.OperatorDefinition]:
        """Returns a list of operator definitions."""
        return [
            cast(swan.OperatorDefinition, operator)
            for operator in self.filter_declarations(
                lambda x: isinstance(x, swan.OperatorDefinition)
            )
        ]

    @property
    def operator_declarations(self) -> List[swan.OperatorDeclaration]:
        """Returns a list of operator declarations."""
        return [
            cast(swan.OperatorDeclaration, op_decl)
            for op_decl in self.filter_declarations(
                lambda x: isinstance(x, swan.OperatorDeclaration)
                and not isinstance(x, swan.OperatorDefinition)
            )
        ]

    def _load_module(self, name: str, mod_dict: dict) -> None:
        swan_file = mod_dict.get(name)
        if swan_file and isinstance(swan_file, SwanFile):
            mod_dict[name] = self._load_source(swan_file)

    def load_module_body(self, name: str) -> None:
        self._load_module(name, self._bodies)

    def load_module_interface(self, name: str) -> None:
        self._load_module(name, self._interfaces)

    def load_test_module(self, name: str) -> None:
        self._load_module(name, self._test_modules)

    def load_all_modules(
        self, bodies: bool = True, interfaces: bool = True, test_modules: bool = True
    ) -> None:
        """Loads systematically all modules.

        Parameters
        ----------
        bodies : bool, optional
            Includes module bodies
        interfaces : bool, optional
            Includes module interfaces
        test_modules : bool, optional
            Includes test modules
        """
        for cond, data, load_fn in [
            (bodies, self._bodies, self.load_module_body),
            (interfaces, self._interfaces, self.load_module_interface),
            (test_modules, self._test_modules, self.load_test_module),
        ]:
            if cond:
                for name in data.keys():
                    load_fn(name)

    @property
    def declarations(self) -> List[swan.GlobalDeclaration]:
        """Declarations found in all modules as a list.

        The Swan code of a module is loaded if not yet loaded.
        """

        declarations = []
        for data, load_fn in [
            (self._interfaces, self.load_module_interface),
            (self._bodies, self.load_module_body),
            (self._test_modules, self.load_test_module),
        ]:
            for swan_code, swan_object in data.items():
                if isinstance(swan_object, SwanFile):
                    swan_object = self._load_source(swan_object)
                    data[swan_code] = swan_object
                elif swan_object is None:
                    swan_object = load_fn(swan_code)
                    data[swan_code] = swan_object
                for decl in swan_object.declarations:  # type: ignore
                    declarations.append(cast(swan.GlobalDeclaration, decl))
        return declarations

    def filter_declarations(
        self, filter_fn: Callable[[swan.GlobalDeclaration], bool]
    ) -> List[swan.GlobalDeclaration]:
        """Returns declarations matched by a filter.

        Parameters
        ----------
        filter_fn : Callable[[GlobalDeclaration], bool]
            A function of one argument of type GlobalDeclaration, returning True or False.

        Returns
        -------
        List[GlobalDeclaration]
            List of matching declarations.
        """
        return list(filter(filter_fn, self.declarations))

    def find_declaration(
        self, predicate_fn: Callable[[swan.GlobalDeclaration], bool]
    ) -> Union[swan.GlobalDeclaration, None]:
        """Finds a declaration for which predicate_fn returns True.

        Parameters
        ----------
        predicate_fn : Callable[[GlobalDeclaration], bool]
            Function taking one GlobalDeclaration as argument and
            returning True when some property holds, else False.

        Returns
        -------
        Union[GlobalDeclaration, None]
            Found declaration or None.
        """
        for decl in self.filter_declarations(predicate_fn):
            return decl
        return None

    def add_test_module(self, swan_elt: Union[SwanFile, swan.TestModule]) -> None:
        """
        Add a test module to the model.

        Parameters
        ----------
        swan_elt : Union[swan.SwanFile, swan.TestModule]
            Content of the test module
        """
        self._add_module(swan_elt, self._test_modules)

    def get_test_module(self, name: str) -> Union[swan.TestModule, None]:
        """Returns test module of name 'name'"""
        if name not in self._test_modules:
            return None
        if isinstance(self._test_modules.get(name), SwanFile):
            self._test_modules[name] = self._load_source(self._test_modules[name])
        return self._test_modules[name]
