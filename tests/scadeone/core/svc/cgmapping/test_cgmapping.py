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

"""Tests for CGMapping class examples."""

import shutil
from typing import cast
import logging

import pytest
from pathlib import Path

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.job import CodeGenerationJob
from ansys.scadeone.core.svc.cgmapping import CGMapping
from ansys.scadeone.core.svc.cgmapping.code import (
    CArray,
    CEnumValue,
    CFunction,
    CGlobal,
    CParameter,
    CPredefinedType,
    CStruct,
    CStructField,
    CUnion,
    CodeContainer,
    CodeTypeBase,
    CTypedef,
    parse_c_declaration,
)
from ansys.scadeone.core.svc.cgmapping.model import (
    ModelGroupVariableProjection,
    ModelSizeParameter,
    ModelTypeParameter,
    ProbeKind,
    ModelEnumValue,
    ModelOperator,
    ModelMonoOperator,
    ModelElement,
    ModelConstant,
    ModelSensor,
    ModelArray,
    ModelStruct,
    ModelEnum,
    ModelStructField,
    ModelVariant,
    ModelVariable,
    ModelProbe,
    ModelGroup,
    ModelProbesGroup,
    ModelGroupProjection,
    ModelVariablesGroup,
    LoopKind,
    ModelNamedType,
    ModelPredefinedType,
    load_model_from_json,
    parse_model_instance,
    parse_probe,
    parse_model_size_parameter,
)
from ansys.scadeone.core.svc.cgmapping.mapping import MappingRole


type_classes = (
    ModelPredefinedType,
    ModelNamedType,
    ModelArray,
    ModelStruct,
    ModelEnum,
    ModelVariant,
)


# To remove all generated code
_remove_swan_cg_code = False


@pytest.fixture(scope="module", autouse=True)
def generate_mapping_files(app):
    project = app.load_project("tests/models/mapping/project.sproj")
    if not project:
        raise RuntimeError("Failed to load project.")
    project.load_jobs()
    for job in project.jobs:
        if not isinstance(job, CodeGenerationJob):
            continue
        if job.name == "WrongVersionNumber":
            continue
        cg_out = job.storage.path.parent / "out"
        if _remove_swan_cg_code:
            shutil.rmtree(str(cg_out), ignore_errors=True)
        if cg_out.exists():
            continue
        result = job.run()
        if result.code != 0:
            raise RuntimeError(f"Code generation job '{job.name}' failed with code {result.code}.")


@pytest.fixture
def mapping():
    test_file = Path("tests/models/mapping/jobs/codegen_CGMultiRoots/out/cg_map.json")
    if test_file.exists():
        return CGMapping.from_file(test_file)
    else:
        assert False, "Test file not found"


class TestCGMappingOperatorIOTypes:
    """Tests for different operator job settings and their impact on input/output types."""

    def test_classic_flow(self):
        test_file = Path("tests/models/mapping/jobs/codegen_CGStandardIn/out/cg_map.json")
        mapping = CGMapping.from_file(test_file)
        operator = mapping.get_all_operators()[0]
        assert len(operator.inputs) == 3
        for input in operator.inputs:
            code = input.get_generated_element()
            assert isinstance(code, CParameter)
            model = code.get_model_element()
            assert model
        function_code = operator.get_generated_element()
        assert function_code is None  # operator code elements are all role-based
        assert isinstance(operator.get_cycle(), CFunction)

    def test_interface_global(self):
        test_file = Path("tests/models/mapping/jobs/codegen_CGGlobalIn/out/cg_map.json")
        mapping = CGMapping.from_file(test_file)
        operator = mapping.get_all_operators()[0]
        assert len(operator.inputs) == 3
        for input in operator.inputs:
            code = input.get_generated_element()
            assert isinstance(code, CGlobal)
        function_code = operator.get_generated_element()
        assert function_code is None  # operator code elements are all role-based
        assert isinstance(operator.get_cycle(), CFunction)

    def test_struct_inputs(self):
        test_file = Path("tests/models/mapping/jobs/codegen_CGStructIn/out/cg_map.json")
        mapping = CGMapping.from_file(test_file)
        operator = mapping.get_all_operators()[0]
        assert len(operator.inputs) == 3

        # Model inputs and code input structure fields are not associated in the mapping of the JSON
        # This is a BUG in the CG that needs to be fixed.
        # TODO uncomment and complete the code block below whenever it is done.

        # for input in operator.inputs:
        #     code = input.get_generated_element()
        #     assert len(code) == 1

        assert operator.get_generated_element() is None  # operator code elements are all role-based
        input_structure = operator.get_input_struct_type()
        assert input_structure is not None
        assert isinstance(input_structure, CTypedef)
        # TODO replace this line by dedicated public method when implemented
        input_structure = mapping._get_code_by_id(input_structure.type)
        assert isinstance(input_structure, CStruct)
        assert len(input_structure.fields) == 3
        for field in input_structure.fields:
            assert isinstance(field, CStructField)
        output_structure = operator.get_output_struct_type()
        assert output_structure is not None
        assert isinstance(output_structure, CTypedef)
        # TODO replace this line by dedicated public method when implemented
        output_structure = mapping._get_code_by_id(output_structure.type)
        assert isinstance(output_structure, CStruct)
        assert len(output_structure.fields) == 2
        for field in output_structure.fields:
            assert isinstance(field, CStructField)


class TestCGMappingExamples:
    """Tests based on CGMapping documentation examples."""

    def test_get_all_operators(self, mapping: CGMapping):
        """Test get_all_operators()."""
        operators = mapping.get_all_operators()
        assert isinstance(operators, list)
        assert len(operators) > 5

        for op in operators:
            assert isinstance(op, ModelOperator | ModelMonoOperator)

    def test_get_root_operators(self, mapping: CGMapping):
        """Test get_root_operators()."""
        root_ops = mapping.get_root_operators()
        assert isinstance(root_ops, list)

        for op in root_ops:
            assert isinstance(op, ModelOperator)
            assert op.root is True

    def test_get_model_by_path(self, mapping: CGMapping):
        """Test get_model_by_path()."""
        all_operators = mapping.get_all_operators()
        assert all_operators
        test_path = all_operators[0].path

        items = mapping.get_model_by_path(test_path)
        assert isinstance(items, list)
        assert len(items) > 0

        for item in items:
            assert hasattr(item, "path")
            assert item.path == test_path

    def test_get_model_by_name(self, mapping: CGMapping):
        """Test get_model_by_name()."""
        all_operators = mapping.get_all_operators()
        if all_operators:
            test_path = all_operators[0].path
            test_name = test_path.split("::")[-1]  # Last component of path

            items = mapping.get_model_by_name(test_name)
            assert isinstance(items, list)

            for item in items:
                if hasattr(item, "path"):
                    path_parts = item.path.split("::")
                    assert path_parts[-1] == test_name

    def test_get_model_by_id(self, mapping: CGMapping):
        """Test get_model_by_id()."""
        all_operators = mapping.get_all_operators()
        if all_operators:
            test_id = all_operators[0].id

            item = mapping._get_model_by_id(test_id)
            assert item is not None
            assert isinstance(item, ModelOperator)

    def test_get_statistics(self, mapping: CGMapping):
        """Test get_statistics()."""
        stats = mapping.get_statistics()
        assert isinstance(stats, dict)

        required_keys = [
            "version",
            "model_items",
            "code_items",
            "mappings",
            "operators",
            "root_operators",
            "constants",
            "sensors",
            "types",
        ]
        for key in required_keys:
            assert key in stats

        assert isinstance(stats["model_items"], int)
        assert isinstance(stats["operators"], int)
        assert isinstance(stats["mappings"], int)
        assert stats["model_items"] > 0
        assert stats["operators"] > 0
        assert stats["mappings"] > 0


