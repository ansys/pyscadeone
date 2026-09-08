.. _ref_diagram:

Diagrams
========

.. currentmodule:: ansys.scadeone.core.swan

A :py:class:`Diagram` object stores the representation of a **diagram**.
It contains the various blocks (see figure) and connections using
:py:class:`Wire` instances.  


.. figure:: diagram.svg

    Diagram class diagram

.. autoclass:: Diagram
    :exclude-members: to_str, add_block, add_def_block, add_expr_block, add_bar, connect, add_data_source, add_instance_under_test, add_oracle, add_set_sensor

.. autoclass:: DiagramObject

Diagram objects
---------------

This section describes the **expr**, **def** and **block** 
related classes.

.. vale Google.Headings = off

Expr block
^^^^^^^^^^

.. autoclass:: ExprBlock

.. vale Google.Headings = on

Def block
^^^^^^^^^

.. autoclass:: DefBlock

Instance block
^^^^^^^^^^^^^^

.. autoclass:: Block


Grouping/ungrouping blocks
--------------------------

Group operator
^^^^^^^^^^^^^^

The :py:class:`GroupBlock` class represents the `(group)` graphical operator. It is the parent class 
of the grouping/ungrouping operators: :py:class:`Bar`, :py:class:`Concat`, :py:class:`ByPos` and :py:class:`ByName`.


.. autoclass:: GroupBlock

Bar operator
^^^^^^^^^^^^ 

.. autoclass:: Bar


Concat operator
^^^^^^^^^^^^^^^

.. autoclass:: Concat

.. vale Google.Headings = off

ByPos operator
^^^^^^^^^^^^^^

.. autoclass:: ByPos

ByName operator
^^^^^^^^^^^^^^^

.. autoclass:: ByName

.. vale Google.Headings = on

Wire and connections
--------------------

.. autoclass:: Wire

.. autoclass:: Connection

Def-by-case blocks
------------------

The **def-by-case** blocks gather the graphical version of then state machine and
activate if/when constructs.

.. autoclass:: StateMachineBlock

.. autoclass:: ActivateIfBlock

.. autoclass:: ActivateWhenBlock

Sections
--------

The :py:class:`SectionObject` contains a Swan *section*, that is
to say, a **let**, **var**, **diagram**, **assert**, **assume** or **guarantee** section.

.. autoclass:: SectionObject

