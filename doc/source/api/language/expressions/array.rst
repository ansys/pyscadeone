Array
=====

The following table lists all array operations. Operations are indicated with respect to
the syntax given in the Scade One documentation.

.. currentmodule:: ansys.scadeone.core.swan

.. list-table:: Array operations
    :header-rows: 1

    * - Operation
      - Class
    * - **^** (Repetition)
      - :py:class:`ArrayRepetition`
    * - **@** (Concatenation)
      - See :ref:`sec_bin_expr` and :ref:`sec_n_ary_expr`
    * - **[_]** (Array constructor)
      - :py:class:`ArrayConstructor`
    * - **.[i]** (Projection)
      - :py:class:`ArrayProjection`
    * - **.[_] default _** (Projection with default)
      - :py:class:`ProjectionWithDefault`
    * - **flatten** 
      - See `Other Array Operations`_
    * - **reverse** 
      - See `Other Array Operations`_
    * - **_[i..j]** (Slice)
      - :py:class:`Slice`
    * - **transpose**
      - See `Other Array Operations`_
    * - **_ with[_]** (Functional update)
      - See :doc:`update`    
    * - **pack**
      - See `Other Array Operations`_
     
.. uml::
  :align: center
  
    @startuml ArrayOperations
    skinparam groupInheritance 2
    left to right direction

    Expression <|-- ArrayConstructor
    Expression <|-- ArrayRepetition
    Expression <|-- Slice
    Expression <|-- ArrayProjection
    Expression <|-- ProjectionWithDefault
    Expression <|-- FunctionalUpdate
    note right: array with update
    
    note as N1
    **flatten**, **reverse**, **transpose**, **pack**:
    [[api/language/expressions/array.html#other-array-operations other operations]]

    @ is a binary or n-ary expression
    end note

    @enduml

Array Operations
----------------

.. autoclass:: ArrayRepetition

.. autoclass:: ArrayConstructor

.. autoclass:: ArrayProjection

.. autoclass:: Slice

.. autoclass:: ProjectionWithDefault

Other Array Operations
----------------------

Arrays support the **flatten**, **reverse**, **pack**, and **transpose** operations.

Operations are implemented by the :py:class:`PrefixPrimitive` with
an enumeration to select the proper operation.

**transpose** is associated with the :py:class:`Transpose`
(derives from :py:class:`PrefixPrimitive`) to handle the
operation parameters.


.. autoclass:: PrefixPrimitive

.. autoclass:: PrefixPrimitiveKind

.. autoclass:: Transpose