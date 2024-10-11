Selection
=========

.. currentmodule:: ansys.scadeone.core.swan

These expressions represent **if** and **case** expressions.

.. uml::
    :align: center
    
    @startuml Selection
    skinparam groupInheritance 2

    Expression <|-- IfteExpr
    Expression <|-- CaseExpr

    @enduml

if/then/else
------------

.. autoclass:: IfteExpr

case
----

.. autoclass:: CaseExpr

.. autoclass:: CaseBranch