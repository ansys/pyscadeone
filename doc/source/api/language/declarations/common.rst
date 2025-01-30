Common classes
==============

This section contains the description of classes that are
commonly used by other classes.

.. currentmodule:: ansys.scadeone.core.swan

SwanItem class
--------------

The :class:`SwanItem` is the top-level class for all constructs.

.. autoclass:: SwanItem
    :no-show-inheritance: 

Identifier classes
------------------

Swan identifiers are represented by the following classes with a simple identifier or 
a path identifier, which is a list of identifiers separated by '::'.

A **luid** is used to identify diagram blocks, connections, but also to name instances
of operators, or parts of automata.

.. autoclass:: Identifier

.. autoclass:: PathIdentifier

.. autoclass:: Luid

Pragma class
------------

The :py:class:`Pragma` stores a pragma information given in the code.

.. autoclass:: Pragma

Protection class
----------------

User code may be syntactically incorrect in a model, but must be
saved and read without errors by the parser. Such invalid code
is protected by markups. Other markups are used by the serialization
mechanism of the editor. 

Such piece of code is represented with a :py:class:`ProtectedItem` (or
derived class) instance, which stores the code text and the markup.

.. autoclass:: ProtectedItem

.. autoclass:: Markup

Miscellaneous
-------------

The following class is a helper for Swan literal expressions.

.. autoclass:: SwanRE
