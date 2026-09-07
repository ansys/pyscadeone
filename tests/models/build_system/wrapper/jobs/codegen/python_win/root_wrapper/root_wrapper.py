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

from pathlib import Path
import ctypes

# load the SCADE executable code
_lib_path = Path(__file__).parent / "root_wrapper.dll"
_lib = ctypes.cdll.LoadLibrary(str(_lib_path))


def _ctypes_array2tuple(value: ctypes.Array) -> tuple:
    if not isinstance(value, ctypes.Array):
        raise TypeError("Expected a ctypes.Array")
    return tuple(
        _ctypes_array2tuple(item) if isinstance(item, ctypes.Array) else item for item in value
    )


# operator inputs
class operator0_module0_Inputs:
    def __init__(self) -> None:
        self._i0: int = 0

    @property
    def i0(self) -> int:
        return self._i0

    @i0.setter
    def i0(self, value: int) -> None:
        self._i0 = value


# operator outputs
class operator0_module0_Outputs:
    def __init__(self) -> None:
        self._o0 = ctypes.c_int32(0)

    @property
    def o0(self) -> int:
        return self._o0


class operator0_module0:
    def __init__(self) -> None:
        self.cycle_fct = _lib.operator0_module0
        self.cycle_fct.argtypes = [
            ctypes.c_int32,
        ]
        self.cycle_fct.restype = ctypes.c_int32
        self.inputs = operator0_module0_Inputs()
        self.outputs = operator0_module0_Outputs()

    def reset(self) -> None:
        # no reset function
        pass

    def cycle(self, cycles: int = 1) -> None:
        for i in range(cycles):
            self.outputs._o0 = self.cycle_fct(
                self.inputs._i0,
            )


# operator inputs
class operator1_module0_Inputs:
    def __init__(self) -> None:
        self._i0: int = 0

    @property
    def i0(self) -> int:
        return self._i0

    @i0.setter
    def i0(self, value: int) -> None:
        self._i0 = value


# operator outputs
class operator1_module0_Outputs:
    def __init__(self) -> None:
        self._o0 = ctypes.c_int32(0)

    @property
    def o0(self) -> int:
        return self._o0


class operator1_module0:
    def __init__(self) -> None:
        self.cycle_fct = _lib.operator1_module0
        self.cycle_fct.argtypes = [
            ctypes.c_int32,
        ]
        self.cycle_fct.restype = ctypes.c_int32
        self.inputs = operator1_module0_Inputs()
        self.outputs = operator1_module0_Outputs()

    def reset(self) -> None:
        # no reset function
        pass

    def cycle(self, cycles: int = 1) -> None:
        for i in range(cycles):
            self.outputs._o0 = self.cycle_fct(
                self.inputs._i0,
            )


# end of file
