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

"""Model module for Swan Code Generator mapping data.

This module implements classes representing elements from the Swan language model.
Each model item has a unique integer ID and can reference other model items by their IDs.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING, cast
from dataclasses import KW_ONLY, dataclass, field
from enum import Enum

from ansys.scadeone.core.common.logger import LOGGER

if TYPE_CHECKING:
    from .mapping import MappingDataBase
    from .code import CodeElement, CStructField, CGlobal, CStruct, CFunction

from .mapping import MappingRole, require_cgmapping


class ProbeKind(Enum):
    """Kind of probe in the model."""

    INPUT = "Input"
    OUTPUT = "Output"
    LOCAL = "Local"
    WIRE = "Wire"


class LoopKind(Enum):
    """Kind of loop instance."""

    ITERATOR = "Iterator"
    FORWARD = "Forward"


GroupProjection = str | int
"""Type alias for group projection"""


@dataclass
class ModelElement:
    """Base class for all Swan model elements.

    This class provides common functionality for all model elements,
    including access to their generated code elements through the mapping system.

    All model elements that inherit from this class must have an 'id' attribute.
    """

    cgmapping: MappingDataBase | None = field(default=None, init=False)

    @require_cgmapping
    def get_generated_element(self) -> CodeElement | None:
        """Get the generated code element for this model element.

        Only the code element associated via a role-less mapping is returned,
        which guarantees at most one result. Code elements associated through
        a named role (e.g. CycleMethod, ResetMethod) are not returned here;
        use the dedicated methods (``get_cycle``, ``get_reset``, etc.) instead.

        Returns
        -------
        CodeElement | None
            The code element mapped to this model element without a role,
            or None if no such mapping exists.

        Raises
        ------
        AttributeError
            If this instance has no 'id' attribute.
        ValueError
            If no cgmapping is set on this instance.
        """

        if not hasattr(self, "id"):
            raise AttributeError(f"{type(self).__name__} must have an 'id' attribute.")

        generated_code = self.cgmapping._get_main_code_for_model(self.id)  # type: ignore[missing-attribute]
        if generated_code is None:
            roles = self.cgmapping._get_mapping_roles(self.id)  # type: ignore[missing-attribute]
            if len(roles) > 0:
                LOGGER.warning(
                    f"Model element with id {self.id} has specific role-based associations: consider using appropriate methods to access them."
                )
            else:
                LOGGER.warning(f"No code mapping found for model element with id {self.id}.")
        return generated_code

    @require_cgmapping
    def get_c_type(self) -> CodeElement | None:
        """Get the generated C type element associated with this model element.

        This method first retrieves the generated code elements for this model element,
        then looks for a code element that has a 'type' attribute and retrieves
        the corresponding C type element.

        Returns
        -------
        CodeElement | None
            The C type element if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """
        # Get the role-less generated code element for this model element
        code_element = self.get_generated_element()

        if (
            code_element is not None
            and hasattr(code_element, "type")
            and code_element.type is not None
        ):
            return self.cgmapping._get_code_by_id(code_element.type)  # type: ignore[missing-attribute]

        return None

    @require_cgmapping
    def get_model_type(self) -> ModelElement | None:
        """Get the model element corresponding to the type of this model element.

        This method first checks if this model element has a 'type' attribute.
        If it does, it retrieves the model element with that ID.
        Otherwise, it gets the generated code element, retrieves its type,
        and returns the model element associated with that type ID.

        Returns
        -------
        ModelElement | None
            The model element representing the type, None if not found.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        # First, check if this model element has a direct 'type' attribute
        if hasattr(self, "type") and getattr(self, "type") is not None:
            model_type = cast(int, getattr(self, "type"))
            return self.cgmapping._get_model_by_id(model_type)  # type: ignore[missing-attribute]

        # Otherwise, get the type from the role-less generated code element
        code_element = self.get_generated_element()
        if code_element is None:
            return None

        if hasattr(code_element, "type") and code_element.type is not None:
            # Get the model elements mapped to this type ID
            model_elements = self.cgmapping._get_model_for_code(code_element.type)  # type: ignore[missing-attribute]
            if model_elements:
                return model_elements[0]

        return None


@dataclass
class ModelGroupProjection(ModelElement):
    """Projection of a group.

    Parameters
    ----------
    id : int
        Unique identifier for the projected model variable.
    projection : list[GroupProjection] | None
        Group projection path for the variable.
    """

    id: int
    projection: list[GroupProjection] | None = None


@dataclass
class ModelGroupVariableProjection(ModelGroupProjection):
    """Projection of a grouped model variable.

    Parameters
    ----------
    id : int
        Unique identifier for the projected model variable.
    projection : list[GroupProjection] | None
        Group projection path for the variable.
    """

    _associated_probe: ModelGroupProbeProjection | None = None

    def _set_associated_probe(self, probe: ModelGroupProbeProjection) -> None:
        self._associated_probe = probe

    def get_associated_probe(self) -> ModelGroupProbeProjection | None:
        """Get the associated probe for this variable projection if it exists."""
        return self._associated_probe


@dataclass
class ModelGroupProbeProjection(ModelGroupProjection):
    """Projection of a grouped model probe.

    Parameters
    ----------
    id : int
        Unique identifier for the projected model probe.
    projection : list[GroupProjection] | None
        Group projection path for the probe.
    """

    @require_cgmapping
    def get_generated_element(self) -> CodeElement | None:
        """Get the generated code element for this probe projection.

        Returns
        -------
        CodeElement | None
            The code element mapped to this probe projection without a role,
            or None if no such mapping exists.
        """
        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.OBS_STRUCT_FIELD)  # type: ignore[missing-attribute]
        if elements:
            return cast("CStructField", elements[0])
        else:
            return super().get_generated_element()


