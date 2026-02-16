# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

import argparse
import random
import traceback

import pytest
from ansys.scadeone.core.common.exception import ScadeOneException
from test_common import *  # noqa
from os import remove
import sys

import ansys.scadeone.core.svc.simdata as sd
from test_sd_common import create_test_file


def test_create_reopen_dump(file_path: str = "test_create_reopen_dump.sd", nb_cycles: int = 10):
    # create .sd file:
    create_test_file(file_path, nb_cycles)

    # reopen .sd file and print it:
    f = sd.open_file(file_path)
    print(f)
    f.close()

    # Call dumper to check file content
    # if platform.system() == 'Windows':
    #    subprocess.call(['..\\x64\\Debug\\s1sd_dump.exe', file_path])

    remove(file_path)


def test_element_update():
    file_path: str = "test_element_update.sd"

    # create .sd file:
    create_test_file(file_path)

    # reopen .sd file and modify element (name, type, kind):
    f = sd.edit_file(file_path)
    # check initial content
    e_char = f.find_element("eChar")
    assert e_char
    assert e_char.sd_type == sd.Char
    assert e_char.kind == sd.ElementKind.NONE
    assert e_char.group_expr == ""
    assert any(e_char.read_values())
    # update element
    e_char.name = "eCharRenamed"
    e_char.sd_type = sd.Int32
    e_char.kind = sd.ElementKind.PROBE
    e_char.group_expr = "(int32, dummy:bool)"
    # check updates in memory (data is erased when modifying element type)
    assert e_char.name == "eCharRenamed"
    assert e_char.sd_type == sd.Int32
    assert e_char.kind == sd.ElementKind.PROBE
    assert e_char.group_expr == "(int32, dummy:bool)"
    assert not any(e_char.read_values())
    f.close()

    # check updates in file:
    f2 = sd.open_file(file_path)
    e_char = f2.find_element("eCharRenamed")
    assert e_char
    assert e_char.sd_type == sd.Int32
    assert e_char.kind == sd.ElementKind.PROBE
    assert e_char.group_expr == "(int32, dummy:bool)"
    assert not any(e_char.read_values())
    f2.close()

    remove(file_path)


def test_element_remove():
    file_path: str = "test_element_remove.sd"

    # create .sd file:
    create_test_file(file_path)

    # reopen .sd file:
    f = sd.edit_file(file_path)
    # check initial content
    e_char = f.find_element("eChar")
    assert e_char
    e_a = f.find_element("A")
    e_a_b = e_a.find_child_element("b")
    assert e_a_b
    # remove elements
    f.remove_element(e_char)
    e_a.remove_child_element(e_a_b)
    # check updates in memory
    assert not f.find_element("eChar")
    assert not e_a.find_child_element("b")
    f.close()

    # check updates in file:
    f2 = sd.open_file(file_path)
    assert not f2.find_element("eChar")
    e_a = f.find_element("A")
    assert not e_a.find_child_element("b")
    f2.close()

    remove(file_path)


def test_element_clear_values():
    file_path: str = "test_element_clear_values.sd"

    # create .sd file:
    create_test_file(file_path)

    # reopen .sd file:
    f = sd.edit_file(file_path)
    # check initial content
    e_char = f.find_element("eChar")
    assert any(e_char.read_values())
    # clear element values
    e_char.clear_values()
    # check updates in memory
    assert not any(e_char.read_values())
    f.close()

    # check updates in file:
    f2 = sd.open_file(file_path)
    e_char = f2.find_element("eChar")
    assert not any(e_char.read_values())
    f2.close()

    remove(file_path)


def test_sequence_append_value():
    file_path: str = "test_sequence_append_value.sd"

    # create .sd file:
    create_test_file(file_path)

    # reopen .sd file and modify element (name, type, kind):
    f = sd.edit_file(file_path)

    # append value to element
    e_sequences = f.find_element("eSequences")
    assert e_sequences
    e_sequences.append_values_sequence([6, 7])
    e_sequences.append_value(2017)
    e_sequences.append_values_sequence([4, 5], 2)
    e_sequences.append_value(2023)
    f.close()

    # check updates in file:
    f2 = sd.open_file(file_path)
    e_seq = f2.find_element("eSequences")
    assert e_seq
    assert not e_seq.find_child_element("2017")
    assert not e_seq.find_child_element("2023")
    f2.close()

    remove(file_path)


def test_append_value_none_sequence():
    file_path: str = "test_append_value_none_sequence.sd"

    # create an empty .sd file:
    f = sd.create_file(file_path)
    f.close()
    # append value to non-existing sequence:
    f1 = sd.edit_file(file_path)
    e_sequences = f1.add_element("eSequences", sd.Float32)
    e_sequences.append_value(2503)
    f1.close()
    # check updates in file:
    f2 = sd.open_file(file_path)
    e_seq = f2.find_element("eSequences")
    assert e_seq
    assert not e_seq.find_child_element("2503")
    f2.close()

    remove(file_path)


