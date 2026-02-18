.. _sec_test_objects:

Swan Test constructs
====================

.. currentmodule:: ansys.scadeone.core.model

Swan Test extends the Swan language by adhering to its syntax and rules while adding extensions to allow testing and debugging of Swan operators.
Interface definitions are not supported in a Test module. The Test module body is exclusively defined by a file with the `.swant` extension.
The Test module includes the following Test objects:

.. toctree::
   :maxdepth: 1

   test_module
   test_harness
   data_source
   set_sensor
   oracle


To include a Test module in a Model, use the :py:meth:`Model.add_test_module()` method.

To get a Test module, use the :py:meth:`Model.get_test_module()` method.

If the :py:meth:`Model.load_all_modules()` method is called, all project modules including Test modules will be loaded.

See also :ref:`ref_test_creation`. 