@dataclass
class ModelGroup(ModelElement):
    """Base class for model variable and probe groups.

    Subclasses hold a ``projections`` list and a shared identifier
    (``name`` for variable groups, ``path`` for probe groups).
    """

    _: KW_ONLY  # marking fields as keyword-only to resolve dataclass fields ordering issues with inheritance
    projections: list[ModelGroupProjection] = field(default_factory=list)

    @require_cgmapping
    def get_group_projection(
        self, projection: list[GroupProjection]
    ) -> ModelGroupProjection | None:
        """Get the group element corresponding to a specific projection.

        Parameters
        ----------
        projection : list[GroupProjection]
            The exact projection path of element.

        Returns
        -------
        ModelGroupProjection | None
            The group element corresponding to the given projection, or None if not found.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        for proj in self.projections:
            if proj.projection == projection:
                return proj
        return None

    @require_cgmapping
    def get_c_type(self) -> None:
        """Not applicable for groups."""
        LOGGER.warning(
            "Groups don't have a direct C type representation. Consider using the C type of the individual projections instead."
        )
        return None

    @require_cgmapping
    def get_model_type(self) -> None:
        """Not applicable for groups."""
        LOGGER.warning(
            "Groups don't have a direct model type representation. Consider using the model type of the individual projections instead."
        )
        return None

    @require_cgmapping
    def get_generated_element(self) -> None:
        """Not applicable for groups."""
        LOGGER.warning(
            "get_generated_element is not applicable for ModelGroups. Please use get_generated_group_elements OR use get_generated_element on individual projections instead."
        )
        return None

    @require_cgmapping
    def get_generated_group_elements(self) -> list[CodeElement]:
        """Get the generated code elements for all projections in this group.

        Returns
        -------
        list[CodeElement]
            List of generated code elements corresponding to each projection in this group.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = []
        for projection in self.projections:
            if isinstance(self, ModelProbesGroup):
                code_element = self.cgmapping._get_code_for_model(  # type: ignore[missing-attribute]
                    projection.id, MappingRole.OBS_STRUCT_FIELD
                )[0]
            else:
                code_element = self.cgmapping._get_main_code_for_model(projection.id)  # type: ignore[missing-attribute]
            if code_element:
                elements.append(code_element)
        return elements


@dataclass
class ModelVariablesGroup(ModelGroup):
    """Group of model variables.

    Each variable of a group shares the same group name and is characterized by its projection,
    which consists of a list of strings (named) and integers (positional) identifying the variable
    within the group structure.

    Parameters
    ----------
    name : str
        Shared group name.
    projections : list[ModelGroupProjection]
        Projected variables that belong to this group.
    """

    name: str

    def _add_projection(self, id: int, projection: list[GroupProjection]) -> None:
        """Add a projection to this group.

        Parameters
        ----------
        id : int
            Unique identifier for the projected model variable.
        projection : list[GroupProjection]
            Group projection path for the variable.
        """
        self.projections.append(ModelGroupVariableProjection(id=id, projection=projection))


