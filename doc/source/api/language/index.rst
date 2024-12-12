.. _ref_swan_api:

*************
Swan language
*************

.. :py:module:: ansys.scadeone.core.swan

This section describes the :py:mod:`ansys.scadeone.core.swan` module which contains all classes
available to represent a Swan model.

Some class descriptions use the `Extended Backus-Naur <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_ form to represent Swan constructs.

.. jinja:: clock_ctx

   {% if clock %}
   .. toctree::
      :maxdepth: 2

      declarations/index
      operator/index
      expressions/index
      group
      clock

   {% else %}

   .. toctree::
      :maxdepth: 2

      declarations/index
      operator/index
      expressions/index
      group

   {% endif %}


.. currentmodule:: None