Basic classes
=============

This section contains the description of classes that are
commonly used by other classes.

.. currentmodule:: ansys.scadeone.core.swan

SwanItem class
--------------

The :class:`SwanItem` is the top-level class for all constructs.

.. autoclass:: SwanItem
    :no-show-inheritance: 

HasPragma class
----------------

The :class:`HasPragma` is the top-level class for all constructs which have
pragmas. It is a subclass of :class:`SwanItem`. 

.. autoclass:: HasPragma


Identifier classes
------------------

Swan identifiers are represented by the following classes with a simple identifier or 
a path identifier, which is a list of identifiers separated by '::'.

A **luid** (:class:`Luid`) is used to name instances of operators, automata, or activate.

A **lunum** (:class:`Lunum`) is used to reference a block in a :class:`Diagram`.

.. autoclass:: Identifier

.. autoclass:: PathIdentifier

.. autoclass:: Luid

.. autoclass:: Lunum


Miscellaneous
-------------

The following class is a helper for Swan literal expressions.

.. autoclass:: SwanRE
