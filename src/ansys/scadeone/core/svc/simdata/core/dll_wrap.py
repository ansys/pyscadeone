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

# flake8: noqa

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
from typing import List, Tuple, Optional, Any, Union

from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.svc.simdata.core as core

###########################################################################
# wrap DLL functions

IS_ARCH_64 = ctypes.sizeof(ctypes.c_void_p) == 8

if IS_ARCH_64:
    root = Path(__file__).parents[3] / "libs"
    dll_name = (
        root / "win-x64" / "swan_sd.dll"
        if platform.system() == "Windows"
        else root / "linux-x64" / "libswan_sd.so"
    )
    dll_path = dll_name.absolute()
    SWAN_SD_CDLL = ctypes.CDLL(str(dll_path))
else:
    SWAN_SD_CDLL = None


def arch_64_error(*args):
    raise ScadeOneException("Simdata module is only compatible with 64 bit architecture")


def wrap_function(lib, func_name, argtypes, restype):
    """Wrapping ctypes functions"""

    if not IS_ARCH_64:
        return arch_64_error

    func = lib.__getattr__(func_name)
    func.restype = restype
    func.argtypes = argtypes
    return func


sdf_create_wrap = wrap_function(SWAN_SD_CDLL, "sdf_wcreate", [ctypes.c_wchar_p], core.sd_id_t)
sdf_open_wrap = wrap_function(SWAN_SD_CDLL, "sdf_wopen", [ctypes.c_wchar_p], core.sd_id_t)
sdf_get_version_wrap = wrap_function(
    SWAN_SD_CDLL, "sdf_get_format_version", [core.sd_id_t], ctypes.c_char_p
)
sdf_dump_wrap = wrap_function(SWAN_SD_CDLL, "sdf_dump", [core.sd_id_t], core.sd_err_t)
sdf_close_wrap = wrap_function(SWAN_SD_CDLL, "sdf_close", [core.sd_id_t], core.sd_err_t)
sdt_get_n_all_types_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_get_n_all_types", [core.sd_id_t], core.sd_size_t
)
sdt_get_all_types_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_get_all_types", [core.sd_id_t, ctypes.POINTER(core.sd_id_t)], core.sd_err_t
)
sdt_get_class_wrap = wrap_function(SWAN_SD_CDLL, "sdt_get_class", [core.sd_id_t], core.sdt_class_t)
sdt_get_size_wrap = wrap_function(SWAN_SD_CDLL, "sdt_get_size", [core.sd_id_t], core.sd_size_t)
sdt_get_name_wrap = wrap_function(SWAN_SD_CDLL, "sdt_get_name", [core.sd_id_t], ctypes.c_char_p)
sdt_set_name_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_set_name", [core.sd_id_t, ctypes.c_char_p], core.sd_err_t
)

sdt_struct_create_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_struct_create", [core.sd_size_t], core.sd_id_t
)
sdt_struct_add_field_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_struct_add_field",
    [core.sd_id_t, ctypes.c_char_p, core.sd_size_t, core.sd_id_t],
    core.sd_err_t,
)
sdt_struct_get_n_fields_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_struct_get_n_fields", [core.sd_id_t], core.sd_size_t
)
sdt_struct_get_field_name_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_struct_get_field_name", [core.sd_id_t, core.sd_size_t], ctypes.c_char_p
)
sdt_struct_get_field_offset_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_struct_get_field_offset", [core.sd_id_t, core.sd_size_t], core.sd_size_t
)
sdt_struct_get_field_type_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_struct_get_field_type", [core.sd_id_t, core.sd_size_t], core.sd_id_t
)
sdt_array_create_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_array_create",
    [core.sd_id_t, core.sd_size_t, ctypes.POINTER(core.sd_size_t)],
    core.sd_id_t,
)
sdt_array_get_base_type_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_array_get_base_type", [core.sd_id_t], core.sd_id_t
)
sdt_array_get_n_dims_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_array_get_n_dims", [core.sd_id_t], core.sd_size_t
)
sdt_array_get_dims_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_array_get_dims",
    [core.sd_id_t, ctypes.POINTER(core.sd_size_t)],
    core.sd_err_t,
)
sdt_enum_create_wrap = wrap_function(SWAN_SD_CDLL, "sdt_enum_create", [core.sd_id_t], core.sd_id_t)
sdt_enum_add_value_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_enum_add_value",
    [core.sd_id_t, ctypes.c_char_p, ctypes.c_void_p],
    core.sd_err_t,
)
sdt_enum_get_base_type_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_enum_get_base_type", [core.sd_id_t], core.sd_id_t
)
sdt_enum_get_n_values_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_enum_get_n_values", [core.sd_id_t], core.sd_size_t
)
sdt_enum_get_value_name_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_enum_get_value_name", [core.sd_id_t, core.sd_size_t], ctypes.c_char_p
)
sdt_enum_get_value_value_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_enum_get_value_value",
    [core.sd_id_t, core.sd_size_t, ctypes.c_void_p],
    core.sd_err_t,
)
sdt_variant_create_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_variant_create", [core.sd_size_t], core.sd_id_t
)
sdt_variant_add_constructor_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_variant_add_constructor",
    [core.sd_id_t, ctypes.c_char_p, core.sd_size_t, core.sd_int32_t, core.sd_size_t, core.sd_id_t],
    core.sd_err_t,
)
sdt_variant_get_n_constructors_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_variant_get_n_constructors", [core.sd_id_t], core.sd_size_t
)
sdt_variant_get_constructor_name_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_variant_get_constructor_name",
    [core.sd_id_t, core.sd_size_t],
    ctypes.c_char_p,
)
sdt_variant_get_constructor_tag_offset_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_variant_get_constructor_tag_offset",
    [core.sd_id_t, core.sd_size_t],
    core.sd_size_t,
)
sdt_variant_get_constructor_tag_value_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_variant_get_constructor_tag_value",
    [core.sd_id_t, core.sd_size_t],
    core.sd_int32_t,
)
sdt_variant_get_constructor_value_offset_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_variant_get_constructor_value_offset",
    [core.sd_id_t, core.sd_size_t],
    core.sd_size_t,
)
sdt_variant_get_constructor_value_type_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_variant_get_constructor_value_type",
    [core.sd_id_t, core.sd_size_t],
    core.sd_id_t,
)

