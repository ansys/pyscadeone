Activations
===========

This section describes the *activate if* and *activate when* constructs.

.. currentmodule:: ansys.scadeone.core.swan
    
Activate If
-----------
The **activate if** operator uses a *tree* of conditional expressions. 
The classes to represent the operator are organized as follows:

.. uml::
    :align: center
    
    @startuml ActivateIf

    ActivateIf *-- IfActivation

    IfActivation "1" *-- "*" IfActivationBranch

    IfActivationBranch  *--  "0..1" Expression
    IfActivationBranch  *--  IfteBranch

    IfteBranch <|-- IfteDataDef
    IfteBranch <|-- IfteIfActivation

    IfteIfActivation *-- IfActivation

    @enduml

The :py:class:`ActivateIf` references the :py:class:`IfActivation` which in turns stores
all the *if ... elsif ... else* branches. Branches are in the order *if*, then *elsif* and *else*.
The class :py:class:`IfActivationBranch` stores an *if*, or *elsif* or *else* branch with 
its condition (but for *else* branch) and its associated computation (*data_def*) or another
decision tree.

.. autoclass:: ActivateIf

.. autoclass:: IfActivation

.. autoclass:: IfActivationBranch

.. autoclass:: IfteBranch

.. autoclass:: IfteDataDef

.. autoclass:: IfteIfActivation

Activate When
-------------

.. autoclass:: ActivateWhen

.. autoclass:: ActivateWhenBranch