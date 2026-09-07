Code section items
===================

.. currentmodule:: ansys.scadeone.core.svc.cgmapping.code

CodeElement subclasses
-----------------------

Each code section item is represented by one of the following classes, which all inherit from :py:class:`CodeElement`,
thus provide the :py:meth:`~CodeElement.get_model_element` method to access the associated model element. (see :doc:`model`)

**Functions and Parameters**

- :py:class:`CFunction` - C function declaration
- :py:class:`CParameter` - Function parameter

**Variables and Macros**

- :py:class:`CGlobal` - Global variable
- :py:class:`CMacro` - Macro definition

**Type Definitions**

- :py:class:`CPredefinedType` - Predefined type
- :py:class:`CArray` - Array type definition
- :py:class:`CStructField` - Field within a structure
- :py:class:`CStruct` - Structure type definition
- :py:class:`CEnum` - Enumeration type definition
- :py:class:`CEnumValue` - Value within an enumeration
- :py:class:`CUnion` - Union type definition
- :py:class:`CUnionVariant` - Variant within a union
- :py:class:`CTypedef` - Typedef definition
- :py:class:`CExternalType` - External type

.. _ref_code_container:

Code Container
--------------

A :py:class:`CodeContainer` represents a code unit associated with a pair of C files:

- an **interface file** (``.h`` header)
- an optional **implementation file** (``.c`` source)

Each container holds a list of :py:class:`CDeclaration` items (functions, variables, types, macros, ...)
that are declared or defined in those files.

A container can also be marked as **user-provided**, meaning it needs to be provided by the user.

The full set of containers is accessible from :py:meth:`~ansys.scadeone.core.svc.cgmapping.cgmapping.CGMapping.get_all_code_containers`.

API Documentation
-----------------

.. automodule:: ansys.scadeone.core.svc.cgmapping.code
   :members:
   :exclude-members: CodeRegistry, load_code_from_json, parse_c_declaration, parse_c_enum_value, parse_c_parameter, parse_c_struct_field, parse_c_union_variant, parse_code_container
   :no-inherited-members:

