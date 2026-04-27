Bitwise, boolean, arithmetic, relational, sequential
====================================================

.. currentmodule:: ansys.scadeone.core.swan

Arithmetic, logical, bitwise, and relational expressions are represented 
by unary expressions (ex: *not X*), binary expressions (ex: *1 + 2*), or n-ary expressions. 

Unary and binary expressions are implemented with the :py:class:`UnaryExpr` and :py:class:`BinaryExpr` classes
with the appropriate operator as an enumeration value.

N-ary expressions correspond to specific operator :py:class:`NAryOperator` 
with the appropriate operator as an enumeration value.


.. figure:: arithmetic.svg

.. list-table:: Bitwise
    :header-rows: 1

    * - Operator
      - Operation
      - Class and operator as enum value
    * - **lnot** 
      - bitwise not
      - :py:class:`UnaryExpr` with ``UnaryOp.Lnot`` operator
    * - **land** 
      - bitwise and
      - :py:class:`BinaryExpr` with ``BinaryOp.Land`` operator / :py:class:`NAryOrator` with ``NaryOp.And`` operator
    * - **lor** 
      - bitwise or
      - :py:class:`BinaryExpr` with ``BinaryOp.Lor`` operator / :py:class:`NAryOrator` with ``NaryOp.Or`` operator
    * - **lxor** 
      - bitwise xor
      - :py:class:`BinaryExpr` with ``BinaryOp.Xor`` operator / :py:class:`NAryOrator` with ``NaryOp.Xor`` operator
    * - **lsl** 
      - logical shift left
      - :py:class:`BinaryExpr` with ``BinaryOp.Lsl`` operator
    * - **lsr** 
      - logical shift right
      - :py:class:`BinaryExpr` with ``BinaryOp.Lsr`` operator

.. list-table:: Boolean
    :header-rows: 1
    
    * - Operator
      - Operation
      - Class and operator as enum value
    * - **not**
      - logical not
      - :py:class:`UnaryExpr` with ``UnaryOp.Not`` operator
    * - **and**
      - logical and
      - :py:class:`BinaryExpr` with ``BinaryOp.And`` operator / :py:class:`NAryOrator` with ``NaryOp.And`` operator
    * - **or**
      - logical or
      - :py:class:`BinaryExpr` with ``BinaryOp.Or`` operator / :py:class:`NAryOrator` with ``NaryOp.Or`` operator
    * - **xor**
      - logical xor
      - :py:class:`BinaryExpr` with ``BinaryOp.Xor`` operator / :py:class:`NAryOrator` with ``NaryOp.Xor`` operator

.. list-table:: Arithmetic
    :header-rows: 1

    * - Operator
      - Operation
      - Class and operator as enum value
    * - **-**
      - minus / subtraction
      - :py:class:`UnaryExp` with ``UnaryOp.Minus`` operator / :py:class:`BinaryExpr` with ``BinaryOp.Minus`` operator
    * - **+** 
      - plus / addition
      - :py:class:`UnaryExpr` with ``UnaryOp.Plus`` operator 
        / :py:class:`BinaryExpr` with ``BinaryOp.Plus`` operator 
        / :py:class:`NAryOrator` with ``NaryOp.Plus`` operator     
    * - **\***
      - multiplication
      - :py:class:`BinaryExpr` with ``BinaryOp.Mult`` operator 
        / :py:class:`NAryOrator` with ``NaryOp.Mult`` operator
    * - */*
      - division
      - :py:class:`BinaryExpr` with ``BinaryOp.Slash`` operator 
    * - *mod*
      - modulo
      - :py:class:`BinaryExpr` with ``BinaryOp.Mod`` operator 
    * - **(:>)**
      - cast operation
      - :py:class:`NumericCast` (special class for cast operator)

.. list-table:: Relational
    :header-rows: 1

    * - Operator
      - Operation
      - Class and operator as enum value
    * - **=**
      - equal
      - :py:class:`BinaryExpr` with ``BinaryOp.Equal`` operator 
    * - **<>**
      - different
      - :py:class:`BinaryExpr` with ``BinaryOp.Diff`` operator 
    * - **<**
      - less than
      - :py:class:`BinaryExpr` with ``BinaryOp.Lt`` operator 
    * - **<=**
      - less than or equal to
      - :py:class:`BinaryExpr` with ``BinaryOp.Leq`` operator 
    * - **>**
      - greater than
      - :py:class:`BinaryExpr` with ``BinaryOp.Gt`` operator 
    * - **>=**
      - greater than or equal to
      - :py:class:`BinaryExpr` with ``BinaryOp.Gte`` operator 



Unary expressions
-----------------

A unary expression is composed of a unary operator and an expression. 
Unary operators are defined with the :py:class:`UnaryExpr` enumeration.


.. autoclass:: UnaryExpr

.. _ref_bin_expr:

Binary expressions
------------------

A binary expression is composed of a binary operator and two expressions. 
Binary operators are defined with the :py:class:`BinaryExpr` enumeration.

.. autoclass:: BinaryExpr

Cast operators
--------------

A cast operator ( :> )  is a specific binary expression as it takes an
expression and a type.

.. autoclass:: NumericCast


.. _ref_n_ary_expr:

N-ary expressions
-----------------

N-ary operators are a special case of operator calls. The n-ary operations
are given by the following enumeration.


.. autoclass:: NAryOperator

Sequential expressions
----------------------

.. autoclass:: PreExpr

.. autoclass:: PreWithInitialValueExpr

.. autoclass:: InitialValueExpr