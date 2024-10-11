.. _sec_user_guide:

==========
User Guide
==========


.. commented

.. jinja:: guide_ctx

   {% if full_guide %}

   .. toctree::
      :maxdepth: 2

      overview
      modeler
      verifier
      testing
      coverage
      toolbox
      example

   {% else %}

   .. toctree::
      :maxdepth: 2

      overview
      modeler
      example
   {% endif %}

   