class HasComputedFlagMixin:
    """Mixin providing computed flag access methods for elements that carry a ``computed_flag``."""

    id: int
    _: KW_ONLY
    cgmapping: MappingDataBase | None = field(default=None, init=False)
    # Keep this to avoid pyrefly errors in subclasses

    @require_cgmapping
    def get_computed_flag(self) -> CStructField | None:
        """Get the computed flag structure for this element.
        The computed flag is set to true when the value of the element is updated during the cycle.

        Returns
        -------
        CStructField | None
            The computed flag structure (CStructField) if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.COMPUTED_FLAG)  # type: ignore[missing-attribute]
        return cast("CStructField", elements[0]) if elements else None


# TODO: consider implementing a function "get_all_probes()" that retrieves all the probes
# from a root operator, taking into account multiple instances of sub operators
class HasProbesMixin:
    """Mixin providing probe access methods for elements that carry a ``probes`` list."""

    probes: list[ModelProbe | ModelProbesGroup]

    def get_probes(self) -> list[ModelProbe | ModelProbesGroup]:
        """Get the probes defined in this element, including groups as is.

        Returns
        -------
        list[ModelProbe | ModelProbesGroup]
            List of probes.
        """
        return self.probes

    def get_flat_probes(self) -> list[ModelProbe]:
        """Get the probes defined in this element, flattening any groups.

        Returns
        -------
        list[ModelProbe]
            List of all probes, including those expanded from groups.
        """
        result = []
        for item in self.probes:
            if isinstance(item, ModelProbesGroup):
                for projection in item.projections:
                    probe = ModelProbe(
                        id=projection.id,
                        path=item.path,
                        kind=item.kind,
                        projection=projection.projection,
                    )
                    if hasattr(self, "cgmapping"):
                        probe.cgmapping = self.cgmapping  # type: ignore[attr-defined]
                    result.append(probe)
            else:
                result.append(item)
        return result


@dataclass
class OperatorBase(HasProbesMixin, ModelElement):
    """Base class providing common operator methods for ModelOperator and ModelMonoOperator."""

    id: int
    path: str
    probes: list[ModelProbe | ModelProbesGroup]
    instances: list[ModelInstance]

    @require_cgmapping
    def get_function_name(self) -> str | None:
        """Get the generated operator name.

        Returns
        -------
        str | None
            The generated operator name if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        # Get the cycle method function to extract its name
        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.CYCLE_METHOD)  # type: ignore[missing-attribute]
        if elements and hasattr(elements[0], "name"):
            return elements[0].name
        return None

    @require_cgmapping
    def get_header_name(self) -> str | None:
        """Get the generated header file name (.h).

        Returns
        -------
        str | None
            The header file name if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        # Get the cycle method function and find its container
        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.CYCLE_METHOD)  # type: ignore[missing-attribute]
        if elements:
            code_item = elements[0]
            # Find the container that contains this code item
            containers = self.cgmapping.get_all_code_containers()  # type: ignore[missing-attribute]
            for container in containers:
                declarations = getattr(container, "declarations", None)
                if not declarations:
                    continue
                code_item_id = getattr(code_item, "id", None)
                if code_item_id is None:
                    continue
                for declaration in declarations:
                    # declaration is a tuple (tag, code_object)
                    if len(declaration) >= 2 and hasattr(declaration[1], "id"):
                        if declaration[1].id == code_item_id:
                            return getattr(container, "interface_file", None)
        return None

    @require_cgmapping
    def get_source_name(self) -> str | None:
        """Get the generated source file name (.c).

        Returns
        -------
        str | None
            The source file name if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        # Get the cycle method function and find its container
        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.CYCLE_METHOD)  # type: ignore[missing-attribute]
        if elements:
            code_item = elements[0]
            # Find the container that contains this code item
            containers = self.cgmapping.get_all_code_containers()  # type: ignore[missing-attribute]
            for container in containers:
                declarations = getattr(container, "declarations", None)
                if not declarations:
                    continue
                code_item_id = getattr(code_item, "id", None)
                if code_item_id is None:
                    continue
                for declaration in declarations:
                    # declaration is a tuple (tag, code_object)
                    if len(declaration) >= 2 and hasattr(declaration[1], "id"):
                        if declaration[1].id == code_item_id:
                            return getattr(container, "implementation_file", None)
        return None

    @require_cgmapping
    def get_reset(self) -> CFunction | None:
        """Get the generated reset function.

        Returns
        -------
        CFunction | None
            The reset function if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.RESET_METHOD)  # type: ignore[missing-attribute]
        return cast("CFunction", elements[0]) if elements else None

    @require_cgmapping
    def get_init(self) -> CFunction | None:
        """Get the generated init function.

        Returns
        -------
        CFunction | None
            The init function if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.INIT_METHOD)  # type: ignore[missing-attribute]
        return cast("CFunction", elements[0]) if elements else None

    @require_cgmapping
    def get_cycle(self) -> CFunction | None:
        """Get the generated cycle function.

        Returns
        -------
        CFunction | None
            The cycle function if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.CYCLE_METHOD)  # type: ignore[missing-attribute]
        return cast("CFunction", elements[0]) if elements else None

    @require_cgmapping
    def get_context_type(self) -> CStruct | None:
        """Get the generated context type structure.

        Returns
        -------
        CStruct | None
            The context type structure if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.CONTEXT_TYPE)  # type: ignore[missing-attribute]
        return cast("CStruct", elements[0]) if elements else None

    @require_cgmapping
    def get_input_struct_type(self) -> CStruct | None:
        """Get the generated input structure type.

        Returns
        -------
        CStruct | None
            The input structure type if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.INPUT_STRUCT_TYPE)  # type: ignore[missing-attribute]
        return cast("CStruct", elements[0]) if elements else None

    @require_cgmapping
    def get_output_struct_type(self) -> CStruct | None:
        """Get the generated output structure type.

        Returns
        -------
        CStruct | None
            The output structure type if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.OUTPUT_STRUCT_TYPE)  # type: ignore[missing-attribute]
        return cast("CStruct", elements[0]) if elements else None

    @require_cgmapping
    def get_obs_struct_type(self) -> CStruct | None:
        """Get the generated observation structure type.

        Returns
        -------
        CStruct | None
            The observation structure type if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.OBS_STRUCT_TYPE)  # type: ignore[missing-attribute]
        return cast("CStruct", elements[0]) if elements else None

    @require_cgmapping
    def is_node(self) -> bool:
        """Whether the operator is a node.
        A node has associated init method, reset method and context in addition to a function operator.

        Returns
        -------
        bool
            True if this operator is a node, False otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        return bool(self.cgmapping._get_code_for_model(self.id, MappingRole.RESET_METHOD))  # type: ignore[missing-attribute]

    def is_function(self) -> bool:
        """Whether the operator is a function.
        An operator is a function if it is not a node.
        A function only has an associated cycle method. No init or reset methods.

        Returns
        -------
        bool
            True if this operator is a function, False otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """
        return not self.is_node()

    @require_cgmapping
    def get_generated_element(self) -> None:
        """Model operators are associated to potentially multiple code elements (cycle method, init method, reset method, context struct, etc.)
        and thus don't have a single role-less generated element.
        Consider using the dedicated methods to access the specific associated code elements instead.

        Returns
        -------
        None
            Operators do not have a single generated code element.
        """
        LOGGER.warning(
            "No generated element returned for an operator. Use specific accessors for operators instead."
        )
        return None


@dataclass
class ModelPredefinedType(ModelElement):
    """Model predefined type.

    Parameters
    ----------
    id : int
        Unique identifier for this type.
    name : str
        Name of the predefined type.
    """

    id: int
    name: str


@dataclass
class ModelArray(ModelElement):
    """Model array type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this array type.
    base_type : int
        Reference ID to the base type of the array.
    size : int
        Size of the array.
    """

    id: int
    base_type: int
    size: int

    @require_cgmapping
    def get_shape(self) -> list[int]:
        """Get the successive dimensions of this array type.

        Returns
        -------
        list[int]
            Array shape as a list of successive dimensions.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """
        shape = [self.size]
        visited_ids = {self.id}
        current_base_type = self.base_type

        while True:
            base_model = self.cgmapping._get_model_by_id(current_base_type)  # type: ignore[missing-attribute]
            if not isinstance(base_model, ModelArray):
                break

            if base_model.id in visited_ids:
                LOGGER.error(
                    f"Cycle detected while resolving array shape for model id {self.id}. "
                    f"Stopping at array id {base_model.id}."
                )
                break

            shape.append(base_model.size)
            visited_ids.add(base_model.id)
            current_base_type = base_model.base_type

        return shape


