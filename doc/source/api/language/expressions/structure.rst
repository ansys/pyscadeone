Structure
=========

.. currentmodule:: ansys.scadeone.core.swan

.. list-table:: Structure operations
    :header-rows: 1

    * - Operation
      - Class
    * - **{}** (Structure constructor)
      - :py:class:`StructConstructor`
    * - **.()** (Structure destructor)
      - :py:class:`StructDestructor`
    * - **.l** (Projection)
      - :py:class:`StructProjection`
    * - **_ with .l** (Functional update)
      - See :doc:`update`    

.. uml::
  :align: center
  
    @startuml StructureOperations
    skinparam groupInheritance 2
    left to right direction

    Expression <|-- StructConstructor 
    Expression <|-- StructProjection 
    Expression <|-- StructDestructor
    Expression <|-- FunctionalUpdate
    note right: structure with update

    @enduml

.. autoclass:: StructConstructor

.. autoclass:: StructDestructor

.. autoclass:: StructProjection