def test_append_wrong_values():
    file_path: str = "test_append_wrong_values.sd"

    # create an empty .sd file:
    f = sd.create_file(file_path)

    oInt8 = f.add_element("O_Int8", sd.Int8, sd.ElementKind.WIRE)
    oInt8.append_value(-128)
    with pytest.raises(ScadeOneException):
        oInt8.append_value(150)  # exceeds maximum value 127 of int8
    with pytest.raises(ScadeOneException):
        oInt8.append_values_sequence([-128, 0, 151])  # same in sequence
    oUint8 = f.add_element("O_Uint8", sd.UInt8, sd.ElementKind.SIGNAL)
    oUint8.append_value(255)
    with pytest.raises(ScadeOneException):
        oUint8.append_value(-3)  # negative value for unsigned int8
    with pytest.raises(ScadeOneException):
        oUint8.append_values_sequence([0, -2, 250])  # same in sequence
    with pytest.raises(ScadeOneException):
        oUint8.append_value(3.14)  # float value for unsigned int8
    with pytest.raises(ScadeOneException):
        oInt8.append_value("C")  # char value for int8
    with pytest.raises(ScadeOneException):
        oUint8.append_value("RED")  # string value for unsigned int8
    S1 = sd.create_struct_type([("f1", sd.UInt8), ("f2", sd.UInt16)], "TestsOfValues::S1")
    oStruct1 = f.add_element("O_Struct1", S1, sd.ElementKind.BRANCH)
    sv1 = (1, 10.1)
    sv2 = (2, 200)
    sv3 = (3, 300)
    with pytest.raises(ScadeOneException):
        oStruct1.append_values_sequence([sv1, sv2, sv3])  # float value for int8 field
    union = sd.create_variant_type(
        [("Either1", None), ("Either2", sd.Float32), ("Either3", sd.Bool)], "TestsOfValues::union"
    )
    oUnion = f.add_element("O_Union", union, sd.ElementKind.NONE)
    vu1 = ("Either2", False)
    vu2 = "Either1"
    vu3 = ("Either3", True)
    with pytest.raises(ScadeOneException):
        oUnion.append_values_sequence([vu1, vu2, vu3])  # boolean value for float32 field
    with pytest.raises(ScadeOneException):
        oInt8.append_values_sequence([3], 5.5)  # repeat factor must be an integer
    f.close()

    remove(file_path)


def test_append_values_with_repeat_factor():
    file_path: str = "test_append_values_with_repeat_factor.sd"

    # create an empty .sd file:
    f = sd.create_file(file_path)
    # Create a sequence element
    e_sequences = f.add_element("testSequences", sd.Int32, sd.ElementKind.NONE)

    # Test repeat factor = 1 (default behavior)
    e_sequences.append_values_sequence([10, 20, 30], 1)

    # Test repeat factor = 3 (should repeat the sequence 3 times)
    e_sequences.append_values_sequence([100, 200], 3)

    # Test that repeat factor = 0 raises an exception
    with pytest.raises(ScadeOneException):
        e_sequences.append_values_sequence([999], 0)  # invalid repeat factor

    f.close()

    # Verify the values were added correctly
    f2 = sd.open_file(file_path)
    e_seq = f2.find_element("testSequences")
    assert e_seq

    # Check that values exist (following pattern from other tests)
    assert any(e_seq.read_values())

    # Count the number of values to verify repeat factor worked
    values_list = list(e_seq.read_values())
    # Should have 3 values from first call + 6 values from second call (2 values * 3 repeats)
    assert len(values_list) == 9

    f2.close()
    remove(file_path)


def test_group():
    file_path: str = "test_group.sd"

    # create .sd file:
    create_test_file(file_path)

    # reopen .sd file:
    f = sd.edit_file(file_path)

    # check content
    e_group = f.find_element("iGroup1")
    assert e_group.group_expr == "m1::group1"
    assert not any(e_group.read_values())
    e_children = e_group.children_elements
    assert len(e_children) == 3
    for child in e_children:
        assert child.kind == sd.ElementKind.GROUP_ITEM
        assert any(child.read_values())
    f.close()

    remove(file_path)


def test_big_array():
    def RandUInt64():
        return random.randint(0, 0xFFFFFFFFFFFFFFFF)

    file_path: str = "test_big_array.sd"
    t = sd.create_array_type(sd.UInt64, [300])
    f = sd.create_file(file_path)
    i0 = f.add_element("i0", t)
    vals = []
    for i in range(10000):
        val = []
        for j in range(300):
            val.append(RandUInt64())
        vals.append(val)
    i0.append_values_sequence(vals, 1)

    print(f)  # checks that this doesn't raise a Windows error
    f.close()
    remove(file_path)


if __name__ == "__main__":
    desc = """
    Generate simulation data file using simdata module (HL API)
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-o", "--out_sd_path", type=str, help="Path to output .sd file")
    parser.add_argument("-n", "--nb_cycles", type=int, help="Number of cycles to generate")
    args = parser.parse_args()

    try:
        test_create_reopen_dump(args.out_sd_path, args.nb_cycles)
    except Exception as e:
        print("Error: " + str(e))
        traceback.print_exc()
        sys.exit(2)

    sys.exit(0)
