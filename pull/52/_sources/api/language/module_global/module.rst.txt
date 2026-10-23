Modules and Interfaces
======================

.. currentmodule:: ansys.scadeone.core.swan

This section describes the classes that represent a module body
or a module interface. It also describes the class representing
a *use* directive which is used to reference a module/interface
in an other module/interface.


.. figure:: module.svg
    :align: center
    
    Module/interface class diagram
   

See also :ref:`ref_op_decl` and :ref:`ref_global_decl`.

.. .. autoclass:: Module

Module body
-----------

.. autoclass:: ModuleBody
    :exclude-members: add_constant, add_declaration, add_enum, add_group, add_operator_definition, add_sensor, add_operator_declaration, 
                      add_struct, add_textual_operator_definition, add_textual_operator_declaration, add_type

Module interface
----------------

.. autoclass:: ModuleInterface
    :exclude-members: add_constant, add_declaration, add_enum, add_group, add_operator_definition, add_sensor, add_operator_declaration,
                      add_struct, add_textual_operator_definition, add_textual_operator_declaration, add_type

Use directive
--------------

.. autoclass:: UseDirective

Module item
-----------

Base classe for module items. 

.. autoclass:: ModuleItem