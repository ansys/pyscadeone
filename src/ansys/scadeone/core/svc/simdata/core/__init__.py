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

from enum import IntEnum


###########################################################################
# .sd types & constants
sd_bool_t = ctypes.c_ubyte
sd_bool_true = ctypes.c_ubyte(1)
sd_bool_false = ctypes.c_ubyte(0)
sd_byte_t = ctypes.c_ubyte

sd_int8_t = ctypes.c_int8
sd_uint8_t = ctypes.c_uint8
sd_int16_t = ctypes.c_int16
sd_uint16_t = ctypes.c_uint16
sd_int32_t = ctypes.c_int32
sd_uint32_t = ctypes.c_uint32
sd_int64_t = ctypes.c_int64
sd_uint64_t = ctypes.c_uint64
sd_float32_t = ctypes.c_float
sd_float64_t = ctypes.c_double

sd_id_t = ctypes.c_int64
sd_err_t = ctypes.c_int32
sd_size_t = ctypes.c_size_t
sde_kind_t = ctypes.c_int32
sdt_class_t = ctypes.c_int32
sdd_value_class_t = ctypes.c_int32
sdd_sequence_class_t = ctypes.c_int32
sd_value_iterator_t = ctypes.c_void_p
sd_value_t = ctypes.c_void_p
sd_sequence_t = ctypes.c_void_p

sd_pfn_vsize_get_bytes_size_t = ctypes.CFUNCTYPE(sd_size_t, ctypes.c_void_p)
sd_pfn_vsize_to_bytes_t = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(sd_byte_t))

SD_ID_INVALID = -1
SD_SIZE_NONE = 2**64 - 1
SD_TAG_VALUE_NONE = -1
SD_ERR_NONE = 0
SDT_NONE = SD_ID_INVALID


class TypeClass(IntEnum):
    UNDEFINED = SD_ID_INVALID
    PREDEF = 0
    STRUCT = 1
    ARRAY = 2
    ENUM = 3
    VARIANT = 4
    IMPORTED = 5


class PredefinedType(IntEnum):
    CHAR = 0
    # CHAR16 = 1 # Reserved
    # CHAR32 = 2 # Reserved
    BOOL = 3
    INT8 = 4
    INT16 = 5
    INT32 = 6
    INT64 = 7
    UINT8 = 8
    UINT16 = 9
    UINT32 = 10
    UINT64 = 11
    FLOAT32 = 12
    FLOAT64 = 13


class SdeKind(IntEnum):
    NONE = SD_ID_INVALID
    SENSOR = 0
    INPUT = 1
    OUTPUT = 2
    WIRE = 3
    LOCAL = 4
    PROBE = 5
    GROUP_ITEM = 6
    ASSUME = 7
    GUARANTEE = 8
    SIGNAL = 9
    OPERATOR = 10
    INSTANCE = 11
    AUTOMATON = 12
    STATE = 13
    FORK = 14
    TRANSITION = 15
    IF_BLOCK = 16
    WHEN_BLOCK = 17
    BRANCH = 18
    ASSERT = 19


class DataClass(IntEnum):
    UNDEFINED = -1
    NONE = 0
    PREDEF = 1
    LIST = 2
    ENUM = 3
    VARIANT = 4
    UNTYPED_VARIANT_CONSTRUCTOR = 5
    IMPORTED = 6
