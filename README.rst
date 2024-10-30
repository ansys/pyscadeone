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
The PyScadeOne project provides a Pythonic interface to Scade One.


How to install
______________
Two installation modes are provided: user and developer.

For users
~~~~~~~~~
User installation can be performed by running:

    python -m pip install pyscadeone

PyScadeOne requires `.NET runtime 8.0.6 <https://dotnet.microsoft.com/en-us/download/dotnet/8.0>`.

For developers
~~~~~~~~~~~~~~
Installing PyScadeOne in developer mode allows to modify the source and enhance it. Before contributing to the project,
please refer to the `PyAnsys Developer's guide <https://dev.docs.pyansys.com/>`.

You will need to follow these steps:

1. Start by cloning this repository:

.. code:: console

        git clone https://github.com/pyansys/pyscadeone

2. Create a fresh-clean Python environment and activate it. Refer to the
   official `venv <https://docs.python.org/3/library/venv.html>` documentation if you require further information:

.. code:: console

        # Create a virtual environment
        python -m venv .venv

        # Activate it in a POSIX system
        source .venv/bin/activate

        # Activate it in Windows CMD environment
        .venv\Scripts\activate.bat

        # Activate it in Windows Powershell
        .venv\Scripts\Activate.ps1

3. Make sure you have the latest version of `pip <https://pypi.org/project/pip/>`:

.. code:: console

    python -m pip install -U pip

4. Install `flit <https://flit.pypa.io/en/stable/index.html>`

.. code:: console

    pip install flit

5. Install the project in editable mode, with all development required packages:

.. code:: console

    flit install --pth_file # Windows/Linux
    flit install --symlink  # Linux only (preferred)


6. Finally, verify your development installation by running:

.. code:: console

    pytest

**Note**

These commands (and others) are grouped in the ``Makefile``. Try:

.. code:: console

    make help

to get the targets for setup, build, checks, ...

Style and Testing
_________________

If required, you can always call the style commands (`black <https://github.com/psf/black>`,
`isort <https://github.com/PyCQA/isort>`, `flake8 <https://flake8.pycqa.org/en/latest/>`...)
or unit testing ones (`pytest <https://docs.pytest.org/en/stable/>`) from the command line.

Documentation
_____________

For building documentation, you can either run the usual rules provided in the
`Sphinx <https://www.sphinx-doc.org/en/master/>` ``doc/Makefile``, such as:

.. code:: console

    make -C doc/ html

    # then open the documentation with (under Linux):
    your_browser_name doc/html/index.html

    # then open the documentation with (under Windows):
    start doc/html/index.html

License and acknowledgments
___________________________

PyScadeOne is licensed under the MIT license.

PyScadeOne makes no commercial claim over Ansys whatsoever. This tool extends the functionality of Scade One by adding
a Python interface to the Scade One service without changing the core behavior or license of the original software.
The use of the PyScadeOne requires a legally licensed local copy of Scade One.

To get a copy of Scade One, visit the`Ansys Scade One <https://www.ansys.com/products/embedded-software/ansys-scade-one>` page on the Ansys webside.
