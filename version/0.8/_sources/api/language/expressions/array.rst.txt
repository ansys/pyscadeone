.. _ref_array_operations:

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
      - :py:class:`ArrayConcatExpr`  / :py:class:`NAryOperator` with ``NaryOp.Concat`` operator
    * - **[_]** (Array constructor)
      - :py:class:`ArrayConstructor`
    * - **.[i]** (Projection)
      - :py:class:`ArrayProjection`
    * - **.[_] default _** (Projection with default)
      - :py:class:`ProjectionWithDefault`
    * - **flatten** 
      - :py:class:`FlattenOperator` 
    * - **reverse** 
      - :py:class:`ReverseOperator`
    * - **_[i..j]** (Slice)
      - :py:class:`Slice`
    * - **transpose**
      - :py:class:`TransposeOperator`
    * - **_ with [_]** (Functional update)
      - See :doc:`update`    
    * - **pack**
      - :py:class:`PackOperator`
     
.. figure:: array_operations.svg
  

Array operations
----------------

.. autoclass:: ArrayRepetition

.. autoclass:: ArrayConstructor

.. autoclass:: ArrayProjection

.. autoclass:: Slice

.. autoclass:: ProjectionWithDefault

.. autoclass:: ArrayConcatExpr

.. autoclass:: ReverseOperator

.. autoclass:: PackOperator

.. autoclass:: FlattenOperator

.. autoclass:: TransposeOperator

