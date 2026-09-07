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

"""Mapping module for Swan Code Generator mapping data.

This module implements classes for mapping between Swan model items and C code items.
Mappings associate model items with their corresponding code implementations, with optional
role specifications for one-to-many relationships.
"""

from __future__ import annotations
import functools
from typing import Optional, Dict, TYPE_CHECKING, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .model import ModelElement
    from .code import CodeElement, CodeContainer


def require_cgmapping(func):
    """Decorator ensuring `self.cgmapping` is set on instance methods
    used by code and model."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "cgmapping", None) is None:
            raise ValueError("No cgmapping set on this instance. Set it during object creation.")
        return func(self, *args, **kwargs)

    return wrapper


class MappingDataBase(ABC):
    """Abstract base class for CGMapping interface
    to prevent circular imports between model, code, and mapping modules."""

    @abstractmethod
    def _get_code_for_model(
        self, model_id: int, role: MappingRole | str | None = None
    ) -> list[CodeElement]:
        """Get code elements mapped to a model item.

        Parameters
        ----------
        model_id : int
            The model item ID.
        role : MappingRole | str | None
            Optional role to filter by.

        Returns
        -------
        list[CodeElement]
            List of code elements.
        """
        pass

    @abstractmethod
    def get_all_code_containers(self) -> list[CodeContainer]:
        """Get all code containers.

        Returns
        -------
        list[CodeContainer]
            List of all code containers.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def _get_code_by_id(self, code_id: int) -> CodeElement | None:
        """Get a code item by its unique ID."""
        pass

    @abstractmethod
    def _get_model_by_id(self, model_id: int) -> ModelElement | None:
        """Get a model item by its unique ID."""
        pass

    @abstractmethod
    def get_all_operators(self) -> list[Any]:
        """Get all operators (regular and monomorphized)."""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def _get_model_for_code(self, code_id: int) -> list[ModelElement]:
        """Get model items mapped to a code item.

        Parameters
        ----------
        code_id : int
            The code item ID.

        Returns
        -------
        list[ModelElement]
            List of model items.
        """
        pass

    @abstractmethod
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
        pass


class MappingRole(Enum):
    """Role types for model-to-code mappings.

    When a model item maps to multiple code items, the role indicates
    the relationship between them.
    """

    #: Cycle method
    CYCLE_METHOD = "CycleMethod"
    #: Reset method
    RESET_METHOD = "ResetMethod"
    #: Initialization method
    INIT_METHOD = "InitMethod"
    #: Context data structure
    CONTEXT_TYPE = "ContextType"
    #: Input structure type
    INPUT_STRUCT_TYPE = "InputStructType"
    #: Output structure type
    OUTPUT_STRUCT_TYPE = "OutputStructType"
    #: Observation structure type
    OBS_STRUCT_TYPE = "ObsStructType"
    #: Observation structure field
    OBS_STRUCT_FIELD = "ObsStructField"
    #: Global context variable
    GLOBAL_CONTEXT = "GlobalContext"
    #: Global observation structure
    GLOBAL_OBS_STRUCT = "GlobalObsStruct"
    #: Computed flag variable
    COMPUTED_FLAG = "ComputedFlag"
    #: Elaboration function
    ELABORATED_FUNCTION = "ElaborationFunction"


@dataclass
class Mapping:
    """Mapping between a Swan model item and a C code item.

    Parameters
    ----------
    model_id : int
        Reference ID to the model item.
    code_id : int
        Reference ID to the code item.
    role : Optional[MappingRole]
        Optional role indicating the relationship type.
    doc : Optional[str]
        Optional documentation string.
    """

    model_id: int
    code_id: int
    role: Optional[MappingRole] = None
    doc: Optional[str] = None


