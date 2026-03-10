Equations
=========

.. currentmodule:: ansys.scadeone.core.swan

Equations are grouped in a **let** section.

.. figure:: equation.svg

    Equation class diagram

.. autoclass:: LetSection
    :exclude-members: to_str

Equation with expression
------------------------

Equations have a left-hand side (LHS), the flows that are defined by the equation
and the equation expression.

.. autoclass:: Equation

.. autoclass:: EquationLHS

.. autoclass:: LHSItem

.. autoclass:: ExprEquation


Equation defined by cases
------------------------- 

.. autoclass:: DefByCase