sdt_imported_create_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_imported_create", [core.sd_size_t], core.sd_id_t
)
sdt_vsize_imported_create_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdt_vsize_imported_create",
    [core.sd_size_t, core.sd_pfn_vsize_get_bytes_size_t, core.sd_pfn_vsize_to_bytes_t],
    core.sd_id_t,
)

sdt_imported_is_variable_size_wrap = wrap_function(
    SWAN_SD_CDLL, "sdt_imported_is_variable_size", [core.sd_id_t], core.sd_bool_t
)

sde_create_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sde_create",
    [core.sd_id_t, ctypes.c_char_p, core.sd_id_t, core.sde_kind_t],
    core.sd_id_t,
)

sde_find_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_find", [core.sd_id_t, ctypes.c_char_p], core.sd_id_t
)
sde_find_part_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sde_find_part",
    [
        core.sd_id_t,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_char_p),
        ctypes.POINTER(core.sd_id_t),
        ctypes.POINTER(core.sd_size_t),
    ],
    core.sd_id_t,
)
sde_get_n_children_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_get_n_children", [core.sd_id_t], core.sd_size_t
)
sde_get_child_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_get_child", [core.sd_id_t, core.sd_size_t], core.sd_id_t
)
sde_get_children_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_get_children", [core.sd_id_t, ctypes.POINTER(core.sd_id_t)], core.sd_err_t
)
sde_get_name_wrap = wrap_function(SWAN_SD_CDLL, "sde_get_name", [core.sd_id_t], ctypes.c_char_p)
sde_get_type_wrap = wrap_function(SWAN_SD_CDLL, "sde_get_type", [core.sd_id_t], core.sd_id_t)
sde_get_kind_wrap = wrap_function(SWAN_SD_CDLL, "sde_get_kind", [core.sd_id_t], core.sde_kind_t)
sde_set_name_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_set_name", [core.sd_id_t, ctypes.c_char_p], core.sd_err_t
)
sde_set_type_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_set_type", [core.sd_id_t, core.sd_id_t], core.sd_err_t
)
sde_set_kind_wrap = wrap_function(
    SWAN_SD_CDLL, "sde_set_kind", [core.sd_id_t, core.sde_kind_t], core.sd_err_t
)
sde_remove_wrap = wrap_function(SWAN_SD_CDLL, "sde_remove", [core.sd_id_t], core.sd_err_t)

