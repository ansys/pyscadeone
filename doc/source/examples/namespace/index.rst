.. _namespace_nav_ex:

Navigation using names
======================

.. currentmodule:: ansys.scadeone.swan

This section present how to search a declaration from a module or from a scope using its namespace.
The search starts on the module or scope moving up to the declarations of scope sections, operators,
module bodies and interfaces. 

The ``QuadFlightControl`` example is used. To setup the example see 
:ref:`ref_QuadFlightControl_python_setup`.

The proper module is retrieved:

.. literalinclude:: quad_flight_control.py
    :lines: 39-46

Getting an  operator from the module
------------------------------------

Operator declarations can be found from a module (:py:class:`ModuleBody` or :py:class:`ModuleInterface`).
This code shows how to get the operator from a module using the :py:meth:`ModuleBody.get_declaration()` method:

.. literalinclude:: quad_flight_control.py
    :lines: 48-49

Get global declarations from operator scope
-------------------------------------------

Global declarations like groups, constants, types, or other operators from the operator scope are found using the
:py:meth:`Scope.get_declaration()` method:

.. literalinclude:: quad_flight_control.py
    :lines: 51-66


With the same method can be used to access to the inputs or outputs of the operator:

.. literalinclude:: quad_flight_control.py
    :lines: 68-72


Get local declarations from any scope
-------------------------------------

In addition to global declarations, local declarations like variables, inputs, or outputs from any scope 
can be found using the :py:meth:`Scope.get_declaration()` method.

This method looks for a declaration of a given name in its current namespace. 
If the declaration is not found, it is searched in the enclosing scope.

Complete example
----------------

This is the complete script for the name-based scope navigation section.

.. literalinclude:: quad_flight_control.py