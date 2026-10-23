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

"""Example demonstrating CGMapping API functionality.

This script shows how to use the CGMapping classes
to explore and query the relationship between model elements and their
generated C code counterparts.
"""

from pathlib import Path
from ansys.scadeone.core.common.logger import LOGGER, LoggerLevel
from ansys.scadeone.core.svc.cgmapping import (
    CGMapping,
    ModelMonoOperator,
    ModelPredefinedType,
    ModelNamedType,
    ModelArray,
    ModelGroup,
)


def demonstrate_model_element_usage():
    # Load a test mapping file from its path
    test_file = Path("cg_map.json")

    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return

    # Load the mapping
    mapping = CGMapping.from_file(test_file)
    print(f"Mapping loaded - version: {mapping.version}")

    # Root operators
    root_ops = mapping.get_root_operators()
    print(f"\nFound {len(root_ops)} root operators:")
    for op in root_ops:
        print(f"  Root operator: {op.path}")

    # Print statistics
    stats = mapping.get_statistics()
    print(f"\nTotal model items: {stats['model_items']}")
    print(f"Total code items: {stats['code_items']}")
    print(f"Total mappings: {stats['mappings']}")

    # Demonstration with operators
    print("\n=== Operators ===")
    operators = mapping.get_all_operators()
    print(f"Number of operators found: {len(operators)}")

    for operator in operators:
        print(f"\nOperator: {operator.path}")

        # Skip mono operators for this demo as they have different characteristics
        if isinstance(operator, ModelMonoOperator):
            print(f"  Mono operator - Source : {operator.get_src_operator().path}")
            continue

        # Display operator inputs
        print(f"  Inputs ({len(operator.inputs)}):")
        for input in operator.inputs:
            if isinstance(input, ModelGroup):
                print(f"    - {input.name} (Group):")
                for projection in input.projections:
                    generated_code = projection.get_generated_element()
                    c_type = projection.get_c_type()
                    model_type = projection.get_model_type()
                    type_name = c_type.name if c_type else "unknown"
                    model_type_name = "unknown"
                    if model_type:
                        if isinstance(model_type, ModelPredefinedType):
                            model_type_name = model_type.name
                        elif isinstance(model_type, (ModelNamedType, ModelArray)):
                            model_type_name = model_type.path
                    print(
                        f"      - Proj {projection.projection} : {generated_code.name}: C Type = {type_name}, Model Type = {model_type_name}"
                    )
            else:
                generated_code = input.get_generated_element()
                c_type = input.get_c_type()
                model_type = input.get_model_type()
                type_name = c_type.name if c_type else "unknown"
                model_type_name = "unknown"
                if model_type:
                    if isinstance(model_type, ModelPredefinedType):
                        model_type_name = model_type.name
                    elif isinstance(model_type, (ModelNamedType, ModelArray)):
                        model_type_name = model_type.path
                print(f"    - {input.name}: C Type = {type_name}, Model Type = {model_type_name}")

        # Specialized methods for operators
        cycle_method = operator.get_cycle()
        print(f"  Cycle method: {cycle_method.name if cycle_method else 'none'}")

        init_method = operator.get_init()
        print(f"  Init method: {init_method.name if init_method else 'none'}")

        reset_method = operator.get_reset()
        print(f"  Reset method: {reset_method.name if reset_method else 'none'}")

        monos = operator.get_mono_operators()
        if monos:
            print(f"  Mono operators: {len(monos)}")
            for mono in monos:
                print(f"    - {mono.path}")

    # Demonstration with constants
    print("\n=== Constants ===")
    constants = mapping.get_all_constants()
    print(f"Number of constants found: {len(constants)}")

    for i, constant in enumerate(constants, 1):
        print(f"\n{i}. Constant: {constant.path}")
        code_item = constant.get_generated_element()
        if code_item:
            print(f"   Generated code element: {type(code_item).__name__} (ID: {code_item.id})")
            print(f"     Name: {code_item.name}")
        else:
            print("   No generated code element")

    # Demonstration with sensors
    print("\n=== Sensors ===")
    sensors = mapping.get_all_sensors()
    print(f"Number of sensors found: {len(sensors)}")

    for i, sensor in enumerate(sensors, 1):
        print(f"\n{i}. Sensor: {sensor.path}")
        code_item = sensor.get_generated_element()
        if code_item:
            print(f"   Generated code element: {type(code_item).__name__} (ID: {code_item.id})")
            print(f"     Name: {code_item.name}")
        else:
            print("   No generated code element")

    # Demonstration with types
    print("\n=== Types ===")
    types = mapping.get_all_types()
    print(f"Number of types found: {len(types)}")

    # Group types by category for better presentation
    predefined_types = [t for t in types if isinstance(t, ModelPredefinedType)]
    named_types = [t for t in types if isinstance(t, ModelNamedType)]
    other_types = [t for t in types if not isinstance(t, (ModelPredefinedType, ModelNamedType))]

    print(f"\nPredefined types: {len(predefined_types)}")
    for i, type_elem in enumerate(predefined_types, 1):
        type_name = type_elem.name
        print(f"  {i}. {type(type_elem).__name__} - {type_name}")
        code_item = type_elem.get_generated_element()
        if code_item:
            print(f"     -> {type(code_item).__name__} : {code_item.name}")

    print(f"\nNamed types: {len(named_types)}")
    for i, type_elem in enumerate(named_types, 1):
        type_name = type_elem.path
        print(f"  {i}. {type(type_elem).__name__} - {type_name}")
        code_item = type_elem.get_generated_element()
        if code_item:
            print(f"     -> {type(code_item).__name__} : {code_item.name}")

    if other_types:
        print(f"\nOther types: {len(other_types)}")
        for i, type_elem in enumerate(other_types, 1):
            type_ID = type_elem.id
            print(f"  {i}. {type(type_elem).__name__} - ID {type_ID}")
            code_item = type_elem.get_generated_element()
            if code_item:
                print(f"     -> {type(code_item).__name__} : {code_item.name}")
            else:
                print("     (No generated code element)")


if __name__ == "__main__":
    log_dir = Path.cwd() / "logs"
    LOGGER.log_to_file(folder_path=log_dir, level=LoggerLevel.DEBUG)

    print("Demonstration of CG mapping API.")
    print("=" * 60)
    demonstrate_model_element_usage()
    print("\n" + "=" * 60)
    print("Demonstration completed.")
    print(f"LOGGER output file: {log_dir / 'pyscadeone.log'}")
