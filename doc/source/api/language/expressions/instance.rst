Operator instance
=================

.. currentmodule:: ansys.scadeone.core.swan

An :py:class:`OperatorInstance` object is an :py:class:`Expression` object 
representing an operator instance call, the called operator being represented 
by an instance of the top-level class :py:class:`OperatorBase`

.. figure:: instance.svg

  Operator instance class diagram


Higher-order operations (operations using an operator as parameter) are 
represented by instances of the :py:class:`OperatorExpression` class.

.. figure:: instance_ho.svg
  
  Operator higher-order class diagram



.. autoclass:: OperatorBase

Operator instance application
-----------------------------


.. autoclass:: OperatorInstance


Named operator instance
-----------------------

.. autoclass:: PathIdOpCall


Anonymous operator instance
---------------------------

.. autoclass:: AnonymousOperatorWithExpression

.. autoclass:: AnonymousOperatorWithDataDefinition


Higher-order operator instance
------------------------------

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

.. autoclass:: Restart


Partial operator instance
-------------------------

.. autoclass:: Partial

.. autoclass:: OptGroupItem


N-ary operator instance
-----------------------

N-ary operator instances are implemented as specific expressions. See :ref:`ref_n_ary_expr` section.


Operator Expressions
--------------------

.. autoclass:: OperatorExpression

.. autoclass:: PrefixOperatorExpression


This class is used when an operator expression is syntactically
incorrect and was protected by the serialization process.

.. autoclass:: ProtectedOpExpr


