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
the application. To deal with the cross-links, we use the :py:class:`IProject` interface [#]_.



.. autoclass:: IProject

.. autoclass:: Project


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

.. rubric:: Footnotes


.. [#] See *How to avoid bidirectional class and module dependencies*  `softwareengineering.stackexchange.com <https://softwareengineering.stackexchange.com/questions/369146/how-to-avoid-bidirectional-class-and-module-dependencies>`_ 