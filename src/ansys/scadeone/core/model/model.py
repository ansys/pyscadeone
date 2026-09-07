# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

from typing import List, Optional, Set, Union, Callable, cast

from ansys.scadeone.core.interfaces import IScadeOne, IModel, IProject
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanFile
import ansys.scadeone.core.swan as swan

from .parser import Parser


class _PreModule:
    """Class used to store a module before it is loaded. It contains the Swan file of the module, and the module name."""

    def __init__(self, swan_file: SwanFile, project: IProject | None):
        self.swan_file = swan_file
        self.name = swan.Module.module_name_from_path(swan_file.path)
        self.project = project


class Model(IModel):
    """Per-project model.

    A :py:class:`Model` describes the Swan content of a single :py:class:`Project`
    (modules in its own ``assets/*.swan|.swani|.swant``). Cross-project lookups
    (``use`` directives, ``Lib::M::id`` paths) are resolved by walking into the
    project's dependencies' models, with cycle protection.

    Loading of Swan sources is lazy: when a module body or interface is needed,
    it is loaded from the Swan source file.
    """

    def __init__(self, project: IProject) -> None:
        # dictionaries of Swan module, interface and test module
        # Key is the Swan name of the module, interface or test module
        self._bodies: dict[
            str, swan.ModuleBody | _PreModule
        ] = {}  # _bodies["N1::N2::M"] = ModuleBody | SwanFile
        self._interfaces: dict[str, swan.ModuleInterface | _PreModule] = {}
        self._test_modules: dict[str, swan.TestModule | _PreModule] = {}
        self._project = project

    @property
    def project(self) -> IProject:
        """Project this model belongs to."""
        return self._project

    @property
    def app(self) -> IScadeOne:
        """Scade One application instance."""
        return self._project.app

    @property
    def parser(self) -> Parser:
        """Swan parser (shared at app level)."""
        return self.app.parser

    def _add_module(self, module: swan.Module, where: dict) -> None:
        """Add Module to its
        proper dictionary *where* (bodies, interfaces, test modules). If Module is given, updates ownership."""
        where[Model._get_swan_name(module)] = module
        module.owner = self

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

    def add_test_module(self, swan_elt: Union[SwanFile, swan.TestModule]) -> None:
        """
        Add a test module to the model.

        Parameters
        ----------
        swan_elt : Union[swan.SwanFile, swan.TestModule]
            Content of the test module
        """
        self._add_module(swan_elt, self._test_modules)

    def module_exists(self, module: swan.Module | SwanFile) -> bool:
        """Check if a module exists by its path in the model.

        Parameters
        ----------
        module : swan.Module | SwanFile
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
            swan_file = cast(SwanFile, module)
            module_name = swan_file.name.replace("-", "::")
            if swan_file.is_module:
                where = self._bodies
            elif swan_file.is_interface:
                where = self._interfaces
            elif swan_file.is_test:
                where = self._test_modules
        if where:
            return module_name in where.keys()
        return False

    @staticmethod
    def _get_swan_name(swan_elt: Union[SwanFile, swan.Module]) -> str:
        """Returns the name of a Swan element.

        Parameters
        ----------
        swan_elt : Union[SwanFile, swan.Module]
            Swan element

        Returns
        -------
        str
            Name of the Swan element.
        """
        if isinstance(swan_elt, SwanFile):
            return swan.Module.module_name_from_path(swan_elt.path)
        return swan_elt.name.as_string.replace("-", "::")

    def load_project(self, project_instance: IProject) -> "Model":
        """Register the model's bound project Swan sources as lazy ``_PreModule``
        entries.

        Parameters
        ----------
        project_instance : IProject
            Must be the project this model is bound to.

        Returns
        -------
        Model
            Itself, for chaining.

        Raises
        ------
        ScadeOneException
            If ``project_instance`` is not the project bound to this model.
        """

        if project_instance is not self._project:
            raise ScadeOneException(
                "Model.load_project: a per-project model only loads its own project."
            )

        if project_instance.storage and project_instance.storage.exists():
            for swan_file in project_instance.swan_sources():
                module_name = swan.Module.module_name_from_path(swan_file.path)

                if swan_file.is_module:
                    dest = self._bodies
                elif swan_file.is_interface:
                    dest = self._interfaces
                elif swan_file.is_test:
                    dest = self._test_modules
                else:
                    raise ScadeOneException(f"Unexpected Swan file kind for file {swan_file.path}.")
                if module_name not in dest.keys():
                    # FIXME: Support only one module with a given name.
                    dest[module_name] = _PreModule(swan_file, project_instance)
        return self

    def _load_source(
        self,
        swan_item: Union[_PreModule, swan.ModuleBody, swan.ModuleInterface, swan.TestModule],
    ) -> swan.Module:
        """Read a Swan file (.swan or .swani or .swant).
        Can be called on a Module, in which case it does nothing.

        Parameters
        ----------
        swan_item : Union[_PreModule, swan.ModuleBody, swan.ModuleInterface, swan.TestModule]
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
            isinstance(swan_item, swan.ModuleBody)
            or isinstance(swan_item, swan.ModuleInterface)
            or isinstance(swan_item, swan.TestModule)
        ):
            return swan_item

        swan_f = swan_item.swan_file
        if swan_f.is_module:
            ast = self.parser.module_body(swan_f)
        elif swan_f.is_interface:
            ast = self.parser.module_interface(swan_f)
        elif swan_f.is_test:
            ast = self.parser.test_module(swan_f)
        else:
            raise ScadeOneException(f"Model.load_source: unexpected file kind {swan_f.path}.")
        ast.source = str(swan_f.path)
        ast.owner = self
        ast.project = swan_item.project
        return ast

    def _load_module(self, name: str, mod_dict: dict) -> None:
        item = mod_dict.get(name)
        if item and isinstance(item, _PreModule):
            mod_dict[name] = self._load_source(item)

    def load_all_modules(
        self,
        *,
        bodies: bool = True,
        interfaces: bool = True,
        test_modules: bool = True,
        dependencies: bool = True,
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
        dependencies : bool, optional
            Includes modules from dependencies
        """
        for cond, data in [
            (bodies, self._bodies),
            (interfaces, self._interfaces),
            (test_modules, self._test_modules),
        ]:
            if cond:
                for name in data.keys():
                    self._load_module(name, data)
        if dependencies:
            for dep in self._project.dependencies(all=True):  # type: ignore[attr-defined]
                dep.model.load_all_modules(
                    bodies=bodies,
                    interfaces=interfaces,
                    test_modules=test_modules,
                    dependencies=True,
                )

    @property
    def is_all_modules_loaded(self) -> bool:
        """Returns True when all Swan modules have been loaded."""
        for mod_dict in [self._bodies, self._interfaces, self._test_modules]:
            for item in mod_dict.values():
                if isinstance(item, _PreModule):
                    return False
        for dep in self._project.dependencies(all=True):  # type: ignore[attr-defined]
            if not cast("Model", dep.model).is_all_modules_loaded:
                return False
        return True

    @property
    def modules(self) -> List[swan.Module]:
        """Returns Module objects of the current Model (module body, module interface, test module) as a list."""
        # Load our modules only.
        self.load_all_modules()
        modules = (
            list(self._bodies.values())
            + list(self._interfaces.values())
            + list(self._test_modules.values())
        )

        return modules

    @property
    def all_modules(self) -> List[swan.Module]:
        """Returns *all* modules (loaded Module objects, or not-yet-loaded module files) as a list."""
        modules = set(self.modules)
        for dep in self._project.dependencies(all=True):  # type: ignore[attr-defined]
            dep_modules = cast("Model", dep.model).modules
            modules.update(dep_modules)
        return list(modules)

    def get_module_body(self, name: str) -> Union[swan.ModuleBody, None]:
        """Returns module body of name 'name', searching dependencies on miss."""
        return cast(
            Optional[swan.ModuleBody],
            self._lookup_module(name, "_bodies", set()),
        )

    def get_module_interface(self, name: str) -> Union[swan.ModuleInterface, None]:
        """Returns module interface of name 'name', searching dependencies on miss."""
        return cast(
            Optional[swan.ModuleInterface],
            self._lookup_module(name, "_interfaces", set()),
        )

    def get_test_module(self, name: str) -> Union[swan.TestModule, None]:
        """Returns test module of name 'name', searching dependencies on miss."""
        return cast(
            Optional[swan.TestModule],
            self._lookup_module(name, "_test_modules", set()),
        )

    def _lookup_module(
        self,
        name: str,
        dict_attr: str,
        visited: Set,
    ) -> Union[swan.Module, None]:
        """Look up a module by name in this model, then recurse into
        the project's direct dependencies. ``visited`` is keyed by project
        storage path to break dependency cycles.
        """
        own = getattr(self, dict_attr)
        if name in own:
            # call the loader to load the module if it is not loaded yet (i.e. if it is a _PreModule)
            self._load_module(name, own)  # side effect: module is loaded in own dict
            entry = own[name]
            if isinstance(entry, swan.Module):
                return entry
            return None
        proj_path = self._project.storage.path
        if proj_path in visited:
            return None
        visited.add(proj_path)
        for dep in self._project.dependencies(all=False):  # type: ignore[attr-defined]
            dep_model = cast("Model", dep.model)
            result = dep_model._lookup_module(name, dict_attr, visited)
            if result is not None:
                return result
        return None

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
        """Returns a list of type declarations.

        Note that this includes all types, including those from model project dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        types = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.TypeDeclarations)):
            for type in cast(swan.TypeDeclarations, decls).types:
                types.append(type)
        return types

    @property
    def sensors(self) -> List[swan.SensorDecl]:
        """Returns a list of sensor declarations.

        Note that this includes all sensors, including those from model project dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        sensors = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.SensorDeclarations)):
            for sensor in cast(swan.SensorDeclarations, decls).sensors:
                sensors.append(sensor)
        return sensors

    @property
    def constants(self) -> List[swan.ConstDecl]:
        """Returns a list of constant declarations.

        Note that this includes all constants, including those from model project dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        consts = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.ConstDeclarations)):
            for const in cast(swan.ConstDeclarations, decls).constants:
                consts.append(const)
        return consts

    @property
    def groups(self) -> List[swan.GroupDecl]:
        """Returns a list of group declarations.

        Note that this includes all groups, including those from model project dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        groups = []
        for decls in self.filter_declarations(lambda x: isinstance(x, swan.GroupDeclarations)):
            for group in cast(swan.GroupDeclarations, decls).groups:
                groups.append(group)
        return groups

    @property
    def operator_definitions(self) -> List[swan.OperatorDefinition]:
        """Returns a list of operator definitions.

        Note that this includes all operator definitions, including those from model project dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        return [
            cast(swan.OperatorDefinition, operator)
            for operator in self.filter_declarations(
                lambda x: isinstance(x, swan.OperatorDefinition)
            )
        ]

    @property
    def operator_declarations(self) -> List[swan.OperatorDeclaration]:
        """Returns a list of operator declarations.

        Note that this includes all operator declarations, including those from model project dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        return [
            cast(swan.OperatorDeclaration, op_decl)
            for op_decl in self.filter_declarations(
                lambda x: (
                    isinstance(x, swan.OperatorDeclaration)
                    and not isinstance(x, swan.OperatorDefinition)
                )
            )
        ]

    def get_declarations(self, all: bool = True) -> List[swan.GlobalDeclaration]:
        """Returns a list of declarations in the model, including those from model project dependencies if *all* is True

        Parameters
        ----------
        all : bool, optional
            If True, include declarations from dependencies, by default True.

        Returns
        -------
        List[swan.GlobalDeclaration]
            List of all declarations.
        """
        declarations = []
        for mod_dict, load_fn in [
            (self._interfaces, self.get_module_interface),
            (self._bodies, self.get_module_body),
            (self._test_modules, self.get_test_module),
        ]:
            for mod_name, module in mod_dict.items():
                if not isinstance(module, swan.Module):
                    module = load_fn(mod_name)
                for decl in module.declarations:  # type: ignore
                    declarations.append(cast(swan.GlobalDeclaration, decl))
        # Explore dependencies if requested.
        if all:
            # Explore dependencies if requested.
            # project.dependencies(all=True) returns all dependencies, including transitive ones.
            # as a unique list (no duplicates), so we don't need to worry about cycles here.
            # Then one need *local* declarations of each model.
            for dep in self._project.dependencies(all=True):  # type: ignore[attr-defined]
                dep_decls = cast("Model", dep.model).get_declarations(all=False)
                declarations.extend(dep_decls)
        return declarations

    @property
    def declarations(self) -> List[swan.GlobalDeclaration]:
        """Declarations in the model.

        Note that this includes all declarations, including those from dependencies.
        Consider using :py:meth:`Model.get_declarations` or :py:meth:`Model.filter_declarations` for more general queries.
        """
        return self.get_declarations(all=True)

    def filter_declarations(
        self, filter_fn: Callable[[swan.GlobalDeclaration], bool], all: bool = True
    ) -> List[swan.GlobalDeclaration]:
        """Returns declarations matched by a filter.

        Parameters
        ----------
        filter_fn : Callable[[GlobalDeclaration], bool]
            A function of one argument of type GlobalDeclaration, returning True or False.
        all : bool, optional
            If True, include declarations from dependencies, by default True, else only declarations
            from the modules of the model project are included.

        Returns
        -------
        List[GlobalDeclaration]
            List of matching declarations.
        """
        return list(filter(filter_fn, self.get_declarations(all=all)))

    def find_declaration(
        self, predicate_fn: Callable[[swan.GlobalDeclaration], bool], all: bool = True
    ) -> Union[swan.GlobalDeclaration, None]:
        """Finds a declaration for which predicate_fn returns True,  else only declarations
            from the modules of the model project are included.

        Parameters
        ----------
        predicate_fn : Callable[[GlobalDeclaration], bool]
            Function taking one GlobalDeclaration as argument and
            returning True when some property holds, else False.
        all : bool, optional
            If True, include declarations from dependencies, by default True.

        Returns
        -------
        Union[GlobalDeclaration, None]
            Found declaration or None.
        """
        for decl in self.filter_declarations(predicate_fn, all=all):
            return decl
        return None
