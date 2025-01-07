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

# cSpell: ignore vsize ndarray

import abc
from typing import Tuple, Optional, Any, List

from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.svc.simdata.core as core
import ansys.scadeone.core.svc.simdata.core.dll_wrap as dll_wrap
import ansys.scadeone.core.svc.simdata.defs as defs


class _SdFactory:
    @classmethod
    def load_type(cls, type_id: int) -> Optional[defs.Type]:
        # Predefined type => return it
        predefined_type = defs.PredefinedType.get(type_id)
        if predefined_type is not None:
            return predefined_type
        name = dll_wrap.sdt_get_name(type_id)
        type_class = dll_wrap.sdt_get_class(type_id)
        if type_class == core.TypeClass.STRUCT:
            nb_fields = dll_wrap.sdt_struct_get_n_fields(type_id)
            fields = []
            for i in range(0, nb_fields):
                field_name = dll_wrap.sdt_struct_get_field_name(type_id, i)
                field_offset = dll_wrap.sdt_struct_get_field_offset(type_id, i)
                field_type_id = dll_wrap.sdt_struct_get_field_type(type_id, i)
                field_type = cls.load_type(field_type_id)
                fields.append(defs.StructTypeField(field_name, field_offset, field_type))
            return defs.StructType(type_id, fields, name)
        elif type_class == core.TypeClass.ARRAY:
            base_type_id = dll_wrap.sdt_array_get_base_type(type_id)
            base_type = cls.load_type(base_type_id)
            dims = dll_wrap.sdt_array_get_dims(type_id)
            return defs.ArrayType(type_id, base_type, dims)
        elif type_class == core.TypeClass.ENUM:
            base_type_id = dll_wrap.sdt_enum_get_base_type(type_id)
            nb_values = dll_wrap.sdt_enum_get_n_values(type_id)
            enum_values = []
            for i in range(0, nb_values):
                tag_name = dll_wrap.sdt_enum_get_value_name(type_id, i)
                int_value = dll_wrap.sdt_enum_get_value_value(type_id, i)
                enum_values.append(defs.EnumTypeValue(tag_name, int_value))
            return defs.EnumType(type_id, defs.PredefinedType.get(base_type_id), enum_values, name)
        elif type_class == core.TypeClass.VARIANT:
            nb_constructors = dll_wrap.sdt_variant_get_n_constructors(type_id)
            constructors = []
            for i in range(0, nb_constructors):
                constructor_name = dll_wrap.sdt_variant_get_constructor_name(type_id, i)
                constructor_value_type_id = dll_wrap.sdt_variant_get_constructor_value_type(
                    type_id, i
                )
                constructor_value_type = (
                    None
                    if constructor_value_type_id == core.SDT_NONE
                    else cls.load_type(constructor_value_type_id)
                )
                constructors.append(
                    defs.VariantTypeConstructor(constructor_name, constructor_value_type)
                )
            return defs.VariantType(type_id, constructors, name)
        elif type_class == core.TypeClass.IMPORTED:
            mem_size = dll_wrap.sdt_get_size(type_id)
            vsize = dll_wrap.sdt_imported_is_variable_size(type_id)
            return defs.ImportedType(type_id, mem_size, vsize, name)
        return None

    @classmethod
    def load_element(
        cls, file: defs.FileBase, parent: Optional[defs.ElementBase], elem_id: int
    ) -> defs.ElementBase:
        elem_name = dll_wrap.sde_get_name(elem_id)
        elem_type_id = dll_wrap.sde_get_type(elem_id)
        elem_type = cls.load_type(elem_type_id)
        elem_kind = defs.ElementKind(dll_wrap.sde_get_kind(elem_id))
        elem = Element(file, elem_id, parent, elem_name, elem_type, elem_kind)
        return elem

    @classmethod
    def build_core_sd_value(cls, py_value: Any, sd_type: defs.Type) -> Optional[core.sd_value_t]:
        if py_value is None:
            return dll_wrap.sdd_value_create_none()
        if isinstance(sd_type, defs.PredefinedType):
            if sd_type.kind == defs.PredefinedTypeKind.CHAR:
                return dll_wrap.sdd_value_create_predef_char(py_value)
            elif sd_type.kind == defs.PredefinedTypeKind.BOOL:
                return dll_wrap.sdd_value_create_predef_bool(py_value)
            elif sd_type.kind == defs.PredefinedTypeKind.INT8:
                return dll_wrap.sdd_value_create_predef_int8(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.INT16:
                return dll_wrap.sdd_value_create_predef_int16(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.INT32:
                return dll_wrap.sdd_value_create_predef_int32(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.INT64:
                return dll_wrap.sdd_value_create_predef_int64(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.UINT8:
                return dll_wrap.sdd_value_create_predef_uint8(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.UINT16:
                return dll_wrap.sdd_value_create_predef_uint16(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.UINT32:
                return dll_wrap.sdd_value_create_predef_uint32(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.UINT64:
                return dll_wrap.sdd_value_create_predef_uint64(int(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.FLOAT32:
                return dll_wrap.sdd_value_create_predef_float32(float(py_value))
            elif sd_type.kind == defs.PredefinedTypeKind.FLOAT64:
                return dll_wrap.sdd_value_create_predef_float64(float(py_value))
            else:
                return None
        elif isinstance(sd_type, defs.StructType):
            if not isinstance(py_value, (list, tuple)) or len(py_value) != len(sd_type.fields):
                return None
            csd_values = []
            for py_value_item, field in zip(py_value, sd_type.fields):
                csd_value = cls.build_core_sd_value(py_value_item, field.sd_type)
                if csd_value is None:
                    return None
                csd_values.append(csd_value)
            return dll_wrap.sdd_value_create_list(len(csd_values), csd_values)
        elif isinstance(sd_type, defs.ArrayType):
            # for numpy ndarray:
            if hasattr(py_value, "shape"):
                if list(py_value.shape) != sd_type.dims:
                    return None
                array_cell_type = (
                    sd_type.base_type
                    if len(sd_type.dims) == 1
                    else defs.ArrayType(0, sd_type.base_type, sd_type.dims[1:])
                )
                csd_values = []
                for py_value_item, i in zip(py_value, range(0, sd_type.dims[0])):
                    csd_value = cls.build_core_sd_value(py_value_item, array_cell_type)
                    if csd_value is None:
                        return None
                    csd_values.append(csd_value)
                return dll_wrap.sdd_value_create_list(len(csd_values), csd_values)
            elif isinstance(py_value, (list, tuple)):
                if len(py_value) != sd_type.dims[0]:
                    return None
                array_cell_type = (
                    sd_type.base_type
                    if len(sd_type.dims) == 1
                    else defs.ArrayType(0, sd_type.base_type, sd_type.dims[1:])
                )
                csd_values = []
                for py_value_item, i in zip(py_value, range(0, sd_type.dims[0])):
                    csd_value = cls.build_core_sd_value(py_value_item, array_cell_type)
                    if csd_value is None:
                        return None
                    csd_values.append(csd_value)
                return dll_wrap.sdd_value_create_list(len(csd_values), csd_values)
            else:
                return None
        elif isinstance(sd_type, defs.EnumType):
            return dll_wrap.sdd_value_create_enum(py_value)
        elif isinstance(sd_type, defs.VariantType):
            csd_value = None
            if isinstance(py_value, tuple):
                if len(py_value) < 1 or len(py_value) > 2:
                    return None
                ctor_name = py_value[0]
                if len(py_value) == 2:
                    ctor = sd_type.find_constructor(ctor_name)
                    if ctor is None or ctor.value_type is None:
                        return None
                    csd_value = cls.build_core_sd_value(py_value[1], ctor.value_type)
            elif isinstance(py_value, str):
                ctor_name = py_value
            else:
                return None
            return dll_wrap.sdd_value_create_variant(ctor_name, csd_value)
        elif isinstance(sd_type, defs.ImportedType):
            return dll_wrap.sdd_value_create_imported(py_value)
        return None

    @classmethod
    def load_sd_value(cls, csd_value: core.sd_value_t) -> defs.Value:
        value_class = dll_wrap.sdd_value_get_class(csd_value)
        if value_class is core.DataClass.NONE:
            return defs.NoneValue()
        if value_class is core.DataClass.PREDEF:
            predef_id = dll_wrap.sdd_value_get_predef_type_id(csd_value)
            if predef_id == core.PredefinedType.CHAR:
                cui8 = dll_wrap.sdd_value_get_predef_uint8(csd_value)
                if cui8 is None:
                    raise ScadeOneException("cannot read char value")
                return defs.PredefinedCharValue(cui8)
            if predef_id == core.PredefinedType.BOOL:
                cui8 = dll_wrap.sdd_value_get_predef_uint8(csd_value)
                if cui8 is None:
                    raise ScadeOneException("cannot read bool value")
                return defs.PredefinedBoolValue(cui8)
            if predef_id == core.PredefinedType.INT8:
                ci8 = dll_wrap.sdd_value_get_predef_int8(csd_value)
                if ci8 is None:
                    raise ScadeOneException("cannot read int8 value")
                return defs.PredefinedInt8Value(ci8)
            if predef_id == core.PredefinedType.INT16:
                ci16 = dll_wrap.sdd_value_get_predef_int16(csd_value)
                if ci16 is None:
                    raise ScadeOneException("cannot read int16 value")
                return defs.PredefinedInt16Value(ci16)
            if predef_id == core.PredefinedType.INT32:
                ci32 = dll_wrap.sdd_value_get_predef_int32(csd_value)
                if ci32 is None:
                    raise ScadeOneException("cannot read int32 value")
                return defs.PredefinedInt32Value(ci32)
            if predef_id == core.PredefinedType.INT64:
                ci64 = dll_wrap.sdd_value_get_predef_int64(csd_value)
                if ci64 is None:
                    raise ScadeOneException("cannot read int64 value")
                return defs.PredefinedInt64Value(ci64)
            if predef_id == core.PredefinedType.UINT8:
                cui8 = dll_wrap.sdd_value_get_predef_uint8(csd_value)
                if cui8 is None:
                    raise ScadeOneException("cannot read uint8 value")
                return defs.PredefinedUInt8Value(cui8)
            if predef_id == core.PredefinedType.UINT16:
                cui16 = dll_wrap.sdd_value_get_predef_uint16(csd_value)
                if cui16 is None:
                    raise ScadeOneException("cannot read uint16 value")
                return defs.PredefinedUInt16Value(cui16)
            if predef_id == core.PredefinedType.UINT32:
                cui32 = dll_wrap.sdd_value_get_predef_uint32(csd_value)
                if cui32 is None:
                    raise ScadeOneException("cannot read uint32 value")
                return defs.PredefinedUInt32Value(cui32)
            if predef_id == core.PredefinedType.UINT64:
                cui64 = dll_wrap.sdd_value_get_predef_uint64(csd_value)
                if cui64 is None:
                    raise ScadeOneException("cannot read uint64 value")
                return defs.PredefinedUInt64Value(cui64)
            if predef_id == core.PredefinedType.FLOAT32:
                cf32 = dll_wrap.sdd_value_get_predef_float32(csd_value)
                if cf32 is None:
                    raise ScadeOneException("cannot read float32 value")
                return defs.PredefinedFloat32Value(cf32)
            if predef_id == core.PredefinedType.FLOAT64:
                cf64 = dll_wrap.sdd_value_get_predef_float64(csd_value)
                if cf64 is None:
                    raise ScadeOneException("cannot read float64 value")
                return defs.PredefinedFloat64Value(cf64)
        if value_class is core.DataClass.LIST:
            n_values = dll_wrap.sdd_value_get_list_n_values(csd_value)
            values = []
            for i in range(0, n_values):
                values.append(cls.load_sd_value(dll_wrap.sdd_value_get_list_value_at(csd_value, i)))
            return defs.ListValue(values)
        if value_class is core.DataClass.ENUM:
            return defs.EnumValue(dll_wrap.sdd_value_get_enum_name(csd_value))
        if value_class is core.DataClass.VARIANT:
            name = dll_wrap.sdd_value_get_variant_name(csd_value)
            csd_variant_value = dll_wrap.sdd_value_get_variant_value(csd_value)
            sd_value = None if csd_variant_value is None else cls.load_sd_value(csd_variant_value)
            return defs.VariantValue(name, sd_value)
        if value_class is core.DataClass.UNTYPED_VARIANT_CONSTRUCTOR:
            return defs.UntypedVariantConstructorValue()
        if value_class is core.DataClass.IMPORTED:
            byte_values = dll_wrap.sdd_value_get_imported_value(csd_value)
            return defs.ImportedValue(byte_values)
        return defs.NoneValue()


class Element(defs.ElementBase):
    """Class for simdata elements"""

    def __init__(
        self,
        file: defs.FileBase,
        elem_id: int,
        parent: Optional[defs.ElementBase],
        name: str,
        sd_type: Optional[defs.Type],
        kind: defs.ElementKind,
    ) -> None:
        super().__init__(file, parent, name, sd_type, kind)
        self._elem_id = elem_id
        # read children elements
        children_elements_ids = dll_wrap.sde_get_children(self._elem_id)
        if children_elements_ids is None:
            raise ScadeOneException('cannot read children elements for "{0}"'.format(self._name))
        for child_id in children_elements_ids:
            self._children_elements.append(_SdFactory.load_element(file, self, child_id))

    @property
    def elem_id(self) -> int:
        return self._elem_id

    @defs.ElementBase.name.setter
    def name(self, name: str) -> None:
        if dll_wrap.sde_set_name(self._elem_id, name) != core.SD_ERR_NONE:
            raise ScadeOneException(
                "cannot set element name for element with id {0}".format(self._elem_id)
            )
        self._name = name

    @defs.ElementBase.sd_type.setter
    def sd_type(self, sd_type: Optional[defs.Type]) -> None:
        if (
            dll_wrap.sde_set_type(self._elem_id, sd_type.type_id if sd_type else core.SDT_NONE)
            != core.SD_ERR_NONE
        ):
            raise ScadeOneException(
                "cannot set element type for element with id {0}".format(self._elem_id)
            )
        self._sd_type = sd_type

    @defs.ElementBase.kind.setter
    def kind(self, kind: defs.ElementKind) -> None:
        if dll_wrap.sde_set_kind(self._elem_id, core.SdeKind(kind)) != core.SD_ERR_NONE:
            raise ScadeOneException(
                "cannot set element kind for element with id {0}".format(self._elem_id)
            )
        self._kind = kind

    def add_child_element(
        self, name: str, sd_type: defs.Type = None, kind: defs.ElementKind = defs.ElementKind.NONE
    ) -> defs.ElementBase:
        """Add a child to element

        Parameters
        ----------
        name : str
            child element name
        sd_type : Type, optional
            child element type
        kind : ElementKind, optional
            child element kind

        Returns
        -------
        ElementBase
            Created child element
        """
        elem_id = dll_wrap.sde_create(
            self._elem_id, name, sd_type.type_id if sd_type else core.SDT_NONE, core.SdeKind(kind)
        )
        elem = Element(self._file, elem_id, self, name, sd_type, kind)
        self._children_elements.append(elem)
        return elem

    def remove_child_element(self, element: "Element") -> None:
        """Remove a child from element

        Parameters
        ----------
        element : Element
            element to remove

        Raises
        ------
        ScadeOneException
            child could not be removed
        """
        if dll_wrap.sde_remove(element.elem_id) != core.SD_ERR_NONE:
            raise ScadeOneException("cannot remove element with id {0}".format(element.elem_id))
        self._children_elements.remove(element)

    def append_value(self, py_value: Any) -> None:
        """Add a value to an element or appends to the last sequence of values if any.
        This method shall NOT be used to add a single value after a multiple cycles sequence
        as it would also be repeated alongside the previous sequence.
        Prefer using append_values([py_value]) instead in such case.

        Parameters
        ----------
        py_value : Any
            value that has a type corresponding to the element

        Raises
        ------
        ScadeOneException
            value is invalid or could not be added
        """
        csd_value = _SdFactory.build_core_sd_value(py_value, self.sd_type)
        if csd_value is None:
            raise ScadeOneException(f"invalid value: {py_value}")
        ret = dll_wrap.sdd_append_value(self._elem_id, csd_value)
        dll_wrap.sdd_value_close(csd_value)
        if ret != core.SD_ERR_NONE:
            raise ScadeOneException("cannot append value")

    def append_nones(self, count: int) -> None:
        """Add a sequence of none values to an element (undefined cycle values)

        Parameters
        ----------
        count : int
            number of Nones to add

        Raises
        ------
        ScadeOneException
            cannot create or append nones sequence
        """
        sequence = dll_wrap.sdd_sequence_create_nones(count)
        if not sequence:
            raise ScadeOneException("cannot create nones sequence")
        ret = dll_wrap.sdd_append_sequence(self.elem_id, sequence)
        dll_wrap.sdd_sequence_close(sequence)
        if ret != core.SD_ERR_NONE:
            raise ScadeOneException("cannot append nones sequence")

    def append_values(self, py_values: List[Any], repeat_factor: Optional[int] = 1) -> None:
        """Create a new sequence of one or multiple values.
        Do not use repeat factor for array and structure types.
        Do not use this for structure or array types that already have any value,
        use append_value() instead in such case.

        Parameters
        ----------
        py_values : List[Any]
            list of value(s) to add
        repeat_factor : Optional[int], optional
            number of times to add, by default 1 (no repeat), do not use with non scalar values

        Raises
        ------
        ScadeOneException
            Invalid repeat, none contained in values, invalid values, cannot create or append
            values sequence, used repeat factor for array or structure types
        """
        if repeat_factor < 1:
            raise ScadeOneException("invalid repeat factor")
        if isinstance(self.sd_type, defs.StructType) or isinstance(self.sd_type, defs.ArrayType):
            if repeat_factor > 1:
                raise ScadeOneException("no repeat factor allowed for structure and array types")
            if any(self.read_values()):
                raise ScadeOneException("structure/array type already has an existing sequence")
        csd_values = []
        for py_value in py_values:
            if py_value is None:
                raise ScadeOneException("values sequence cannot contain 'none'")
            csd_value = _SdFactory.build_core_sd_value(py_value, self.sd_type)
            if csd_value is None:
                raise ScadeOneException(f"invalid value: {py_value} from {py_values}")
            csd_values.append(csd_value)
        sequence = dll_wrap.sdd_sequence_create_values(
            self.sd_type.type_id, len(csd_values), csd_values, repeat_factor
        )
        if not sequence:
            raise ScadeOneException("cannot create values sequence")
        ret = dll_wrap.sdd_append_sequence(self._elem_id, sequence)
        dll_wrap.sdd_sequence_close(sequence)
        if ret != core.SD_ERR_NONE:
            raise ScadeOneException("cannot append values sequence")

    def read_values(
        self, start: Optional[int] = None, n: Optional[int] = None
    ) -> defs.Iterator[defs.Value]:
        """Read element values

        Parameters
        ----------
        start : int, optional
            start index for reading, beginning if not specified
        n : int, optional
            number of values to read, runs until end if not specified

        Yields
        ------
        Iterator[Value]
            each value read
        """
        value_iter = dll_wrap.sdd_value_iter_create(self._elem_id)
        if value_iter:
            if start:
                if dll_wrap.sdd_value_iter_seek(value_iter, start) != core.SD_ERR_NONE:
                    raise ScadeOneException(
                        "cannot seek index for element with id {1}: invalid start index {0}".format(
                            start, self._elem_id
                        )
                    )
            if n is None:
                n = core.SD_SIZE_NONE

            for i in range(0, n):
                csd_value = dll_wrap.sdd_value_iter_get_value(value_iter)
                if csd_value is None:
                    break
                yield _SdFactory.load_sd_value(csd_value)
                dll_wrap.sdd_value_close(csd_value)
            dll_wrap.sdd_value_iter_close(value_iter)

    def clear_values(self) -> None:
        """Clear all values of element

        Raises
        ------
        ScadeOneException
            values could not be cleared
        """
        value_iter = dll_wrap.sdd_value_iter_create(self._elem_id)
        if value_iter and dll_wrap.sdd_value_iter_clear_values(value_iter) != core.SD_ERR_NONE:
            raise ScadeOneException(
                "cannot clear values for element with id {0}".format(self._elem_id)
            )


class File(defs.FileBase):
    """Simdata files class"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, file_id: int) -> None:
        super().__init__()
        self._file_id = file_id
        # read root elements
        elements_ids = dll_wrap.sde_get_children(self._file_id)
        if elements_ids is None:
            raise ScadeOneException("cannot read root elements")
        for elem_id in elements_ids:
            self._elements.append(_SdFactory.load_element(self, None, elem_id))

    def add_element(
        self, name: str, sd_type: defs.Type = None, kind: defs.ElementKind = defs.ElementKind.NONE
    ) -> defs.ElementBase:
        """Create and add an element to file

        Parameters
        ----------
        name : str
            element name
        sd_type : Type, optional
            type of element
        kind : ElementKind, optional
            kind of element

        Returns
        -------
        ElementBase
            The new element that was added to file
        """

        elem_id = dll_wrap.sde_create(
            self._file_id, name, sd_type.type_id if sd_type else core.SDT_NONE, core.SdeKind(kind)
        )
        elem = _SdFactory.load_element(self, None, elem_id)
        self._elements.append(elem)
        return elem

    def remove_element(self, element: Element) -> None:
        """Delete an element from file

        Parameters
        ----------
        element : Element
            element to delete

        Raises
        ------
        ScadeOneException
            element could not be found or deleted
        """
        if dll_wrap.sde_remove(element.elem_id) != core.SD_ERR_NONE:
            raise ScadeOneException("cannot remove element with id {0}".format(element.elem_id))
        self._elements.remove(element)

    def get_version(self) -> str:
        """Get the file version

        Returns
        -------
        str
            Version number
        """
        return dll_wrap.sdf_get_version(self._file_id)

    def close(self) -> None:
        """Close a file

        Raises
        ------
        ScadeOneException
            Could not close file or file was not opened
        """
        if dll_wrap.sdf_close(self._file_id) != core.SD_ERR_NONE:
            raise ScadeOneException("cannot close file with id {0}".format(self._file_id))

    def __str__(self) -> str:
        s = "*** Elements:\n"
        for elem in self._elements:
            s += str(elem)
        return s


def open_file(file_path: str) -> defs.FileBase:
    """Open a simdata file

    Parameters
    ----------
    file_path : str
        path of the file

    Returns
    -------
    FileBase
        The opened file

    Raises
    ------
    ScadeOneException
        file could not be opened
    """
    file_id = dll_wrap.sdf_open(file_path)
    if file_id == core.SD_ID_INVALID:
        raise ScadeOneException('cannot open file "{0}"'.format(file_path))
    return File(file_id)


def create_file(file_path: str) -> defs.FileBase:
    """Create a simdata file

    Parameters
    ----------
    file_path : str
        path of the file

    Returns
    -------
    FileBase
        The created file

    Raises
    ------
    ScadeOneException
        file could not be created
    """
    file_id = dll_wrap.sdf_create(file_path)
    if file_id == core.SD_ID_INVALID:
        raise ScadeOneException('cannot create file "{0}"'.format(file_path))
    return File(file_id)


def create_struct_type(fields: List[Tuple], name: str = "") -> defs.StructType:
    """Create a structure type

    Parameters
    ----------
    fields : List[Tuple]
        all fields of the structure
    name : str, optional
        structure name

    Returns
    -------
    StructType
        The created structure type

    Raises
    ------
    ScadeOneException
        structure type could not be created,
        arguments are invalid, or field names duplicate
    """
    if (
        not isinstance(fields, list)
        or len(fields) == 0
        or not all(
            isinstance(f, tuple)
            and len(f) == 2
            and isinstance(f[0], str)
            and isinstance(f[1], defs.Type)
            for f in fields
        )
    ):
        raise ScadeOneException("invalid arguments in creation of struct type")
    struct_fields = []
    field_names = []
    for f in fields:
        field_name = f[0]
        field_type = f[1]
        if not isinstance(field_name, str):
            raise ScadeOneException("argument type error in creation of struct type")
        if field_name in field_names:
            raise ScadeOneException(
                'cannot add again field "{0}" to struct type'.format(field_name)
            )
        field_names.append(field_name)
        struct_fields.append(defs.StructTypeField(field_name, core.SD_SIZE_NONE, field_type))

    struct_type_id = dll_wrap.sdt_struct_create(core.SD_SIZE_NONE)
    if struct_type_id == core.SD_ID_INVALID:
        raise ScadeOneException("cannot create structure type")
    dll_wrap.sdt_set_name(struct_type_id, name)
    for struct_field in struct_fields:
        err = dll_wrap.sdt_struct_add_field(
            struct_type_id, struct_field.name, struct_field.offset, struct_field.sd_type.type_id
        )
        if err != core.SD_ERR_NONE:
            raise ScadeOneException(
                'cannot create field "{0}" of structure type'.format(struct_field.name)
            )
    return defs.StructType(struct_type_id, struct_fields, name)


def create_array_type(base_type: defs.Type, dims: List[int], name: str = "") -> defs.ArrayType:
    """Create a multi dimensional array type

    Parameters
    ----------
    base_type : Type
        type of array
    dims : List[int]
        array dimensions
    name : str, optional
        array name

    Returns
    -------
    ArrayType
        Created array type

    Raises
    ------
    ScadeOneException
        array type could not be created, argument error or none type passed
    """
    if base_type is None:
        raise ScadeOneException("cannot create array type. Base type shall not be None")
    if (
        not isinstance(base_type, defs.Type)
        or not isinstance(dims, list)
        or not all(isinstance(x, int) for x in dims)
        or len(dims) == 0
    ):
        raise ScadeOneException("argument type error in creation of array type")
    array_type_id = dll_wrap.sdt_array_create(base_type.type_id, len(dims), dims)
    if array_type_id == core.SD_ID_INVALID:
        raise ScadeOneException("cannot create array type")
    dll_wrap.sdt_set_name(array_type_id, name)
    return defs.ArrayType(array_type_id, base_type, dims, name)


def create_enum_type(values: List[str], name: str = "") -> defs.EnumType:
    """Create an enumeration type

    Parameters
    ----------
    values : List[str]
        values of the enumeration type
    name : str, optional
        name of enumeration type

    Returns
    -------
    EnumType
        Created enumeration type

    Raises
    ------
    ScadeOneException
        could not create enumeration type, create a value of passed argument
        or invalid arguments in creation
    """
    if len(values) == 0 or not all(isinstance(arg, str) for arg in values):
        raise ScadeOneException("argument type error in creation of enum type")

    enum_type_id = dll_wrap.sdt_enum_create(defs.Int64.type_id)
    if enum_type_id == core.SD_ID_INVALID:
        raise ScadeOneException("cannot create enum type")
    dll_wrap.sdt_set_name(enum_type_id, name)
    int_value = 0
    enum_values = []
    for value_name in values:
        err = dll_wrap.sdt_enum_add_value(enum_type_id, value_name, int_value)
        if err != core.SD_ERR_NONE:
            raise ScadeOneException('cannot create value "{0}" of enum type'.format(value_name))
        int_value = int_value + 1
        enum_values.append(defs.EnumTypeValue(value_name, int_value))
    return defs.EnumType(enum_type_id, defs.Int64, enum_values, name)


def create_variant_type(constructors: List[Tuple], name: str = "") -> defs.VariantType:
    """Create a variant type

    Parameters
    ----------
    constructors : List[Tuple]
        constructors of the variant type
    name : str, optional
        name of variant type

    Returns
    -------
    VariantType
        Created variant type

    Raises
    ------
    ScadeOneException
        variant type could not be created, invalid arguments or duplicate constructor names
    """
    if (
        not isinstance(constructors, list)
        or len(constructors) == 0
        or not all(
            isinstance(c, tuple)
            and len(c) == 2
            and isinstance(c[0], str)
            and (c[1] is None or isinstance(c[1], defs.Type))
            for c in constructors
        )
    ):
        raise ScadeOneException("invalid arguments in creation of variant type")

    variant_constructors = []
    constructor_names = []
    for constructor in constructors:
        constructor_name = constructor[0]
        constructor_value_type = constructor[1]
        if (
            not isinstance(constructor_name, str)
            or not isinstance(constructor_value_type, defs.Type)
            and constructor_value_type
        ):
            raise ScadeOneException("argument type error in creation of variant type")
        if constructor_name in constructor_names:
            raise ScadeOneException(
                'cannot add again constructor "{0}" to variant type'.format(constructor_name)
            )
        constructor_names.append(constructor_name)
        variant_constructors.append(
            defs.VariantTypeConstructor(constructor_name, constructor_value_type)
        )

    variant_type_id = dll_wrap.sdt_variant_create(core.SD_SIZE_NONE)
    if variant_type_id == core.SD_ID_INVALID:
        raise ScadeOneException("cannot create variant type")
    dll_wrap.sdt_set_name(variant_type_id, name)
    for variant_constructor in variant_constructors:
        err = dll_wrap.sdt_variant_add_constructor(
            variant_type_id,
            variant_constructor.name,
            core.SD_SIZE_NONE,
            core.SD_TAG_VALUE_NONE,
            core.SD_SIZE_NONE,
            (
                variant_constructor.value_type.type_id
                if variant_constructor.value_type
                else core.SDT_NONE
            ),
        )
        if err != core.SD_ERR_NONE:
            raise ScadeOneException(
                'cannot create constructor "{0}" of variant type'.format(variant_constructor.name)
            )
    return defs.VariantType(variant_type_id, variant_constructors, name)


def create_imported_type(mem_size: int, name: str = "") -> defs.ImportedType:
    """Create an imported type

    Parameters
    ----------
    mem_size : int
        memory size
    name : str, optional
        imported type name

    Returns
    -------
    ImportedType
        Created imported type

    Raises
    ------
    ScadeOneException
        could not create imported type, argument type error or argument type error
    """
    if not isinstance(mem_size, int) or mem_size is None:
        raise ScadeOneException("argument type error in creation of imported type")
    imported_type_id = dll_wrap.sdt_imported_create(mem_size)
    if imported_type_id == core.SD_ID_INVALID:
        raise ScadeOneException("cannot create imported type")
    dll_wrap.sdt_set_name(imported_type_id, name)
    return defs.ImportedType(imported_type_id, mem_size, False, None, None, name)


def create_vsize_imported_type(
    mem_size: int,
    pfn_vsize_get_bytes_size: defs.PfnVsizeGetBytesSize,
    pfn_vsize_to_bytes: defs.PfnVsizeToBytes,
    name: str = "",
) -> defs.ImportedType:
    if not isinstance(mem_size, int):
        raise ScadeOneException("argument type error in creation of imported type")
    imported_type_id = dll_wrap.sdt_vsize_imported_create(
        mem_size, pfn_vsize_get_bytes_size, pfn_vsize_to_bytes
    )
    if imported_type_id == core.SD_ID_INVALID:
        raise ScadeOneException("cannot create imported type")
    dll_wrap.sdt_set_name(imported_type_id, name)
    return defs.ImportedType(
        imported_type_id, mem_size, True, pfn_vsize_get_bytes_size, pfn_vsize_to_bytes, name
    )