sdd_append_raw_value_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_append_raw_value", [core.sd_id_t, ctypes.c_void_p], core.sd_err_t
)
sdd_append_value_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_append_value", [core.sd_id_t, core.sd_value_t], core.sd_err_t
)
sdd_append_sequence_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_append_sequence", [core.sd_id_t, core.sd_sequence_t], core.sd_err_t
)
sdd_value_iter_create_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_create", [core.sd_id_t, core.sd_id_t], core.sd_value_iterator_t
)
sdd_value_iter_create_part_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_iter_create_part",
    [core.sd_id_t, ctypes.c_char_p, core.sd_id_t],
    core.sd_value_iterator_t,
)
sdd_value_iter_get_file_type_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_get_file_type", [core.sd_value_iterator_t], core.sd_id_t
)
sdd_value_iter_get_mem_type_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_get_mem_type", [core.sd_value_iterator_t], core.sd_id_t
)
sdd_value_iter_seek_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_seek", [core.sd_value_iterator_t, core.sd_size_t], core.sd_err_t
)
sdd_value_iter_get_raw_value_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_iter_get_raw_value",
    [
        core.sd_value_iterator_t,
        ctypes.c_void_p,
        ctypes.POINTER(core.sd_bool_t),
        ctypes.POINTER(core.sd_bool_t),
    ],
    core.sd_err_t,
)
sdd_value_iter_get_raw_values_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_iter_get_raw_values",
    [core.sd_value_iterator_t, core.sd_size_t, ctypes.c_void_p, ctypes.POINTER(core.sd_bool_t)],
    core.sd_size_t,
)
sdd_value_iter_get_value_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_get_value", [core.sd_value_iterator_t], core.sd_value_t
)
sdd_value_iter_set_raw_value_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_iter_set_raw_value",
    [core.sd_value_iterator_t, ctypes.c_void_p],
    core.sd_err_t,
)
sdd_value_iter_set_value_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_iter_set_value",
    [core.sd_value_iterator_t, core.sd_value_t],
    core.sd_err_t,
)
sdd_value_iter_clear_values_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_clear_values", [core.sd_value_iterator_t], core.sd_err_t
)
sdd_value_iter_close_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_iter_close", [core.sd_value_iterator_t], None
)

# 'sequence iterator' object = an iterator on element sequences ('sequence' objects)
# TODO

sdd_value_create_none_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_none", [], core.sd_value_t
)
sdd_value_create_predef_char_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_char8", [core.sd_uint8_t], core.sd_value_t
)
sdd_value_create_predef_bool_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_bool", [core.sd_bool_t], core.sd_value_t
)
sdd_value_create_predef_int8_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_int8", [core.sd_int8_t], core.sd_value_t
)
sdd_value_create_predef_int16_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_int16", [core.sd_int16_t], core.sd_value_t
)
sdd_value_create_predef_int32_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_int32", [core.sd_int32_t], core.sd_value_t
)
sdd_value_create_predef_int64_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_int64", [core.sd_int64_t], core.sd_value_t
)
sdd_value_create_predef_uint8_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_uint8", [core.sd_uint8_t], core.sd_value_t
)
sdd_value_create_predef_uint16_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_uint16", [core.sd_uint16_t], core.sd_value_t
)
sdd_value_create_predef_uint32_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_uint32", [core.sd_uint32_t], core.sd_value_t
)
sdd_value_create_predef_uint64_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_uint64", [core.sd_uint64_t], core.sd_value_t
)
sdd_value_create_predef_float32_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_float32", [core.sd_float32_t], core.sd_value_t
)
sdd_value_create_predef_float64_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_predef_float64", [core.sd_float64_t], core.sd_value_t
)
sdd_value_create_list_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_create_list",
    [core.sd_size_t, ctypes.POINTER(core.sd_value_t)],
    core.sd_value_t,
)
sdd_value_create_enum_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_enum", [ctypes.c_char_p], core.sd_value_t
)
sdd_value_create_variant_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_variant", [ctypes.c_char_p, core.sd_value_t], core.sd_value_t
)
sdd_value_create_imported_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_create_imported", [core.sd_size_t, ctypes.c_void_p], core.sd_value_t
)
sdd_value_close_wrap = wrap_function(SWAN_SD_CDLL, "sdd_value_close", [core.sd_value_t], None)
sdd_value_get_class_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_class", [core.sd_value_t], core.sdd_value_class_t
)
sdd_value_get_predef_type_id_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_predef_type_id", [core.sd_value_t], core.sd_id_t
)
sdd_value_get_predef_raw_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_predef_raw", [core.sd_value_t, ctypes.c_void_p], core.sd_err_t
)
sdd_value_get_predef_int8_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_int8",
    [core.sd_value_t, ctypes.POINTER(core.sd_int8_t)],
    core.sd_err_t,
)
sdd_value_get_predef_int16_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_int16",
    [core.sd_value_t, ctypes.POINTER(core.sd_int16_t)],
    core.sd_err_t,
)
sdd_value_get_predef_int32_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_int32",
    [core.sd_value_t, ctypes.POINTER(core.sd_int32_t)],
    core.sd_err_t,
)
sdd_value_get_predef_int64_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_int64",
    [core.sd_value_t, ctypes.POINTER(core.sd_int64_t)],
    core.sd_err_t,
)
sdd_value_get_predef_uint8_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_uint8",
    [core.sd_value_t, ctypes.POINTER(core.sd_uint8_t)],
    core.sd_err_t,
)
sdd_value_get_predef_uint16_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_uint16",
    [core.sd_value_t, ctypes.POINTER(core.sd_uint16_t)],
    core.sd_err_t,
)
sdd_value_get_predef_uint32_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_uint32",
    [core.sd_value_t, ctypes.POINTER(core.sd_uint32_t)],
    core.sd_err_t,
)
sdd_value_get_predef_uint64_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_uint64",
    [core.sd_value_t, ctypes.POINTER(core.sd_uint64_t)],
    core.sd_err_t,
)
sdd_value_get_predef_float32_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_float32",
    [core.sd_value_t, ctypes.POINTER(core.sd_float32_t)],
    core.sd_err_t,
)
sdd_value_get_predef_float64_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_value_get_predef_float64",
    [core.sd_value_t, ctypes.POINTER(core.sd_float64_t)],
    core.sd_err_t,
)
sdd_value_get_enum_name_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_enum_name", [core.sd_value_t], ctypes.c_char_p
)
sdd_value_get_enum_value_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_enum_value", [core.sd_value_t], core.sd_value_t
)
sdd_value_get_list_n_values_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_list_n_values", [core.sd_value_t], core.sd_size_t
)
sdd_value_get_list_value_at_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_list_value_at", [core.sd_value_t, core.sd_size_t], core.sd_value_t
)
sdd_value_get_variant_name_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_variant_name", [core.sd_value_t], ctypes.c_char_p
)
sdd_value_get_variant_value_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_variant_value", [core.sd_value_t], core.sd_value_t
)
sdd_value_get_imported_size_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_imported_size", [core.sd_value_t], core.sd_size_t
)
sdd_value_get_imported_value_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_value_get_imported_value", [core.sd_value_t, ctypes.c_void_p], core.sd_err_t
)
sdd_sequence_create_nones_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_sequence_create_nones", [core.sd_size_t], core.sd_sequence_t
)
sdd_sequence_create_values_wrap = wrap_function(
    SWAN_SD_CDLL,
    "sdd_sequence_create_values",
    [core.sd_id_t, core.sd_size_t, ctypes.POINTER(core.sd_value_t), core.sd_size_t],
    core.sd_sequence_t,
)
sdd_sequence_close_wrap = wrap_function(
    SWAN_SD_CDLL, "sdd_sequence_close", [core.sd_sequence_t], None
)


