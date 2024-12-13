.. _ref_getting_started:

===============
Getting started
===============

Installation
------------

.. _venv: https://docs.python.org/3/library/venv.html

PyScadeOne is compatible with any Python version greater than Python 3.9. 
It has been tested with Python 3.9 and 3.12. It is distributed as a wheel package. 

To install PyScadeOne use the command:

.. code::

    pip install ansys_scadeone-<version>-py3-none-any.whl

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
