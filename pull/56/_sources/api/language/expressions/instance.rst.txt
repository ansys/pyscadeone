Operator instance
=================

.. currentmodule:: ansys.scadeone.core.swan

An :py:class:`OperatorInstanceApplication` object is an :py:class:`Expression` object 
representing an operator instance call, the called operator being represented 
by an instance of the top-level class :py:class:`OperatorInstance`

A **block** can refer to an operator instance or an operator expression.

.. figure:: instance.svg

  Operator instance class diagram


Note: array-related operations are described in the :ref:`ref_array_operations` section.

Operator instance application
-----------------------------

.. autoclass:: OperatorInstanceApplication


Operator instance base class
----------------------------

.. autoclass:: OperatorInstance



Named operator instance
-----------------------

.. autoclass:: NamedInstance


Operator expressions
--------------------

The :py:class:`OperatorExpression` class is used to represent an operator
expression. The :py:class:`OperatorExpressionInstance` class is used to represent an operator
expression instance, which corresponds to the syntax "*( operator_expression )*".

.. figure:: op_expr.svg

  Operator expression class diagram


.. autoclass:: OperatorExpression

.. autoclass:: OperatorExpressionInstance

Anonymous operator instance
---------------------------

.. autoclass:: AnonymousOperatorWithExpression

.. autoclass:: AnonymousOperatorWithDataDefinition


Higher-order operator instance
------------------------------

Higher-order operations (operations using an operator as parameter) are 
represented by instances of the :py:class:`OperatorExpression` class.

.. figure:: instance_ho.svg
  
  Operator higher-order class diagram

.. list-table:: Higher-order operators 
    :header-rows: 1

    * - Higher-order
      - Application
    * - **map**, **fold**, **mapfold**, **mapi** **foldi**, **mapfoldi**
      - array iterators
    * - **activate** *operator expression* **every**
      - conditional activation
    * - **restart** *operator expression* **every**  
      - conditional restart
      

Iterator
^^^^^^^^

.. autoclass:: Iterator

.. autoclass:: IteratorKind

Activate
^^^^^^^^

.. autoclass:: ActivateEvery

Restart
^^^^^^^

.. autoclass:: RestartOperator


Partial operator instance
-------------------------

.. autoclass:: PartialOperator

.. autoclass:: OptGroupItem


N-ary operator instance
-----------------------

N-ary operator instances are implemented as specific expressions. See :ref:`ref_n_ary_expr` section.


Protected operator expression
-----------------------------

This class is used when an operator expression is syntactically
incorrect and was protected by the serialization process.

.. autoclass:: ProtectedOpExpr