class TestCGMappingComplexTypes:
    """Tests for complex data types and monomorphized operators."""

    def test_get_all_mono_operators(self, mapping: CGMapping):
        """Test getting all monomorphized operators from model registry."""
        mono_ops = mapping._model_registry.get_by_type(ModelMonoOperator)
        if not mono_ops:
            pytest.skip("No monomorphized operators found in test data")
        assert isinstance(mono_ops, list)
        assert all(isinstance(mono_op, ModelMonoOperator) for mono_op in mono_ops)
        assert mono_ops[0].src == mono_ops[1].src
        assert mono_ops[0].type_parameters[0].name == mono_ops[1].type_parameters[0].name
        assert mono_ops[0].type_parameters[0].type != mono_ops[1].type_parameters[0].type
        src_operator = mapping._get_model_by_id(mono_ops[0].src)
        assert isinstance(src_operator, ModelOperator)
        all_ops = mapping.get_all_operators()
        assert mono_ops[0] in all_ops
        assert mono_ops[1] in all_ops

    def test_get_all_arrays(self, mapping: CGMapping):
        """Test getting all array types."""
        arrays = mapping._model_registry.get_by_type(ModelArray)
        assert isinstance(arrays, list)

        for array in arrays:
            assert isinstance(array, ModelArray)

            # Verify it's included in get_all_types()
            all_types = mapping.get_all_types()
            assert array in all_types

    def test_array_type_resolution(self, mapping: CGMapping):
        """Test resolving array base types."""
        arrays = mapping._model_registry.get_by_type(ModelArray)
        if not arrays:
            pytest.skip("No array types found in test data")

        for array in arrays:
            base_type = mapping._resolve_type(array.base_type)
            assert isinstance(base_type, type_classes)

    def test_get_all_structs(self, mapping: CGMapping):
        """Test getting all struct types."""
        structs = mapping._model_registry.get_by_type(ModelStruct)
        all_types = mapping.get_all_types()
        assert isinstance(structs, list)

        for struct in structs:
            assert isinstance(struct, ModelStruct)
            assert struct in all_types

    def test_struct_fields(self, mapping: CGMapping):
        """Test struct field properties."""
        structs = mapping._model_registry.get_by_type(ModelStruct)
        if not structs:
            pytest.skip("No struct types found in test data")

        struct = structs[0]

        # Test fields
        assert isinstance(struct.fields, list)

        for field in struct.fields:
            assert isinstance(field, ModelStructField)

            # Resolve field type
            field_type = mapping._resolve_type(field.type)
            assert field_type is not None
            assert isinstance(field_type, type_classes)

    def test_get_all_enums(self, mapping: CGMapping):
        """Test getting all enum types."""
        enums = mapping._model_registry.get_by_type(ModelEnum)
        assert isinstance(enums, list)
        all_types = mapping.get_all_types()

        for enum in enums:
            assert isinstance(enum, ModelEnum)
            assert enum in all_types

    def test_get_all_variants(self, mapping: CGMapping):
        """Test getting all variant types."""
        variants = mapping._model_registry.get_by_type(ModelVariant)
        assert isinstance(variants, list)
        all_types = mapping.get_all_types()

        for variant in variants:
            assert isinstance(variant, ModelVariant)
            assert variant in all_types

    def test_get_all_named_types(self, mapping: CGMapping):
        """Test getting all named types."""
        named_types = mapping._model_registry.get_by_type(ModelNamedType)
        assert isinstance(named_types, list)
        all_types = mapping.get_all_types()

        for named_type in named_types:
            assert isinstance(named_type, ModelNamedType)
            assert named_type in all_types

    def test_named_type_resolution(self, mapping: CGMapping):
        """Test resolving named type definitions."""
        named_types = mapping._model_registry.get_by_type(ModelNamedType)
        if not named_types:
            pytest.skip("No named types found in test data")

        named_type = named_types[0]

        # Resolve type definition
        definition = mapping._resolve_type(named_type.definition)
        assert definition is not None
        assert isinstance(definition, type_classes)

    def test_predefined_types(self, mapping: CGMapping):
        """Test predefined types."""
        predefined = mapping._model_registry.get_by_type(ModelPredefinedType)
        assert isinstance(predefined, list)

        for ptype in predefined:
            assert isinstance(ptype, ModelPredefinedType)
            assert isinstance(ptype.name, str)

            # Common predefined types
            assert ptype.name in [
                "int8",
                "int16",
                "int32",
                "int64",
                "uint8",
                "uint16",
                "uint32",
                "uint64",
                "float32",
                "float64",
                "bool",
                "char",
                "string",
            ] or ptype.name.startswith("size_")

    def test_complex_type_mappings(self, mapping: CGMapping):
        """Test that complex types have code mappings."""
        all_types = mapping.get_all_types()

        # Filter for complex types only
        complex_types = []
        for type_item in all_types:
            if isinstance(type_item, (ModelArray, ModelStruct, ModelEnum, ModelVariant)):
                complex_types.append(type_item)

        assert len(complex_types) > 8
        for ctype in complex_types:
            # Test that type can have code mappings
            code_items = mapping._get_code_for_model(ctype.id)
            assert isinstance(code_items, list)
            assert isinstance(ctype, ModelElement)
            generated = ctype.get_generated_element()
            assert generated is not None or isinstance(ctype, ModelArray)
            # Array definitions don't necessarily have associated items

    def test_mono_operator_code_generation(self, mapping: CGMapping):
        """Test code generation for monomorphized operators."""
        # Use get_all_operators to get objects with cgmapping properly assigned
        all_ops = mapping.get_all_operators()
        mono_ops = [op for op in all_ops if isinstance(op, ModelMonoOperator)]
        if not mono_ops:
            pytest.skip("No monomorphized operators found in test data")

        mono_op = cast(ModelMonoOperator, mono_ops[0])

        # _get_code_for_model returns all code items (including role-based)
        code_items = mapping._get_code_for_model(mono_op.id)
        assert isinstance(code_items, list)

        # get_generated_element() returns only the role-less code item
        code_item = mono_op.get_generated_element()
        assert code_item is None  # mono operator code elements are all role-based

        # Test specific roles if they exist
        cycle_methods = mapping._get_code_for_model(mono_op.id, MappingRole.CYCLE_METHOD)
        assert isinstance(cycle_methods[0], CFunction)

    def test_type_statistics(self, mapping: CGMapping):
        """Test that statistics include complex types."""
        stats = mapping.get_statistics()

        # Calculate expected counts
        arrays = len(mapping._model_registry.get_by_type(ModelArray))
        structs = len(mapping._model_registry.get_by_type(ModelStruct))
        enums = len(mapping._model_registry.get_by_type(ModelEnum))
        variants = len(mapping._model_registry.get_by_type(ModelVariant))
        named_types = len(mapping._model_registry.get_by_type(ModelNamedType))
        predefined = len(mapping._model_registry.get_by_type(ModelPredefinedType))

        expected_types = arrays + structs + enums + variants + named_types + predefined
        assert stats["types"] == expected_types

    def test_model_array_get_shape(self, mapping: CGMapping):
        """Test ModelArray.get_shape() for nested array dimensions."""
        arrays = mapping._model_registry.get_by_type(ModelArray)
        if not arrays:
            pytest.skip("No ModelArray elements found")

        for array in arrays:
            assert isinstance(array, ModelArray)

            shape = array.get_shape()
            assert shape
            assert shape[0] == array.size
            assert all(isinstance(dim, int) for dim in shape)

            expected_shape = [array.size]
            visited_ids = {array.id}
            current_type = mapping._get_model_by_id(array.base_type)

            while isinstance(current_type, ModelArray) and current_type.id not in visited_ids:
                expected_shape.append(current_type.size)
                visited_ids.add(current_type.id)
                current_type = mapping._get_model_by_id(current_type.base_type)

            assert shape == expected_shape


