.. _ref_getting_started:

===============
Getting started
===============

Installation
------------

.. _venv: https://docs.python.org/3/library/venv.html

.. _PyPi: https://pypi.org/project/ansys-scadeone-core/

PyScadeOne is compatible with any Python version strictly greater than Python 3.9. 
It has been tested with Python 3.10 and 3.12. It can be found on `PyPi`_ 
and it also distributed as a wheel package with the Scade One tool. 

To install PyScadeOne use the command:

.. code::

    pip install ansys-scadeone-core

.. note::

    PyScadeOne comes with two (2) sets of package dependencies:

    - **Direct dependencies** are the packages that PyScadeOne directly relies on, 
      with their minimum required versions. This is the default installation mode.

    - **Frozen dependencies** include both the direct and indirect packages that 
      PyScadeOne depends on, with their exact versions. This is an optional installation mode.
      Frozen dependencies are useful when you want to install the exact versions of the dependencies 
      that PyScadeOne was tested and validated with.


    To install PyScadeOne with the frozen dependencies, use the command:
    
        pip install ansys-scadeone-core[frozen-dependencies]
        
    The installation may fail if the exact version of a frozen dependency is not compatible 
    with a version in the Python environment. A *virtual environment* is recommended to avoid conflicts.

You may want to install PyScadeOne in a Python virtual environment. Please look at
the Python `venv`_ module.

Requirements
------------

.. _dotnet: https://dotnet.microsoft.com/en-us/download/dotnet/

.. _scripts: https://dotnet.microsoft.com/en-us/download/dotnet/scripts

.. _FSharp: https://www.nuget.org/packages/FSharp.Core/

.. _FsYaccFsLex: https://fsprojects.github.io/FsLexYacc/

PyScadeOne requires .NET Runtime 8 on your host.
Please look at `dotnet`_ and at the installation `scripts`_. 

PyScadeOne uses the following .NET libraries:

- `FsYaccFsLex`_, required for the Swan language parser 
- `FSharp`_, required for the Swan language parser

The required DLLs are delivered with PyScadeOne.

Supported versions
------------------

.. include:: versions.rst

Quick start
-----------

Here is a small script showing how to load a Scade One project 
and get its model.

.. code:: python

    from ansys.scadeone.core import ScadeOne

    my_project = "some_project.sproj"

    with ScadeOne() as app:
        # load a project
        project = app.load_project(my_project)
        # explore project resources: dependencies, files, ...
        swan_model = project.model
        # do something nice with the swan model
    
More details can be found in :ref:`Modeler <ref_modeler>` section,
and in :ref:`API <ref_api>` sections.

Limitations
-----------

- :ref:`ref_python_wrapper` limitations:

  - Two sensors with the same name in different modules cannot be correctly generated.

- Swan language limitations:

  - The optional *luid* of a **diagram** construct is ignored.

