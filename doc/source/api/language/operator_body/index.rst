.. _ref_op_body:

Operator body
=============

Operator declarations are detailed in :ref:`ref_op_decl`.

The body of an operator consists of *sections*, detailed as follows:

* Scope in the section :doc:`scope`
* Variable declaration in the section :doc:`var`
* Equation declaration in the section :doc:`equation`
* Activations and state machines, which are parts of equation concepts are 
  described in the separate sections: :doc:`activation` and :doc:`automaton` 
* Formal property sections for **assume**, **guarantee** and **assert** are grouped in the
  section :doc:`formal_props`
* Emissions with the **emission** scope in the section :doc:`emission`
* Diagrams are detailed in the section :doc:`diagram`


.. toctree::
   :maxdepth: 1
   
   scope
   var
   equation
   activation
   automaton
   formal_props
   emission
   diagram