class TestModelElementGeneratedElement:
    """Tests for new ModelElement.get_generated_element() functionality."""

    def test_model_operator_get_generated_element(self, mapping: CGMapping):
        """Test get_generated_element() for ModelOperator."""
        # Get a test operator
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            assert isinstance(operator, ModelElement)
            # get_generated_element() returns None for operators since all their
            # code elements are associated via named roles (CycleMethod, etc.)
            assert operator.get_generated_element() is None

    def test_model_operator_specialized_methods(self, mapping: CGMapping):
        """Test specialized methods for accessing specific code elements."""
        operators = mapping.get_all_operators()
        assert operators

        # Test specialized methods
        cycle_method = operators[0].get_cycle()
        if cycle_method:
            assert isinstance(cycle_method, CFunction)

        # Test init method
        init_method = operators[0].get_init()
        if init_method:
            assert isinstance(init_method, CFunction)

    def test_model_constant_get_generated_element(self, mapping: CGMapping):
        """Test get_generated_element() for ModelConstant."""
        constants = mapping.get_all_constants()
        assert constants

        constant = constants[0]

        # Verify constant inherits from ModelElement
        assert isinstance(constant, ModelConstant)

        code_item = constant.get_generated_element()
        assert isinstance(code_item, CGlobal)

    def test_model_sensor_get_generated_element(self, mapping: CGMapping):
        """Test get_generated_element() for ModelSensor."""
        sensors = mapping.get_all_sensors()
        assert sensors

        sensor = sensors[0]
        assert isinstance(sensor, ModelSensor)

        code_item = sensor.get_generated_element()
        assert isinstance(code_item, CGlobal)


