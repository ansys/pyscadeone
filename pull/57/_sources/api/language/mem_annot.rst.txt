Memory annotations
==================

The Swan language supports memory annotations to specify how data is stored and accessed in memory.

.. currentmodule:: ansys.scadeone.core.swan

.. list-table:: Memory annotations
    :header-rows: 1

    * - Annotation
      - Description
      - Class
    * - ! *expr*
      - Bang unary operator for duplicate permission
      - :py:class:`UnaryExpr` with ``UnaryOp.Bang`` operator
    * - var_id * [: type]
      - Starred input which value can be modified in place by an output.
      - :py:class:`VarDecl`, property ``is_starred=True``
    * - var_id **at** ID [: type]
      - Output variable which value is stored at a specific memory location, corresponding to an input.
      - :py:class:`VarDecl`, property ``at=ID``
    * - (expr **with**  * *modifier* {{ ; *modifier* }} [[ ; ]])
      - Copy with modification, replacing functional update.
      - :py:class:`FunctionalUpdate`, property ``is_starred=True``
    * - (*expr* **at** ID)
      - Expression stored at a specific memory location.
      - :py:class:`Expression`, property ``at=ID``. This property is defined for all expressions.

