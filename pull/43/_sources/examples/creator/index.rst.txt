.. _ref_creator_ex:

Create a Scade One project
==========================
This section presents how to create a Scade One project using the Python API.
You can start by creating a new project, then add modules, declarations, a diagram,
blocks, and connections between them.

.. note:: 
    Project dependencies have not supported yet. You should add the dependencies manually.
    
.. currentmodule:: ansys.scadeone.core

Create a new project
---------------------
Using the :py:class:`ScadeOne` class, you can create a new project:

.. literalinclude:: create_project.py
    :start-at: from ansys.scadeone.core
    :end-at: project = 

Once the project is created, you can add a new module interface:

.. literalinclude:: create_project.py
    :lines: 34

Also, you can add a new module:

.. literalinclude:: create_project.py
    :lines: 35

Namespace is also supported for creating new modules:

.. literalinclude:: create_project.py
    :lines: 36

In the new module, you can add a new declaration using the Scade One text syntax:

.. literalinclude:: create_project.py
    :lines: 38

.. currentmodule:: ansys.scadeone.core.swan

Also, a declaration can be added using the :py:class:`ModuleBody` or :py:class:`ModuleInterface`
*add_<declaration>()* methods.

For instance, to create a new constant, or new operators:

.. literalinclude:: create_project.py
    :lines: 39-40, 46

You can also add textual operators:

.. literalinclude:: create_project.py
    :lines: 52-59

Once an operator is added to the module, you can add inputs or outputs:

.. literalinclude:: create_project.py
    :lines: 41-44

.. currentmodule:: ansys.scadeone.core.svc.swan_creator

A module can be used in another module:

.. literalinclude:: create_project.py
    :lines: 65

You can add a diagram, blocks, and connections between blocks to the operator,
as it is presented in the following diagram:

.. figure:: images/diagram.png

The corresponding code is:

.. literalinclude:: create_project.py
    :lines: 67-85

Finally, save the project, and look at the generated code:

.. literalinclude:: create_project.py
    :lines: 87-91
    
Complete example
----------------

This is the complete script presenting a Scade One model creation.

.. literalinclude:: create_project.py
    :lines: 23-92