###########################################################################
# file operations


def sdf_create(file_path: Union[str, Path]) -> int:
    if isinstance(file_path, Path):
        file_path = str(file_path)
    b_file_path = ctypes.c_wchar_p(file_path)
    return sdf_create_wrap(b_file_path)


def sdf_open(file_path: Union[str, Path]) -> int:
    if isinstance(file_path, Path):
        file_path = str(file_path)
    b_file_path = ctypes.c_wchar_p(file_path)
    return sdf_open_wrap(b_file_path)


def sdf_get_version(file_id: int) -> str:
    b_version = sdf_get_version_wrap(file_id)
    return b_version.decode("utf-8") if b_version is not None else ""


def sdf_dump(file_id: int) -> int:
    return sdf_dump_wrap(file_id)


def sdf_close(file_id: int) -> int:
    return sdf_close_wrap(file_id)


###########################################################################
# data types


# - common


def sdt_get_n_all_types(file_id: int) -> int:
    return sdt_get_n_all_types_wrap(file_id)


def sdt_get_all_types(file_id: int) -> List[int]:
    n_types = sdt_get_n_all_types(file_id)
    types_ids = (core.sd_id_t * n_types)()
    err = sdt_get_all_types_wrap(file_id, types_ids)
    return None if err != core.SD_ERR_NONE else list(types_ids)


def sdt_get_class(type_id: int) -> core.TypeClass:
    klass = sdt_get_class_wrap(type_id)
    return core.TypeClass(klass)


def sdt_get_size(type_id: int) -> int:
    return sdt_get_size_wrap(type_id)


def sdt_get_name(type_id: int) -> str:
    b_name = sdt_get_name_wrap(type_id)
    return b_name.decode("utf-8") if b_name is not None else ""


def sdt_set_name(type_id: int, name: str):
    b_name = name.encode("utf-8")
    return sdt_set_name_wrap(type_id, b_name)


# - struct


def sdt_struct_create(mem_size: int) -> int:
    return sdt_struct_create_wrap(mem_size)


def sdt_struct_add_field(struct_id: int, name: str, offset: int, type_id: int) -> int:
    b_name = name.encode("utf-8")
    return sdt_struct_add_field_wrap(struct_id, b_name, offset, type_id)


def sdt_struct_get_n_fields(struct_id: int) -> int:
    return sdt_struct_get_n_fields_wrap(struct_id)


