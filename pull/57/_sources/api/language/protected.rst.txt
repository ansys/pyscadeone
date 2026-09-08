.. _ref_protected_items:

Protected items
===============

.. currentmodule:: ansys.scadeone.core.swan

Swan code in a model may be syntactically incorrect but must still be
saved and read without errors by the parser. Such invalid code
is protected using markups. Invalid syntax is protected as ``{syntax%invalid code %syntax}`` 
and corresponds to a specific token of the Swan grammar used by the tools [#f1]_. 

Additionally, other markups are used by the serialization
mechanism of the editor [#f2]_. 

Such pieces of code are represented by a :py:class:`ProtectedItem` 
(or a derived class) instance, which stores the code text and the associated markup.

Protection class
---------------- 

.. autoclass:: ProtectedItem

List of protected items
-----------------------

The following table lists the classes derived from :py:class:`ProtectedItem`, which protect
invalid textual parts entered in the Scade One editor. The *Sibling class* column indicates 
the base class of the protected item. Even though the item is invalid, it is part of a Swan construct.

.. list-table::
    :header-rows: 1

    
    * - Class
      - Description
      - Other base
    * - :py:class:`ProtectedItem`
      - Sibling class.
      - None
    * - :py:class:`ProtectedDecl`
      - Protected declaration (constant, type, sensor, group, **use** directive).
      - :py:class:`GlobalDeclaration`
    * - :py:class:`ProtectedExpr`
      - Protected expression.
      - :py:class:`Expression`
    * - :py:class:`ProtectedGroupRenaming`
      - Protected group renaming.
      - :py:class:`GroupRenaming` 
    * - :py:class:`ProtectedOpExpr`
      - Protected operator expression within an instance block.
      - :py:class:`OperatorExpression`
    * - :py:class:`ProtectedPattern`
      - Protected pattern in **activate**.
      - :py:class:`Pattern`
    * - :py:class:`ProtectedSection`
      - Protected section (ex: invalid **let** equation block).
      - :py:class:`ScopeSection`
    * - :py:class:`ProtectedTypeExpr`
      - Protected type expression.
      - :py:class:`TypeExpression`
    * - :py:class:`ProtectedVariable`
      - Protected variable declaration (in **var** section, inputs or outputs).
      - :py:class:`Variable`
    * - :py:class:`ProtectedForwardReturnItem`
      - Protected forward return.
      - :py:class:`ForwardReturnItem`

Markup helper
-------------

.. autoclass:: Markup




.. rubric:: Footnotes

.. [#f1] Other markups than ``syntax`` are used by the editor to protect invalid code. 
   Having only ``syntax`` would result in an invalid grammar.

.. [#f2] These additional markups are used as specific information for the Scade One editor. 
   They are processed by the PyScadeOne library and do not appear as protected items.
