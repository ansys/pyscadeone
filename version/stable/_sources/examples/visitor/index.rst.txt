.. _ref_visitor_example:

=======
Visitor 
=======

This example shows how to use a visitor to retrieve cross-references between operators.

Setup
-----

The same ``QuadFlightControl`` example is used. To setup the example, see 
:ref:`ref_QuadFlightControl_python_setup`.

All modules are loaded:

.. code::

    model.load_all_modules()

Visitor definition
------------------

The :py:class:`ReferenceVisitor` is derived from :py:class:`SwanVisitor` class. One needs:

- an attribute to store the current visited operator
- dictionaries to store the cross-references between operators
- some methods to retrieve the data

.. literalinclude:: quad_flight_control.py
    :lines: 78-92

The following methods are implemented, overridden from the base class:

- the ``ReferenceVisitor.visit_OperatorDefinition``: it keeps track of the current operator that is the caller, 
  and calls the default process to go on.
- and ``ReferenceVisitor.visit_PathIdCall`` which implements the name of a called operator, amongst the
  possible operator expressions. Here, one first checks that the call corresponds to an operator declaration.
  Then one creates the cross-references (see :ref:`ref_visitor_full_code`).

.. literalinclude:: quad_flight_control.py
    :lines: 93-111

The visitor is instantiated, and visits all modules in the model:

.. literalinclude:: quad_flight_control.py
    :lines: 129-131

Finally, ``caller_stat`` and ``called_stat`` functions 
print the results for a given operator. These functions use the 
``ReferenceVisitor.get_caller`` and ``ReferenceVisitor.get_called``
methods (see :ref:`ref_visitor_full_code`).

.. _ref_visitor_full_code:

Complete example
----------------

This is the complete script for the visitor section. Some logging support is shown
in the code, as well as the use of the ``doctest`` Python library. If one runs the
example, nothing is shown as the test succeeds.

.. literalinclude:: quad_flight_control.py











