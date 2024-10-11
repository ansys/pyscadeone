Modules and Interfaces
======================

.. currentmodule:: ansys.scadeone.core.swan

This section describes the classes that represent a module body
or a module interface. It also describes the class representing
a *use* directive which is used to reference a module/interface
in an other module/interface.

.. uml:: 
    :align: center
    
    @startuml Module
    Module <|-- ModuleInterface
    Module <|-- ModuleBody
    Module *-- "*" ModuleItem
    ModuleItemDeclaration <|-- Signature
    Signature <|-- Operator
    ModuleItem <|-- UseDirective
    ModuleItem <|-- GlobalDeclaration
    note left of GlobalDeclaration
     **type**, **sensor**, **const**
    and **group** declarations
    end note 
    @enduml

See also :ref:`sec_op_decl` and :ref:`sec_global_decl`.

.. .. autoclass:: Module

.. autoclass:: ModuleBody

.. autoclass:: ModuleInterface

.. autoclass:: UseDirective
