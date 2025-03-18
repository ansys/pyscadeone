.. _ref_create_project:

Project creation
================
This section provides the elements for creating or modifying a Scade One project.
An example is provided in :ref:`creator_ex`.

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.factory

Factory
_______
The :py:class:`ScadeOneFactory` allows to create in an easy way the following Scade One objects:

- Variable declarations

.. autoclass:: ScadeOneFactory
    :members:

High-level API
______________
This section describes a high-level API to create or modify a Scade One project. Only classes and methods
related to the project creation are listed.

.. currentmodule:: ansys.scadeone.core.scadeone
.. autoclass:: ScadeOne
    :no-index:
    :exclude-members: close, load_project, subst_in_path, install_dir, projects

.. currentmodule:: ansys.scadeone.core.project
.. autoclass:: Project
    :no-index:
    :exclude-members: build_sproj, check_exists, dependencies, swan_sources, app, directory, storage, data

.. currentmodule:: ansys.scadeone.core.swan.modules
.. autoclass:: Module
    :no-index:
    :exclude-members: name, source, declaration, use_directives, extension, file_name, filter_declarations,
        types, sensors, constants, groups, get_full_path, get_declaration, get_use_directive, interface, body,
        harness, gen_code, declarations, is_protected, model, module, owner, set_owner

.. currentmodule:: ansys.scadeone.core.swan.operators
.. autoclass:: Operator
    :no-index:
    :exclude-members: get_full_path, set_owner, to_str, body, constraints, diagrams, has_body, id, inputs,
        is_equation_body, is_node, is_protected, is_text, model, module, outputs, owner, pragmas, signature,
        sizes, specialization, has_inline

.. currentmodule:: ansys.scadeone.core.swan.diagram
.. autoclass:: Diagram
    :no-index:
    :exclude-members: get_block_sources, get_block_targets, get_full_path, set_owner, to_str, is_protected, is_text,
        model, module, objects, owner









