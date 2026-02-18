.. _ref_python_wrapper:

.. currentmodule:: ansys.scadeone.core.svc.wrapper

Python wrapper
==============

The Python wrapper is a PyScadeOne service that allows running a Scade One model in Python.

It works by generating a Python proxy for each root operator defined in the code generation job. This generation
can be performed using
:ref:`the PythonWrapper class <ref_python_wrapper_class_use>` or
:ref:`the Python wrapper command line <ref_python_wrapper_command_line>`. An example of use is given in
the :ref:`ref_python_wrapper_example` section.

This operator has to be a root operator of a code generation job,
and this job must be executed before using the Python wrapper service.

.. _ref_python_proxy:

Python proxy
------------

The Python proxy is a Python module containing a class that represents the root operators selected in the code
generation job.

This class has the following properties:

- inputs: the list of input variables
- outputs: the list of output variables

and the following methods:

- cycle: call the cycle function
- reset: call the reset function

The module also contains the sensors used by the root operator. The sensors are defined in
a global variable `sensors`.

The Python wrapper service only supports:

- root operators listed in the code generation job
- sensors
- scalar types for sensors
- scalar, structure, enum and array types for inputs and outputs. The array, scalar, structure,
  and enum types can only be defined by scalar types.

Once the module is generated, it can be used in a Python script to execute a root operator,
providing the input values and getting the output ones:

.. code:: python

    # Import the generated Python proxy module
    import <proxy_name>

    # Create an instance of a root operator
    root_operator = <proxy_name>.<root_operator_name>()

    # Set the input variables
    root_operator.inputs.<input_variable_name> = <input_value>

    # Set the sensors
    sensors = <proxy_name>.sensors
    sensors.<sensor_name> = <sensor_value>

    # Execute the cycle function
    root_operator.cycle()

    # It could be executed multiple times
    root_operator.cycle(5) # the cycle function will be executed 5 times

    # Get the output variables
    output = root_operator.outputs.<output_variable_name>

    # Print the output value
    print(output)

    # Reset the operator
    root_operator.reset()

.. _ref_python_wrapper_class_use:

The :py:class:`PythonWrapper` class use
---------------------------------------

.. currentmodule:: ansys.scadeone.core.svc.wrapper.python_wrapper

The Python proxy can be generated using the :py:class:`PythonWrapper` class as follows:

.. code:: python

    from ansys.scadeone.core.svc.wrapper import PythonWrapper

    # Before using `PythonWrapper`, code generation job must be executed

    install_dir = <s_one_install>
    project_path = <scade_one_project_path>
    job_name = <codegen_job_name>
    proxy_name = <proxy_name>
    target_path = <target_path>

    app = ScadeOne(install_dir)
    project = app.load_project(project_path)

    # Create a PythonWrapper instance
    wrapper = PythonWrapper(project, job_name, proxy_name, target_path)
    wrapper.generate()

.. _ref_python_wrapper_command_line:

Python wrapper command line
---------------------------

The Python wrapper can also be generated using the PyScadeOne command line, by selecting the `wrapper` command.
All expected arguments can be passed through this command. A complete list of arguments is given by `\-\-help`.

.. code:: sh

    pyscadeone pycodewrap --help

.. code::

    usage: pyscadeone pycodewrap [-h] --install-dir INSTALL_DIR -j JOB [-o OUTPUT]
                             [--target-dir TARGET_DIR]
                             project

    positional arguments:
      project               Scade One project

    options:
      -h, --help            show this help message and exit
      --install-dir INSTALL_DIR
                            Scade One installation directory
      -j JOB, --job JOB     Generated Code job name
      -o OUTPUT, --output OUTPUT
                            Name of the Python wrapper module. By default, the
                            name is `root_wrapper`
      --target-dir TARGET_DIR
                            Wrapper directory. By default, a
                            directory with the wrapper name is created in the
                            current directory.

.. _ref_python_wrapper_doc:

Python wrapper class documentation
----------------------------------

This section gives the documenation of the :py:class:`PythonWrapper` class.

.. currentmodule:: ansys.scadeone.core.svc.wrapper

.. autoclass:: PythonWrapper
    :class-doc-from: init
    :member-order: bysource
