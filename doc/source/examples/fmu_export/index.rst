.. _Export FMU Example:

.. currentmodule:: ansys.scadeone.core.svc.fmu

==========
Export FMU
==========
In this section, we present how we can build an FMU package for FMI 2.0 (see :ref:`FMU Export`).

This can also be done through the command line, see how :ref:`at the end of the section <FMUex_command_line>`.

We use the same ``QuadFlightControl`` example. To set up the example see 
:ref:`QuadFlightControl python setup`.

In addition, we import the FMU related package:

.. code-block:: python

    from ansys.scadeone.core.svc.fmu import FMU_2_Export

For that example, we rely on a code generation job named `CodeGen`.
We first create a :py:class:`FMU_2_Export` object for this job:

.. literalinclude:: quad_flight_control-fmu.py
    :lines: 17-22

To generate and build the FMU, we need to have the code generation job executed, 
which produces the C code from the Swan model (execution is done from the Scade One IDE).
The script can then access the generated code data.

.. note::
    The :py:class:`GeneratedCode` object is accessible using the :py:attr:`FMU_2_Export.codegen` property.
    From there, you can check if code is generated with the :py:attr:`GeneratedCode.is_code_generated` property.

    .. literalinclude:: quad_flight_control-fmu.py
        :lines: 24-26

The FMI 2.0 files are generated using the :py:meth:`FMU_2_Export.generate` method:

.. literalinclude:: quad_flight_control-fmu.py
    :lines: 32

The FMU package is built from the FMI 2.0 and the Scade One generated files
using the :py:meth:`FMU_2_Export.build` method:

.. literalinclude:: quad_flight_control-fmu.py
    :lines: 33

.. important::
    The FMU is built using the gcc compiler provided with Scade One, unless it is already in the PATH.
    Explicit compiler path can also be provided using the *gcc_path* key *args* build argument.

    For the QuadFlightControl example, some library operators are defined in an include file.
    This file must be added to the ``swan_config.h``  file.
    This is done using the *args* build argument, by setting the *swan_config_end* key to the proper #include directive:

    .. literalinclude:: quad_flight_control-fmu.py
        :lines: 28-29


The FMU package is named *QuadFlightControl_QuadFlightControl.fmu* and is located under *QuadFlight_FMU_ME* sub directory.

.. note::
    The FMU package has been built for Model Exchange (ME). To build it for Co-Simulation (CS), set the *kind* parameter of the :py:meth:`FMU_2_Export.generate` method to "CS".

    .. literalinclude:: quad_flight_control-fmu.py
        :lines: 39-40

.. _FMUex_command_line:

-------------------------
Example with Command line
-------------------------

The FMU package can be built using the pyscadeone command line as follow:

.. code-block:: sh

    pyscadeone fmu "<s_one_install>/examples/QuadFlightControl/QuadFlightControl/QuadFlightControl.sproj"
    CodeGen --install_dir "<s_one_install> --outdir QuadFlight_FMU_ME --with_sources
    --build_arguments swan_config_end '#include "<s_one_install>/libraries/Math/resources/math_stdc.h"'

Refer to :ref:`FMU Export Command Line` for more details on command line usage.





