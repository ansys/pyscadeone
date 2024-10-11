Namespace-Based Navigation
==========================

Access to a model element by its name is done with namespace-based navigation.

Name objects are:

- global: sensor, constant, type, group, or operator declaration
- local: input/output of an operator, a flow defined with **var**

Objects can be found in an other module, or can be hidden (an input by a local flow for instance).

The `get_declaration` from the :py:class:`ModuleBody` and :py:class:`ModuleInterface` returns
the global object (if any) with a given name (either an *id*, or *module::id* form).

The `get_declaration` from the :py:class:`Scope` returns
the object (if any) with a given name (either an *id*, or *module::id* form) in the current scope,
or in the enclosing scope, possibly reaching the module level.

See also :ref:`namespace_nav_ex` for a detailed example.