def sdt_struct_get_field_name(struct_id: int, field_idx: int) -> str:
    b_name = sdt_struct_get_field_name_wrap(struct_id, field_idx)
    return b_name.decode("utf-8")


def sdt_struct_get_field_offset(struct_id: int, field_idx: int) -> int:
    return sdt_struct_get_field_offset_wrap(struct_id, field_idx)


def sdt_struct_get_field_type(struct_id: int, field_idx: int) -> int:
    return sdt_struct_get_field_type_wrap(struct_id, field_idx)


# - array


def sdt_array_create(base_type_id: int, n_dims: int, dims: List[int]):
    dims_array_type = core.sd_size_t * len(dims)
    dims_array = dims_array_type(*dims)
    return sdt_array_create_wrap(base_type_id, n_dims, dims_array)


def sdt_array_get_base_type(array_id: int) -> int:
    return sdt_array_get_base_type_wrap(array_id)


def sdt_array_get_n_dims(array_id: int) -> int:
    return sdt_array_get_n_dims_wrap(array_id)


def sdt_array_get_dims(array_id: int) -> List[int]:
    n_dims = sdt_array_get_n_dims(array_id)
    dims = (core.sd_size_t * n_dims)()
    err = sdt_array_get_dims_wrap(array_id, dims)
    return None if err != core.SD_ERR_NONE else list(dims)


# - enum


def sdt_enum_create(base_type_id: int) -> int:
    return sdt_enum_create_wrap(base_type_id)


def sdt_enum_add_value(enum_id: int, name: str, value: int) -> int:
    b_name = name.encode("utf-8")
    p_value = ctypes.addressof(ctypes.c_longlong(value))
    return sdt_enum_add_value_wrap(enum_id, b_name, p_value)


def sdt_enum_get_base_type(enum_id: int) -> int:
    return sdt_enum_get_base_type_wrap(enum_id)


def sdt_enum_get_n_values(enum_id: int) -> int:
    return sdt_enum_get_n_values_wrap(enum_id)


def sdt_enum_get_value_name(enum_id: int, value_idx: int) -> str:
    b_name = sdt_enum_get_value_name_wrap(enum_id, value_idx)
    return b_name.decode("utf-8")


def sdt_enum_get_value_value(enum_id: int, value_idx: int) -> int:
    v = ctypes.c_longlong(0)
    if sdt_enum_get_base_type(enum_id) == core.PredefinedType.UINT64.value:
        v = ctypes.c_ulonglong(0)
    err = sdt_enum_get_value_value_wrap(enum_id, value_idx, ctypes.byref(v))
    return None if err != core.SD_ERR_NONE else v.value


# - variant


def sdt_variant_create(mem_size: int) -> int:
    return sdt_variant_create_wrap(mem_size)


def sdt_variant_add_constructor(
    variant_id: int,
    name: str,
    tag_offset: int,
    tag_value: int,
    value_offset: int,
    value_type_id: int,
) -> int:
    b_name = name.encode("utf-8")
    return sdt_variant_add_constructor_wrap(
        variant_id, b_name, tag_offset, tag_value, value_offset, value_type_id
    )


def sdt_variant_get_n_constructors(variant_id: int) -> int:
    return sdt_variant_get_n_constructors_wrap(variant_id)


def sdt_variant_get_constructor_name(variant_id: int, constructor_idx: int) -> str:
    b_name = sdt_variant_get_constructor_name_wrap(variant_id, constructor_idx)
    return b_name.decode("utf-8")


def sdt_variant_get_constructor_tag_offset(variant_id: int, constructor_idx: int) -> int:
    return sdt_variant_get_constructor_tag_offset_wrap(variant_id, constructor_idx)


def sdt_variant_get_constructor_tag_value(variant_id: int, constructor_idx: int) -> int:
    return sdt_variant_get_constructor_tag_value_wrap(variant_id, constructor_idx)


def sdt_variant_get_constructor_value_offset(variant_id: int, constructor_idx: int) -> int:
    return sdt_variant_get_constructor_value_offset_wrap(variant_id, constructor_idx)


def sdt_variant_get_constructor_value_type(variant_id: int, constructor_idx: int) -> int:
    return sdt_variant_get_constructor_value_type_wrap(variant_id, constructor_idx)


# - imported


def sdt_imported_create(mem_size: int) -> int:
    return sdt_imported_create_wrap(mem_size)


to_avoid_gc = []


