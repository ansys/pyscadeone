
Types declaration
=================

.. currentmodule:: ansys.scadeone.core.swan


A type declaration is a type name and its optional definition.
Type definitions are type expressions, enumerations, variants, and structures. 

.. autoclass:: TypeDecl

Several type declarations can be grouped in a :py:class:`TypeDeclarations` instance.

.. autoclass:: TypeDeclarations

Type definition
---------------

The class hierarchy of type definition is shown in the next figure:

.. figure:: type_defs.svg

  Type definitions class diagram


.. autoclass:: TypeDefinition

.. autoclass:: ExprTypeDefinition

Enumeration
~~~~~~~~~~~~

.. autoclass:: EnumTypeDefinition

Variant
~~~~~~~

A variant is represented by a :py:class:`VariantTypeDefinition` instance which contains
a list of :py:class:`VariantConstructor` instances representing the variant cases:

- a simple tag
- a tag with a type expression
- a complex tag with structure expression

.. autoclass:: VariantTypeDefinition

.. autoclass:: VariantConstructor

.. autoclass:: VariantSimple

.. autoclass:: VariantTypeExpression

.. autoclass:: VariantStruct

Structures
~~~~~~~~~~

.. autoclass:: StructTypeDefinition

.. autoclass:: StructField


Type expression
---------------

A type defined by a type expression has its definition stored as 
a :py:class:`ExprTypeDefinition` instance which contains the type expression
as a :py:class:`TypeExpression` instance. The :py:class:`TypeExpression` is the
base class for the type expressions given by the following figure:

.. figure:: type_expr.svg

  Type expressions class diagram

.. autoclass:: TypeExpression 

Predefined types
~~~~~~~~~~~~~~~~

:py:class:`PredefinedType` class is the base class for the classes:

Signed integer types
  Int8Type, Int16Type, Int32Type, Int64Type

Unsigned integer types 
  Uint8Type, Uint16Type, Uint32Type, Uint64Type

Floating point types
  Float32Type, Float64Type

Other types
  BoolType, CharType


.. autoclass:: PredefinedType

Sized types
~~~~~~~~~~~

Definition of types like ``T = signed<<n>>`` or ``T = unsigned<<n>>`` where *n* statically evaluates to one 
of the values: 8, 16, 32, or 64. 


.. autoclass:: SizedTypeExpression

Reference to other types and generic types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: TypeReferenceExpression

.. autoclass:: VariableTypeExpression

Arrays
~~~~~~

.. autoclass:: ArrayTypeExpression

Protected type expression
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ProtectedTypeExpression
