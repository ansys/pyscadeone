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

import ctypes
from test_common import VSizeImported, vsize_imported_get_bytes_size, vsize_imported_to_bytes
import pytest
from os import remove

import ansys.scadeone.core.svc.simdata.core.dll_wrap as dll_wrap
import ansys.scadeone.core.svc.simdata.core as core

try:
    import numpy as np

    imported_numpy = True
except Exception:
    imported_numpy = False


def get_value(p_val: ctypes.c_void_p):
    val_class = dll_wrap.sdd_value_get_class(p_val)
    if val_class == core.DataClass.NONE:
        return None
    elif val_class == core.DataClass.ENUM:
        v_enum = dll_wrap.sdd_value_get_enum_value(p_val)
        return get_value(v_enum)
    elif val_class == core.DataClass.PREDEF:
        predef_t_id = dll_wrap.sdd_value_get_predef_type_id(p_val)
        if predef_t_id == core.PredefinedType.CHAR:
            return dll_wrap.sdd_value_get_predef_uint8(p_val)
        elif predef_t_id == core.PredefinedType.BOOL:
            return dll_wrap.sdd_value_get_predef_uint8(p_val)
        elif predef_t_id == core.PredefinedType.INT8:
            return dll_wrap.sdd_value_get_predef_int8(p_val)
        elif predef_t_id == core.PredefinedType.INT16:
            return dll_wrap.sdd_value_get_predef_int16(p_val)
        elif predef_t_id == core.PredefinedType.INT32:
            return dll_wrap.sdd_value_get_predef_int32(p_val)
        elif predef_t_id == core.PredefinedType.INT64:
            return dll_wrap.sdd_value_get_predef_int64(p_val)
        elif predef_t_id == core.PredefinedType.UINT8:
            return dll_wrap.sdd_value_get_predef_uint8(p_val)
        elif predef_t_id == core.PredefinedType.UINT16:
            return dll_wrap.sdd_value_get_predef_uint16(p_val)
        elif predef_t_id == core.PredefinedType.UINT32:
            return dll_wrap.sdd_value_get_predef_uint32(p_val)
        elif predef_t_id == core.PredefinedType.UINT64:
            return dll_wrap.sdd_value_get_predef_uint64(p_val)
        elif predef_t_id == core.PredefinedType.FLOAT32:
            return dll_wrap.sdd_value_get_predef_float32(p_val)
        elif predef_t_id == core.PredefinedType.FLOAT64:
            return dll_wrap.sdd_value_get_predef_float64(p_val)
        else:
            assert False
    elif val_class == core.DataClass.LIST:
        size = dll_wrap.sdd_value_get_list_n_values(p_val)
        result = []
        for i in range(0, size):
            result.append(get_value(dll_wrap.sdd_value_get_list_value_at(p_val, i)))
        return result
    elif val_class == core.DataClass.VARIANT:
        v_variant = dll_wrap.sdd_value_get_variant_value(p_val)
        if v_variant is None:
            return None
        return get_value(v_variant)
    elif val_class == core.DataClass.UNTYPED_VARIANT_CONSTRUCTOR:
        return ""
    elif val_class == core.DataClass.IMPORTED:
        return dll_wrap.sdd_value_get_imported_value(p_val)
    else:
        assert False


def assert_list_equal(l1, l2):
    if l1 is None:
        assert l2 is None
    else:
        transformed = False
        if isinstance(l1, ctypes.Array):
            transformed = True
            l1 = l1[:]
        assert len(l1) == len(l2)
        for i in range(0, len(l2)):
            if l1[i] is None:
                assert l2[i] is None
            elif isinstance(l1[i], list) or isinstance(l1[i], ctypes.Array):
                assert isinstance(l2[i], list) and assert_list_equal(l1[i], l2[i])
            elif isinstance(l1[i], str):
                assert l2[i] == l1[i]
            else:
                if transformed:
                    assert l2[i] == pytest.approx(l1[i])
                else:
                    assert l2[i] == pytest.approx((l1[i]).value)
    return True


def read_raw_values(file_id: int, elem_path: str, start: int, v_t, expected_results):
    iterator = dll_wrap.sdd_value_iter_create_part(file_id, elem_path)
    if iterator is None or (
        start != 0 and dll_wrap.sdd_value_iter_seek(iterator, start) != core.SD_ERR_NONE
    ):
        assert expected_results == []
    status = core.SD_ERR_NONE
    val = v_t(0)
    is_none = core.sd_bool_t(0)
    is_last = core.sd_bool_t(0)
    vals = []
    while status == core.SD_ERR_NONE:
        status = dll_wrap.sdd_value_iter_get_raw_value(
            iterator, ctypes.byref(val), ctypes.byref(is_none), ctypes.byref(is_last)
        )
        if status == core.SD_ERR_NONE:
            if is_none:
                vals.append(None)
            else:
                vals.append(v_t(val.value))
    dll_wrap.sdd_value_iter_close(iterator)
    assert_list_equal(vals, expected_results)


def read_n_raw_values(
    file_id: int, elem_path: str, start: int, n_values: int, v_t, expected_results
):
    iterator = dll_wrap.sdd_value_iter_create_part(file_id, elem_path)
    if iterator is None or (
        start != 0 and dll_wrap.sdd_value_iter_seek(iterator, start) != core.SD_ERR_NONE
    ):
        assert expected_results == []
    vals = (v_t * n_values)()
    is_none = (core.sd_bool_t * n_values)()
    n_read = dll_wrap.sdd_value_iter_get_raw_values(iterator, n_values, vals, is_none)
    dll_wrap.sdd_value_iter_close(iterator)
    if n_read == 0:
        assert expected_results == []
    values = []
    for i in range(0, n_read):
        if is_none[i]:
            values.append(None)
        else:
            values.append(v_t(vals[i]))
    assert_list_equal(values, expected_results)


def read_values(file_id: int, start: int, n_values: int, elem_path: str, expected_results):
    u_n = ctypes.c_ulonglong(n_values)
    n_values = u_n.value
    iterator = dll_wrap.sdd_value_iter_create_part(file_id, elem_path)
    if iterator is None or (
        start != 0 and dll_wrap.sdd_value_iter_seek(iterator, start) != core.SD_ERR_NONE
    ):
        assert expected_results == []
    i = 0
    vals = []
    while True:
        p_val = dll_wrap.sdd_value_iter_get_value(iterator)
        if p_val:
            v = get_value(p_val)
            vals.append(v)
            dll_wrap.sdd_value_close(p_val)
        i = i + 1
        if p_val is None or i >= n_values:
            break
    dll_wrap.sdd_value_iter_close(iterator)
    assert_list_equal(vals, expected_results)