def sdt_vsize_imported_create(
    mem_size: int,
    pfn_get_bytes_size: core.sd_pfn_vsize_get_bytes_size_t,  # type: ignore
    pfn_vsize_to_bytes: core.sd_pfn_vsize_to_bytes_t,  # type: ignore
) -> int:
    f1 = core.sd_pfn_vsize_get_bytes_size_t(pfn_get_bytes_size)
    f2 = core.sd_pfn_vsize_to_bytes_t(pfn_vsize_to_bytes)
    to_avoid_gc.append([f1, f2])
    return sdt_vsize_imported_create_wrap(mem_size, f1, f2)


def sdt_imported_is_variable_size(imported_id: int) -> bool:
    return False if sdt_imported_is_variable_size_wrap(imported_id) == 0 else True


###########################################################################
# elements tree


# - create element


def sde_create(file_id: int, name: str, type_id: int, kind: core.SdeKind) -> int:
    b_name = name.encode("utf-8")
    return sde_create_wrap(file_id, b_name, type_id, kind.value)


# - find element in tree


def sde_find(file_or_elem_id: int, path: str) -> int:
    b_path = path.encode("utf-8")
    return sde_find_wrap(file_or_elem_id, b_path)


def sde_find_part(file_or_elem_id: int, path: str) -> Tuple[int, str, int, int]:
    b_path = path.encode("utf-8")
    part_path = ctypes.c_char_p()
    part_type_id = core.sd_id_t()
    part_offset = core.sd_size_t()
    elem_id = sde_find_part_wrap(
        file_or_elem_id,
        b_path,
        ctypes.byref(part_path),
        ctypes.byref(part_type_id),
        ctypes.byref(part_offset),
    )
    return (
        elem_id,
        None if part_path.value is None else part_path.value.decode("utf-8"),
        part_type_id.value,
        part_offset.value,
    )


# - access element properties / update / remove element


def sde_get_n_children(file_or_elem_id: int) -> int:
    return sde_get_n_children_wrap(file_or_elem_id)


def sde_get_child(file_or_elem_id: int, index: int) -> int:
    return sde_get_child_wrap(file_or_elem_id, index)


def sde_get_children(file_or_elem_id: int) -> List[int]:
    n_children = sde_get_n_children(file_or_elem_id)
    children_ids = (core.sd_id_t * n_children)()
    err = sde_get_children_wrap(file_or_elem_id, children_ids)
    return None if err != core.SD_ERR_NONE else list(children_ids)


def sde_get_name(elem_id: int) -> str:
    b_name = sde_get_name_wrap(elem_id)
    return b_name.decode("utf-8")


def sde_get_type(elem_id: int) -> int:
    return sde_get_type_wrap(elem_id)


def sde_get_kind(elem_id: int) -> core.SdeKind:
    kind = sde_get_kind_wrap(elem_id)
    return core.SdeKind(kind)


def sde_set_name(elem_id: int, name: str):
    b_name = name.encode("utf-8")
    return sde_set_name_wrap(elem_id, b_name)


def sde_set_type(elem_id: int, type_id: int) -> int:
    return sde_set_type_wrap(elem_id, type_id)


def sde_set_kind(elem_id: int, kind: core.SdeKind) -> int:
    return sde_set_kind_wrap(elem_id, kind.value)


def sde_remove(elem_id: int) -> int:
    return sde_remove_wrap(elem_id)


###########################################################################
# simulation data


# append value/sequence to element


def sdd_append_raw_value(elem_id: int, data: int) -> int:
    return sdd_append_raw_value_wrap(elem_id, data)


def sdd_append_value(elem_id: int, value: core.sd_value_t) -> int:
    return sdd_append_value_wrap(elem_id, value)


def sdd_append_sequence(elem_id: int, sequence: core.sd_sequence_t) -> int:
    return sdd_append_sequence_wrap(elem_id, sequence)


# 'value iterator' object = an iterator on element (or part of it) values ('value' objects / raw data)


def sdd_value_iter_create(
    elem_id: int, mem_type_id: int = core.SDT_NONE
) -> core.sd_value_iterator_t:
    return sdd_value_iter_create_wrap(elem_id, mem_type_id)


def sdd_value_iter_create_part(
    file_id: int, path: str, mem_type_id: int = core.SDT_NONE
) -> core.sd_value_iterator_t:
    b_path = path.encode("utf-8")
    return sdd_value_iter_create_part_wrap(file_id, b_path, mem_type_id)


def sdd_value_iter_get_file_type(iterator: core.sd_value_iterator_t) -> int:
    return sdd_value_iter_get_file_type_wrap(iterator)


def sdd_value_iter_get_mem_type(iterator: core.sd_value_iterator_t) -> int:
    return sdd_value_iter_get_mem_type_wrap(iterator)


def sdd_value_iter_seek(iterator: core.sd_value_iterator_t, n_values: int) -> int:
    return sdd_value_iter_seek_wrap(iterator, n_values)