@dataclass
class ModelStructField(ModelElement):
    """Model structure field.

    Parameters
    ----------
    id : int
        Unique identifier for this field.
    name : str
        Name of the field.
    type : int
        Reference ID to the type of the field.
    """

    id: int
    name: str
    type: int


@dataclass
class ModelStruct(ModelElement):
    """Model structure type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this struct type.
    fields : list[ModelStructField]
        List of fields in the structure.
    """

    id: int
    fields: list[ModelStructField]


@dataclass
class ModelEnumValue(ModelElement):
    """Model enum type value.

    Parameters
    ----------
    id : int
        Unique identifier for this enum value.
    path : str
        Path to the enum value.
    default : bool | None
        Whether this is the default value.
    """

    id: int
    path: str
    default: bool | None = None


@dataclass
class ModelEnum(ModelElement):
    """Model enum type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this enum type.
    values : list[ModelEnumValue]
        List of enum values.
    """

    id: int
    values: list[ModelEnumValue]


@dataclass
class ModelVariantConstructor(ModelElement):
    """Model variant type constructor.

    Parameters
    ----------
    id : int
        Unique identifier for this constructor.
    name : str
        Name of the constructor.
    type : int | None
        Reference ID to the type of the constructor (if any).
    """

    id: int
    name: str
    type: int | None = None


@dataclass
class ModelVariant(ModelElement):
    """Model variant type definition.

    Parameters
    ----------
    id : int
        Unique identifier for this variant type.
    constructors : list[ModelVariantConstructor]
        List of constructors for the variant.
    """

    id: int
    constructors: list[ModelVariantConstructor]


@dataclass
class ModelNamedType(ModelElement):
    """Model named type.

    Parameters
    ----------
    id : int
        Unique identifier for this named type.
    path : str
        Path to the named type.
    definition : int | None
        Reference ID to the type definition (if any).
    """

    id: int
    path: str
    definition: int | None = None

    @require_cgmapping
    def get_model_type(self) -> ModelElement | None:
        """Get the model element corresponding to the definition of this named type.

        Returns
        -------
        ModelElement | None
            The model element representing the definition, None if not found.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """
        if self.definition is not None:
            return self.cgmapping._get_model_by_id(self.definition)  # type: ignore[missing-attribute]
        return None


@dataclass
class ModelConstant(ModelElement):
    """Model constant.

    Parameters
    ----------
    id : int
        Unique identifier for this constant.
    path : str
        Path to the constant.
    type : int
        Reference ID to the type of the constant.
    external : bool | None
        Whether this constant is external.
    """

    id: int
    path: str
    type: int
    external: bool | None = None

    @require_cgmapping
    def get_elaborated_function(self) -> CFunction | None:
        """Get the generated function for this constant's elaboration.

        Returns
        -------
        CFunction | None
            The function if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """
        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.ELABORATED_FUNCTION)  # type: ignore[missing-attribute]
        return cast("CFunction", elements[0]) if elements else None

    @require_cgmapping
    def is_elaborated(self) -> bool:
        """Whether this constant is elaborated.
        Returns True if the constant has an associated elaborated function, False otherwise."""

        return bool(self.cgmapping._get_code_for_model(self.id, MappingRole.ELABORATED_FUNCTION))  # type: ignore[missing-attribute]


@dataclass
class ModelSensor(ModelElement):
    """Model sensor.

    Parameters
    ----------
    id : int
        Unique identifier for this sensor.
    path : str
        Path to the sensor.
    type : int
        Reference ID to the type of the sensor.
    """

    id: int
    path: str
    type: int


@dataclass
class ModelVariable(ModelElement):
    """Model variable.

    Parameters
    ----------
    id : int
        Unique identifier for this variable.
    name : str
        Name of the variable.
    projection : list[GroupProjection] | None
        Group projection for the variable.
    """

    id: int
    name: str
    projection: list[GroupProjection] | None = None
    _associated_probe: ModelProbe | None = None

    def _set_associated_probe(self, probe: ModelProbe) -> None:
        self._associated_probe = probe

    def get_associated_probe(self) -> ModelProbe | None:
        """Get the associated probe for this variable."""
        return self._associated_probe


@dataclass
class ModelMonoVariable(ModelElement):
    """Model variable monomorphization.

    Parameters
    ----------
    id : int
        Unique identifier for this monomorphized variable.
    src : int
        Reference ID to the source variable.
    """

    id: int
    src: int
    _associated_probe: ModelProbe | None = None

    def _set_associated_probe(self, probe: ModelProbe) -> None:
        self._associated_probe = probe

    def get_associated_probe(self) -> ModelProbe | None:
        """Get the associated probe for this variable."""
        return self._associated_probe


@dataclass
class ModelTypeParameter(ModelElement):
    """Model monomorphization operator type parameter.

    Parameters
    ----------
    id : int
        Unique identifier for this type parameter.
    name : str
        Name of the type parameter.
    type : int
        Reference ID to the type.
    """

    id: int
    name: str
    type: int


@dataclass
class ModelSizeParameter(ModelElement):
    """Model monomorphization operator size parameter.

    Parameters
    ----------
    id : int
        Unique identifier for this size parameter.
    name : str
        Name of the size parameter.
    value : int
        Value of the size parameter.
    """

    id: int
    name: str
    value: int