def test_all_functions():
    file_path = "trace.sd"
    # create empty file
    file_id = dll_wrap.sdf_open(file_path, core.FileOpenMode.CREATE)
    assert file_id != core.SD_ID_INVALID

    # create struct type
    class TStruct(ctypes.Structure):
        _fields_ = [("eI16", ctypes.c_short), ("eBool", ctypes.c_ubyte)]

    struct_type_id = dll_wrap.sdt_struct_create(ctypes.sizeof(TStruct))
    assert struct_type_id != core.SD_ID_INVALID
    assert dll_wrap.sdt_set_name(struct_type_id, "p1::tStruct") == core.SD_ERR_NONE
    assert (
        dll_wrap.sdt_struct_add_field(
            struct_type_id, "eI16", TStruct.eI16.offset, core.PredefinedType.INT16.value
        )
        == core.SD_ERR_NONE
    )
    assert (
        dll_wrap.sdt_struct_add_field(
            struct_type_id, "eBool", TStruct.eBool.offset, core.PredefinedType.BOOL.value
        )
        == core.SD_ERR_NONE
    )

    # create array type
    dims = [2, 3, 4]
    array_type_id = dll_wrap.sdt_array_create(core.PredefinedType.INT64.value, 3, dims)
    assert dll_wrap.sdt_set_name(array_type_id, "p1::tArray") == core.SD_ERR_NONE
    assert array_type_id != core.SD_ID_INVALID

    # create enum type
    enum_type_id = dll_wrap.sdt_enum_create(core.PredefinedType.INT32.value)
    assert enum_type_id != core.SD_ID_INVALID
    assert dll_wrap.sdt_set_name(enum_type_id, "p1::tEnum") == core.SD_ERR_NONE
    enum_val_red = 2
    enum_val_green = 3
    enum_val_blue = -1
    assert dll_wrap.sdt_enum_add_value(enum_type_id, "red", enum_val_red) == core.SD_ERR_NONE
    assert dll_wrap.sdt_enum_add_value(enum_type_id, "green", enum_val_green) == core.SD_ERR_NONE
    assert dll_wrap.sdt_enum_add_value(enum_type_id, "blue", enum_val_blue) == core.SD_ERR_NONE

    # create variant types
    class variant_SPEED_LIMIT_START_traffic_sign(ctypes.Structure):
        _fields_ = [("tag", ctypes.c_int32), ("value", ctypes.c_int32)]

    class variant_SPEED_LIMIT_END_traffic_sign(ctypes.Structure):
        _fields_ = [("tag", ctypes.c_int32)]

    class traffic_sign(ctypes.Union):
        _fields_ = [
            ("SPEED_LIMIT_START", variant_SPEED_LIMIT_START_traffic_sign),
            ("SPEED_LIMIT_END", variant_SPEED_LIMIT_END_traffic_sign),
        ]

    variant_type_1_id = dll_wrap.sdt_variant_create(ctypes.sizeof(traffic_sign))
    assert variant_type_1_id != core.SD_ID_INVALID
    assert dll_wrap.sdt_set_name(variant_type_1_id, "p1::tVariantSign") == core.SD_ERR_NONE
    assert (
        dll_wrap.sdt_variant_add_constructor(
            variant_type_1_id,
            "SPEED_LIMIT_START",
            variant_SPEED_LIMIT_START_traffic_sign.tag.offset,
            0,
            variant_SPEED_LIMIT_START_traffic_sign.value.offset,
            core.PredefinedType.INT32.value,
        )
        == core.SD_ERR_NONE
    )
    assert (
        dll_wrap.sdt_variant_add_constructor(
            variant_type_1_id,
            "SPEED_LIMIT_END",
            variant_SPEED_LIMIT_END_traffic_sign.tag.offset,
            1,
            0,
            core.SDT_NONE,
        )
        == core.SD_ERR_NONE
    )

    class variant_TS_NONE_traffic_sign_opt(ctypes.Structure):
        _fields_ = [("tag", ctypes.c_int32)]

    class variant_TS_SOME_traffic_sign_opt(ctypes.Structure):
        _fields_ = [("tag", ctypes.c_int32), ("value", traffic_sign)]

    class traffic_sign_opt(ctypes.Union):
        _fields_ = [
            ("TS_NONE", variant_TS_NONE_traffic_sign_opt),
            ("TS_SOME", variant_TS_SOME_traffic_sign_opt),
        ]

    variant_type_2_id = dll_wrap.sdt_variant_create(ctypes.sizeof(traffic_sign_opt))
    assert variant_type_2_id != core.SD_ID_INVALID
    assert dll_wrap.sdt_set_name(variant_type_2_id, "p1::tVariantSignOpt") == core.SD_ERR_NONE
    assert (
        dll_wrap.sdt_variant_add_constructor(
            variant_type_2_id,
            "TS_NONE",
            variant_TS_NONE_traffic_sign_opt.tag.offset,
            0,
            0,
            core.SDT_NONE,
        )
        == core.SD_ERR_NONE
    )
    assert (
        dll_wrap.sdt_variant_add_constructor(
            variant_type_2_id,
            "TS_SOME",
            variant_TS_SOME_traffic_sign_opt.tag.offset,
            1,
            variant_TS_SOME_traffic_sign_opt.value.offset,
            variant_type_1_id,
        )
        == core.SD_ERR_NONE
    )

    # variant possible values
    sign_vals = [traffic_sign_opt(), traffic_sign_opt(), traffic_sign_opt()]
    # TS_NONE{}
    sign_vals[0].TS_NONE.tag = 0
    # TS_SOME{SPEED_LIMIT_START{50}}
    sign_vals[1].TS_SOME.tag = 1
    sign_vals[1].TS_SOME.value.SPEED_LIMIT_START.tag = 0
    sign_vals[1].TS_SOME.value.SPEED_LIMIT_START.value = 50
    # TS_SOME{SPEED_LIMIT_END{}}
    sign_vals[2].TS_SOME.tag = 1
    sign_vals[2].TS_SOME.value.SPEED_LIMIT_END.tag = 1

    # create imported type
    class imported(ctypes.Structure):
        _fields_ = [("eChar", ctypes.c_char), ("eShort", ctypes.c_short), ("eInt", ctypes.c_int32)]

    imported_type_id = dll_wrap.sdt_imported_create(ctypes.sizeof(imported))
    assert imported_type_id != core.SD_ID_INVALID
    assert dll_wrap.sdt_set_name(imported_type_id, "p1::tImported") == core.SD_ERR_NONE
    vsize_imported_type_id = dll_wrap.sdt_vsize_imported_create(
        ctypes.sizeof(VSizeImported), vsize_imported_get_bytes_size, vsize_imported_to_bytes
    )
    assert vsize_imported_type_id != core.SD_ID_INVALID
    assert dll_wrap.sdt_set_name(vsize_imported_type_id, "p1::tVSizeImported") == core.SD_ERR_NONE

    # create elements
    sStruct_id = dll_wrap.sde_create(file_id, "M::Sensor1", struct_type_id, core.SdeKind.SENSOR, "")
    root_op_id = dll_wrap.sde_create(file_id, "R::Root", core.SDT_NONE, core.SdeKind.OPERATOR, "")
    assert root_op_id != core.SD_ID_INVALID
    iStruct_id = dll_wrap.sde_create(root_op_id, "iStruct", struct_type_id, core.SdeKind.INPUT, "")
    iArray_id = dll_wrap.sde_create(root_op_id, "iArray", array_type_id, core.SdeKind.INPUT, "")
    iEnum_id = dll_wrap.sde_create(root_op_id, "iEnum", enum_type_id, core.SdeKind.INPUT, "")
    iFloat32_id = dll_wrap.sde_create(
        root_op_id, "iFloat32", core.PredefinedType.FLOAT32.value, core.SdeKind.INPUT, ""
    )
    iVariant_id = dll_wrap.sde_create(
        root_op_id, "iVariant", variant_type_2_id, core.SdeKind.INPUT, ""
    )
    iImported_id = dll_wrap.sde_create(
        root_op_id, "iImported", imported_type_id, core.SdeKind.INPUT, ""
    )
    iVSizeImported_id = dll_wrap.sde_create(
        root_op_id, "iVSizeImported", vsize_imported_type_id, core.SdeKind.INPUT, ""
    )
    iGroup_id = dll_wrap.sde_create(root_op_id, "iGroup", core.SDT_NONE, core.SdeKind.INPUT, "")
    iGroupItem1Float32_id = dll_wrap.sde_create(
        iGroup_id, ".(.1)", core.PredefinedType.FLOAT32.value, core.SdeKind.GROUP_ITEM, ""
    )
    iGroupItem2Enum_id = dll_wrap.sde_create(
        iGroup_id, ".(.name.1)", enum_type_id, core.SdeKind.GROUP_ITEM, ""
    )
    inst_id = dll_wrap.sde_create(
        root_op_id, "(OpInst#1)", core.SDT_NONE, core.SdeKind.INSTANCE, ""
    )
    pChar_id = dll_wrap.sde_create(
        inst_id, "Probe1", core.PredefinedType.CHAR.value, core.SdeKind.PROBE, ""
    )
    assert dll_wrap.sde_set_group_expr(iStruct_id, "(int32, dummy:bool)") == core.SD_ERR_NONE

    # append values
    NB_CYCLES = 10
    vSStruct = TStruct(0, 0)
    p_vSStruct = ctypes.addressof(vSStruct)
    vIStruct = TStruct(0, 0)
    p_vIStruct = ctypes.addressof(vIStruct)
    if imported_numpy:
        vIArray_2_3_4 = np.empty(shape=(2, 3, 4), dtype=np.int64)
        vIArray_2_3_4_all = []
    vIImported = imported(0, 0, 0)
    p_vIImported = ctypes.addressof(vIImported)
    clock3 = False
    for i in range(0, NB_CYCLES):
        vSStruct.eI16 = i
        vSStruct.eBool = not vSStruct.eBool
        vIStruct.eI16 = 2 * i
        vIStruct.eBool = not vSStruct.eBool
        if imported_numpy:
            for j, k, n in np.ndindex(2, 3, 4):
                vIArray_2_3_4[j][k][n] = i + j + k + n
            vIArray_2_3_4_all.append(vIArray_2_3_4.tolist())
        mod = i % 3
        if mod == 0:
            clock3 = not clock3
            vIEnum = ctypes.c_int32(enum_val_red)
            vIVariant = sign_vals[0]
            strIVSizeImported = "tny"
        elif mod == 1:
            vIEnum = ctypes.c_int32(enum_val_green)
            vIVariant = sign_vals[1]
            strIVSizeImported = "short"
        else:
            vIEnum = ctypes.c_int32(enum_val_blue)
            vIVariant = sign_vals[2]
            strIVSizeImported = "very long"
        vIFloat32 = ctypes.c_float(3.14 + i)
        vIImported.eChar = ctypes.c_char(i)
        vIImported.eShort = ctypes.c_short(i)
        vIImported.eInt = ctypes.c_int32(i)
        vIVSizeImported = VSizeImported(strIVSizeImported)
        vPChar = ctypes.c_char(ord("a") + i % 26)
        vIGroupItem1Float32 = ctypes.c_float(6.28 + i)
        vIGroupItem2Enum = vIEnum

        if imported_numpy:
            dll_wrap.sdd_append_raw_value(iArray_id, vIArray_2_3_4.ctypes.data)
        dll_wrap.sdd_append_raw_value(sStruct_id, p_vSStruct)
        dll_wrap.sdd_append_raw_value(iStruct_id, p_vIStruct)
        dll_wrap.sdd_append_raw_value(iEnum_id, ctypes.addressof(vIEnum))
        dll_wrap.sdd_append_raw_value(iFloat32_id, 0 if clock3 else ctypes.addressof(vIFloat32))
        dll_wrap.sdd_append_raw_value(iVariant_id, ctypes.addressof(vIVariant))
        dll_wrap.sdd_append_raw_value(iImported_id, p_vIImported)
        dll_wrap.sdd_append_raw_value(iVSizeImported_id, ctypes.addressof(vIVSizeImported))
        dll_wrap.sdd_append_raw_value(pChar_id, ctypes.addressof(vPChar))
        dll_wrap.sdd_append_raw_value(iGroupItem1Float32_id, ctypes.addressof(vIGroupItem1Float32))
        dll_wrap.sdd_append_raw_value(iGroupItem2Enum_id, ctypes.addressof(vIGroupItem2Enum))

    assert dll_wrap.sdf_close(file_id) == 0

    # reopen for read and dump
    file_id = dll_wrap.sdf_open(file_path, core.FileOpenMode.READ)
    assert file_id != core.SD_ID_INVALID
    assert dll_wrap.sdf_get_version(file_id)
    assert dll_wrap.sdf_dump(file_id) == 0

    # read types
    assert dll_wrap.sdt_get_n_all_types(file_id) == 21
    types_ids = dll_wrap.sdt_get_all_types(file_id)
    assert types_ids is not None

    struct_type_id = types_ids[14]
    assert dll_wrap.sdt_get_class(struct_type_id) == core.TypeClass.STRUCT
    assert dll_wrap.sdt_get_name(struct_type_id) == "p1::tStruct"
    assert dll_wrap.sdt_get_size(struct_type_id) == ctypes.sizeof(TStruct)
    assert dll_wrap.sdt_struct_get_n_fields(struct_type_id) == 2
    assert dll_wrap.sdt_struct_get_field_name(struct_type_id, 0) == "eI16"
    assert dll_wrap.sdt_struct_get_field_name(struct_type_id, 1) == "eBool"
    assert dll_wrap.sdt_struct_get_field_offset(struct_type_id, 1) == TStruct.eBool.offset
    assert dll_wrap.sdt_struct_get_field_type(struct_type_id, 1) == core.PredefinedType.BOOL.value

    array_type_id = types_ids[15]
    assert dll_wrap.sdt_get_class(array_type_id) == core.TypeClass.ARRAY
    assert dll_wrap.sdt_get_name(array_type_id) == "p1::tArray"
    assert dll_wrap.sdt_array_get_base_type(array_type_id) == core.PredefinedType.INT64.value
    assert dll_wrap.sdt_array_get_n_dims(array_type_id) == 3
    dims = dll_wrap.sdt_array_get_dims(array_type_id)
    assert dims == [2, 3, 4]

    enum_type_id = types_ids[16]
    assert dll_wrap.sdt_get_class(enum_type_id) == core.TypeClass.ENUM
    assert dll_wrap.sdt_get_name(enum_type_id) == "p1::tEnum"
    assert dll_wrap.sdt_enum_get_base_type(enum_type_id) == core.PredefinedType.INT32.value
    assert dll_wrap.sdt_enum_get_n_values(enum_type_id) == 3
    assert dll_wrap.sdt_enum_get_value_name(enum_type_id, 1) == "green"
    assert dll_wrap.sdt_enum_get_value_value(enum_type_id, 1) == 3

    variant_type_1_id = types_ids[17]
    assert dll_wrap.sdt_get_class(variant_type_1_id) == core.TypeClass.VARIANT
    assert dll_wrap.sdt_get_name(variant_type_1_id) == "p1::tVariantSign"
    assert dll_wrap.sdt_get_size(variant_type_1_id) == ctypes.sizeof(traffic_sign)
    assert dll_wrap.sdt_variant_get_n_constructors(variant_type_1_id) == 2
    assert dll_wrap.sdt_variant_get_constructor_name(variant_type_1_id, 1) == "SPEED_LIMIT_END"
    assert (
        dll_wrap.sdt_variant_get_constructor_tag_offset(variant_type_1_id, 1)
        == variant_SPEED_LIMIT_END_traffic_sign.tag.offset
    )
    assert dll_wrap.sdt_variant_get_constructor_tag_value(variant_type_1_id, 1) == 1
    assert dll_wrap.sdt_variant_get_constructor_value_offset(variant_type_1_id, 1) == 0
    assert dll_wrap.sdt_variant_get_constructor_value_type(variant_type_1_id, 1) == core.SDT_NONE

    variant_type_2_id = types_ids[18]
    assert dll_wrap.sdt_get_class(variant_type_2_id) == core.TypeClass.VARIANT
    assert dll_wrap.sdt_get_name(variant_type_2_id) == "p1::tVariantSignOpt"
    assert dll_wrap.sdt_get_size(variant_type_2_id) == ctypes.sizeof(traffic_sign_opt)

    imported_type_id = types_ids[19]
    assert dll_wrap.sdt_get_class(imported_type_id) == core.TypeClass.IMPORTED
    assert dll_wrap.sdt_get_name(imported_type_id) == "p1::tImported"
    assert not dll_wrap.sdt_imported_is_variable_size(imported_type_id)

    vsize_imported_type_id = types_ids[20]
    assert dll_wrap.sdt_get_class(vsize_imported_type_id) == core.TypeClass.IMPORTED
    assert dll_wrap.sdt_get_name(vsize_imported_type_id) == "p1::tVSizeImported"
    assert dll_wrap.sdt_imported_is_variable_size(vsize_imported_type_id)

    # find elements
    assert dll_wrap.sde_get_n_children(file_id) == 2
    root_op_id = dll_wrap.sde_get_child(file_id, 1)
    assert dll_wrap.sde_get_name(root_op_id) == "R::Root"
    assert dll_wrap.sde_get_n_children(root_op_id) == 9
    assert dll_wrap.sde_get_type(root_op_id) == core.SDT_NONE
    iStruct_id = dll_wrap.sde_get_child(root_op_id, 0)
    assert dll_wrap.sde_get_name(iStruct_id) == "iStruct"
    assert dll_wrap.sde_get_type(iStruct_id) == struct_type_id
    assert dll_wrap.sde_get_group_expr(iStruct_id) == "(int32, dummy:bool)"
    iArray_id = dll_wrap.sde_get_child(root_op_id, 1)
    assert dll_wrap.sde_get_name(iArray_id) == "iArray"
    assert dll_wrap.sde_get_kind(iArray_id) == core.SdeKind.INPUT
    iFloat32_id = dll_wrap.sde_get_child(root_op_id, 3)
    assert dll_wrap.sde_get_name(iFloat32_id) == "iFloat32"

    assert dll_wrap.sde_find(file_id, "R::Root/iStruct") == iStruct_id
    assert dll_wrap.sde_find_part(file_id, "R::Root/iStruct") == (
        iStruct_id,
        None,
        struct_type_id,
        0,
    )
    elem_id, part_path, part_type_id, part_offset = dll_wrap.sde_find_part(
        file_id, "R::Root/iStruct.eBool"
    )
    assert (
        elem_id != core.SD_ID_INVALID
        and part_path == ".eBool"
        and part_type_id == core.PredefinedType.BOOL.value
        and part_offset == 2
    )
    assert dll_wrap.sde_find_part(file_id, "R::Root/iArray[1][2][3]") == (
        iArray_id,
        "[1][2][3]",
        core.PredefinedType.INT64.value,
        184,
    )

    assert (
        dll_wrap.sde_find(file_id, "R::Root/iStruct.eI16") == core.SD_ID_INVALID
    )  # [E] sde_find() on path with projection

    def assert_error_find_part(path: str):
        found_elem_id, _, _, _ = dll_wrap.sde_find_part(file_id, path)
        assert found_elem_id == core.SD_ID_INVALID

    assert_error_find_part("R::Root/invalid_var.eI16")  # [E] invalid element path
    assert_error_find_part("R::Root/iStruct/invalid_var")  # [E] unexpected element path
    assert_error_find_part("R::Root/iStruct.invalid")  # [E] invalid struct field
    assert_error_find_part("R::Root/iStruct[0]")  # [E] array projection on struct
    assert_error_find_part("R::Root/iStruct..eI16")  # [E] malformed struct projection 1
    assert_error_find_part("R::Root/iStruct.")  # [E] malformed struct projection 2
    assert_error_find_part("R::Root/iArray[1][2][4]")  # [E] invalid array projection 1
    assert_error_find_part("R::Root/iArray[2][2][3]")  # [E] invalid array projection 2
    assert_error_find_part("R::Root/iArray[1")  # [E] malformed array projection 1
    assert_error_find_part("R::Root/iArray[")  # [E] malformed array projection 2
    assert_error_find_part("R::Root/iArray[1.field")  # [E] malformed array projection 3
    assert_error_find_part("R::Root/iArray[1]field")  # [E] malformed array projection 4
    assert_error_find_part("R::Root/iArray.field")  # [E] struct projection on array

    # read raw values (bytes)
    # TODO add assertions
    iterator = dll_wrap.sdd_value_iter_create_part(file_id, "R::Root/iFloat32")
    assert (
        iterator is not None
        and dll_wrap.sdd_value_iter_get_file_type(iterator) == core.PredefinedType.FLOAT32.value
    )

    read_raw_values(
        file_id,
        "R::Root/iFloat32",
        0,
        ctypes.c_float,
        [None, None, None, 6.14, 7.14, 8.14, None, None, None, 12.14],
    )  # [N] predefined typed var, all values
    read_n_raw_values(
        file_id, "R::Root/iFloat32", 3, 4, ctypes.c_float, [6.14, 7.14, 8.14, None]
    )  # [N] predefined typed var, range [3..6]
    read_n_raw_values(
        file_id,
        "R::Root/iFloat32",
        3,
        1000,
        ctypes.c_float,
        [6.14, 7.14, 8.14, None, None, None, 12.14],
    )  # [N] predefined typed var, range [3..]
    read_raw_values(
        file_id, "R::Root/iStruct.eI16", 0, ctypes.c_short, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    )  # [N] predefined typed struct field, all values
    read_n_raw_values(
        file_id, "R::Root/iStruct.eI16", 3, 4, ctypes.c_short, [6, 8, 10, 12]
    )  # [N] predefined typed struct field, range [3..6]
    read_n_raw_values(
        file_id, "R::Root/iStruct.eI16", 3, 1000, ctypes.c_short, [6, 8, 10, 12, 14, 16, 18]
    )  # [N] predefined typed struct field, range [3..]

    # read structured values (objects)
    read_values(
        file_id,
        0,
        -1,
        "R::Root/iFloat32",
        [None, None, None, 6.14, 7.14, 8.14, None, None, None, 12.14],
    )  # [N] predefined type, all values
    read_values(
        file_id, 3, -1, "R::Root/iFloat32", [6.14, 7.14, 8.14, None, None, None, 12.14]
    )  # [N] predefined type, range [3..]
    read_values(
        file_id, 4, 3, "R::Root/iFloat32", [7.14, 8.14, None]
    )  # [N] predefined type, range [4..7]
    read_values(file_id, 0, -1, "R::Root/iEnum", [2, 3, -1, 2, 3, -1, 2, 3, -1, 2])  # [N] enum type
    if imported_numpy:
        read_values(file_id, 0, -1, "R::Root/iArray", vIArray_2_3_4_all)  # [N] array type
    read_values(
        file_id,
        0,
        -1,
        "R::Root/iStruct",
        [[0, 0], [2, 1], [4, 0], [6, 1], [8, 0], [10, 1], [12, 0], [14, 1], [16, 0], [18, 1]],
    )  # [N] struct type
    read_values(
        file_id, 0, -1, "R::Root/iVariant", [None, 50, None, None, 50, None, None, 50, None, None]
    )  # [N] variant type
    read_values(
        file_id,
        0,
        -1,
        "R::Root/iVariant.TS_NONE",
        ["", None, None, "", None, None, "", None, None, ""],
    )  # [N] variant empty projection
    read_values(
        file_id,
        0,
        -1,
        "R::Root/iVariant.TS_SOME",
        [None, 50, None, None, 50, None, None, 50, None, None],
    )  # [N] variant projection
    read_values(
        file_id, 0, -1, "R::Root/iStruct.eBool", [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    )  # [N] struct projection, all values
    read_values(
        file_id, 3, -1, "R::Root/iStruct.eBool", [1, 0, 1, 0, 1, 0, 1]
    )  # [N] struct projection, range [3..]
    read_values(
        file_id, 4, 3, "R::Root/iStruct.eBool", [0, 1, 0]
    )  # [N] struct projection, range [4..7]
    if imported_numpy:
        read_values(
            file_id, 0, -1, "R::Root/iArray[1][2][3]", [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        )  # [N] array projection, all values
    read_values(
        file_id,
        0,
        -1,
        "R::Root/iImported",
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0, 0, 0],
            [2, 0, 2, 0, 2, 0, 0, 0],
            [3, 0, 3, 0, 3, 0, 0, 0],
            [4, 0, 4, 0, 4, 0, 0, 0],
            [5, 0, 5, 0, 5, 0, 0, 0],
            [6, 0, 6, 0, 6, 0, 0, 0],
            [7, 0, 7, 0, 7, 0, 0, 0],
            [8, 0, 8, 0, 8, 0, 0, 0],
            [9, 0, 9, 0, 9, 0, 0, 0],
        ],
    )  # [N] imported type, all values
    # "tny", "short", "very long"
    read_values(
        file_id,
        0,
        -1,
        "R::Root/iVSizeImported",
        [
            [3, 0, 116, 110, 121],
            [5, 0, 115, 104, 111, 114, 116],
            [9, 0, 118, 101, 114, 121, 32, 108, 111, 110, 103],
            [3, 0, 116, 110, 121],
            [5, 0, 115, 104, 111, 114, 116],
            [9, 0, 118, 101, 114, 121, 32, 108, 111, 110, 103],
            [3, 0, 116, 110, 121],
            [5, 0, 115, 104, 111, 114, 116],
            [9, 0, 118, 101, 114, 121, 32, 108, 111, 110, 103],
            [3, 0, 116, 110, 121],
        ],
    )  # [N] variable size imported type, all values

    read_values(file_id, 0, 1, "R::Root/invalid_var.eI16", [])  # [E] invalid element path
    read_values(file_id, 0, 1, "R::Root/iStruct.invalid", [])  # [E] invalid struct field
    read_values(file_id, 0, 1, "R::Root/iArray[1][2][4]", [])  # [E] invalid array projection

    assert dll_wrap.sdf_close(file_id) == 0
    remove(file_path)