def sdd_value_iter_get_raw_value(
    iterator: core.sd_value_iterator_t,
    data: ctypes.c_void_p,
    is_none: ctypes._POINTER[core.sd_bool_t],
    is_last: ctypes._POINTER[core.sd_bool_t],
) -> int:
    return sdd_value_iter_get_raw_value_wrap(iterator, data, is_none, is_last)


def sdd_value_iter_get_raw_values(
    iterator: core.sd_value_iterator_t,
    n_values: int,
    data: ctypes.c_void_p,
    is_none: ctypes._POINTER[core.sd_bool_t],
) -> int:
    return sdd_value_iter_get_raw_values_wrap(iterator, n_values, data, is_none)


def sdd_value_iter_get_value(iterator: core.sd_value_iterator_t) -> core.sd_value_t:
    return sdd_value_iter_get_value_wrap(iterator)


def sdd_value_iter_set_raw_value(iterator: core.sd_value_iterator_t, data: ctypes.c_void_p) -> int:
    return sdd_value_iter_set_raw_value_wrap(iterator, data)


def sdd_value_iter_set_value(iterator: core.sd_value_iterator_t, value: core.sd_value_t) -> int:
    return sdd_value_iter_set_value_wrap(iterator, value)


def sdd_value_iter_clear_values(iterator: core.sd_value_iterator_t) -> int:
    return sdd_value_iter_clear_values_wrap(iterator)


def sdd_value_iter_close(iterator: core.sd_value_iterator_t) -> None:
    sdd_value_iter_close_wrap(iterator)


# 'sequence iterator' object = an iterator on element sequences ('sequence' objects)
# TODO

# - 'value' constructors


def sdd_value_create_none() -> core.sd_value_t:
    return sdd_value_create_none_wrap()


def sdd_value_create_predef_char(value: str) -> Optional[core.sd_value_t]:
    if not isinstance(value, str) or len(value) != 1:
        return None
    return sdd_value_create_predef_char_wrap(core.sd_uint8_t(ord(value[0])))


def sdd_value_create_predef_bool(value: bool) -> Optional[core.sd_value_t]:
    if not isinstance(value, bool):
        return None
    return sdd_value_create_predef_bool_wrap(core.sd_bool_true if value else core.sd_bool_false)


