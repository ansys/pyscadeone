# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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
import traceback
from test_common import *  # noqa
from os import remove

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
    f = sd.open_file(file_path)
    # check initial content
    e_char = f.find_element("eChar")
    assert e_char
    assert e_char.sd_type == sd.Char
    assert e_char.kind == sd.ElementKind.NONE
    assert any(e_char.read_values())
    # update element
    e_char.name = "eCharRenamed"
    e_char.sd_type = sd.Int32
    e_char.kind = sd.ElementKind.PROBE
    # check updates in memory (data is erased when modifying element type)
    assert e_char.name == "eCharRenamed"
    assert e_char.sd_type == sd.Int32
    assert e_char.kind == sd.ElementKind.PROBE
    assert not any(e_char.read_values())
    f.close()

    # check updates in file:
    f2 = sd.open_file(file_path)
    e_char = f2.find_element("eCharRenamed")
    assert e_char
    assert e_char.sd_type == sd.Int32
    assert e_char.kind == sd.ElementKind.PROBE
    assert not any(e_char.read_values())
    f2.close()

    remove(file_path)


def test_element_remove():
    file_path: str = "test_element_remove.sd"

    # create .sd file:
    create_test_file(file_path)

    # reopen .sd file:
    f = sd.open_file(file_path)
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
    f = sd.open_file(file_path)
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
