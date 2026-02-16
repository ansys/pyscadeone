.. _ref_global_decl:

Declaration base classes
========================

.. currentmodule:: ansys.scadeone.core.swan

The :py:class:`Declaration` class serves as the base class for all declarations of constructs with an identifier. 
Declarations of the same kind (e.g., constant, type, sensor, group) are *grouped* into a list of declarations,
contained within classes derived from :py:class:`GlobalDeclaration`. 

.. figure:: global.svg
    :name: fig_global_declarations
    
    Declaration classes hierarchy

.. note::
    In Swan, a global declaration can contain multiple declarations. For example, one can write:
    ``const C1: int32; C2: int32;`` or ``const C1: int32; const C2: int32;``.
    While the Swan editor produces the second form, having a list of declarations
    in the first form is also valid.

.. autoclass:: Declaration

.. autoclass:: GlobalDeclaration

.. autoclass:: ProtectedDecl
