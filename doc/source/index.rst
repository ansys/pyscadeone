PyScadeOne Documentation  |version|
===================================
..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.


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

.. grid:: 3

   .. grid-item-card::
            :img-top: _static/assets/index_getting_started.png

            Getting started
            ^^^^^^^^^^^^^^^

            Learn how to install and run PyScadeOne.
            Check for supported versions.

            +++

            .. button-link:: getting_started/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Getting started

   .. grid-item-card::
            :img-top: _static/assets/index_user_guide.png

            User guide
            ^^^^^^^^^^

            Understand key PyScadeOne concepts for projects and models.

            +++
            .. button-link:: user_guide/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  User guide

   .. grid-item-card::
            :img-top: _static/assets/index_api.png

            Scade One API reference
            ^^^^^^^^^^^^^^^^^^^^^^^

            Understand PyScadeOne API, its capabilities,
            and how to use it programmatically.

            +++
            .. button-link:: api/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  PyScadeOne API reference


.. grid:: 2


   .. grid-item-card::
            :img-top: _static/assets/index_examples.png

            Examples
            ^^^^^^^^

            Explore examples that show how to use PyScadeOne. 

            +++
            .. button-link:: examples/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Examples

   .. grid-item-card::
            :img-top: _static/assets/index_contribute.png

            Contribute
            ^^^^^^^^^^
            Learn how to contribute to the PyScadeOne codebase
            or documentation.

            +++
            .. button-link:: contrib.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Contribute


.. toctree::
   :hidden:
   :maxdepth: 3

   getting_started/index
   user_guide/index
   api/index
   examples/index
   contrib

Indices and tables
==================
* :ref:`genindex`
* :ref:`search`
