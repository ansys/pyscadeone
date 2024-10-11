#
# Copyright (c) 2022-2025 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

import ansys.scadeone.core.svc.simdata as sd
from test_common import *  # noqa.

try:
    import numpy as np

    imported_numpy = True
except:
    imported_numpy = False


def create_test_file(file_path: str, nb_cycles: int = 10):
    # create data types:
    t_struct1 = sd.create_struct_type([("f1", sd.Bool), ("f2", sd.Int32)], "p1::tStruct1")
    t_array1 = sd.create_array_type(sd.Int32, [3, 4], "p1::tArray1")
    t_array2 = sd.create_array_type(t_struct1, [2, 3], "p1::tArray2")
    t_enum1 = sd.create_enum_type(["RED", "GREEN", "BLUE"], "p1::tEnum1")
    t_variant1 = sd.create_variant_type([("c1", sd.Bool), ("c2", None)], "p1::tVariant1")
    t_variant2 = sd.create_variant_type([("c3", None), ("c4", t_struct1)], "p1::tVariant2")
    t_imported1 = sd.create_imported_type(ctypes.sizeof(Imported), "p1::tImported1")
    t_imported2 = sd.create_vsize_imported_type(
        ctypes.sizeof(VSizeImported),
        vsize_imported_get_bytes_size,
        vsize_imported_to_bytes,
        "p1::tImported2",
    )

    # create file:
    f = sd.create_file(file_path)

    # add elements:
    e_char = f.add_element("eChar", sd.Char)
    e_bool = f.add_element("eBool", sd.Bool)
    e_int8 = f.add_element("eInt8", sd.Int8)
    e_int16 = f.add_element("eInt16", sd.Int16)
    e_int32 = f.add_element("eInt32", sd.Int32)
    e_int64 = f.add_element("eInt64", sd.Int64)
    e_uint8 = f.add_element("eUInt8", sd.UInt8)
    e_uint16 = f.add_element("eUInt16", sd.UInt16)
    e_uint32 = f.add_element("eUInt32", sd.UInt32)
    e_uint64 = f.add_element("eUInt64", sd.UInt64)
    e_float32 = f.add_element("eFloat32", sd.Float32)
    e_float64 = f.add_element("eFloat64", sd.Float64)
    e_struct1 = f.add_element("eStruct1", t_struct1)
    e_array1 = f.add_element("eArray1", t_array1)
    e_array2 = f.add_element("eArray2", t_array2)
    e_enum1 = f.add_element("eEnum1", t_enum1)
    e_variant1 = f.add_element("eVariant1", t_variant1)
    e_variant2 = f.add_element("eVariant2", t_variant2)
    e_imported1 = f.add_element("eImported1", t_imported1)
    e_imported2 = f.add_element("eImported2", t_imported2)
    e_sequences = f.add_element("eSequences", sd.Float32)

    e_a = f.add_element("A", None, sd.ElementKind.OPERATOR)
    e_a.add_child_element("b", None, sd.ElementKind.PROBE)
    e_c = f.add_element("C")
    e_d = e_c.add_child_element("D")
    e_d.add_child_element("e")
    e_d.add_child_element("f")
    e_c.add_child_element("g")

    # append values to elements:
    clock3 = False
    v_enum = "RED"
    v_variant1 = ("c1", True)
    v_variant2 = "c3"
    v_imported2 = VSizeImported("tny")
    for i in range(0, nb_cycles):
        mod = i % 3
        if mod == 0:
            clock3 = not clock3
            v_enum = "RED"
            v_variant1 = ("c1", True)
            v_variant2 = "c3"
            v_imported2 = VSizeImported("tny")
        elif mod == 1:
            v_enum = "GREEN"
            v_variant1 = ("c1", False)
            v_variant2 = ("c4", [True, i + 19])
            v_imported2 = VSizeImported("short")
        elif mod == 2:
            v_enum = "BLUE"
            v_variant1 = "c2"
            v_variant2 = ("c4", [False, i + 19])
            v_imported2 = VSizeImported("very long")
        e_char.append_value(chr(ord("a") + i % 26))
        e_bool.append_value(clock3)
        e_int8.append_value(4 + i)
        e_int16.append_value(5 + i)
        e_int32.append_value(6 + i)
        e_int64.append_value(7 + i)
        e_uint8.append_value(8 + i)
        e_uint16.append_value(9 + i)
        e_uint32.append_value(10 + i)
        e_uint64.append_value(11 + i)
        if clock3:
            e_float32.append_value(12.2 + i)
        else:
            e_float32.append_value(None)
        e_float64.append_value(13.3 + i)
        e_struct1.append_value([clock3, i + 14])
        if imported_numpy:
            e_array1.append_value(
                np.array(
                    [
                        [i + 15, i + 16, i + 17, i + 18],
                        [i + 19, i + 20, i + 21, i + 22],
                        [i + 23, i + 24, i + 25, i + 26],
                    ]
                )
            )
        else:
            e_array1.append_value(
                [
                    [i + 15, i + 16, i + 17, i + 18],
                    [i + 19, i + 20, i + 21, i + 22],
                    [i + 23, i + 24, i + 25, i + 26],
                ]
            )
        e_array2.append_value(
            [
                [[clock3, i + 16], [not clock3, i + 17], [clock3, i + 18]],
                [[not clock3, i + 19], [clock3, i + 20], [not clock3, i + 21]],
            ]
        )
        e_enum1.append_value(v_enum)
        e_variant1.append_value(v_variant1)
        e_variant2.append_value(v_variant2)
        e_imported1.append_value(Imported(i + 20, i + 21))
        e_imported2.append_value(v_imported2)
    e_sequences.append_values([1, 2], 2)
    e_sequences.append_nones(3)
    e_sequences.append_values([3, 4], 3)
    f.close()
