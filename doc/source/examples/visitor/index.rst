.. _ref_visitor_example:

=======
Visitor 
=======

This example shows how to use a visitor to retrieve cross-references between operators.

Setup
-----

The same ``QuadFlightControl`` example is used. To setup the example, see 
:ref:`QuadFlightControl python setup`.

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

- the :py:meth:`SwanVisitor.visit_Operator`: it keeps track of the current operator that is the caller, 
  and calls the default process to go-on.
- and :py:meth:`SwanVisitor.visit_PathIdCall` which implements the name of a called operator, amongst the
  possible operator expressions. Here, we first assess that the call corresponds to an operator declaration.
  Then we create the cross-references (see :ref:`ref_visitor_full_code`).

.. literalinclude:: quad_flight_control.py
    :lines: 93-111

The visitor is instantiated, and visits all modules in the model:

.. literalinclude:: quad_flight_control.py
    :lines: 129-131

Finally, the :py:func:`caller_stat` and :py:func:`called_stat` functions 
print the results for a given operator. These functions use the 
:py:meth:`ReferenceVisitor.get_caller` and :py:meth:`ReferenceVisitor.get_called`
methods (see :ref:`ref_visitor_full_code`).

.. _ref_visitor_full_code:

Complete example
----------------

This is the complete script for the visitor section. Some logging support is shown
in the code, as well as the use of the ``doctest`` Python library. If one runs the
example, nothing is shown as the test succeeds.

.. literalinclude:: quad_flight_control.py