class _MappingRegistry:
    """Registry to manage mappings between model and code items.

    This class stores mappings and provides efficient lookup methods for
    querying relationships between model and code items. It supports
    one-to-many relationships where a single model item can map to
    multiple code items with different roles.

    Attributes
    ----------
    mappings : list[Mapping]
        List of all mappings.
    _by_model_id : Dict[int, list[Mapping]]
        Index of mappings by model_id for fast lookup.
    _by_code_id : Dict[int, list[Mapping]]
        Index of mappings by code_id for reverse lookup.
    """

    def __init__(self):
        """Initialize an empty mapping registry."""
        self.mappings: list[Mapping] = []
        self._by_model_id: Dict[int, list[Mapping]] = {}
        self._by_code_id: Dict[int, list[Mapping]] = {}

    def add(self, mapping: Mapping) -> None:
        """Add a mapping to the registry.

        Parameters
        ----------
        mapping : Mapping
            The mapping to add.
        """
        self.mappings.append(mapping)

        # Index by model_id
        if mapping.model_id not in self._by_model_id:
            self._by_model_id[mapping.model_id] = []
        self._by_model_id[mapping.model_id].append(mapping)

        # Index by code_id
        if mapping.code_id not in self._by_code_id:
            self._by_code_id[mapping.code_id] = []
        self._by_code_id[mapping.code_id].append(mapping)

    def get_by_model_id(self, model_id: int, role: Optional[MappingRole] = None) -> list[Mapping]:
        """Get all mappings for a model item, optionally filtered by role.

        Parameters
        ----------
        model_id : int
            The model item ID to search for.
        role : Optional[MappingRole]
            Optional role to filter by.

        Returns
        -------
        list[Mapping]
            List of mappings for the specified model item.
        """
        mappings = self._by_model_id.get(model_id, [])

        if role is not None:
            mappings = [m for m in mappings if m.role == role]

        return mappings

    def get_by_code_id(self, code_id: int) -> list[Mapping]:
        """Get all mappings for a code item (reverse lookup).

        Parameters
        ----------
        code_id : int
            The code item ID to search for.

        Returns
        -------
        list[Mapping]
            List of mappings for the specified code item.
        """
        return self._by_code_id.get(code_id, [])

    def get_code_ids_for_model(
        self, model_id: int, role: Optional[MappingRole] = None
    ) -> list[int]:
        """Get all code item IDs associated with a model item.

        Parameters
        ----------
        model_id : int
            The model item ID to search for.
        role : Optional[MappingRole]
            Optional role to filter by.

        Returns
        -------
        list[int]
            List of code item IDs.
        """
        mappings = self.get_by_model_id(model_id, role)
        return [m.code_id for m in mappings]

    def get_code_id_for_model_no_role(self, model_id: int) -> int | None:
        """Get the code item ID associated with a model item via a role-less mapping.

        Parameters
        ----------
        model_id : int
            The model item ID to search for.

        Returns
        -------
        int | None
            The code item ID if a role-less mapping exists, None otherwise.
        """
        mappings = self._by_model_id.get(model_id, [])
        for m in mappings:
            if m.role is None:
                return m.code_id
        return None

    def get_model_ids_for_code(self, code_id: int) -> list[int]:
        """Get all model item IDs associated with a code item.

        Parameters
        ----------
        code_id : int
            The code item ID to search for.

        Returns
        -------
        list[int]
            List of model item IDs.
        """
        mappings = self.get_by_code_id(code_id)
        return [m.model_id for m in mappings]

    def get_roles_for_model(self, model_id: int) -> list[MappingRole]:
        """Get all roles used in mappings for a model item.

        Parameters
        ----------
        model_id : int
            The model item ID.

        Returns
        -------
        list[MappingRole]
            List of unique roles (excluding None).
        """
        mappings = self.get_by_model_id(model_id)
        roles = [m.role for m in mappings if m.role is not None]
        return list(set(roles))

    def clear(self) -> None:
        """Clear all mappings from the registry."""
        self.mappings.clear()
        self._by_model_id.clear()
        self._by_code_id.clear()

    def __len__(self) -> int:
        """Return the number of mappings in the registry."""
        return len(self.mappings)

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f"MappingRegistry({len(self.mappings)} mappings)"


def parse_mapping(data: dict) -> Mapping:
    """Parse a Mapping from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the mapping.

    Returns
    -------
    Mapping
        Parsed mapping object.
    """
    role = None
    if "role" in data:
        role = MappingRole(data["role"])

    return Mapping(
        model_id=data["model_id"],
        code_id=data["code_id"],
        role=role,
        doc=data.get("$doc"),
    )


def load_mapping_from_json(
    mapping_data: list[dict], registry: Optional[_MappingRegistry] = None
) -> _MappingRegistry:
    """Load mappings from JSON data into a registry.

    Parameters
    ----------
    mapping_data : list[dict]
        List of mapping dictionaries from JSON.
    registry : Optional[MappingRegistry]
        Existing registry to use, or None to create a new one.

    Returns
    -------
    MappingRegistry
        Registry containing all parsed mappings.
    """
    if registry is None:
        registry = _MappingRegistry()

    for mapping_dict in mapping_data:
        mapping = parse_mapping(mapping_dict)
        registry.add(mapping)

    return registry
