Sequential
==========

.. currentmodule:: ansys.scadeone.core.swan

.. list-table:: Sequential
    :header-rows: 1

    * - Operator
      - Operation
      - Class and operator as enum value
    * - **pre**
      - Unit delay
      - :py:class:`UnaryExpr` with ``UnaryOp.Pre`` operator / :py:class:`BinaryExpr` with ``BinaryOp.Pre`` operator
    * - **->**
      - initial value
      - :py:class:`BinaryExpr` with ``BinaryOp.Arrow`` operator
    * - **window** 
      - temporal window
      - See :py:class:`Window`

.. figure:: sequential.svg
  
.. autoclass:: Window