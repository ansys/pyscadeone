.. _ref_contributing:

============
Contributing
============

PyScadeOne is part of the `Scade One <https://www.ansys.com/products/embedded-software/ansys-scade-one>`_ product, and is developed by its R&D team.

Contributing to PyScadeOne is welcomed and can be in the form of discussions, code, documentation or issue reports


Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all style guidelines before attempting to contribute to PyScadeOne.
 
The following contribution information is specific to PyScadeOne.

Viewing PyScadeOne Documentation
--------------------------------
Documentation for the latest stable release of PyScadeOne is hosted at
`PyScadeOne Documentation <https://scadeone.docs.pyansys.com>`_.

This version is automatically kept up to date via GitHub actions.


Posting Issues
--------------

Use the `PyScadeOne Issues <https://github.com/ansys/pyscadeone/issues>`_
page to submit questions, report bugs, and request new features. When possible, we
recommend that you use one of the existing templates


To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

Discussions
-----------

Use the `PyScadeOne Discussions <https://github.com/ansys/pyscadeone/discussions>`_	
page to ask questions, share ideas, and connect with other users.


Contributing Code
-----------------

.. Note::
   As PyScadeOne is a component of the Scade One product, the development team
   is responsible for the code. Any contribution will be analyzed and possibly
   integrated by the development team.

Getting the Source Code
^^^^^^^^^^^^^^^^^^^^^^^
Run this code to clone and install the latest version of PyScadeOne in development mode:

.. code::

    git clone https://github.com/ansys/pyscadeone
    cd pyscadeone
    pip install pip -U
    pip install -e .

Code Style
^^^^^^^^^^
PyScadeOne follows PEP8 standard as outlined in the `PyAnsys Development Guide
<https://dev.docs.pyansys.com>`_.


Testing
^^^^^^^

PyScadeOne uses `pytest`. In the main directory use:

.. code::

    pytest

Tests are in `tests` folder. Please add your own tests for non-regression.
