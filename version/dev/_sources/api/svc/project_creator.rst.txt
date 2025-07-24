.. _ref_create_project:

Project creation
================
This section provides the elements for creating or modifying a Scade One project.
An example is provided in :ref:`ref_creator_ex`.

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.factory

Best practices
-------------- 

Constructing a Scade One project can be a complex task. The following best practices are recommended:

- Create objects in the order of their dependencies. For example, create a module before creating its declarations.
- Create a **use** directive before adding objects from other modules to its module. For instance, if a constant is created in a module,
  that constant cannot be used in another module unless the proper directive is created first. In the *consumer* module, 
  the identifier of the constant depends on the **use** directive.

Project creation
-----------------

.. currentmodule:: ansys.scadeone.core.scadeone

Following :py:class:`ScadeOne` methods is used for creation:

.. automethod:: ScadeOne.new_project

.. autoproperty:: ScadeOne.version

Module body and interface creation
---------------------------------- 

A module body or a module interface can be created from a model or a project.
When added to a project, the module body or interface is automatically added to the model and its source
is updated with respect to the project path.

.. currentmodule:: ansys.scadeone.core.model.model

Following :py:class:`Model` methods are used for creation:

.. automethod:: Model.add_body

.. automethod:: Model.add_interface

.. currentmodule:: ansys.scadeone.core.project

Following :py:class:`Project` methods are used for creation:


.. automethod:: Project.add_module

.. automethod:: Project.add_module_interface


Module declarations
-------------------

.. currentmodule:: ansys.scadeone.core.swan.modules

Following :py:class:`ModuleBody` and :py:class:`ModuleInterface` methods are used for creation:

Any declaration
^^^^^^^^^^^^^^^ 

Add a declaration of any kind. 

.. automethod:: Module.add_declaration

Use directive creation
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: Module.use

Constant and sensor declarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: Module.add_constant

.. automethod:: Module.add_sensor

Type creation
^^^^^^^^^^^^^ 

.. automethod:: Module.add_enum

.. automethod:: Module.add_struct

.. automethod:: Module.add_group

.. automethod:: Module.add_type

Operator creation
^^^^^^^^^^^^^^^^^^

.. automethod:: Module.add_operator

.. automethod:: Module.add_signature

.. automethod:: Module.add_textual_operator

.. automethod:: Module.add_textual_signature


Operator content creation
-------------------------- 

.. currentmodule:: ansys.scadeone.core.swan.operators

Following :py:class:`Operator` methods are used for creation:

.. automethod:: Operator.add_input

.. automethod:: Operator.add_output

.. automethod:: Operator.add_diagram



Diagram content creation
------------------------- 

.. currentmodule:: ansys.scadeone.core.swan.diagram

Following :py:class:`Diagram` methods are used for creation:

.. automethod:: Diagram.add_block

.. automethod:: Diagram.add_def_block

.. automethod:: Diagram.add_expr_block

.. automethod:: Diagram.add_bar

.. automethod:: Diagram.connect

