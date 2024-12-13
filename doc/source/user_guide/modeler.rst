.. _ref_modeler:

Modeler
=======


This section uses the **QuadFlightControl** example provided with Scade One.
The example is located in the ``examples/QuadFlightControl/QuadFlightControl`` folder in the Scade One
installation directory.

.. literalinclude:: quad_flight_control.py
    :lines: 7-12

ScadeOne instance
-----------------

A *ScadeOne* instance is created with the following code:

.. literalinclude:: quad_flight_control.py
    :lines: 14

where :py:attr:`install_dir` is the location of Scade One installation and it could take a string or a
a :py:class:`pathlib.Path` object as value. The *app* object is then used to access to projects.


Swan projects
-------------

A Swan project is opened with :py:meth:`ansys.scadeone.core.ScadeOne.load_project`.

.. literalinclude:: quad_flight_control.py
    :lines: 15

The :py:meth:`ansys.scadeone.core.ScadeOne.load_project` can take a string
or a :py:class:`pathlib.Path` object as parameter.

If the project exists, a :py:class:`ansys.scadeone.core.project.Project` object is
returned, else *None*. 

Several projects can be loaded, with successive calls to the `load_project()` method.
They can be accessed using the `app.projects` property.

.. note::
    
    From the :py:attr:`ansys.pyscadeone.core.project.Project.app`, one has access to the
    Scade One app containing the project.

Dependencies
^^^^^^^^^^^^

A project may have several sub-projects as *dependencies*. 
The list of dependencies is returned with
the :py:meth:`ansys.scadeone.core.project.Project.dependencies` method.

.. literalinclude:: quad_flight_control.py
    :lines: 17-21


Swan module bodies and interfaces files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Swan module bodies (*.swan* files) and Swan module interfaces (*.swani* files)
can be listed with the :py:meth:`ansys.scadeone.core.project.Project.swan_sources`
method.

.. literalinclude:: quad_flight_control.py
    :lines: 23-27


Swan model
----------

A :py:class:`ansys.scadeone.core.model.Model` object represents a Swan model or program.
A model is built from the sources of the project.

The project's model can be accessed with the 
:py:attr:`ansys.scadeone.core.project.Project.model` property.

.. code:: python

    # Get the model
    model = project.model

.. note::

    From a model, one can access to the Scade One instance, 
    with the model's *project* property as in `my_app = model.project.app`

A model contains all modules (body or interface) from the Swan sources. For each module,
one has access to the declarations it contains. 

From a :py:class:`ansys.scadeone.core.model.Model` object, one can therefore access to:

- the modules,
- all declarations,
- specific declarations, like types or constants
- or a particular declaration.

Here are some examples:

.. literalinclude:: quad_flight_control.py
    :lines: 32-36


.. note::

    PyScadeOne tries to be lazy to handle large projects. For instance,
    looking for all sensors requires to load all sources.

    Looking for a specific item, the sources are loaded until the required
    item is found.

In the following example, the :py:meth:`ansys.scadeone.core.model.Model.find_declaration`
is used to filter a specific operator. In that case, the search stops (and the load)
when the requested operator is found. As we will use Swan constructs, we need to import
their definitions:

.. code:: python

    # Module defining all Swan-related classes, see below
    import ansys.scadeone.core.swan as swan

Here an example to filter declarations to get specific operator:

.. literalinclude:: quad_flight_control.py
    :lines: 39-47


Swan language
-------------

The model content represents the structure of the Swan program, starting with
the declarations: types, constants, groups, sensors, operators, and signatures.

For an operator or a signature, one can access to the input and output flows
and to the body for operator. Then from the body, one can access to the content of diagrams, equations, etc.

All Swan language constructs are represented by classes from the 
:py:mod:`ansys.scadeone.core.swan` module. The section :ref:`ref_swan_api` describes
the Swan classes, with respect to the structure of the language reference documentation in the product.

Resuming with the previous code example, here is a usage sample of the Swan language API:

.. literalinclude:: quad_flight_control.py
    :lines: 49-
