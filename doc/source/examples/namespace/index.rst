.. _namespace_nav_ex:

Namespace-Based Navigation
===========================

.. currentmodule:: ansys.scadeone.swan

In this section, we present how we can search a declaration from a module or from a scope using its namespace.
The search starts on the module or scope moving up to the declarations of scope sections, operators,
module bodies and interfaces. 

We use the same ``QuadFlightControl`` example. To setup the example see 
:ref:`QuadFlightControl python setup`.

Then we get the proper module:

.. literalinclude:: quad_flight_control.py
    :lines: 17-24

Get Operator from Module
________________________
We can get the declaration of operators defined in a module (:py:class:`ModuleBody` or :py:class:`ModuleInterface`).
For instance, we can get the operator from a module using the :py:meth:`ModuleBody.get_declaration()` method:

.. literalinclude:: quad_flight_control.py
    :lines: 26-27

Get Global Declarations from Operator Scope
___________________________________________
We can also get global declarations like groups, constants, types, or other operators from the operator scope using the
:py:meth:`Scope.get_declaration()` method:

.. literalinclude:: quad_flight_control.py
    :lines: 29-44


With the same method, we can access to the inputs or outputs of the operator:

.. literalinclude:: quad_flight_control.py
    :lines: 46-50


Get Local Declarations from Any Scope
_____________________________________
In addition to global declarations, we can get local declarations like variables, inputs, or outputs from any scope using the
:py:meth:`Scope.get_declaration()` method.

This method looks for a declaration of a given name in its current namespace. 
If the declaration is not found, it is searched in the enclosing scope.

Complete Example
________________
This is the complete script for the name-based scope navigation section.

.. literalinclude:: quad_flight_control.py