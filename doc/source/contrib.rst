.. _ref_contributing:

============
Contributing
============
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/overview/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all `Guidelines and Best Practices
<https://dev.docs.pyansys.com/guidelines/index.html>`_ before attempting to
contribute to PyScadeOne.
 
The following contribution information is specific to PyScadeOne.

Cloning the PyScadeOne Repository
---------------------------------
Run this code to clone and install the latest version of PyScadeOne in development mode:

.. code::

    git clone https://github.com/pyansys/pyscadeone
    cd pyscadeone
    pip install pip -U
    pip install -e .


Posting Issues
--------------
Use the `PyScadeOne Issues <https://github.com/pyansys/pyscadeone/issues>`_
page to submit questions, report bugs, and request new features. When possible, we
recommend that you use these issue templates:

* Bug report template
* Feature request template

If your issue does not fit into one of these categories, create your own issue.

To reach the project support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Viewing PyScadeOne Documentation
--------------------------------
Documentation for the latest stable release of PyScadeOne is hosted at
`PyScadeOne Documentation <https://scadeonedocs.pyansys.com>`_.

Documentation for the latest development version, which tracks the
``main`` branch, is hosted at  `Development PyScadeOne Documentation <https://dev.scadeonedocs.pyansys.com/>`_.
This version is automatically kept up to date via GitHub actions.

Testing Scade One
-----------------

PyScadeOne uses `pytest`. In the main directory use:

.. code::

    pytest

Tests are in `tests` folder. Please add your own tests for non-regression.

Code Style
----------
PyScadeOne follows PEP8 standard as outlined in the `PyAnsys Development Guide
<https://dev.docs.pyansys.com>`_ and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks. For example::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed


Log errors
~~~~~~~~~~

PyScadeOne has a logging tool and a log file that is automatically generated in the project folder.

The logging tool is a attached to a ScadeOne instance, and the instance
is passed to projects, project is passed to models, etc.

.. code:: python

    app = ScadeOne()
    app.logger.error("This is an error message.")
    app.logger.warning("This is a warning message.")
    app.logger.info("This is an info message.")


Maximum line length
~~~~~~~~~~~~~~~~~~~
Best practice is to keep the length at or below 120 characters for code, docstrings,
and comments. Lines longer than this might not display properly on some terminals
and tools or might be difficult to follow.
