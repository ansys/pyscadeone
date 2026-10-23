.. _ref_fmu_example:

.. currentmodule:: ansys.scadeone.core.svc.fmu

==========
Export FMU
==========
This section presents how to build an FMU package for FMI 2.0 (see :ref:`ref_fmu_export`).

This can also be done through the command line, see how 
:ref:`at the end of the section <fmu_export_cli>`.

The  ``QuadFlightControl`` example is used. To set up the example see 
:ref:`ref_QuadFlightControl_python_setup`.

The following package must be used:

.. code-block:: python

    from ansys.scadeone.core.svc.fmu import FMU_2_Export

The example relies on a code generation job named `CodeGen`.
A :py:class:`FMU_2_Export` object is created for this job:

.. literalinclude:: quad_flight_control-fmu.py
    :lines: 39-44

To generate and build the FMU, ensure to have the code generation job executed, 
which produces the C code from the Swan model (execution is done from the Scade One IDE).
The script can then access the generated code data.

.. note::
    The :py:class:`GeneratedCode` object is accessible using the :py:attr:`FMU_2_Export.codegen` property.
    From there, you can check if code is generated with the :py:attr:`GeneratedCode.is_code_generated` property.

    .. literalinclude:: quad_flight_control-fmu.py
        :lines: 46-48

The FMI 2.0 files are generated using the :py:meth:`FMU_2_Export.generate` method:

.. literalinclude:: quad_flight_control-fmu.py
    :lines: 54

The FMU package is built from the FMI 2.0 and the Scade One generated files
using the :py:meth:`FMU_2_Export.build` method:

.. literalinclude:: quad_flight_control-fmu.py
    :lines: 55

.. important::
    The FMU is built using the gcc compiler provided with Scade One, unless it is already in the PATH.
    Explicit compiler path can also be provided using the *gcc_path* key *args* build argument.

    For the QuadFlightControl example, some library operators are defined in an include file.
    This file must be added to the ``swan_config.h``  file.
    This is done using the *args* build argument, by setting the *swan_config_end* key to the proper #include directive:

    .. literalinclude:: quad_flight_control-fmu.py
        :lines: 50-51


The FMU package is named *QuadFlightControl_QuadFlightControl.fmu* and is located under *QuadFlight_FMU_ME* sub directory.

.. note::
    The FMU package has been built for Model Exchange (ME). To build it for Co-Simulation (CS), 
    set the *kind* parameter of the :py:meth:`FMU_2_Export.generate` method to "CS".

    .. literalinclude:: quad_flight_control-fmu.py
        :lines: 61-62

.. _ref_fmu_command_line:

-------------------------
Example with command line
-------------------------

The FMU package can be built using the pyscadeone command line as follow:

.. code-block:: sh

    pyscadeone fmu "<s_one_install>/examples/QuadFlightControl/QuadFlightControl/QuadFlightControl.sproj"
    CodeGen --install_dir "<s_one_install> --outdir QuadFlight_FMU_ME --with_sources
    --build_arguments swan_config_end '#include "<s_one_install>/libraries/Math/resources/math_stdc.h"'

Refer to :ref:`fmu_export_cli` for more details on command line usage.





