Modules and Interfaces
======================

.. currentmodule:: ansys.scadeone.core.swan

This section describes the classes that represent a module body
or a module interface. It also describes the class representing
a *use* directive which is used to reference a module/interface
in an other module/interface.

.. figure:: module.svg
   

See also :ref:`ref_op_decl` and :ref:`ref_global_decl`.

.. .. autoclass:: Module

.. autoclass:: ModuleBody
    :exclude-members: add_constant, add_declaration, add_enum, add_group, add_operator, add_sensor, add_signature, 
                      add_struct, add_textual_operator, add_textual_signature, add_type

.. autoclass:: ModuleInterface
    :exclude-members: add_constant, add_declaration, add_enum, add_group, add_operator, add_sensor, add_signature,
                      add_struct, add_textual_operator, add_textual_signature, add_type

.. autoclass:: UseDirective
