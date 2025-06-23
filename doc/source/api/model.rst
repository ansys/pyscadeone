Model
=====

A Model object gives access to the model items defined in the Swan sources 
of a project. The *unique* Model instance of a project is the object returned 
by the :py:attr:`ansys.scadeone.core.project.Project.model` property of a
project instance. 

.. code:: python

    from ansys.scadeone.core import ScadeOne
    with ScadeOne() as app:
        project = app.load_project('project.sproj')
        model = project.model



Model documentation
-------------------

.. currentmodule:: ansys.scadeone.core.model

.. autoclass:: Model
    :exclude-members: add_body, add_interface



