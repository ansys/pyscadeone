
PyScadeOne documentation  |release|
===================================

.. _link_scadeone: https://www.ansys.com/products/embedded-software/ansys-scade-one
.. _link_psyscadeone: https://github.com/ansys/pyscadeone
.. _link_student: https://www.ansys.com/academic/students
.. _link_primer: https://github.com/ansys/DevRelPublic/blob/main/Downloads/ScadeOne/SwanPrimer_Rev_2_1.pdf

PyScadeOne is a Python library for the
`Ansys Scade One <link_scadeone_>`_
model-based development environment. 

This library allows:

- data access

  - reading and editing of :ref:`models <ref_model_sec>`
  - reading :ref:`projects <ref_create_project>` and navigating in models
  - reading and execution of :ref:`jobs <ref_jobs>`
  - reading and editing :ref:`simulation data <ref_sim_data>` files
  - reading :ref:`test results <ref_test_results>`
  - reading information about the :ref:`generated code <ref_generated_code>`

- ecosystem integration

  - wrapping generated code as Python code via a :ref:`Python wrapper <ref_python_wrapper>` service
   
  - :ref:`exporting FMI 2.0 <ref_fmu_export>` components
      - For more information, consult the `FMI website <https://fmi-standard.org/>`_.

.. grid:: 3

   .. grid-item-card:: :fa:`terminal` Getting started
      :link: ref_getting_started
      :link-type: ref

      Learn how to install and run PyScadeOne.
      Check for supported versions.


   .. grid-item-card:: :fa:`book` User guide
      :link: ref_user_guide
      :link-type: ref

      Understand key PyScadeOne concepts for projects and models.

   .. grid-item-card:: :fa:`book-open-reader` Library reference
      :link: ref_api
      :link-type: ref

      Understand PyScadeOne library, its capabilities,
      and how to use it programmatically.


.. grid:: 3


   .. grid-item-card:: :fa:`gears` Examples
      :link: ref_examples
      :link-type: ref

      Explore examples that show how to use PyScadeOne. 


   .. grid-item-card:: :fa:`users` Contribute
      :link: ref_contributing
      :link-type: ref
  
      Learn how to contribute to the PyScadeOne codebase
      or documentation.

   .. grid-item-card:: :fa:`link` Useful links

      - `PyScadeOne GitHub repository <link_psyscadeone_>`_
      - `Ansys Scade One <link_scadeone_>`_
      - `Ansys Scade One for students <link_student_>`_
      - `Swan language primer (version 2025.0) <link_primer_>`_

.. toctree::
   :hidden:
   :maxdepth: 3

   getting_started/index
   user_guide/index
   api/index
   examples/index
   contrib
