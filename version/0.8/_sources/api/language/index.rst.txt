.. _ref_swan_api:

***************
Swan constructs
***************

.. currentmodule:: ansys.scadeone.core.swan

This section describes the **ansys.scadeone.core.swan** module which contains all classes
available to represent a Swan model.

Some class descriptions use the `Extended Backus-Naur <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_ 
form to represent Swan constructs.

Each class defined in this module corresponds to a Swan construct. For instance the :py:class:`ModuleBody` class 
represents a Swan module body, the :py:class:`ConstDeclarations` class represents constant declarations, 
and the :py:class:`Diagram` class represents a diagram. This pattern continues for all Swan constructs.

The class hierarchy closely mirrors the Swan language and its grammar. Refer to the *Help* menu in the
Swan IDE for a complete description of the Swan language.

Swan objects can be created from a Swan model read from a project or built from scratch using the classes
described in the following sections.

Swan objects as strings
-----------------------

Swan objects can be complex, and pretty-printing them is often desirable. The default `__str__()` method is not always 
sufficient to represent a Swan object as a string. To obtain a string representation of a Swan construct, 
use the `ansys.scadeone.core.swan.swan_to_str()` method. Example:

.. code:: python

   from ansys.scadeone.core.swan import swan_to_str
   print(swan_to_str(my_construct))


The default `__str__()` method is implemented for the following classes: 
:class:`Luid`, 
:class:`Lunum`,
:class:`Literal`,
:class:`Identifier`,
:class:`PathIdentifier`,
:class:`Pattern` derived classes,
:class:`Pragma`, and  pragma related classes (see: :ref:`sec_diag_pragmas`), and
:class:`ProtectedItem`.

Protected object concept
------------------------

The Swan editor allows the user to enter syntactically invalid Swan code. Such code is *protected* to become acceptable tokens
for the Swan parser. See :ref:`ref_protected_items` for more details.

.. toctree::
   :maxdepth: 2

   common
   module_global/index
   operator_body/index
   expressions/index
   group
   mem_annot
   pragmas/index
   protected



.. currentmodule:: None