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

# cSpell: ignore vsize

import abc
from typing import List, Optional, Any, Iterator
from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.svc.simdata.core as core


###########################################################################
# data types


class Type:
    """Represents an abstract data type."""

    def __init__(self, type_id: int, name: str = ""):
        self._type_id = type_id
        self._name = name

    @property
    def type_id(self) -> int:
        return self._type_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name


PredefinedTypeKind = core.PredefinedType


class PredefinedType(Type):
    """
    Predefined Swan types are not stored in file.
    They have hard-coded identifiers that can be used in user types definitions.
    """

    _instances = {}

    def __init__(self, type_id: int):
        try:
            self._kind = PredefinedTypeKind(type_id)
        except:  # noqa: E722
            raise ScadeOneException("cannot create predefined type with id {0}".format(type_id))
        super().__init__(type_id, self.__str__())
        PredefinedType._instances[type_id] = self

    def __str__(self) -> str:
        if self._kind == PredefinedTypeKind.CHAR:
            return "char"
        elif self._kind == PredefinedTypeKind.BOOL:
            return "bool"
        elif self._kind == PredefinedTypeKind.INT8:
            return "int8"
        elif self._kind == PredefinedTypeKind.INT16:
            return "int16"
        elif self._kind == PredefinedTypeKind.INT32:
            return "int32"
        elif self._kind == PredefinedTypeKind.INT64:
            return "int64"
        elif self._kind == PredefinedTypeKind.UINT8:
            return "uint8"
        elif self._kind == PredefinedTypeKind.UINT16:
            return "uint16"
        elif self._kind == PredefinedTypeKind.UINT32:
            return "uint32"
        elif self._kind == PredefinedTypeKind.UINT64:
            return "uint64"
        elif self._kind == PredefinedTypeKind.FLOAT32:
            return "float32"
        elif self._kind == PredefinedTypeKind.FLOAT64:
            return "float64"
        return "<unknown>"

    @property
    def kind(self):
        return self._kind

    @classmethod
    def get(cls, type_id: int) -> Optional["PredefinedType"]:
        return cls._instances[type_id] if type_id in cls._instances else None


Char = PredefinedType(int(PredefinedTypeKind.CHAR))
Bool = PredefinedType(int(PredefinedTypeKind.BOOL))
Int8 = PredefinedType(int(PredefinedTypeKind.INT8))
Int16 = PredefinedType(int(PredefinedTypeKind.INT16))
Int32 = PredefinedType(int(PredefinedTypeKind.INT32))
Int64 = PredefinedType(int(PredefinedTypeKind.INT64))
UInt8 = PredefinedType(int(PredefinedTypeKind.UINT8))
UInt16 = PredefinedType(int(PredefinedTypeKind.UINT16))
UInt32 = PredefinedType(int(PredefinedTypeKind.UINT32))
UInt64 = PredefinedType(int(PredefinedTypeKind.UINT64))
Float32 = PredefinedType(int(PredefinedTypeKind.FLOAT32))
Float64 = PredefinedType(int(PredefinedTypeKind.FLOAT64))


class StructTypeField:
    """Structure type's fields"""

    def __init__(self, name: str, offset: int, sd_type: Type):
        self._name = name
        self._offset = offset
        self._sd_type = sd_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def sd_type(self) -> Type:
        return self._sd_type


class StructType(Type):
    """Structure type defined with structure type fields"""

    def __init__(self, type_id: int, fields: List[StructTypeField], name: str = ""):
        self._fields = fields
        super().__init__(type_id, name)

    @property
    def fields(self) -> List[StructTypeField]:
        return self._fields

    def __str__(self) -> str:
        return "struct{" + ",".join([f.name + ":" + str(f.sd_type) for f in self.fields]) + "}"


class ArrayType(Type):
    """Multidimensional array type"""

    def __init__(self, type_id: int, base_type: Type, dims: List[int], name: str = ""):
        self._base_type = base_type
        self._dims = dims
        super().__init__(type_id, name)

    @property
    def base_type(self) -> Type:
        return self._base_type

    @property
    def dims(self) -> List[int]:
        return self._dims

    def __str__(self) -> str:
        return str(self.base_type) + "^" + "^".join([str(d) for d in self.dims])


class EnumTypeValue:
    """Enumeration type value"""

    def __init__(self, name: str, int_value: int):
        self._name = name
        self._int_value = int_value

    @property
    def name(self) -> str:
        return self._name

    @property
    def int_value(self) -> int:
        return self._int_value


class EnumType(Type):
    """Enumeration type defined with enumeration values"""

    def __init__(
        self, type_id: int, base_type: PredefinedType, values: List[EnumTypeValue], name: str = ""
    ):
        self._base_type = base_type
        self._values = values
        super().__init__(type_id, name)

    @property
    def base_type(self) -> PredefinedType:
        return self._base_type

    @property
    def values(self) -> List[EnumTypeValue]:
        return self._values

    def __str__(self) -> str:
        return (
            self.name
            + " enum{"
            + ",".join([v.name + ":" + str(v.int_value) for v in self.values])
            + "}"
        )


