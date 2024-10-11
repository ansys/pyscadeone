.. _Visitor Example:

=======
Visitor 
=======

.. include:: quad_flight_control.py
    :start-line: 1
    :end-line: 25

Setup
-----

We use the same ``QuadFlightControl`` example. To setup the example, see 
:ref:`QuadFlightControl python setup`.

For that example, we load all modules:

.. code::

    model.load_all_modules()

Visitor Definition
------------------

The :py:class:`ReferenceVisitor` is derived from :py:class:`SwanVisitor` class. One needs:

- an attribute to store the current visited operator
- dictionaries to store the cross-references between operators
- some methods to retrieve the data

.. literalinclude:: quad_flight_control.py
    :lines: 55-68

Then we override:

- the :py:meth:`SwanVisitor.visit_Operator`: we want to keep track of the operator that is the caller, and calls
  the default process to go-on.
- and :py:meth:`SwanVisitor.visit_PathIdCall` which implements the name of a called operator, amongst the
  possible operator expressions. Here, we first assess that the call corresponds to an operator declaration.
  Then we create the cross-references (see :ref:`visitor full code`).

.. literalinclude:: quad_flight_control.py
    :lines: 70-88

We instantiate the visitor, and visit all modules in the model:

.. literalinclude:: quad_flight_control.py
    :lines: 106-108

Finally, we create the :py:func:`caller_stat` and :py:func:`called_stat` to
print the results for a given operator. These functions use the 
:py:meth:`ReferenceVisitor.get_caller` and :py:meth:`ReferenceVisitor.get_called`
methods (see :ref:`visitor full code`).

.. _visitor full code:

Complete Example
----------------

This is the complete script for the visitor section. Some logging support is shown
in the code, as well as the use of the ``doctest`` Python library. If one runs the
example, nothing is shown as the test succeeds.

.. literalinclude:: quad_flight_control.py











