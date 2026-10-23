.. _ref_scope:

Operator sections
====================

.. currentmodule:: ansys.scadeone.core.swan


Scope contains scope sections which define :doc:`variables <var>`, :doc:`equations <equation>`,
:doc:`diagrams <diagram>`,  :doc:`formal properties <formal_props>` and :doc:`emissions <emission>`.

The :py:class:`Scope` class is used to define the scope and contains a list of :py:class:`ScopeSection`.
It derives from the :py:class:`HasPragma` class as a scope can have pragmas for the layout of
*blocks* defined by:py:class:`ActivateIf` and :py:class:`ActivateWhen` constructs.

.. autoclass:: Scope

.. autoclass:: ScopeSection
    :exclude-members: to_str

.. autoclass:: ProtectedSection

