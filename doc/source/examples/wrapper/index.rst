.. _ref_python_wrapper_example:

.. currentmodule:: ansys.scadeone.core.svc.wrapper

Python wrapper
==============
This section describes how to generate and use the Python wrapper (see :ref:`ref_python_wrapper`).

The **QuadFlightControl** example is used to illustrate the use of the Python wrapper service.

.. note::
    The **QuadFlightControl** example is not completely supported by the Python wrapper service. The following code
    presents only how to use the service. A simpler Scade One project should be used to generate a Python wrapper
    according to service support (see :ref:`ref_python_proxy`).

Generation
----------

.. currentmodule:: ansys.scadeone.core.svc.wrapper.python_wrapper

The Python wrapper can be generated using the :py:class:`PythonWrapper` class or the PyScadeOne command line.

The code generation job must be executed before generating the Python wrapper. The job execution can be performed via
the Scade One IDE or the PyScadeOne job service (see :ref:`ref_jobs`).

The Python wrapper produces a Python class that wraps the root operators of the Scade One model. The generated class
can be found in the same output directory of the code generation job.

The :py:class:`PythonWrapper` class use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following script shows how to generate the Python wrapper using the :py:class:`PythonWrapper` class:

.. literalinclude:: python_wrapper.py

Command line use
^^^^^^^^^^^^^^^^
The Python wrapper service can be built using the PyScadeOne command line as follows:

.. code-block:: sh

    pyscadeone wrapper "<s_one_install>/examples/QuadFlightControl/QuadFlightControl/QuadFlightControl.sproj"
    "CodeGen" "QuadFlightControl::FlightControl" --install_dir "<s_one_install> --out_name "opt_wrapper"

For more details on command line usage, consult :ref:`ref_python_wrapper_command_line`.

Usage
-----
Once the Python wrapper is generated, it can be used to interact with the Scade One model in Python. The following
example shows how to use the Python wrapper to interact with the **QuadFlightControl** model:

.. literalinclude:: python_wrapper_usage.py





