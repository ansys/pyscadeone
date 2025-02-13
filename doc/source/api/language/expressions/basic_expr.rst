Bitwise, boolean, arithmetic, relational
========================================

.. currentmodule:: ansys.scadeone.core.swan

Arithmetic, logical, bitwise, and relational expressions are represented 
by unary expressions (ex: *not X*), binary expressions (ex: *1 + 2*), or n-ary expressions. 

Unary and binary expressions are implemented with the :py:class:`UnaryExpr` and :py:class:`BinaryExpr` classes with the appropriate operator as an enumeration.

N-ary expressions correspond to specific operator instance calls which use the :py:class:`NaryOp` enumeration.

.. figure:: arithmetic.svg


.. list-table:: Operators
    :header-rows: 1

    * - Operator
      - Operation
      - Kind
    * - **-**
      - minus / subtraction
      - unary / binary
    * - **+** 
      - plus / addition
      - unary / binary, n-ary 
    * - **\***
      - multiplication
      - binary, n-ary
    * - */*
      - division
      - binary
    * - **lnot** 
      - bitwise not
      - unary
    * - **land** 
      - bitwise and
      - binary, n-ary
    * - **lor** 
      - bitwise or
      - binary, n-ary
    * - **lxor** 
      - bitwise xor
      - binary, n-ary
    * - **lsl** 
      - bitwise left-shift
      - binary
    * - **lsr** 
      - bitwise right-shift
      - binary
    * - **not**
      - logical not
      - unary
    * - **and**
      - logical and
      - binary, n-ary
    * - **or**
      - logical and
      - binary, n-ary
    * - **xor**
      - logical and
      - binary, n-ary
    * - **pre**
      - Unit delay
      - unary (not initial value), binary (initial value)
    * - **=**
      - relation equal
      - binary
    * - **<>**
      - relation difference
      - binary
    * - **<**
      - relation less than
      - binary
    * - **<=**
      - relation less than or equal to
      - binary
    * - **>**
      - relation greater than
      - binary
    * - **>=**
      - relation greater than or equal to
      - binary
    * - **->**
      - initial value
      - binary
    * - **@**
      - array concatenation
      - binary
    * - **(:>)**
      - cast operation
      - binary


Unary expressions
-----------------

A unary expression is composed of a unary operator and an expression. 
Unary operators are defined with the :py:class:`UnaryOp` enumeration.


.. autoclass:: UnaryOp
    :exclude-members: to_str

.. autoclass:: UnaryExpr

.. _ref_bin_expr:

Binary expressions
------------------

A binary expression is composed of a binary operator and two expressions. 
Binary operators are defined with the :py:class:`BinaryOp` enumeration.

.. autoclass:: BinaryOp

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

.. autoclass:: NaryOp

.. autoclass:: NAryOperator