def sdd_value_create_predef_int8(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_int8_wrap(core.sd_int8_t(value))


def sdd_value_create_predef_int16(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_int16_wrap(core.sd_int16_t(value))


def sdd_value_create_predef_int32(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_int32_wrap(core.sd_int32_t(value))


def sdd_value_create_predef_int64(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_int64_wrap(core.sd_int64_t(value))


def sdd_value_create_predef_uint8(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_uint8_wrap(core.sd_uint8_t(value))


def sdd_value_create_predef_uint16(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_uint16_wrap(core.sd_uint16_t(value))


def sdd_value_create_predef_uint32(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_uint32_wrap(core.sd_uint32_t(value))


def sdd_value_create_predef_uint64(value: int) -> Optional[core.sd_value_t]:
    if not isinstance(value, int):
        return None
    return sdd_value_create_predef_uint64_wrap(core.sd_uint64_t(value))


def sdd_value_create_predef_float32(value: float) -> Optional[core.sd_value_t]:
    if not isinstance(value, float):
        return None
    return sdd_value_create_predef_float32_wrap(core.sd_float32_t(value))


def sdd_value_create_predef_float64(value: float) -> Optional[core.sd_value_t]:
    if not isinstance(value, float):
        return None
    return sdd_value_create_predef_float64_wrap(core.sd_float64_t(value))


def sdd_value_create_list(
    n_values: int, values: List[core.sd_value_t]
) -> Optional[core.sd_value_t]:
    if not isinstance(values, list):
        return None
    values_array_type = core.sd_value_t * len(values)
    values_array = values_array_type(*values)
    return sdd_value_create_list_wrap(n_values, values_array)


def sdd_value_create_enum(value: str) -> Optional[core.sd_value_t]:
    if not isinstance(value, str):
        return None
    return sdd_value_create_enum_wrap(value.encode("utf-8"))


def sdd_value_create_variant(
    name: str, value: Optional[core.sd_value_t]
) -> Optional[core.sd_value_t]:
    if not isinstance(name, str):
        return None
    return sdd_value_create_variant_wrap(
        name.encode("utf-8"), value if value is not None else core.sd_value_t(0)
    )


def sdd_value_create_imported(value: Any) -> Optional[core.sd_value_t]:
    c_t = value.__class__
    if not issubclass(c_t, (ctypes._SimpleCData, ctypes.Array, ctypes.Structure, ctypes.Union)):
        return None
    return sdd_value_create_imported_wrap(ctypes.sizeof(c_t), ctypes.addressof(value))


# - 'value' destructor


def sdd_value_close(value: core.sd_value_t) -> None:
    sdd_value_close_wrap(value)


# - 'value' accessors


def sdd_value_get_class(value: core.sd_value_t) -> core.DataClass:
    klass = sdd_value_get_class_wrap(value)
    return core.DataClass(klass)


def sdd_value_get_predef_type_id(value: core.sd_value_t) -> core.PredefinedType:
    kind = sdd_value_get_predef_type_id_wrap(value)
    return core.PredefinedType(kind)


def sdd_value_get_predef_raw(value: core.sd_value_t, data: ctypes.c_void_p) -> int:
    return sdd_value_get_predef_raw_wrap(value, data)


def sdd_value_get_predef_uint8(value: core.sd_value_t) -> Optional[core.sd_uint8_t]:
    data = core.sd_uint8_t(0)
    err = sdd_value_get_predef_uint8_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_uint16(value: core.sd_value_t) -> Optional[core.sd_uint16_t]:
    data = core.sd_uint16_t(0)
    err = sdd_value_get_predef_uint16_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_uint32(value: core.sd_value_t) -> Optional[core.sd_uint32_t]:
    data = core.sd_uint32_t(0)
    err = sdd_value_get_predef_uint32_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_uint64(value: core.sd_value_t) -> Optional[core.sd_uint64_t]:
    data = core.sd_uint64_t(0)
    err = sdd_value_get_predef_uint64_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_int8(value: core.sd_value_t) -> Optional[core.sd_int8_t]:
    data = core.sd_int8_t(0)
    err = sdd_value_get_predef_int8_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_int16(value: core.sd_value_t) -> Optional[core.sd_int16_t]:
    data = core.sd_int16_t(0)
    err = sdd_value_get_predef_int16_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_int32(value: core.sd_value_t) -> Optional[core.sd_int32_t]:
    data = core.sd_int32_t(0)
    err = sdd_value_get_predef_int32_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_int64(value: core.sd_value_t) -> Optional[core.sd_int64_t]:
    data = core.sd_int64_t(0)
    err = sdd_value_get_predef_int64_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_float32(value: core.sd_value_t) -> Optional[core.sd_float32_t]:
    data = core.sd_float32_t(0.0)
    err = sdd_value_get_predef_float32_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_predef_float64(value: core.sd_value_t) -> Optional[core.sd_float64_t]:
    data = core.sd_float64_t(0.0)
    err = sdd_value_get_predef_float64_wrap(value, ctypes.byref(data))
    return None if err != core.SD_ERR_NONE else data


def sdd_value_get_enum_name(value: core.sd_value_t) -> str:
    b_name = sdd_value_get_enum_name_wrap(value)
    return b_name.decode("utf-8")


def sdd_value_get_enum_value(value: core.sd_value_t) -> core.sd_value_t:
    return sdd_value_get_enum_value_wrap(value)


def sdd_value_get_list_n_values(value: core.sd_value_t) -> int:
    return sdd_value_get_list_n_values_wrap(value)


def sdd_value_get_list_value_at(value: core.sd_value_t, index: int) -> core.sd_value_t:
    return sdd_value_get_list_value_at_wrap(value, index)


def sdd_value_get_variant_name(value: core.sd_value_t) -> str:
    b_name = sdd_value_get_variant_name_wrap(value)
    return b_name.decode("utf-8")


def sdd_value_get_variant_value(value: core.sd_value_t) -> core.sd_value_t:
    return sdd_value_get_variant_value_wrap(value)


def sdd_value_get_imported_size(value: core.sd_value_t) -> int:
    return sdd_value_get_imported_size_wrap(value)


def sdd_value_get_imported_value(value: core.sd_value_t):
    size = sdd_value_get_imported_size(value)
    bytes_data = (core.sd_byte_t * size)()
    err = sdd_value_get_imported_value_wrap(value, bytes_data)
    return None if err != core.SD_ERR_NONE else bytes_data


# 'sequence' object = (none | a list of values | a ramp [first..last]) * a repeat factor


# - 'sequence' constructors
def sdd_sequence_create_nones(count: int) -> Optional[core.sd_sequence_t]:
    return sdd_sequence_create_nones_wrap(count)


def sdd_sequence_create_values(
    type_id: int, count: int, values: List[core.sd_value_t], repeat_factor: int
) -> Optional[core.sd_sequence_t]:
    if not isinstance(values, list):
        return None
    values_array_type = core.sd_value_t * len(values)
    values_array = values_array_type(*values)
    return sdd_sequence_create_values_wrap(type_id, count, values_array, repeat_factor)


# - 'sequence' destructor


def sdd_sequence_close(sequence: core.sd_sequence_t) -> None:
    sdd_sequence_close_wrap(sequence)
