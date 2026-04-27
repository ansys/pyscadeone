Navigation using names
======================

Access to a model element by its name is done with namespace-based navigation.

Named objects are:

- Global: sensor, constant, type, group, or operator declaration
- Local: input/output of an operator, a flow defined with **var**.

Objects can be found in another module, or can be hidden (an input by a local flow for instance).

The :py:func:`get_declaration` function returns:

- The global object (if any) with a given name (either an *id*, or *module::id* form), from the :py:class:`ModuleBody` and :py:class:`ModuleInterface`.
- The object (if any) with a given name (either an *id*, or *module::id* form) in the current scope, or in the enclosing scope, possibly reaching the module level, from the :py:class:`Scope`.

See also :ref:`namespace_nav_ex` for a detailed example.
