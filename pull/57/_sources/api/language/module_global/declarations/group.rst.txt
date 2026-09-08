.. _ref_group_decl:

.. currentmodule:: ansys.scadeone.core.swan

Group declaration
-----------------

A :py:class:`GroupDecl` object defines a **group** declaration, with a name and 
a :py:class:`GroupTypeExpression` for the type.

A :py:class:`GroupTypeExpression` can be:

- a type expression, represented by a :py:class:`TypeGroupTypeExpression` instance
- or a list of :py:class:`GroupTypeExpression` items, decomposed into two lists:

  - a positional list of :py:class:`GroupTypeExpression` items
  - followed by a list of named :py:class:`GroupTypeExpression` items, represented
    with :py:class:`NamedGroupTypeExpression` instances.


.. figure:: group_type_expr.svg


.. autoclass:: GroupDecl

.. autoclass:: GroupTypeExpression

.. autoclass:: TypeGroupTypeExpression

.. autoclass:: NamedGroupTypeExpression

.. autoclass:: GroupTypeExpressionList

.. autoclass:: GroupDeclarations