class TestCGMappingCodeQueries:
    """Tests for code item queries and bidirectional mappings."""

    def test_get_code_by_id(self, mapping: CGMapping):
        """Test get_code_by_id() functionality."""
        # First get some code items to find valid IDs
        containers = mapping.get_all_code_containers()
        assert containers

        # Find a code item ID from the first container
        container = containers[0]
        if hasattr(container, "declarations") and container.declarations:
            # CDeclaration is tuple[str, Union[CFunction, CGlobal, ...]]
            tag, code_item = container.declarations[0]
            code_id = code_item.id

            # Test get_code_by_id
            retrieved_item = mapping._get_code_by_id(code_id)
            assert retrieved_item is not None
            assert retrieved_item.id == code_id
            assert retrieved_item is code_item

    def test_get_code_by_id_invalid(self, mapping: CGMapping):
        """Test get_code_by_id() with invalid ID."""
        # Test with non-existent ID
        result = mapping._get_code_by_id(999999)
        assert result is None

    def test_get_code_by_name(self, mapping: CGMapping):
        """Test get_code_by_name() functionality."""
        containers = mapping.get_all_code_containers()
        assert containers

        # Find a code item with a name
        code_item = None
        for container in containers:
            if hasattr(container, "declarations") and container.declarations:
                for declaration in container.declarations:
                    # CDeclaration is tuple[str, Union[CFunction, CGlobal, ...]]
                    tag, obj = declaration
                    if hasattr(obj, "name"):
                        code_item = obj
                        break
                if code_item:
                    break

        if not code_item:
            pytest.skip("No named code items found in test data")

        # Test get_code_by_name
        items = mapping.get_code_by_name(code_item.name)
        assert isinstance(items, list)
        assert len(items) > 0
        assert code_item in items

    def test_get_code_by_name_empty(self, mapping: CGMapping):
        """Test get_code_by_name() with non-existent name."""
        items = mapping.get_code_by_name("NonExistentCodeItem")
        assert not items

    def test_get_all_code_containers(self, mapping: CGMapping):
        """Test get_all_code_containers() functionality."""
        containers = mapping.get_all_code_containers()
        assert isinstance(containers, list)
        assert containers
        for container in containers:
            # Verify basic container properties
            assert isinstance(container, CodeContainer)
            assert isinstance(container.declarations, list)

            # Test that declarations have proper CDeclaration structure
            for declaration in container.declarations:
                # CDeclaration is tuple[str, Union[CFunction, CGlobal, ...]]
                assert isinstance(declaration, tuple)
                assert len(declaration) == 2
                tag, obj = declaration
                assert isinstance(tag, str)
                assert hasattr(obj, "id")
                assert isinstance(obj.id, int)

    def test_get_model_for_code(self, mapping: CGMapping):
        """Test get_model_for_code() reverse lookup."""
        containers = mapping.get_all_code_containers()
        if not containers:
            pytest.skip("No code containers found in test data")

        # Find a code item that has model mappings
        code_item_with_mapping = None
        for container in containers:
            if hasattr(container, "declarations"):
                for declaration in container.declarations:
                    # CDeclaration is tuple[str, Union[CFunction, CGlobal, ...]]
                    tag, obj = declaration
                    model_items = mapping._get_model_for_code(obj.id)
                    if model_items:
                        code_item_with_mapping = obj
                        break
                if code_item_with_mapping:
                    break

        if not code_item_with_mapping:
            pytest.skip("No code items with model mappings found")

        # Test the reverse lookup
        model_items = mapping._get_model_for_code(code_item_with_mapping.id)
        assert isinstance(model_items, list)
        assert len(model_items) > 0

        for model_item in model_items:
            assert hasattr(model_item, "id")
            # Verify bidirectional mapping
            code_items = mapping._get_code_for_model(model_item.id)
            assert code_item_with_mapping in code_items

    def test_get_model_for_code_invalid(self, mapping: CGMapping):
        """Test get_model_for_code() with invalid code ID."""
        model_items = mapping._get_model_for_code(999999)
        assert not model_items

    def test_get_mapping_roles(self, mapping: CGMapping):
        """Test get_mapping_roles() functionality."""
        # Find an operator with mappings
        operators = mapping.get_all_operators()
        assert operators

        operator_with_roles = None
        for operator in operators:
            roles = mapping._get_mapping_roles(operator.id)
            if roles:
                operator_with_roles = operator
                break

        assert operator_with_roles

        # Test get_mapping_roles
        roles = mapping._get_mapping_roles(operator_with_roles.id)
        assert isinstance(roles, list)
        assert len(roles) > 0

        for role in roles:
            assert isinstance(role, MappingRole)
            # Verify we can get code items for this role
            code_items = mapping._get_code_for_model(operator_with_roles.id, role)
            assert code_items[0]

    def test_get_mapping_roles_invalid(self, mapping: CGMapping):
        """Test get_mapping_roles() with invalid model ID."""
        roles = mapping._get_mapping_roles(999999)
        assert not roles

    def test_code_element_get_model_element_function(self, mapping: CGMapping):
        """Test get_model_element() specifically for CFunction objects."""
        containers = mapping.get_all_code_containers()

        # Find a CFunction with mappings
        test_function = None
        for container in containers:
            if hasattr(container, "declarations"):
                for declaration in container.declarations:
                    tag, obj = declaration
                    if tag == "function" and isinstance(obj, CFunction):
                        if obj.get_model_element() is not None:
                            test_function = obj
                            break
                if test_function:
                    break

        if not test_function:
            pytest.skip("No CFunction objects with model mappings found")

        # Verify model item properties
        model_item = test_function.get_model_element()
        assert isinstance(model_item, ModelConstant | ModelOperator | ModelMonoOperator)
        assert hasattr(model_item, "id")
        # Test that we can get back to the function
        generated_code = [
            model_item.get_generated_element(),
            model_item.get_elaborated_function()
            if isinstance(model_item, ModelConstant)
            else model_item.get_cycle(),
        ]
        assert test_function in generated_code

    def test_code_element_get_model_element_global(self, mapping: CGMapping):
        """Test get_model_element() specifically for CGlobal objects."""
        containers = mapping.get_all_code_containers()

        # Find a CGlobal with mappings
        test_global = None
        for container in containers:
            if hasattr(container, "declarations"):
                for declaration in container.declarations:
                    tag, obj = declaration
                    if tag == "global" and isinstance(obj, CGlobal):
                        if obj.get_model_element() is not None:
                            test_global = obj
                            break
                if test_global:
                    break

        if not test_global:
            pytest.skip("No CGlobal objects with model mappings found")

        # Verify model item properties
        model_item = test_global.get_model_element()
        assert model_item is not None
        assert hasattr(model_item, "id")

    def test_code_element_get_model_element_struct(self, mapping: CGMapping):
        """Test get_model_element() specifically for CStruct objects."""
        containers = mapping.get_all_code_containers()

        # Find a CStruct with mappings
        test_struct = None
        for container in containers:
            if hasattr(container, "declarations"):
                for declaration in container.declarations:
                    tag, obj = declaration
                    if tag == "struct" and isinstance(obj, CStruct):
                        if obj.get_model_element() is not None:
                            test_struct = obj
                            break
                if test_struct:
                    break

        if not test_struct:
            pytest.skip("No CStruct objects with model mappings found")

        # Verify model item properties
        model_item = test_struct.get_model_element()
        assert model_item is not None
        assert hasattr(model_item, "id")

    def test_code_registry(self, mapping: CGMapping):
        """Test code registry methods"""

        # assert isinstance(mapping._code_registry, CodeRegistry)
        model_registry = mapping._model_registry
        code_registry = mapping._code_registry
        mapping_registry = mapping._mapping_registry

        container = code_registry.get_container_by_interface("non_existent_file.h")
        assert container is None
        container = code_registry.get_container_by_interface("operator1_module0.h")
        assert container is not None
        assert isinstance(container, CodeContainer)

        assert model_registry.items
        model_registry.clear()
        assert not model_registry.items

        assert code_registry.items
        assert code_registry.containers
        code_registry.clear()
        assert not code_registry.items
        assert not code_registry.containers

        assert mapping_registry.mappings
        assert mapping_registry._by_model_id
        assert mapping_registry._by_code_id
        mapping_registry.clear()
        assert not mapping_registry.mappings
        assert not mapping_registry._by_model_id
        assert not mapping_registry._by_code_id

    @pytest.mark.parametrize("CType", [CFunction, CGlobal, CStruct, CParameter, CPredefinedType])
    def test_code_registry_get_by_type(self, CType: type, mapping: CGMapping):
        """Test CodeRegistry.get_by_type() method for different types."""

        code_elements = mapping._code_registry.get_by_type(CType)
        assert len(code_elements) > 0
        for code_element in code_elements:
            assert isinstance(code_element, CType)


class TestCodeTypeBaseMethods:
    """Tests for CodeTypeBase.get_equality_function() and get_equality_use_macro()."""

    @pytest.mark.parametrize("CType", [CArray, CStruct, CUnion])
    def test_get_equality_function_returns_cfunction_or_none(self, CType: type, mapping: CGMapping):
        """Test get_equality_function() returns a CFunction or None for array/struct/union types."""
        code_elements = mapping._code_registry.get_by_type(CType)
        if not code_elements:
            pytest.skip(f"No {CType.__name__} elements found in test data")

        for elem in code_elements:
            assert isinstance(elem, CodeTypeBase)
            result = elem.get_equality_function()
            assert result is None or isinstance(result, CFunction)

    @pytest.mark.parametrize("CType", [CArray, CStruct, CUnion])
    def test_get_equality_use_macro_returns_str_or_none(self, CType: type, mapping: CGMapping):
        """Test get_equality_use_macro() returns a string or None for array/struct/union types."""
        code_elements = mapping._code_registry.get_by_type(CType)
        if not code_elements:
            pytest.skip(f"No {CType.__name__} elements found in test data")

        for elem in code_elements:
            assert isinstance(elem, CodeTypeBase)
            result = elem.get_equality_use_macro()
            assert result is None or isinstance(result, str)

    def test_get_equality_function_consistent_with_equality_field(self, mapping: CGMapping):
        """Test that get_equality_function() is consistent with the equality ID field."""
        for CType in (CArray, CStruct, CUnion):
            for elem in mapping._code_registry.get_by_type(CType):
                fn = elem.get_equality_function()
                if elem.equality is not None:
                    assert fn is not None
                    assert isinstance(fn, CFunction)
                    assert fn.id == elem.equality
                else:
                    assert fn is None

    def test_get_equality_use_macro_consistent_with_equality_use_field(self, mapping: CGMapping):
        """Test that get_equality_use_macro() is consistent with the equality_use field."""
        for CType in (CArray, CStruct, CUnion):
            for elem in mapping._code_registry.get_by_type(CType):
                macro_name = elem.get_equality_use_macro()
                assert macro_name is None or (isinstance(macro_name, str) and "use" in macro_name)

    def test_get_equality_function_raises_without_cgmapping(self):
        """Test get_equality_function() raises ValueError when cgmapping is not set."""
        struct = CStruct(id=1, name="S", fields=[], equality=42)
        with pytest.raises(ValueError, match="No cgmapping set"):
            struct.get_equality_function()

    def test_get_equality_use_macro_no_cgmapping_needed(self):
        """Test get_equality_use_macro() does not require cgmapping."""
        struct = CStruct(id=1, name="S", fields=[], equality_use="MY_EQ_MACRO")
        assert struct.get_equality_use_macro() == "MY_EQ_MACRO"

        array = CArray(id=2, name="A", base_type=0, size=4, equality_use=None)
        assert array.get_equality_use_macro() is None


class TestCGMappingErrorHandling:
    """Tests for error handling and edge cases."""

    def test_deprecated_version(self):
        test_file = Path("tests/models/mapping/jobs/codegen_WrongVersionNumber/out/cg_map.json")
        with pytest.raises(ScadeOneException, match="Version mismatch"):
            CGMapping.from_file(test_file)

    def test_resolve_type_chain(self, mapping: CGMapping):
        """Test resolving complex type chains."""
        # Test with named types that reference other types
        named_types = mapping._model_registry.get_by_type(ModelNamedType)
        if named_types:
            for named_type in named_types:
                # Resolve the definition
                definition = mapping._resolve_type(named_type.definition)
                assert definition is not None

                # If it's another named type, we can resolve further
                if isinstance(definition, ModelNamedType):
                    further_definition = mapping._resolve_type(definition.definition)
                    assert further_definition is not None

        # Test with arrays
        arrays = mapping._model_registry.get_by_type(ModelArray)
        if arrays:
            array = arrays[0]
            base_type = mapping._resolve_type(array.base_type)
            assert base_type is not None

    def test_resolve_type_invalid(self, mapping: CGMapping):
        """Test resolve_type() with invalid type ID."""
        result = mapping._resolve_type(999999)
        assert result is None

    def test_get_code_for_model_invalid_role(self, mapping: CGMapping):
        """Test get_code_for_model() with invalid role string."""
        operators = mapping.get_all_operators()
        if operators:
            operator = operators[0]

            # Test with invalid role string
            result = mapping._get_code_for_model(operator.id, "InvalidRole")
            assert not result

    def test_get_code_for_model_invalid_id(self, mapping: CGMapping):
        """Test get_code_for_model() with invalid model ID."""
        result = mapping._get_code_for_model(999999)
        assert not result

    def test_statistics_consistency(self, mapping: CGMapping):
        """Test that statistics are consistent with actual counts."""
        stats = mapping.get_statistics()

        # Verify operators count
        all_operators = mapping.get_all_operators()
        assert stats["operators"] == len(all_operators)

        # Verify root operators count
        root_operators = mapping.get_root_operators()
        assert stats["root_operators"] == len(root_operators)

        # Verify constants count
        constants = mapping.get_all_constants()
        assert stats["constants"] == len(constants)

        # Verify sensors count
        sensors = mapping.get_all_sensors()
        assert stats["sensors"] == len(sensors)

        # Verify types count
        all_types = mapping.get_all_types()
        assert stats["types"] == len(all_types)

    def test_empty_searches(self, mapping: CGMapping):
        """Test searches that return empty results."""
        # Search for non-existent paths and names
        empty_path_results = mapping.get_model_by_path("NonExistent::Path")
        assert isinstance(empty_path_results, list)
        assert len(empty_path_results) == 0

        empty_name_results = mapping.get_model_by_name("NonExistentName")
        assert isinstance(empty_name_results, list)
        assert len(empty_name_results) == 0

    def test_role_enumeration_coverage(self, mapping: CGMapping):
        """Test that all used mapping roles are valid MappingRole enum values."""
        # Get all operators and their roles
        operators = mapping.get_all_operators()
        all_used_roles = set()

        for operator in operators:
            roles = mapping._get_mapping_roles(operator.id)
            if isinstance(operator, ModelMonoOperator):
                pass
            elif len(roles) > 2:
                assert operator.is_node()
            else:
                assert operator.is_function()
            all_used_roles.update(roles)

        # Verify all roles are valid enum values
        for role in all_used_roles:
            assert isinstance(role, MappingRole)
            assert hasattr(MappingRole, role.name)

    def test_bidirectional_mapping_consistency(self, mapping: CGMapping):
        """Test that mappings are consistent in both directions."""
        # Get a few operators with code mappings
        operators = mapping.get_all_operators()

        for operator in operators:
            code_items = mapping._get_code_for_model(operator.id)

            for code_item in code_items:
                # Reverse lookup should include our original operator
                model_items = mapping._get_model_for_code(code_item.id)
                assert operator in model_items

    def test_type_inheritance_verification(self, mapping: CGMapping):
        """Test that all model items inherit from expected base classes."""
        # Test operators
        operators = mapping.get_all_operators()
        for op in operators:
            assert isinstance(op, (ModelOperator, ModelMonoOperator))
            assert isinstance(op, ModelElement)

        # Test types
        all_types = mapping.get_all_types()
        for t in all_types:
            assert isinstance(t, ModelElement)
            assert isinstance(t, type_classes)


