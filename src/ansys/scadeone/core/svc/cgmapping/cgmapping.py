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

"""High-level user-facing interface for Swan Code Generator mapping data.

This module provides the main CGMapping class that encapsulates all functionality
for querying CG mapping data. It hides internal implementation details
and provides intuitive methods for accessing model and code items and their relationships.
"""

from __future__ import annotations
from typing import Any, cast
from pathlib import Path

from .code import CodeElement, CodeContainer

from .loader import CGMappingData, load_cg_mapping
from .model import (
    ModelElement,
    ModelGroup,
    ModelProbesGroup,
    ModelVariable,
    ModelOperator,
    ModelMonoOperator,
    ModelConstant,
    ModelSensor,
    ModelNamedType,
    ModelPredefinedType,
    ModelArray,
    ModelStruct,
    ModelEnum,
    ModelVariant,
)
from .mapping import MappingRole, MappingDataBase


class CGMapping(MappingDataBase):
    """High-level interface for querying code generator mapping data.

    This class provides a user-friendly API to access Swan model items,
    C code items, and their mappings. It encapsulates the internal registries
    and provides convenient methods for common queries.

    Attributes
    ----------
    version : str
        File format version from the loaded data.
    """

    def __init__(self, data: CGMappingData):
        """Initialize CGMapping from loaded data.

        Parameters
        ----------
        data : CGMappingData
            The loaded mapping data containing all registries.
        """
        self._data = data
        self.version = data.version
        self._model_registry = data.model_registry
        self._code_registry = data.code_registry
        self._mapping_registry = data.mapping_registry

    @classmethod
    def from_file(cls, file_path: str | Path) -> CGMapping:
        """Load mapping data from a JSON file.

        Parameters
        ----------
        file_path : str | Path
            Path to the JSON file to load.

        Returns
        -------
        CGMapping
            A new CGMapping instance with loaded data.

        Raises
        ------
        ScadeOneException
            If the file cannot be read or parsed or if the specified file does not exist.
        """
        data = load_cg_mapping(file_path)
        mapping = cls(data)
        # Set cgmapping on all model elements
        for model_item in mapping._model_registry.items.values():
            mapping._set_cgmapping_recursive(model_item)
        # Set cgmapping on all code elements
        for code_item in mapping._code_registry.items.values():
            code_item.cgmapping = mapping
        return mapping

    def _set_cgmapping_recursive(self, obj: "ModelElement") -> None:
        """Set cgmapping on an object and its nested ModelElement objects."""
        from .model import ModelElement

        if isinstance(obj, ModelElement):
            obj.cgmapping = self

        # Set cgmapping on nested elements - use separate ifs, not elif
        if hasattr(obj, "fields"):
            for field_item in obj.fields:
                self._set_cgmapping_recursive(field_item)

        if hasattr(obj, "values"):
            for value in obj.values:
                self._set_cgmapping_recursive(value)

        if hasattr(obj, "constructors"):
            for constructor in obj.constructors:
                self._set_cgmapping_recursive(constructor)

        if hasattr(obj, "inputs"):
            for item in obj.inputs:
                if isinstance(item, ModelGroup):
                    self._set_cgmapping_recursive(item)
                    for projection in item.projections:
                        self._set_cgmapping_recursive(projection)
                elif isinstance(item, ModelVariable):
                    self._set_cgmapping_recursive(item)

        if hasattr(obj, "outputs"):
            for item in obj.outputs:
                if isinstance(item, ModelGroup):
                    self._set_cgmapping_recursive(item)
                    for projection in item.projections:
                        self._set_cgmapping_recursive(projection)
                elif isinstance(item, ModelVariable):
                    self._set_cgmapping_recursive(item)

        if hasattr(obj, "probes"):
            for probe in obj.probes:
                self._set_cgmapping_recursive(probe)
                if isinstance(probe, ModelProbesGroup):
                    for projection in probe.projections:
                        self._set_cgmapping_recursive(projection)

        if hasattr(obj, "instances"):
            for instance_tuple in obj.instances:
                if isinstance(instance_tuple, tuple) and len(instance_tuple) == 2:
                    instance_obj = instance_tuple[1]
                    self._set_cgmapping_recursive(instance_obj)

        if hasattr(obj, "type_parameters"):
            for type_param in obj.type_parameters:
                self._set_cgmapping_recursive(type_param)

        if hasattr(obj, "size_parameters"):
            for size_param in obj.size_parameters:
                self._set_cgmapping_recursive(size_param)

    # -------------------------------------------------------------------------
    # Model item queries
    # -------------------------------------------------------------------------

    def _get_model_by_id(self, model_id: int) -> ModelElement | None:
        """Get a model item by its unique ID.

        Parameters
        ----------
        model_id : int
            The unique identifier of the model item.

        Returns
        -------
        ModelElement | None
            The model item if found, None otherwise.
        """
        model_item = self._model_registry.get(model_id)

        # Ensure the model item has cgmapping set
        if (
            model_item is not None
            and hasattr(model_item, "cgmapping")
            and model_item.cgmapping is None
        ):
            model_item.cgmapping = self

        return model_item

    def get_model_by_path(self, path: str) -> list[ModelElement]:
        """Get model items by their path.

        Parameters
        ----------
        path : str
            The path to search for (e.g., "MyPackage::MyOperator").

        Returns
        -------
        list[ModelElement]
            List of model items with the specified path.
        """
        result = []
        for item in self._model_registry.items.values():
            if hasattr(item, "path") and item.path == path:
                result.append(item)
        return result

    def get_model_by_name(self, name: str) -> list[ModelElement]:
        """Get model items by their name.

        For items with a 'path' attribute, this searches for the last
        component of the path (after the last '::').

        Parameters
        ----------
        name : str
            The name to search for.

        Returns
        -------
        list[ModelElement]
            List of model items matching the name.
        """
        result = []
        for item in self._model_registry.items.values():
            # Check if item has a 'name' attribute
            if hasattr(item, "name") and item.name == name:
                result.append(item)
            # For items with 'path', check the last component
            elif hasattr(item, "path"):
                path_parts = item.path.split("::")
                if path_parts[-1] == name:
                    result.append(item)
        return result

    def get_all_operators(self) -> list[ModelOperator | ModelMonoOperator]:
        """Get all operators (both regular and monomorphized).

        Returns
        -------
        list[ModelOperator | ModelMonoOperator]
            List of all operator items.
        """
        regular_ops = cast(list[ModelOperator], self._model_registry.get_by_type(ModelOperator))
        mono_ops = cast(
            list[ModelMonoOperator], self._model_registry.get_by_type(ModelMonoOperator)
        )
        all_ops: list[ModelOperator | ModelMonoOperator] = regular_ops + mono_ops

        # Ensure all operators have cgmapping set
        for op in all_ops:
            if op.cgmapping is None:
                op.cgmapping = self

        return all_ops

    def get_root_operators(self) -> list[ModelOperator]:
        """Get all root operators.

        Returns
        -------
        list[ModelOperator]
            List of operators marked as root.
        """
        all_operators = cast(list[ModelOperator], self._model_registry.get_by_type(ModelOperator))
        root_ops = [op for op in all_operators if op.root is True]

        # Ensure all root operators have cgmapping set
        for op in root_ops:
            if op.cgmapping is None:
                op.cgmapping = self

        return root_ops

    def get_all_constants(self) -> list[ModelConstant]:
        """Get all model constants.

        Returns
        -------
        list[ModelConstant]
            List of all constant items.
        """
        constants = cast(list[ModelConstant], self._model_registry.get_by_type(ModelConstant))

        # Ensure all constants have cgmapping set
        for const in constants:
            if const.cgmapping is None:
                const.cgmapping = self

        return constants

    def get_all_sensors(self) -> list[ModelSensor]:
        """Get all model sensors.

        Returns
        -------
        list[ModelSensor]
            List of all sensor items.
        """
        sensors = cast(list[ModelSensor], self._model_registry.get_by_type(ModelSensor))

        # Ensure all sensors have cgmapping set
        for sensor in sensors:
            if sensor.cgmapping is None:
                sensor.cgmapping = self

        return sensors

    def get_all_types(self) -> list[ModelElement]:
        """Get all type declarations (predefined, named, array, struct, enum, variant).

        Returns
        -------
        list[ModelElement]
            List of all type declaration items.
        """
        result = []
        result.extend(self._model_registry.get_by_type(ModelPredefinedType))
        result.extend(self._model_registry.get_by_type(ModelNamedType))
        result.extend(self._model_registry.get_by_type(ModelArray))
        result.extend(self._model_registry.get_by_type(ModelStruct))
        result.extend(self._model_registry.get_by_type(ModelEnum))
        result.extend(self._model_registry.get_by_type(ModelVariant))

        # Ensure all types have cgmapping set
        for type_item in result:
            if hasattr(type_item, "cgmapping") and type_item.cgmapping is None:
                type_item.cgmapping = self

        return result

    # -------------------------------------------------------------------------
    # Code item queries
    # -------------------------------------------------------------------------

    def _get_code_by_id(self, code_id: int) -> CodeElement | None:
        """Get a code item by its unique ID.

        Parameters
        ----------
        code_id : int
            The unique identifier of the code item.

        Returns
        -------
        CodeElement | None
            The code item if found, None otherwise.
        """
        code_item = self._code_registry.get(code_id)

        # Ensure the code item has cgmapping set
        if isinstance(code_item, CodeElement) and code_item.cgmapping is None:
            code_item.cgmapping = self

        return code_item

    def get_code_by_name(self, name: str) -> list[CodeElement]:
        """Get code items by their name.

        Parameters
        ----------
        name : str
            The name to search for.

        Returns
        -------
        list[CodeElement]
            List of code items with the specified name.
        """
        code_items = self._code_registry.get_by_name(name)

        # Ensure all code items have cgmapping set
        for code_item in code_items:
            if isinstance(code_item, CodeElement) and code_item.cgmapping is None:
                code_item.cgmapping = self

        return code_items

    def get_all_code_containers(self) -> list[CodeContainer]:
        """Get all code containers (files with declarations).

        Returns
        -------
        list[CodeContainer]
            List of all code containers.
        """
        containers = self._code_registry.get_containers()

        # Ensure all code containers have cgmapping set if they are CodeElements
        for container in containers:
            if isinstance(container, CodeElement) and container.cgmapping is None:
                container.cgmapping = self

            # Also assign cgmapping to nested code elements in declarations
            if hasattr(container, "declarations"):
                for declaration in container.declarations:
                    # declaration is a tuple (tag, code_element)
                    if len(declaration) >= 2:
                        tag, code_element = declaration[:2]
                        if isinstance(code_element, CodeElement) and code_element.cgmapping is None:
                            code_element.cgmapping = self

        return containers

    # -------------------------------------------------------------------------
    # Mapping queries
    # -------------------------------------------------------------------------

    def _get_code_for_model(
        self, model_id: int, role: MappingRole | str | None = None
    ) -> list[CodeElement]:
        """Get code items mapped to a model item.

        Parameters
        ----------
        model_id : int
            The model item ID.
        role : MappingRole | str | None
            Optional role to filter by. Can be a MappingRole enum value
            or a string like "CycleMethod".

        Returns
        -------
        list[CodeElement]
            List of code items mapped to the model item.
        """
        # Convert string to MappingRole if needed
        if isinstance(role, str):
            try:
                role = MappingRole(role)
            except ValueError:
                return []

        # Get code IDs from mappings
        code_ids = self._mapping_registry.get_code_ids_for_model(model_id, role)

        # Resolve IDs to actual code items
        result = []
        for code_id in code_ids:
            code_item = self._code_registry.get(code_id)
            if code_item is not None:
                # Ensure the code item has cgmapping set
                if isinstance(code_item, CodeElement) and code_item.cgmapping is None:
                    code_item.cgmapping = self
                result.append(code_item)

        return result

    def _get_main_code_for_model(self, model_id: int) -> CodeElement | None:
        """Get the single code element mapped to a model item via a role-less mapping,
        if it exists.

        Parameters
        ----------
        model_id : int
            The model item ID.

        Returns
        -------
        CodeElement | None
            The code element if a role-less mapping exists, None otherwise.
        """
        code_id = self._mapping_registry.get_code_id_for_model_no_role(model_id)
        if code_id is None:
            return None
        code_item = self._code_registry.get(code_id)
        if (
            code_item is not None
            and isinstance(code_item, CodeElement)
            and code_item.cgmapping is None
        ):
            code_item.cgmapping = self
        return code_item

    def _get_model_for_code(self, code_id: int) -> list[ModelElement]:
        """Get model items mapped to a code item (reverse lookup).

        Parameters
        ----------
        code_id : int
            The code item ID.

        Returns
        -------
        list[ModelElement]
            List of model items mapped to the code item.
        """
        # Get model IDs from mappings
        model_ids = self._mapping_registry.get_model_ids_for_code(code_id)

        # Resolve IDs to actual model items
        result = []
        for model_id in model_ids:
            model_item = self._model_registry.get(model_id)
            if model_item is not None:
                # Ensure the model item has cgmapping set
                if hasattr(model_item, "cgmapping") and model_item.cgmapping is None:
                    model_item.cgmapping = self
                result.append(model_item)

        return result

    def _get_mapping_roles(self, model_id: int) -> list[MappingRole]:
        """Get all roles used in mappings for a model item.

        Parameters
        ----------
        model_id : int
            The model item ID.

        Returns
        -------
        list[MappingRole]
            List of roles used in mappings for this model item.
        """
        return self._mapping_registry.get_roles_for_model(model_id)

    def _has_code_mapping_role(self, code_id: int, role: MappingRole) -> bool:
        """Check if a code item has a mapping with a specific role.

        Parameters
        ----------
        code_id : int
            The code item ID.
        role : MappingRole
            The role to check for.

        Returns
        -------
        bool
            True if a mapping with the given role exists for this code item.
        """
        return any(m.role == role for m in self._mapping_registry.get_by_code_id(code_id))

    # -------------------------------------------------------------------------
    # Type resolution
    # -------------------------------------------------------------------------

    def _resolve_type(self, type_id: int) -> Any | None:
        """Resolve a type ID to its actual type object.

        This is a convenience method equivalent to get_model_by_id()
        but with a more descriptive name for type resolution.

        Parameters
        ----------
        type_id : int
            The type ID to resolve.

        Returns
        -------
        Any | None
            The type object if found, None otherwise.
        """
        return self._model_registry.get(type_id)

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------

    def get_statistics(self) -> dict:
        """Get statistics about the loaded mapping data.

        - version: File format version
        - model_items: Total number of model items
        - code_items: Total number of code items
        - code_containers: Total number of code containers
        - mappings: Total number of mappings
        - operators: Total number of operators
        - root_operators: Total number of root operators
        - constants: Total number of constants
        - sensors: Total number of sensors
        - types: Total number of types

        Returns
        -------
        dict
            Dictionary containing statistics like counts of various items.
        """
        return {
            "version": self.version,
            "model_items": len(self._model_registry.items),
            "code_items": len(self._code_registry.items),
            "code_containers": len(self._code_registry.containers),
            "mappings": len(self._mapping_registry.mappings),
            "operators": len(self.get_all_operators()),
            "root_operators": len(self.get_root_operators()),
            "constants": len(self.get_all_constants()),
            "sensors": len(self.get_all_sensors()),
            "types": len(self.get_all_types()),
        }

    def __repr__(self) -> str:
        """Return a string representation of the mapping."""
        stats = self.get_statistics()
        return (
            f"CGMapping(version={self.version!r}, "
            f"model_items={stats['model_items']}, "
            f"code_items={stats['code_items']}, "
            f"mappings={stats['mappings']})"
        )
