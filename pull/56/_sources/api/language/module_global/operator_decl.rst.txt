.. _ref_op_decl:

Operators
=========

.. currentmodule:: ansys.scadeone.core.swan

Operator are declared with the :py:class:`OperatorDeclaration` class and defined with the :py:class:`OperatorDefinition` class.

.. figure:: operator_decl.svg

   Operator class diagram

Operator declaration
--------------------

Declares an operator, giving its interface only. In a module interface, an operator declaration can be the declaration of an operator 
which body definition is given in the module body, or it can declare a public imported operator. 
In a module body, an operator declaration is the declaration of a private imported operator if the module has an interface,
otherwise it is the declaration of a public imported operator.

The class :py:class:`SizeParameter` defines size parameters that can be used for array sizes.

The class :py:class:`TypeConstraint` defines constraints that can be applied to generic types.


.. autoclass:: OperatorDeclaration
    :exclude-members: to_str, add_input, add_output, add_diagram

Size parameters
^^^^^^^^^^^^^^^

.. autoclass:: SizeParameter
    :exclude-members: to_str

Type constraints
^^^^^^^^^^^^^^^^

.. autoclass:: TypeConstraint

.. autoclass:: NumericKind

Operator definition
-------------------

Defines an operator with a body in a module body. See :ref:`ref_op_body` for content of the body.
The operator definition has the same interface as the corresponding operator declaration in the module interface, if any,
see :py:class:`OperatorDeclaration`, :py:class:`SizeParameter` and :py:class:`TypeConstraint`.

.. autoclass:: OperatorDefinition
    :exclude-members: to_str, add_input, add_output, add_diagram