@dataclass
class ModelProbe(HasComputedFlagMixin, ModelElement):
    """Model element marked as probe.

    Parameters
    ----------
    id : int
        Unique identifier for this probe.
    path : str
        Path to the probe.
    kind : ProbeKind
        Kind of probe (Input, Output, Local, Wire).
    projection : list[GroupProjection] | None
        Group projection for the probe.
    """

    id: int
    path: str
    kind: ProbeKind
    projection: list[GroupProjection] | None = None

    @require_cgmapping
    def get_generated_element(self) -> CodeElement | None:
        """Get the generated code element for this probe.

        Returns
        -------
        CodeElement | None
            The code element mapped to this probe without a role,
            or None if no such mapping exists.
        """
        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.OBS_STRUCT_FIELD)  # type: ignore[missing-attribute]
        if elements:
            # Probes of type input/output may appear twice in the model with the same ID
            # (once as a probe and once as a variable). Probes always use the role association
            return cast("CStructField", elements[0])
        else:
            # The probe isn't an input/output, hence its ID is unique so shall use
            # the default get_generated_element() method
            return super().get_generated_element()


@dataclass
class ModelProbesGroup(ModelGroup):
    """Group of probes sharing the same path.

    Each probe in the group has the same ``path`` and ``kind`` and is distinguished by its
    ``projection`` (a list of label strings and positional integers).

    Parameters
    ----------
    path : str
        Shared probe path (used as the group identifier).
    kind : ProbeKind
        Kind of the probes (Input, Output, Local, Wire).
    """

    path: str
    kind: ProbeKind

    def _add_projection(self, id: int, projection: list[GroupProjection]) -> None:
        """Add a projection to this group.

        Parameters
        ----------
        id : int
            Unique identifier for the projected model variable.
        projection : list[GroupProjection]
            Group projection path for the variable.
        """
        self.projections.append(ModelGroupProbeProjection(id=id, projection=projection))


@dataclass
class ModelOperatorInstance(HasProbesMixin, HasComputedFlagMixin, ModelElement):
    """Model instance of an operator.

    Parameters
    ----------
    id : int
        Unique identifier for this operator instance.
    path : str
        Path to the operator instance.
    operator : int
        Reference ID to the operator.
    probes : list[ModelProbe | ModelProbesGroup]
        List of probes in this instance.
    instances : list[ModelInstance]
        List of nested instances.
    """

    id: int
    path: str
    operator: int
    probes: list[ModelProbe | ModelProbesGroup]
    instances: list[ModelInstance]


@dataclass
class ModelLoopInstance(HasProbesMixin, HasComputedFlagMixin, ModelElement):
    """Model loop instance.

    Parameters
    ----------
    id : int
        Unique identifier for this loop instance.
    path : str
        Path to the loop instance.
    bound : int
        Loop bound.
    kind : LoopKind | None
        Kind of loop (Iterator or Forward).
    partial : bool | None
        Whether the loop is partial.
    probes : list[ModelProbe | ModelProbesGroup]
        List of probes in this loop.
    instances : list[ModelInstance]
        List of nested instances.
    """

    id: int
    path: str
    bound: int
    probes: list[ModelProbe | ModelProbesGroup]
    instances: list[ModelInstance]
    kind: LoopKind | None = None
    partial: bool | None = None


@dataclass
class ModelOperator(OperatorBase):
    """Model operator.

    Parameters
    ----------
    id : int
        Unique identifier for this operator.
    path : str
        Path to the operator.
    root : bool | None
        Whether this is a root operator.
    external : bool | None
        Whether this operator is external.
    expanded : bool | None
        Whether this operator is expanded.
    specialize : int | None
        Reference ID to specialization (if any).
    inputs : list[ModelVariable | ModelGroup]
        List of input variables and groups. A ModelGroup is created only
        if the variable has a non-None projection attribute.
    outputs : list[ModelVariable | ModelGroup]
        List of output variables and groups. A ModelGroup is created only
        if the variable has a non-None projection attribute.
    probes : list[ModelProbe | ModelProbesGroup]
        List of probes.
    instances : list[ModelInstance]
        List of instances.
    """

    inputs: list[ModelVariable | ModelVariablesGroup]
    outputs: list[ModelVariable | ModelVariablesGroup]
    root: bool | None = None
    external: bool | None = None
    expanded: bool | None = None
    specialize: int | None = None

    def get_inputs(self) -> list[ModelVariable | ModelVariablesGroup]:
        """Get operator inputs (variables and groups)."""
        return self.inputs

    def get_outputs(self) -> list[ModelVariable | ModelVariablesGroup]:
        """Get operator outputs (variables and groups)."""
        return self.outputs

    def get_flat_inputs(self) -> list[ModelVariable]:
        """Get all input variables flattened from groups.

        Returns
        -------
        list[ModelVariable]
            All input variables from all groups in order.
        """
        result = []
        for item in self.inputs:
            if isinstance(item, ModelVariablesGroup):
                for projection in item.projections:
                    var = ModelVariable(
                        id=projection.id,
                        name=item.name,
                        projection=projection.projection,
                    )
                    var.cgmapping = self.cgmapping
                    result.append(var)
            else:
                result.append(item)
        return result

    def get_flat_outputs(self) -> list[ModelVariable]:
        """Get all output variables flattened from groups.

        Returns
        -------
        list[ModelVariable]
            All output variables from all groups in order.
        """
        result = []
        for item in self.outputs:
            if isinstance(item, ModelVariablesGroup):
                for projection in item.projections:
                    var = ModelVariable(
                        id=projection.id,
                        name=item.name,
                        projection=projection.projection,
                    )
                    var.cgmapping = self.cgmapping
                    result.append(var)
            else:
                result.append(item)
        return result

    def get_input_groups(self) -> list[ModelVariablesGroup]:
        """Get operator input groups only (excluding ungrouped variables)."""
        return [item for item in self.inputs if isinstance(item, ModelVariablesGroup)]

    def get_output_groups(self) -> list[ModelVariablesGroup]:
        """Get operator output groups only (excluding ungrouped variables)."""
        return [item for item in self.outputs if isinstance(item, ModelVariablesGroup)]

    @require_cgmapping
    def get_global_context(self) -> CGlobal | None:
        """Get the generated global context variable.

        Returns
        -------
        CGlobal | None
            The global context variable if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.GLOBAL_CONTEXT)  # type: ignore[missing-attribute]
        return cast("CGlobal", elements[0]) if elements else None

    @require_cgmapping
    def get_global_obs_struct(self) -> CStruct | None:
        """Get the generated global observation structure.

        Returns
        -------
        CStruct | None
            The global observation structure if available, None otherwise.

        Raises
        ------
        ValueError
            If no cgmapping is set on this instance.
        """

        elements = self.cgmapping._get_code_for_model(self.id, MappingRole.GLOBAL_OBS_STRUCT)  # type: ignore[missing-attribute]
        return cast("CStruct", elements[0]) if elements else None

    @require_cgmapping
    def get_mono_operators(self) -> list[ModelMonoOperator]:
        """Get the monomorphized operators derived from this operator.

        Returns
        -------
        list[ModelMonoOperator]
            List of monomorphized operators that have this operator as their source.
            Returns empty list if none found or if no cgmapping is set.
        """

        # Get all mono operators and filter those that have this operator as source
        all_operators = self.cgmapping.get_all_operators()  # type: ignore[missing-attribute]
        mono_operators = []

        for op in all_operators:
            if isinstance(op, ModelMonoOperator) and op.src == self.id:
                mono_operators.append(op)

        return mono_operators


@dataclass
class ModelMonoOperator(OperatorBase):
    """Model operator monomorphization.

    Parameters
    ----------
    id : int
        Unique identifier for this monomorphized operator.
    path : str
        Path to the operator.
    src : int
        Reference ID to the source operator.
    type_parameters : list[ModelTypeParameter]
        List of type parameters.
    size_parameters : list[ModelSizeParameter]
        List of size parameters.
    inputs : list[ModelMonoVariable]
        List of monomorphized input variables.
    outputs : list[ModelMonoVariable]
        List of monomorphized output variables.
    probes : list[ModelProbe | ModelProbesGroup]
        List of probes.
    instances : list[ModelInstance]
        List of instances.
    """

    src: int
    type_parameters: list[ModelTypeParameter]
    size_parameters: list[ModelSizeParameter]
    inputs: list[ModelMonoVariable]
    outputs: list[ModelMonoVariable]

    def get_inputs(self) -> list[ModelMonoVariable]:
        """Get monomorphized operator inputs."""
        return self.inputs

    def get_outputs(self) -> list[ModelMonoVariable]:
        """Get monomorphized operator outputs."""
        return self.outputs

    def get_flat_inputs(self) -> list[ModelMonoVariable]:
        """Get all monomorphized input variables.

        Returns
        -------
        list[ModelMonoVariable]
            All input variables in order.
        """
        return list(self.inputs)

    def get_flat_outputs(self) -> list[ModelMonoVariable]:
        """Get all monomorphized output variables.

        Returns
        -------
        list[ModelMonoVariable]
            All output variables in order.
        """
        return list(self.outputs)

    def get_input_groups(self) -> list[ModelVariablesGroup]:
        """Always empty: monomorphized operators have no variable groups."""
        return []

    def get_output_groups(self) -> list[ModelVariablesGroup]:
        """Always empty: monomorphized operators have no variable groups."""
        return []

    @require_cgmapping
    def get_src_operator(self) -> ModelOperator | None:
        """Get the source operator for this monomorphized operator.

        Returns
        -------
        ModelOperator | None
            The source operator if found, None if not found or if no cgmapping is set.
        """

        # Get the source operator by its ID
        src_operator = self.cgmapping._get_model_by_id(self.src)  # type: ignore[missing-attribute]
        return src_operator if isinstance(src_operator, ModelOperator) else None


type ModelInstance = tuple[str, ModelOperatorInstance | ModelLoopInstance]
"""Type alias for model instances (discriminated union)"""


type ModelDeclaration = tuple[
    str,
    ModelPredefinedType
    | ModelArray
    | ModelStruct
    | ModelEnum
    | ModelVariant
    | ModelNamedType
    | ModelConstant
    | ModelSensor
    | ModelOperator
    | ModelMonoOperator,
]
"""Type alias for model declarations (discriminated union)"""


class _ModelRegistry:
    """Registry to manage all model items and resolve ID references.

    This class stores all model items indexed by their unique IDs and provides
    methods to load from JSON and resolve references between items.

    Attributes
    ----------
    items : dict[int, ModelElement]
        Dictionary mapping item IDs to their corresponding objects.
    """

    def __init__(self):
        """Initialize an empty model registry."""
        self.items: dict[int, ModelElement] = {}

    def register(self, item: ModelElement) -> None:
        """Register a model item in the registry.

        Parameters
        ----------
        item : ModelElement
            The model item to register. Must have an 'id' attribute.

        Raises
        ------
        ValueError
            If an item with the same ID is already registered or the ID is missing.
        """
        if not hasattr(item, "id"):
            raise ValueError(f"Item {item} does not have an 'id' attribute")

        if item.id in self.items:
            # The only situation where two items can have the same ID is for probes
            # with type input/output, as they are also represented as variables in the model.
            if isinstance(item, ModelProbe):
                flow = self.items[item.id]
                assert isinstance(flow, ModelVariable | ModelMonoVariable)
                flow._set_associated_probe(item)
            elif isinstance(item, ModelVariable | ModelMonoVariable):
                probe = self.items[item.id]
                assert isinstance(probe, ModelProbe)
                item._set_associated_probe(probe)
                self.items[item.id] = item
            elif isinstance(item, ModelGroupProbeProjection):
                flow = self.items[item.id]
                assert isinstance(flow, ModelGroupVariableProjection)
                flow._set_associated_probe(item)
            elif isinstance(item, ModelGroupVariableProjection):
                probe = self.items[item.id]
                assert isinstance(probe, ModelGroupProbeProjection)
                item._set_associated_probe(probe)
                self.items[item.id] = item
            else:
                raise ValueError(f"Unexpected duplicate ID {item.id}")
        else:
            self.items[item.id] = item

    def get(self, item_id: int) -> ModelElement | None:
        """Get a model item by its ID.

        Parameters
        ----------
        item_id : int
            The unique ID of the item to retrieve.

        Returns
        -------
        ModelElement | None
            The model item if found, None otherwise.
        """
        return self.items.get(item_id)

    def get_by_type(self, item_type: type) -> list[ModelElement]:
        """Get all model items of a specific type.

        Parameters
        ----------
        item_type : type
            The type of items to retrieve.

        Returns
        -------
        list[ModelElement]
            List of all items matching the specified type.
        """
        return [item for item in self.items.values() if isinstance(item, item_type)]

    def clear(self) -> None:
        """Clear all items from the registry."""
        self.items.clear()

    def __len__(self) -> int:
        """Return the number of items in the registry."""
        return len(self.items)

    def __contains__(self, item_id: int) -> bool:
        """Check if an item ID is in the registry."""
        return item_id in self.items

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f"_ModelRegistry({len(self.items)} items)"


def _build_mixed_variables(
    variables: list[ModelVariable],
) -> list[ModelVariable | ModelVariablesGroup]:
    """Build a mixed list of variables and groups based on projection attribute.

    A ModelVariableGroup is created only if the variable has a non-None projection.
    Otherwise, the variable is kept as-is.

    Parameters
    ----------
    variables : list[ModelVariable]
        List of model variables to process.

    Returns
    -------
    list[ModelVariable | ModelVariableGroup]
        Mixed list of variables and groups.
    """
    result: list[ModelVariable | ModelVariablesGroup] = []
    groups = {}
    for variable in variables:
        if variable.projection is not None:
            if variable.name not in groups:
                groups[variable.name] = ModelVariablesGroup(variable.name)
            groups[variable.name]._add_projection(variable.id, variable.projection)
        else:
            # Keep the variable as-is
            result.append(variable)
    result.extend(groups.values())

    return result


def _build_mixed_probes(
    probes: list[ModelProbe],
) -> list[ModelProbe | ModelProbesGroup]:
    """Build a mixed list of probes and probe groups based on the projection attribute.

    A ModelProbesGroup is created only if a probe has a non-None projection.
    Probes with the same ``path`` and non-None projections are collected into
    the same ``ModelProbesGroup``.  Probes with a ``None`` projection are kept
    as standalone ``ModelProbe`` items.

    Parameters
    ----------
    probes : list[ModelProbe]
        List of model probes to process.

    Returns
    -------
    list[ModelProbe | ModelProbesGroup]
        Mixed list of standalone probes and probe groups.
    """
    result: list[ModelProbe | ModelProbesGroup] = []
    groups: dict[str, ModelProbesGroup] = {}
    for probe in probes:
        if probe.projection is not None:
            if probe.path not in groups:
                groups[probe.path] = ModelProbesGroup(probe.path, probe.kind)
            groups[probe.path]._add_projection(probe.id, probe.projection)
        else:
            result.append(probe)
    result.extend(groups.values())
    return result


def parse_probe(data: dict) -> ModelProbe:
    """Parse a Probe from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the probe.

    Returns
    -------
    Probe
        Parsed probe object.
    """
    return ModelProbe(
        id=data["id"],
        path=data["path"],
        kind=ProbeKind(data["kind"]),
        projection=data.get("projection"),
    )


def parse_model_variable(data: dict) -> ModelVariable:
    """Parse a ModelVariable from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the variable.

    Returns
    -------
    ModelVariable
        Parsed variable object.
    """
    return ModelVariable(id=data["id"], name=data["name"], projection=data.get("projection"))


def parse_model_mono_variable(data: dict) -> ModelMonoVariable:
    """Parse a ModelMonoVariable from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the monomorphized variable.

    Returns
    -------
    ModelMonoVariable
        Parsed monomorphized variable object.
    """
    return ModelMonoVariable(id=data["id"], src=data["src"])


def parse_model_type_parameter(data: dict) -> ModelTypeParameter:
    """Parse a ModelTypeParameter from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the type parameter.

    Returns
    -------
    ModelTypeParameter
        Parsed type parameter object.
    """
    return ModelTypeParameter(id=data["id"], name=data["name"], type=data["type"])


def parse_model_size_parameter(data: dict) -> ModelSizeParameter:
    """Parse a ModelSizeParameter from JSON data.

    Parameters
    ----------
    data : dict
        JSON data for the size parameter.

    Returns
    -------
    ModelSizeParameter
        Parsed size parameter object.
    """
    return ModelSizeParameter(id=data["id"], name=data["name"], value=data["value"])


def parse_model_instance(data: tuple[str, dict[str, Any]]) -> ModelInstance:
    """Parse a ModelInstance from JSON data.

    Parameters
    ----------
    data : tuple
        JSON data as a tuple [type_name, instance_data].

    Returns
    -------
    ModelInstance
        Parsed instance as a tuple (type_name, instance_object).
    """
    instance_type, instance_data = data

    if instance_type == "operator":
        instance = ModelOperatorInstance(
            id=instance_data["id"],
            path=instance_data["path"],
            operator=instance_data["operator"],
            probes=_build_mixed_probes([parse_probe(p) for p in instance_data.get("probes", [])]),
            instances=[parse_model_instance(i) for i in instance_data.get("instances", [])],
        )
    elif instance_type == "loop":
        instance = ModelLoopInstance(
            id=instance_data["id"],
            path=instance_data["path"],
            bound=instance_data["bound"],
            kind=LoopKind(instance_data["kind"]) if "kind" in instance_data else None,
            partial=instance_data.get("partial"),
            probes=_build_mixed_probes([parse_probe(p) for p in instance_data.get("probes", [])]),
            instances=[parse_model_instance(i) for i in instance_data.get("instances", [])],
        )
    else:
        raise ValueError(f"Unknown instance type: {instance_type}")

    return (instance_type, instance)


def parse_model_declaration(data: tuple[str, dict[str, Any]]) -> ModelDeclaration:
    """Parse a ModelDeclaration from JSON data.

    Parameters
    ----------
    data : tuple
        JSON data as a tuple [type_name, declaration_data].

    Returns
    -------
    ModelDeclaration
        Parsed declaration as a tuple (type_name, declaration_object).
    """
    decl_type, decl_data = data

    if decl_type == "predefined_type":
        obj = ModelPredefinedType(id=decl_data["id"], name=decl_data["name"])

    elif decl_type == "array":
        obj = ModelArray(
            id=decl_data["id"], base_type=decl_data["base_type"], size=decl_data["size"]
        )

    elif decl_type == "struct":
        fields = [
            ModelStructField(id=f["id"], name=f["name"], type=f["type"])
            for f in decl_data.get("fields", [])
        ]
        obj = ModelStruct(id=decl_data["id"], fields=fields)

    elif decl_type == "enum":
        values = [
            ModelEnumValue(id=v["id"], path=v["path"], default=v.get("default"))
            for v in decl_data.get("values", [])
        ]
        obj = ModelEnum(id=decl_data["id"], values=values)

    elif decl_type == "variant":
        constructors = [
            ModelVariantConstructor(id=c["id"], name=c["name"], type=c.get("type"))
            for c in decl_data.get("constructors", [])
        ]
        obj = ModelVariant(id=decl_data["id"], constructors=constructors)

    elif decl_type == "named_type":
        obj = ModelNamedType(
            id=decl_data["id"],
            path=decl_data["path"],
            definition=decl_data.get("definition"),
        )

    elif decl_type == "const":
        obj = ModelConstant(
            id=decl_data["id"],
            path=decl_data["path"],
            type=decl_data["type"],
            external=decl_data.get("external"),
        )

    elif decl_type == "sensor":
        obj = ModelSensor(id=decl_data["id"], path=decl_data["path"], type=decl_data["type"])

    elif decl_type == "operator":
        input_vars = [parse_model_variable(v) for v in decl_data.get("inputs", [])]
        output_vars = [parse_model_variable(v) for v in decl_data.get("outputs", [])]
        mixed_inputs = _build_mixed_variables(input_vars)
        mixed_outputs = _build_mixed_variables(output_vars)
        obj = ModelOperator(
            id=decl_data["id"],
            path=decl_data["path"],
            root=decl_data.get("root"),
            external=decl_data.get("external"),
            expanded=decl_data.get("expanded"),
            specialize=decl_data.get("specialize"),
            inputs=mixed_inputs,
            outputs=mixed_outputs,
            probes=_build_mixed_probes([parse_probe(p) for p in decl_data.get("probes", [])]),
            instances=[parse_model_instance(i) for i in decl_data.get("instances", [])],
        )

    elif decl_type == "mono":
        obj = ModelMonoOperator(
            id=decl_data["id"],
            path=decl_data["path"],
            src=decl_data["src"],
            type_parameters=[
                parse_model_type_parameter(tp) for tp in decl_data.get("type_parameters", [])
            ],
            size_parameters=[
                parse_model_size_parameter(sp) for sp in decl_data.get("size_parameters", [])
            ],
            inputs=[parse_model_mono_variable(v) for v in decl_data.get("inputs", [])],
            outputs=[parse_model_mono_variable(v) for v in decl_data.get("outputs", [])],
            probes=_build_mixed_probes([parse_probe(p) for p in decl_data.get("probes", [])]),
            instances=[parse_model_instance(i) for i in decl_data.get("instances", [])],
        )

    else:
        raise ValueError(f"Unknown model declaration type: {decl_type}")

    return (decl_type, obj)


def load_model_from_json(
    model_data: list[tuple],
    registry: _ModelRegistry | None = None,
) -> _ModelRegistry:
    """Load model declarations from JSON data into a registry.

    Parameters
    ----------
    model_data : list[tuple]
        List of model declarations as tuples from JSON.
    registry : _ModelRegistry | None, optional
        Existing registry to use, or None to create a new one.

    Returns
    -------
    _ModelRegistry
        Registry containing all parsed model items.
    """
    if registry is None:
        registry = _ModelRegistry()

    for decl_tuple in model_data:
        decl_type, decl_obj = parse_model_declaration(decl_tuple)

        registry.register(decl_obj)

        # Also register nested items
        if isinstance(decl_obj, ModelStruct):
            for struct_field in decl_obj.fields:
                registry.register(struct_field)
        elif isinstance(decl_obj, ModelEnum):
            for value in decl_obj.values:
                registry.register(value)
        elif isinstance(decl_obj, ModelVariant):
            for constructor in decl_obj.constructors:
                registry.register(constructor)
        elif isinstance(decl_obj, ModelOperator):
            for item in decl_obj.inputs + decl_obj.outputs:
                if isinstance(item, ModelGroup):
                    for projection in item.projections:
                        registry.register(projection)
                elif isinstance(item, ModelVariable):
                    registry.register(item)
            for probe in decl_obj.probes:
                if isinstance(probe, ModelProbesGroup):
                    for projection in probe.projections:
                        registry.register(projection)
                else:
                    registry.register(probe)
        elif isinstance(decl_obj, ModelMonoOperator):
            for var in decl_obj.inputs + decl_obj.outputs:
                registry.register(var)
            for probe in decl_obj.probes:
                if isinstance(probe, ModelProbesGroup):
                    for projection in probe.projections:
                        registry.register(projection)
                else:
                    registry.register(probe)

    return registry
