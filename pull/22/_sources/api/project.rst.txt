Project management
==================

This section contains the classes related to Scade One projects.

.. code:: python
   
    from ansys.scadeone.core import ScadeOne, ProjectFile
    
    with ScadeOne() as app:
      project = app.load_project("project.sproj")
      ...

Project documentation
---------------------

This section gives the description of project class which
is used to manage Scade One projects.

.. currentmodule:: ansys.scadeone.core.project

Projects are used by :py:class:`ScadeOne` objects, and projects have a link to 
the application. To deal with the cross-links, we use the :py:class:`IProject` interface.



.. autoclass:: IProject

.. autoclass:: Project
   :exclude-members: add_module_body, add_module_interface, add_resource, add_dependency, remove_dependency


Project items
-------------

A project can manipulate different items saved using the **storage** module.
The API handles projects and Swan sources (*.swan* and *.swani* files).

Project file
~~~~~~~~~~~~

.. currentmodule:: ansys.scadeone.core.common.storage

.. autoclass:: ProjectFile
   :inherited-members:

Swan code
~~~~~~~~~

.. autoclass:: SwanFile
   :inherited-members:


.. _ref_resources:

Resources
~~~~~~~~~

.. currentmodule:: ansys.scadeone.core.project

A project can also use :py:class:`Resource` files. Resource are categorized in 3 different :py:class:`ResourceKind`,
each supports one file format:

- Header: **.h** files
- Source: **.c** files
- Simulation data: **.sd** files

.. autoclass:: Resource

.. autoclass:: ResourceKind