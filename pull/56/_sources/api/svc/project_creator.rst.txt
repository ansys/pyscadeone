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

Following :py:class:`ScadeOne` method is used for creation:

.. automethod:: ScadeOne.new_project

.. autoproperty:: ScadeOne.version


Resource creation
^^^^^^^^^^^^^^^^^

.. currentmodule:: ansys.scadeone.core.project

:py:class:`Resource` files can be added to a project and used on it. For more information about resources,
see :ref:`ref_resources`.

For simulation data creation or edition, see :ref:`ref_sim_data`.

Following :py:class:`Project` methods are used for managing resources:

.. automethod:: Project.add_resource

Dependencies management
^^^^^^^^^^^^^^^^^^^^^^^

Following :py:class:`Project` methods are used for managing dependencies:

.. automethod:: Project.add_dependency

.. automethod:: Project.remove_dependency

.. _ref_test_creation:


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


.. automethod:: Project.add_module_body

.. automethod:: Project.add_module_interface

.. _ref_module_creation:

Module declarations
-------------------

.. currentmodule:: ansys.scadeone.core.swan.modules

Following :py:class:`ModuleBody` and :py:class:`ModuleInterface` methods are used for creation:

Any declaration
^^^^^^^^^^^^^^^

Add a declaration of any kind.

.. automethod:: ModuleBodyCreator.add_declaration

Use directive creation
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ModuleBodyCreator.use

Constant and sensor declarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ModuleBodyCreator.add_constant

.. automethod:: ModuleBodyCreator.add_sensor

Type creation
^^^^^^^^^^^^^

.. automethod:: ModuleBodyCreator.add_enum

.. automethod:: ModuleBodyCreator.add_struct

.. automethod:: ModuleBodyCreator.add_group

.. automethod:: ModuleBodyCreator.add_type

Operator creation
^^^^^^^^^^^^^^^^^^

.. automethod:: ModuleBodyCreator.add_operator_definition

.. automethod:: ModuleBodyCreator.add_operator_declaration

.. automethod:: ModuleBodyCreator.add_textual_operator_definition

.. automethod:: ModuleBodyCreator.add_textual_operator_declaration


Operator content creation
--------------------------

.. currentmodule:: ansys.scadeone.core.swan.operators

Following :py:class:`OperatorDefinition` methods are used for creation:

.. automethod:: OperatorDefinition.add_input

.. automethod:: OperatorDefinition.add_output

.. automethod:: OperatorDefinition.add_diagram


.. _ref_diagram_creation:

Diagram content creation
-------------------------

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.diagram_creator

Following :py:class:`DiagramCreator` methods are used for creation:

.. automethod:: DiagramCreator.add_block

.. automethod:: DiagramCreator.add_def_block

.. automethod:: DiagramCreator.add_expr_block

.. automethod:: DiagramCreator.add_bar

.. automethod:: DiagramCreator.connect

Test creation
-------------

Test module creation
^^^^^^^^^^^^^^^^^^^^

Module level:

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.module_creator

.. automethod:: TestModuleCreator.add_test_harness

Test harness creation
^^^^^^^^^^^^^^^^^^^^^

A harness contains a diagram. 

.. currentmodule:: ansys.scadeone.core.swan.harness

.. automethod:: TestHarness.add_diagram

see :ref:`ref_diagram_creation` section.

Harness specific methods:

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.diagram_creator

.. automethod:: DiagramCreator.add_data_source

.. automethod:: DiagramCreator.add_oracle

.. automethod:: DiagramCreator.add_set_sensor

.. automethod:: DiagramCreator.add_instance_under_test