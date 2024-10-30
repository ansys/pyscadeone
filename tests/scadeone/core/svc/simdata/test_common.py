#
# Copyright (c) 2022-2025 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

import ctypes
import sys


class Imported(ctypes.Structure):
    _fields_ = [("f1", ctypes.c_int8), ("f2", ctypes.c_int16)]


class VSizeImported(ctypes.Structure):
    _fields_ = [("eLen", ctypes.c_short), ("eValue", ctypes.c_void_p)]

    def __init__(self, str_value: str, *args, **kw):
        super().__init__(*args, **kw)
        bytes_value = bytearray(str_value.encode("utf-8"))
        c_bytes_type = ctypes.c_uint8 * len(bytes_value)
        self.c_bytes = c_bytes_type.from_buffer(bytes_value)
        self.eLen = len(bytes_value)
        self.eValue = ctypes.addressof(self.c_bytes)


def vsize_imported_get_bytes_size(src_data: ctypes.c_void_p) -> int:
    vsi_data = ctypes.cast(src_data, ctypes.POINTER(VSizeImported)).contents
    return ctypes.sizeof(ctypes.c_short) + vsi_data.eLen


def vsize_imported_to_bytes(src_data: ctypes.c_void_p, dst_bytes: ctypes.c_void_p) -> None:
    vsi_data = ctypes.cast(src_data, ctypes.POINTER(VSizeImported)).contents
    src_bytes = ctypes.cast(vsi_data.eValue, ctypes.POINTER(ctypes.c_uint8))
    dst_bytes = ctypes.cast(dst_bytes, ctypes.POINTER(ctypes.c_uint8))

    len_bytes = vsi_data.eLen.to_bytes(2, sys.byteorder)
    dst_bytes[0] = ctypes.c_uint8(len_bytes[0])
    dst_bytes[1] = ctypes.c_uint8(len_bytes[1])
    for i_byte in range(0, vsi_data.eLen):
        dst_bytes[i_byte + 2] = src_bytes[i_byte]
