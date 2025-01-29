PyScadeOne
##########

|pyansys| |doc| |license| |ruff| |CI-CD|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?labelColor=black&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |doc| image:: https://img.shields.io/badge/docs-pyscadeone-green.svg?style=flat
   :target: https://scadeone.docs.pyansys.com/
   :alt: Doc

.. |license| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff

.. |CI-CD| image:: https://github.com/ansys/pyscadeone/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/ansys/pyscadeone/actions/workflows/ci.yml
   :alt: CI-CD


About
=====

PyScadeOne is a Python library for the `Ansys Scade One`_ model-based
development environment.

This library allows:

- Data access

  - Reading projects and navigating in models
  - Reading and editing simulation data files
  - Reading test results
  - Reading information about the generated code

- Ecosystem integration

  - Importing `SCADE Test`_ tests procedures
  - Exporting `FMI 2.0`_ components

Prerequisites
=============

PyScadeOne requires `.NET runtime 8.0`_.

Installation
============

Refer to the `official installation guidelines`_.

Documentation
=============

The documentation of PyScadeOne contains the following chapters:

- `Getting started`_. This section provides a brief overview and instructions
  on how to get started with the project. It typically includes information on
  how to install the project, set up any necessary dependencies, and run a
  basic example or test to ensure everything is functioning correctly.
 
- `User guide`_. The user guide section offers detailed documentation and
  instructions on how to use the project. It provides comprehensive
  explanations of the project's features, functionalities, and configuration
  options. The user guide aims to help users understand the project's concepts,
  best practices, and recommended workflows.
 
- `API reference`_. The API reference section provides detailed documentation
  for the project's application programming interface (API). It includes
  information about classes, functions, methods, and their parameters, return
  values, and usage examples. This reference helps developers understand the
  available API endpoints, their functionalities, and how to interact with them
  programmatically.
 
- `Examples`_. The examples section showcases practical code examples that
  demonstrate how to use the project in real-world scenarios. It provides
  sample code snippets or complete scripts that illustrate different use cases
  or demonstrate specific features of the project. Examples serve as practical
  references for developers, helping them understand how to apply the project
  to their own applications.

License
=======

The license of the PyScadeOne project is MIT. Read the full text of the license
in the `LICENSE`_ file.


.. References and links

.. _ansys scade one: https://www.ansys.com/products/embedded-software/ansys-scade-one

.. _SCADE Test: https://www.ansys.com/products/embedded-software/ansys-scade-test
.. _FMI 2.0: https://fmi-standard.org/

.. _.Net runtime 8.0: https://dotnet.microsoft.com/en-us/download/dotnet/8.0
.. _official installation guidelines: https://scadeone.docs.pyansys.com/version/dev/getting_started/index.html

.. _getting started: https://scadeone.docs.pyansys.com/version/dev/getting_started/index.html
.. _user guide: https://scadeone.docs.pyansys.com/version/dev/user_guide/index.html
.. _api reference: https://scadeone.docs.pyansys.com/version/dev/api/index.html
.. _examples: https://scadeone.docs.pyansys.com/version/dev/examples/index.html
