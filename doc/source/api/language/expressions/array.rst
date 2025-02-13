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
      - See :ref:`ref_bin_expr` and :ref:`ref_n_ary_expr`
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
     
.. figure:: array_operations.svg
  

Array operations
----------------

.. autoclass:: ArrayRepetition

.. autoclass:: ArrayConstructor

.. autoclass:: ArrayProjection

.. autoclass:: Slice

.. autoclass:: ProjectionWithDefault

Other array operations
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