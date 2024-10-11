Operator Instance
=================

.. currentmodule:: ansys.scadeone.core.swan

An :py:class:`OperatorInstance` object is an :py:class:`Expression` object 
representing an operator instance call, the called operator being represented 
by an instance of the top-level class :py:class:`OperatorBase`

.. uml::
  :align: center

  @startuml OperatorInstance
  skinparam groupInheritance 2

  Expression <|-- OperatorInstance
  OperatorInstance *-- OperatorBase

  OperatorBase <|-- PathIdOpCall
  OperatorBase <|-- PrefixPrimitive
  note top of PrefixPrimitive
  **flatten**, **pack**, **reverse**
  end note
  PrefixPrimitive <|-- Transpose
  OperatorBase <|-- PrefixOperatorExpression
  note top of PrefixOperatorExpression
  (//op_expr//) [size]
  end note
  PrefixOperatorExpression *-- OperatorExpression
  @enduml

Higher-order operations (operations using an operator as parameter) are 
represented by instances of the :py:class:`OperatorExpression` class.

.. uml::
  :align: center
  
  @startuml HO
  left to right direction
  skinparam groupInheritance 2
  
  OperatorExpression <|-- Iterator
  OperatorExpression <|-- ActivateEvery
  OperatorExpression <|-- Restart
  OperatorExpression <|-- NaryOperator
  OperatorExpression <|-- AnonymousOperatorWithExpression
  OperatorExpression <|-- AnonymousOperatorWithDataDefinition

  @enduml


.. autoclass:: OperatorBase

Operator Instance Application
-----------------------------


.. autoclass:: OperatorInstance


Named Operator Instance
-----------------------

.. autoclass:: PathIdOpCall


Anonymous Operator Instance
---------------------------

.. autoclass:: AnonymousOperatorWithExpression

.. autoclass:: AnonymousOperatorWithDataDefinition


Higher-Order Operator Instance
------------------------------

.. list-table:: Higher-order operators 
    :header-rows: 1

    * - Higher-order
      - Application
    * - **map**, **fold**, **mapfold**, **mapi** **foldi**, **mapfoldi**
      - array iterators
    * - **activate** ... **every**
      - conditional activation
    * - **restart** ... **every**  
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


Partial Operator Instance
-------------------------

.. autoclass:: Partial

.. autoclass:: OptGroupItem


N-Ary Operator Instance
-----------------------

N-ary operator instances are implemented as specific expressions. See :ref:`sec_n_ary_expr` section.


Operator Expressions
--------------------

.. autoclass:: OperatorExpression

.. autoclass:: PrefixOperatorExpression


This class is used when an operator expression is syntactically
incorrect and was protected by the serialization process.

.. autoclass:: ProtectedOpExpr