class TestModelOperatorNewMethods:
    """Integration tests for new ModelOperator methods."""

    def test_operator_get_name_integration(self, mapping: CGMapping):
        """Test get_name() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_name method
                name = operator.get_function_name()

                # If name is available, it should be a string
                if name is not None:
                    assert isinstance(name, str)
                    assert len(name) > 0

                # Verify it's consistent with getting the cycle method directly
                cycle_method = operator.get_cycle()
                if cycle_method and hasattr(cycle_method, "name"):
                    assert name == cycle_method.name
                else:
                    assert name is None

    def test_operator_get_header_name_integration(self, mapping: CGMapping):
        """Test get_header_name() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_header_name method
                header = operator.get_header_name()

                # If header is available, it should be a string
                if header is not None:
                    assert isinstance(header, str)
                    assert len(header) > 0
                    # Header files typically have .h extension
                    assert header.endswith(".h")

                # Verify by manually checking containers (since this is a new feature)
                cycle_method = operator.get_cycle()
                if cycle_method:
                    containers = mapping.get_all_code_containers()
                    found_header = None
                    for container in containers:
                        for declaration in container.declarations:
                            if len(declaration) >= 2 and hasattr(declaration[1], "id"):
                                if declaration[1].id == cycle_method.id:
                                    found_header = getattr(container, "interface_file", None)
                                    break
                        if found_header:
                            break
                    assert header == found_header
                else:
                    assert header is None

    def test_operator_get_source_name(self, mapping: CGMapping):
        """Test get_source_name() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            assert False, "No operators found in test data"

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_source_name method
                source = operator.get_source_name()
                if source:
                    # If source is available, it should be a string
                    assert isinstance(source, str)
                    assert len(source) > 0
                    # Source files typically have .c extension
                    assert source.endswith(".c")

    def test_operator_get_context_integration(self, mapping: CGMapping):
        """Test get_context() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_context_type and get_global_context methods
                context_type = operator.get_context_type()
                global_context = operator.get_global_context()

                # Context may or may not be available depending on the operator type
                # Just verify that if something is returned, it's a valid object
                if context_type is not None:
                    assert isinstance(context_type, CStruct | CTypedef)
                if global_context is not None:
                    assert isinstance(global_context, CGlobal)

    def test_operator_get_reset_integration(self, mapping: CGMapping):
        """Test get_reset() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_reset method
                reset = operator.get_reset()

                # If reset is available, it should be a function-like object
                if reset is not None:
                    # Should have an id and typically a name
                    assert hasattr(reset, "id")
                    if hasattr(reset, "name"):
                        assert isinstance(reset.name, str)
                        assert "reset" in reset.name.lower() or "init" in reset.name.lower()

    def test_operator_get_init_integration(self, mapping: CGMapping):
        """Test get_init() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_init method
                init = operator.get_init()

                # If init is available, verify it's a proper function
                if init is not None:
                    assert hasattr(init, "id")
                    if hasattr(init, "name"):
                        assert isinstance(init.name, str)

    def test_operator_get_cycle_integration(self, mapping: CGMapping):
        """Test get_cycle() method with real data."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        for operator in operators:
            if isinstance(operator, ModelOperator):
                # Test get_cycle method
                cycle = operator.get_cycle()

                # If cycle is available, verify it's a proper function
                if cycle is not None:
                    assert hasattr(cycle, "id")
                    if hasattr(cycle, "name"):
                        assert isinstance(cycle.name, str)

    def test_operator_all_methods_together(self, mapping: CGMapping):
        """Test methods of node operator."""
        operators = mapping.get_all_operators()
        if not operators:
            pytest.skip("No operators found in test data")

        # Find an operator with at least one mapped element
        test_operator = None
        for operator in operators:
            if isinstance(operator, ModelOperator):
                assert not operator.get_generated_element()
                if operator.is_node():
                    test_operator = operator
                    break

        if test_operator is None:
            pytest.skip("No node operator found")

        # Test all methods on the same operator
        assert test_operator.get_function_name()
        assert test_operator.get_header_name()
        assert test_operator.get_source_name()
        assert test_operator.get_context_type()
        assert test_operator.get_reset()
        assert test_operator.get_init()
        assert test_operator.get_cycle()

    def test_operator_methods_with_mono_operators(self, mapping: CGMapping):
        """Test that new methods work with monomorphized operators too."""
        # Use public API to get objects with cgmapping properly assigned
        all_operators = mapping.get_all_operators()
        mono_operators = [op for op in all_operators if isinstance(op, ModelMonoOperator)]
        if not mono_operators:
            pytest.skip("No monomorphized operators found in test data")

        # ModelMonoOperator should also inherit these methods from ModelElementMixin
        for mono_op in mono_operators:
            # Test that the methods exist and are callable
            assert hasattr(mono_op, "get_generated_element")

            # Mono operators must have an associated cycle method
            code_item = mono_op.get_generated_element()
            assert code_item is None
            cycle = mono_op.get_cycle()
            assert cycle is None or isinstance(cycle, CFunction)

    def test_get_c_type_and_get_model_type(self, mapping: CGMapping):
        """Test get_c_type() and get_model_type() methods on various model elements."""

        # Test with operator inputs and outputs
        operators = mapping.get_all_operators()
        assert operators, "No operators found in mapping"

        operator_with_ios = None
        for op in operators:
            if len(op.inputs) > 3 and len(op.outputs) > 3:
                operator_with_ios = op
                break
        if not operator_with_ios:
            assert False, "No operator with sufficient inputs and outputs found"

        if operator_with_ios:
            # Test get_c_type and get_model_type on operator inputs
            for input_var in operator_with_ios.inputs:
                c_type = input_var.get_c_type()
                model_type = input_var.get_model_type()

                # Verify return types
                assert c_type
                assert isinstance(c_type, CPredefinedType)

                # Model type can be empty string or None
                assert isinstance(model_type, type_classes)

            # Test get_c_type and get_model_type on operator outputs
            for output_var in operator_with_ios.outputs:
                c_type = output_var.get_c_type()
                model_type = output_var.get_model_type()

                assert c_type

        # Test with sensors
        sensors = mapping.get_all_sensors()
        sensor = sensors[0]
        c_type = sensor.get_c_type()
        model_type = sensor.get_model_type()

        assert c_type is not None
        assert isinstance(model_type, type_classes)

        # Test with constants
        constants = mapping.get_all_constants()
        for constant in constants:
            c_type = constant.get_c_type()
            model_type = constant.get_model_type()

            assert c_type is not None
            assert isinstance(model_type, type_classes)

    def test_probes(self, mapping: CGMapping):
        """Test that probes are correctly assigned."""
        for operator in mapping.get_all_operators():
            expected_flat_probes_number = 0
            for probe in operator.get_probes():
                if isinstance(probe, ModelProbe):
                    expected_flat_probes_number += 1
                    assert probe.path
                    assert probe.projection is None
                    code = probe.get_generated_element()
                    assert isinstance(code, CStructField)
                    model = code.get_model_element()
                    assert model is probe
                elif isinstance(probe, ModelProbesGroup):
                    assert probe.path
                    assert probe.kind
                    code = probe.get_generated_element()
                    assert code is None
                    codes = probe.get_generated_group_elements()
                    number_of_projections = len(probe.projections)
                    assert len(codes) == number_of_projections
                    expected_flat_probes_number += number_of_projections
                    for code in codes:
                        assert isinstance(code, CParameter | CStructField)
                        model = code.get_model_element()
                        assert model in probe.projections
                else:
                    assert False, f"Unknown probe type: {type(probe)}"
            assert expected_flat_probes_number == len(operator.get_flat_probes())


class TestModelGroupMethods:
    """Tests for ModelGroup and ModelGroupProjection methods."""

    @staticmethod
    def _find_group(mapping: CGMapping) -> ModelGroup | None:
        """Find a group from operator inputs/outputs if present in mapping data."""
        for operator in mapping.get_all_operators():
            for item in [*operator.inputs, *operator.outputs]:
                if isinstance(item, ModelGroup):
                    return item
        return None

    def test_group_methods_return_none_and_log_warning(self, mapping: CGMapping, caplog):
        """Test group methods returning direct type/code element produce warnings and None."""
        group = self._find_group(mapping)
        if group is None:
            pytest.skip("No ModelGroup found in test data")

        with caplog.at_level(logging.WARNING, logger="PyScadeOne"):
            assert group.get_c_type() is None
            assert group.get_model_type() is None
            assert group.get_generated_element() is None
            assert group.get_group_projection([99, "nonexistent"]) is None

        messages = [record.message for record in caplog.records]
        assert any("direct C type representation" in msg for msg in messages)
        assert any("direct model type representation" in msg for msg in messages)
        assert any("not applicable for ModelGroups" in msg for msg in messages)

    def test_group_projections_and_generated_group_elements(self, mapping: CGMapping):
        """Test projections structure and generated elements aggregation on groups."""
        group = self._find_group(mapping)
        if group is None:
            pytest.skip("No ModelGroup found in test data")

        assert group.projections
        expected_elements = []
        for projection in group.projections:
            assert isinstance(projection, ModelGroupProjection)
            element = projection.get_generated_element()
            if element is not None:
                expected_elements.append(element)
            variable = mapping._get_model_by_id(projection.id)
            assert variable.projection is not None
            assert projection == group.get_group_projection(variable.projection)

        assert group.get_generated_group_elements() == expected_elements

    def test_group_generated_group_elements_requires_cgmapping(self):
        """Test get_generated_group_elements raises without cgmapping."""
        group = ModelVariablesGroup(name="g")
        with pytest.raises(ValueError, match="No cgmapping set"):
            group.get_generated_group_elements()

    def test_flat_inputs(self, mapping: CGMapping):
        """Check that flat inputs correctly returns each group element."""
        for operator in mapping.get_all_operators():
            for item in operator.inputs:
                if isinstance(item, ModelGroup):
                    flat_projections = []
                    for flat_input in operator.get_flat_inputs():
                        if flat_input.projection:
                            flat_projections.append(flat_input.projection)
                    group_projections = [
                        proj.projection
                        for proj in item.projections
                        if proj.get_generated_element() is not None
                    ]
                    assert len(flat_projections) == len(group_projections)
                    assert flat_projections == group_projections
                    return
        assert False, "No ModelGroup with projections found in test data"


class TestModelParsers:
    """Tests for standalone model parsing helpers."""

    def test_parse_c_declaration(self):
        """Test parse_c_declaration() with a function declaration."""
        data = (
            "function",
            {
                "id": 30,
                "name": "f_cycle",
                "return_type": 1,
                "parameters": [{"id": 31, "name": "arg", "type": 2}],
            },
        )

        decl_type, decl_obj = parse_c_declaration(data)

        assert decl_type == "function"
        assert isinstance(decl_obj, CFunction)
        assert decl_obj.id == 30
        assert decl_obj.name == "f_cycle"
        assert decl_obj.return_type == 1
        assert len(decl_obj.parameters) == 1
        assert decl_obj.parameters[0].name == "arg"

    def test_parse_probe(self):
        """Test parse_probe() with minimal valid input."""
        data = {"id": 10, "path": "MyOp::p", "kind": "Input", "projection": [0, "field"]}

        probe = parse_probe(data)

        assert probe.id == 10
        assert probe.path == "MyOp::p"
        assert probe.kind == ProbeKind.INPUT
        assert probe.projection == [0, "field"]

    def test_parse_model_size_parameter(self):
        """Test parse_model_size_parameter() with minimal valid input."""
        data = {"id": 20, "name": "N", "value": 64}

        size_parameter = parse_model_size_parameter(data)

        assert size_parameter.id == 20
        assert size_parameter.name == "N"
        assert size_parameter.value == 64

    def test_parse_model_instance(self):
        """Test parse_model_instance() with an operator instance."""
        data = (
            "operator",
            {
                "id": 40,
                "path": "MyOp::inst",
                "operator": 41,
                "probes": [{"id": 42, "path": "MyOp::inst::p", "kind": "Output"}],
                "instances": [],
            },
        )

        instance_type, instance_obj = parse_model_instance(data)

        assert instance_type == "operator"
        assert instance_obj.id == 40
        assert instance_obj.path == "MyOp::inst"
        assert instance_obj.operator == 41
        assert len(instance_obj.probes) == 1
        assert instance_obj.probes[0].kind == ProbeKind.OUTPUT

        data = (
            "loop",
            {
                "id": 43,
                "path": "MyOp::loop",
                "bound": 12,
                "kind": "Iterator",
                "partial": True,
                "probes": [{"id": 44, "path": "MyOp::loop::p", "kind": "Local"}],
                "instances": [],
            },
        )

        instance_type, instance_obj = parse_model_instance(data)

        assert instance_type == "loop"
        assert instance_obj.id == 43
        assert instance_obj.path == "MyOp::loop"
        assert instance_obj.bound == 12
        assert instance_obj.kind == LoopKind.ITERATOR
        assert instance_obj.partial is True
        assert len(instance_obj.probes) == 1
        assert instance_obj.probes[0].kind == ProbeKind.LOCAL

    def test_load_model_from_json(self):
        """Test load_model_from_json() registers declaration and nested items."""
        model_data = [
            (
                "operator",
                {
                    "id": 50,
                    "path": "M::Op",
                    "inputs": [{"id": 51, "name": "in0"}],
                    "outputs": [{"id": 52, "name": "out0"}],
                    "probes": [{"id": 53, "path": "M::Op::p", "kind": "Input"}],
                    "instances": [],
                },
            )
        ]

        registry = load_model_from_json(model_data)

        assert isinstance(registry.get(50), ModelOperator)
        assert isinstance(registry.get(51), ModelVariable)
        assert isinstance(registry.get(52), ModelVariable)
        assert isinstance(registry.get(53), ModelProbe)
        assert registry.get(54) is None


class TestHardCodedData:
    """Tests on specific hard-coded data in given cg_map.json.
    Must be updated according to any modifications in the used cg_map.json file."""

    def test_main(self, mapping: CGMapping):
        """Test various methods."""

        stats = mapping.get_statistics()
        assert stats["version"] == FormatVersions.version("cgmap")
        assert stats["model_items"] == 112
        assert stats["code_items"] == 220
        assert stats["code_containers"] == 12
        assert stats["mappings"] == 120
        assert stats["operators"] == 8
        assert stats["root_operators"] == 4
        assert stats["constants"] == 2
        assert stats["sensors"] == 1
        assert stats["types"] == 29

        operator = mapping.get_model_by_path("module0::function0")[0]
        assert isinstance(operator, ModelOperator)
        assert operator.is_function()
        assert not operator.get_reset()
        assert not operator.get_context_type()
        assert not operator.get_global_obs_struct()

        for input in operator.inputs:
            if isinstance(input, ModelGroup):
                assert input.get_group_projection(["group1"]) is None
                assert input.get_group_projection(["y"]) is None
                assert (input_projection := input.get_group_projection(["group1", "y"])) is not None
                code = input_projection.get_generated_element()
                assert isinstance(code, CParameter)
                assert code.name == "g6_iGroup"
                break
        else:
            assert False

        operator = mapping.get_model_by_path("module0::node0")[0]
        assert isinstance(operator, ModelOperator)
        assert operator.is_node()

        reset_function = operator.get_reset()
        init_function = operator.get_init()
        cycle_function = operator.get_cycle()
        assert isinstance(reset_function, CFunction)
        assert isinstance(init_function, CFunction)
        assert isinstance(cycle_function, CFunction)
        assert reset_function.name == "node0_reset_module0"
        assert init_function.name == "node0_init_module0"
        assert cycle_function.name == "node0_module0"

        context_type = operator.get_context_type()
        assert isinstance(context_type, CTypedef)
        assert context_type.name == "outC_node0_module0"
        # assert len(context_type.fields) == 2

        obs_struct_type = operator.get_obs_struct_type()
        assert isinstance(obs_struct_type, CTypedef)
        assert obs_struct_type.name == "obsS_node0_module0"
        # assert len(obs_struct_type.fields) == 4
        # TODO implement method to get CStruct from CTypedef and uncomment
        # these unitests for the CStruct

        assert operator.get_source_name() == "node0_module0.c"
        assert operator.get_header_name() == "node0_module0.h"
        probes = operator.get_probes()
        assert len(probes) == 4

        probe = probes[0]
        assert isinstance(probe, ModelProbe)
        assert probe.kind is ProbeKind.INPUT
        assert probe.path == "i0"
        assert probe.projection is None
        code = probe.get_generated_element()
        assert isinstance(code, CStructField)
        assert code.name == "i0"
        model = code.get_model_element()
        assert model is probe

        # ID of the probe is the same as the ID of the input variable
        input = mapping._get_model_by_id(probe.id)
        assert isinstance(input, ModelVariable)
        assert input.get_associated_probe() is probe
        # test that the associations are correctly done for input and not probe
        code = input.get_generated_element()
        assert isinstance(code, CParameter)
        model = code.get_model_element()
        assert model is input

        probe = probes[1]
        assert isinstance(probe, ModelProbe)
        assert probe.kind is ProbeKind.LOCAL
        assert probe.path == "x0"
        assert probe.projection is None
        code = probe.get_generated_element()
        assert isinstance(code, CStructField)
        assert code.name == "x0"
        model = code.get_model_element()
        assert model is probe

        # case for group probe: variables have the same IDs as their probes
        probe = probes[2]
        assert isinstance(probe, ModelProbesGroup)
        assert probe.kind is ProbeKind.OUTPUT
        assert probe.path == "o2"
        # groups must use "generated_group_element"
        code = probe.get_generated_element()
        assert code is None
        codes = probe.get_generated_group_elements()
        assert len(codes) == 2
        for code in codes:
            assert isinstance(code, CStructField)
            assert "_o2" in code.name
        output = operator.outputs[2]
        assert isinstance(output, ModelVariablesGroup)
        for projection in output.projections:
            assert isinstance(projection, ModelGroupVariableProjection)
            # probe use the same ID, so need this method to get the probe
            projection_probe = projection.get_associated_probe()
            assert projection_probe in probe.projections
            assert projection.id == projection_probe.id
            code_output = projection.get_generated_element()
            code_probe = projection_probe.get_generated_element()
            # probe must be included in "get_generated_group_elements" but not output
            assert code_output not in codes
            assert code_probe in codes
            # probe is associated to structure field, output to parameter
            assert isinstance(code_output, CParameter)
            assert isinstance(code_probe, CStructField)
            # reverse mapping should map the right item, despite using a same ID
            model_output = code_output.get_model_element()
            model_probe = code_probe.get_model_element()
            assert model_output is projection
            assert model_probe is projection_probe

        probe = probes[3]
        assert isinstance(probe, ModelProbesGroup)
        assert probe.path == "x1"
        assert probe.kind is ProbeKind.LOCAL

        assert probe.get_group_projection([2]) is not None
        assert probe.get_group_projection([3]) is None
        code = probe.get_generated_element()
        assert code is None
        codes = probe.get_generated_group_elements()
        assert len(codes) == 2
        for code in codes:
            assert isinstance(code, CStructField)
            assert "_x1" in code.name

        result = mapping.get_model_by_path("module0::sensor0")
        assert len(result) == 1
        assert isinstance(result[0], ModelSensor)
        code = result[0].get_generated_element()
        assert isinstance(code, CGlobal)

        result = mapping.get_model_by_path("module0::C1")
        assert len(result) == 1
        assert isinstance(result[0], ModelConstant)
        code = result[0].get_generated_element()
        assert isinstance(code, CGlobal)
        assert code.name == "C1_module0"

        code = result[0].get_generated_element()
        assert isinstance(code, CGlobal)
        assert code.name == "C1_module0"
        assert result[0].is_elaborated()
        elab = result[0].get_elaborated_function()
        assert elab is not None
        assert isinstance(elab, CFunction)

        result = mapping.get_model_by_path("module0::C2")
        assert isinstance(result[0], ModelConstant)
        code = result[0].get_generated_element()
        assert isinstance(code, CGlobal)
        assert code.name == "C2_module0"
        assert not result[0].is_elaborated()
        elab = result[0].get_elaborated_function()
        assert elab is None

        result = mapping.get_model_by_path("module0::array0")
        assert len(result) == 1
        assert isinstance(result[0], ModelNamedType)
        code = result[0].get_generated_element()
        assert isinstance(code, CArray)
        assert code.name == "array0_module0"
        assert code.get_equality_use_macro() == "swan_use_array0_module0"
        equality_function = code.get_equality_function()
        function_name = code.get_copy_function_name()
        use_macro = code.get_equality_use_macro()
        assert isinstance(equality_function, CFunction)
        assert equality_function.name == "swan_eq_array0_module0"
        assert function_name == "swan_cp_array0_module0"
        assert use_macro == "swan_use_array0_module0"

        result = mapping.get_model_by_path("module0::GREEN")
        assert len(result) == 1
        assert isinstance(result[0], ModelEnumValue)
        code = result[0].get_generated_element()
        assert isinstance(code, CEnumValue)

        named_type = mapping.get_model_by_path("module0::array1")[0]
        assert mapping.get_model_by_name("array1")[0] is named_type
        assert isinstance(named_type, ModelNamedType)
        array = named_type.get_model_type()
        assert isinstance(array, ModelArray)
        shape = array.get_shape()
        assert shape == [4, 2, 3]
        code = named_type.get_generated_element()
        assert isinstance(code, CArray)
        # TODO should we be able to access generated code from the ModelArray rather than NamedType?

        mono_op = mapping.get_model_by_path("module0::genericSquare[N0=2][T0=int32]")[0]
        assert isinstance(mono_op, ModelMonoOperator)
        type_param = mono_op.type_parameters[0]
        assert isinstance(type_param, ModelTypeParameter)
        code = type_param.get_generated_element()
        assert code is None
        size_param = mono_op.size_parameters[0]
        assert isinstance(size_param, ModelSizeParameter)
        code = size_param.get_generated_element()
        assert code is None

        output = mono_op.outputs[0]
        probe = output.get_associated_probe()
        assert isinstance(probe, ModelProbe)
        probe_code = probe.get_generated_element()
        assert isinstance(probe_code, CStructField)
        assert probe_code.get_model_element() is probe


if __name__ == "__main__":
    pytest.main([__file__])