class VariantTypeConstructor:
    """Variant type constructor"""

    def __init__(self, name: str, value_type: Optional[Type]):
        self._name = name
        self._value_type = value_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def value_type(self) -> Optional[Type]:
        return self._value_type


class VariantType(Type):
    """Variant type defined with variant type constructors"""

    def __init__(self, type_id: int, constructors: List[VariantTypeConstructor], name: str = ""):
        self._constructors = constructors
        super().__init__(type_id, name)

    @property
    def constructors(self) -> List[VariantTypeConstructor]:
        return self._constructors

    def find_constructor(self, name: str) -> Optional[VariantTypeConstructor]:
        for c in self._constructors:
            if c.name == name:
                return c
        return None

    def __str__(self) -> str:
        return "|".join(
            [
                c.name + "{" + (str(c.value_type) if c.value_type is not None else "") + "}"
                for c in self.constructors
            ]
        )


PfnVsizeGetBytesSize = core.sd_pfn_vsize_get_bytes_size_t

PfnVsizeToBytes = core.sd_pfn_vsize_to_bytes_t


class ImportedType(Type):
    """Imported Types (stored as byte arrays)"""

    def __init__(
        self,
        type_id: int,
        mem_size: int,
        vsize: bool = False,
        pfn_vsize_get_bytes_size: PfnVsizeGetBytesSize = None,
        pfn_vsize_to_bytes: PfnVsizeToBytes = None,
        name: str = "",
    ):
        self._mem_size = mem_size
        self._vsize = vsize
        self._pfn_vsize_get_bytes_size = pfn_vsize_get_bytes_size
        self._pfn_vsize_to_bytes = pfn_vsize_to_bytes
        super().__init__(type_id, name)

    @property
    def mem_size(self) -> int:
        return self._mem_size

    @property
    def vsize(self) -> bool:
        return self._vsize

    @property
    def pfn_vsize_get_bytes_size(self) -> PfnVsizeGetBytesSize:
        return self._pfn_vsize_get_bytes_size

    @pfn_vsize_get_bytes_size.setter
    def pfn_vsize_get_bytes_size(self, pfn_vsize_get_bytes_size: PfnVsizeGetBytesSize):
        self._pfn_vsize_get_bytes_size = pfn_vsize_get_bytes_size

    @property
    def pfn_vsize_to_bytes(self) -> PfnVsizeToBytes:
        return self._pfn_vsize_to_bytes

    @pfn_vsize_to_bytes.setter
    def pfn_vsize_to_bytes(self, pfn_vsize_to_bytes: PfnVsizeToBytes):
        self._pfn_vsize_to_bytes = pfn_vsize_to_bytes

    def __str__(self) -> str:
        return "<variable size imported>" if self.vsize else "<imported>"


class Value:
    """Interface for all element types values that shall provide a readable string representation"""

    pass


class PredefinedValue(Value):
    """Values for predefined Swan Types"""

    pass


class NoneValue(Value):
    """None Values"""

    def __str__(self):
        return "none"


class PredefinedCharValue(PredefinedValue):
    """Values for predefined type char"""

    def __init__(self, value: core.sd_uint8_t):
        self._value = value

    def __str__(self):
        return "'" + chr(self._value.value) + "'"


class PredefinedBoolValue(PredefinedValue):
    """Values for predefined type boolean"""

    def __init__(self, value: core.sd_uint8_t):
        self._value = True if value else False

    def __str__(self):
        return "true" if self._value else "false"


