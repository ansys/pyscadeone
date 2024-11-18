PyScadeOne
==========
|pyansys| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

Overview
________
PyScadeOne is a Python library for the
`Ansys Scade One <https://www.ansys.com/products/embedded-software/ansys-scade-one>`_:superscript:`TM`
model-based development environment.

This library allows:

- data access

  - reading projects and navigating in models
  - reading and editing simulation data files
  - reading test results
  - reading information about the generated code

- ecosystem integration

  - importing `SCADE Test <https://www.ansys.com/products/embedded-software/ansys-scade-test>`_ tests procedures
  - exporting `FMI 2.0 <https://fmi-standard.org/>`_ components


Documentation and issues
------------------------
Documentation for the latest stable release of PyScadeOne is hosted at
`PyScadeOne documentation <https://scadeone.docs.pyansys.com/version/stable/>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release to
viewing the documentation for the development version or previously released
versions.


On the
`PyScadeOne Issues <https://github.com/ansys/pyscadone/issues>`_
page, you can create issues to report bugs and request new features.
On the
`PyScadeOne Discussions <https://github.com/ansys/pyscadone/discussions>`_
page, you can post questions, share ideas, and get community feedback.

To reach the project support team, email
`pyansys.core@ansys.com <pyansys.core@ansys.com>`_.


Installation
------------
The  ``ansys-scadeone-core`` package supports Python 3.7 through Python 3.12 on Windows and Linux.

Install the latest release from `PyPI <https://pypi.org/project/ansys-scadeone-core/>`_ with:

.. code:: console

    pip install ansys-scadeone-core

Dependencies
------------

PyScadeOne requires
`.NET runtime 8.0 <https://dotnet.microsoft.com/en-us/download/dotnet/8.0>`_.


For developers
--------------
If you plan on doing local *development* of PyScadeOne with Git, install
the latest release with:

.. code:: console

   git clone https://github.com/ansys/pyscadeone.git
   cd pyscadeone
   pip install pip -U
   pip install -e .



Getting started
---------------

To use the PyScadeOne library, create a ``ScadeOne`` object:

.. code:: python

    from ansys.scadeone.core import ScadeOne

    my_project = "some_project.sproj"

    with ScadeOne() as app:
        # load a project
        project = app.load_project(my_project)
        # explore project resources: dependencies, files, ...
        swan_model = app.model
        # explore the Swan model, read data, ...

If your model uses the libraries provided with the Scade One installation,
you must create the ``ScadeOne`` object with the path to the Scade One installation:

.. code:: python

    scadeone_path = "C:/Program Files/Ansys/v251/ScadeOne"

    with ScadeOne(install=scadeone_path) as app:
        ...

For examples on how to use PyScadeOne, see the
`Examples <https://scadeone.docs.pyansys.com/version/stable/examples/index.html>`_
in the PyScadeOne documentation.

License and acknowledgments
---------------------------

PyScadeOne is licensed under the MIT license.


For more information about Ansys Scade One, see the
`Ansys Scade One <https://www.ansys.com/products/embedded-software/ansys-scade-one>`_
page on the Ansys website.
