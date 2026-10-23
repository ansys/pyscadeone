.. _ref_swan_api:

*************
Swan language
*************

.. currentmodule:: ansys.scadeone.core.swan

This section describes the :py:mod:`ansys.scadeone.core.swan` module which contains all classes
available to represent a Swan model.

Some class descriptions use the `Extended Backus-Naur <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_ form to represent Swan constructs.

The classes represent each Swan construct as given in the language documentation and are *mapped* on the
Swan grammar rules. These classes are data containers in the sense that they correspond to the model structure
as read from a Swan file. They do not contain any logic to interpret the model or to perform any kind of analysis.

.. note::

   To obtain a string from a Swan construct, use the :py:meth:`ansys.scadeone.core.swan.swan_to_str` method,
   like this::

      print(swan_to_str(my_construct))

   *Basic* constructs have the `__str__()` method implemented, so you can use the `str()` function 
   to obtain a string representation. 

Classes with `__str__()` method implemented are: 
:class:`Luid`, 
:class:`Lunum`,
:class:`Literal`,
:class:`Identifier` (only the identifier is transformed into a string, its pragmas are not included),
:class:`PathIdentifier`,
:class:`Pattern` derived classes,
:class:`Pragma`, and  pragma related classes (see: :ref:`sec_diag_pragmas`), and
:class:`ProtectedItem`.

.. jinja:: clock_ctx

   {% if clock %}
   .. toctree::
      :maxdepth: 2

      declarations/index
      operator/index
      expressions/index
      group
      clock
      pragmas/index

   {% else %}

   .. toctree::
      :maxdepth: 2

      declarations/index
      operator/index
      expressions/index
      group
      pragmas/index

   {% endif %}


.. currentmodule:: None