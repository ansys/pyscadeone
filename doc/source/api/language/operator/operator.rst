.. _ref_op_decl:

Operator declaration
====================

.. currentmodule:: ansys.scadeone.core.swan

Signature
---------

Operator interface declaration, found in module interface.

.. autoclass:: Signature
    :exclude-members: to_str

Operator
---------

Operator definition, found in module body.

.. autoclass:: Operator
    :exclude-members: to_str

Constraints
-----------

Constraint that can be applied to generic types.

.. autoclass:: TypeConstraint

.. autoclass:: NumericKind

Scopes
------

Scope contains scope sections which define :doc:`variables <var>`, :doc:`equations <equation>`,
:doc:`diagrams <diagram>` and  :doc:`other sections <other_sections>`.

.. autoclass:: Scope

.. autoclass:: ScopeSection
    :exclude-members: to_str

.. autoclass:: ProtectedSection

