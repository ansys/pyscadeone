Activations
===========

This section describes the *activate if* and *activate when* constructs.

.. currentmodule:: ansys.scadeone.core.swan
    
Activate if
-----------
The **activate if** operator uses a *tree* of conditional expressions. 
The classes to represent the operator are organized as follows:

.. figure:: activate_if.svg

    Activate If class diagram   

The :py:class:`ActivateIf` references the :py:class:`IfActivation` which in turns stores
all the *if condition elsif condition else* branches. Branches are in the order *if*, then *elsif* and *else*.
The class :py:class:`IfActivationBranch` stores an *if*, or *elsif* or *else* branch with 
its condition (but for *else* branch) and its associated computation (*data_def*) or another
decision tree.

.. autoclass:: ActivateIf

.. autoclass:: IfActivation

.. autoclass:: IfActivationBranch

.. autoclass:: IfteBranch

.. autoclass:: IfteDataDef

.. autoclass:: IfteIfActivation

Activate when
-------------

.. autoclass:: ActivateWhen

.. autoclass:: ActivateWhenBranch