class PredefinedInt8Value(PredefinedValue):
    """Values for predefined type int 8"""

    def __init__(self, value: core.sd_int8_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedInt16Value(PredefinedValue):
    """Values for predefined type int 16"""

    def __init__(self, value: core.sd_int16_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedInt32Value(PredefinedValue):
    """Values for predefined type int 32"""

    def __init__(self, value: core.sd_int32_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedInt64Value(PredefinedValue):
    """Values for predefined type int 64"""

    def __init__(self, value: core.sd_int64_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedUInt8Value(PredefinedValue):
    """Values for predefined type unsigned int 8"""

    def __init__(self, value: core.sd_uint8_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedUInt16Value(PredefinedValue):
    """Values for predefined type unsigned int 16"""

    def __init__(self, value: core.sd_uint16_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedUInt32Value(PredefinedValue):
    """Values for predefined type unsigned int 32"""

    def __init__(self, value: core.sd_uint32_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedUInt64Value(PredefinedValue):
    """Values for predefined type unsigned int 64"""

    def __init__(self, value: core.sd_uint64_t):
        self._value = value

    def __str__(self):
        return str(self._value.value)


class PredefinedFloat32Value(PredefinedValue):
    """Values for predefined type float 32"""

    def __init__(self, value: core.sd_float32_t):
        self._value = value

    def __str__(self):
        return f"{self._value.value:.5g}"


class PredefinedFloat64Value(PredefinedValue):
    """Values for predefined type float 64"""

    def __init__(self, value: core.sd_float64_t):
        self._value = value

    def __str__(self):
        return f"{self._value.value:.5g}"


class ListValue(Value):
    """Values for list types"""

    def __init__(self, values: List[Value]):
        self._values = values

    def __str__(self):
        return "(" + ",".join([str(v) for v in self._values]) + ")"


class EnumValue(Value):
    """Values for enumeration types"""

    def __init__(self, name: str):
        self._name = name

    def __str__(self):
        return self._name


class VariantValue(Value):
    """Values for variant types"""

    def __init__(self, name: str, value: Optional[Value]):
        self._name = name
        self._value = value

    def __str__(self):
        return self._name + "{" + (str(self._value) if self._value is not None else "") + "}"


class UntypedVariantConstructorValue(Value):
    """No value to return for untyped variant constructor"""

    def __str__(self):
        return ""


class ImportedValue(Value):
    """Values for imported types"""

    def __init__(self, bytes_data):
        self._bytes_data = bytes_data

    def __str__(self):
        return (
            "" if self._bytes_data is None else "".join([f"{by:0>4X}" for by in self._bytes_data])
        )


ElementKind = core.SdeKind


class ElementBase(metaclass=abc.ABCMeta):
    def __init__(
        self,
        file: "FileBase",
        parent: Optional["ElementBase"],
        name: str,
        sd_type: Optional[Type],
        kind: ElementKind,
    ):
        self._file = file
        self._parent = parent
        self._name = name
        self._sd_type = sd_type
        self._kind = kind
        self._children_elements = []  # type: List[ElementBase]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @abc.abstractmethod
    def name(self, name: str) -> None:
        pass

    @property
    def sd_type(self) -> Optional[Type]:
        return self._sd_type

    @sd_type.setter
    @abc.abstractmethod
    def sd_type(self, sd_type: Optional[Type]) -> None:
        pass

    @property
    def kind(self) -> ElementKind:
        return self._kind

    @kind.setter
    @abc.abstractmethod
    def kind(self, kind: ElementKind) -> None:
        pass

    @property
    def parent(self) -> Optional["ElementBase"]:
        return self._parent

    @property
    def children_elements(self) -> List["ElementBase"]:
        return self._children_elements

    @property
    def nb_parents(self):
        if self.parent is None:
            return 0
        return self.parent.nb_parents + 1

    @abc.abstractmethod
    def add_child_element(
        self, name: str, sd_type: Type = None, kind: ElementKind = ElementKind.NONE
    ) -> "ElementBase":
        pass

    @abc.abstractmethod
    def remove_child_element(self, element: "ElementBase") -> None:
        pass

    def find_child_element(self, name: str) -> Optional["ElementBase"]:
        for e in self.children_elements:
            if e.name == name:
                return e
        return None

    @abc.abstractmethod
    def append_value(self, py_value: Any) -> None:
        pass

    def append_nones(self, count) -> None:
        pass

    def append_values(self, py_values: List[Any], repeat_factor: Optional[int] = 1) -> None:
        pass

    @abc.abstractmethod
    def read_values(self, start: Optional[int] = None, n: Optional[int] = None) -> Iterator[Value]:
        pass

    @abc.abstractmethod
    def clear_values(self) -> None:
        pass

    def __str__(self) -> str:
        indent = "    " * self.nb_parents
        type_str = "" if self.sd_type is None else ": " + str(self.sd_type)
        kind_str = self.kind.name if self.kind != ElementKind.NONE else ""
        s = "{0}{1} {2}{3}: ".format(indent, kind_str, self.name, type_str)
        for v in self.read_values():
            s += str(v) + " | "
        s += "\n"
        for child in self.children_elements:
            s += str(child)
        return s


class FileBase:
    def __init__(self) -> None:
        self._elements = []  # type: List[ElementBase]

    @property
    def elements(self) -> List[ElementBase]:
        return self._elements

    @abc.abstractmethod
    def add_element(
        self, name: str, sd_type: Type = None, kind: ElementKind = ElementKind.NONE
    ) -> ElementBase:
        pass

    @abc.abstractmethod
    def remove_element(self, element: ElementBase) -> None:
        pass

    @abc.abstractmethod
    def get_version(self) -> str:
        pass

    @abc.abstractmethod
    def close(self) -> None:
        pass

    def find_element(self, name: str) -> Optional[ElementBase]:
        for e in self.elements:
            if e.name == name:
                return e
        return None

    def __str__(self) -> str:
        s = "*** Elements:\n"
        for elem in self.elements:
            s += str(elem)
        return s
