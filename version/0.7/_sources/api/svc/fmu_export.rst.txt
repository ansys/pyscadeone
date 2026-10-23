.. _ref_fmu_export:

.. currentmodule:: ansys.scadeone.core.svc.fmu

FMU export
==========

.. _FMU/FMI: https://fmi-standard.org/

This section contains the classes related to Scade One FMU Export.

The FMU Export supports the FMI 2.0 version for Model-Exchange and Co-Simulation.

The principle is to build a FMU package from a given Scade One operator.
This operator has to be a root operator of a code generation job,
and this job must have been executed before FMU export.

For more information about the FMI standard, consult `FMU/FMI`_.

.. code:: python

    from ansys.scadeone.core import ScadeOne
    from ansys.scadeone.core.svc.fmu import FMU_2_Export
	
    with ScadeOne('<install_dir>') as app:
        project = app.load_project('project.sproj')

        fmu = FMU_2_Export(project, 'CodeGen')

        fmu.generate('ME', 'project_ME')
        fmu.build(True)

.. admonition:: Limitations
   :class: warning

   **Imported Types**

   The FMU export is not possible if imported types are used for any of the inputs or outputs
   of the selected operator, or sensors in the scope of the export.

   **Supported Platforms**

   This version only supports gcc compiler on 64 bits Windows platform.

.. _fmu_export_cli:

FMU export command line
-----------------------

The FMU Export can also be performed using the pyscadeone command line, by selecting the fmu command.
The command performs the complete export, by running :py:meth:`FMU_2_Export.generate`
and :py:meth:`FMU_2_Export.build` methods of the :py:class:`FMU_2_Export` class.
All expected arguments can be passed through this command. Complete list is given by --help.

.. code:: sh

    pyscadeone fmu --help

.. code::

    usage: pyscadeone fmu [-h] [-inst INSTALL_DIR] [-op OPER_NAME]
                          [-max MAX_VARIABLES] [-k KIND] [-o OUTDIR] [-p PERIOD]
                          [-ws] [-args key value]
                          project job_name

    positional arguments:
      project               Scade One project
      job_name              Generated Code job name

    optional arguments:
      -h, --help            Show this help message and exit
      -inst INSTALL_DIR, --install_dir INSTALL_DIR
                            Scade One installation directory
      -op OPER_NAME, --oper_name OPER_NAME
                            Root operator name
      -max MAX_VARIABLES, --max_variables MAX_VARIABLES
                            Maximum number on FMI variables (flattened sensors,
                            inputs and outputs) supported by the export (1000 by
                            default).
      -k KIND, --kind KIND  FMI kind: ‘ME’ for Model Exchange (default), ‘CS’ for
                            Co-Simulation
      -o OUTDIR, --outdir OUTDIR
                            Directory where the FMU is built (by default,
                            'FMU_Export_<kind>_<job_name>')
      -p PERIOD, --period PERIOD
                            Execution period in seconds
      -ws, --with_sources   Keep the sources in the FMU package
      -args key value, --build_arguments key value
                            Build arguments. Use one -args argument per key.
                            Supported keys are: cc: compiler name (only gcc
                            supported), arch: compiler architecture (only win64
                            supported), gcc_path: path on the bin directory where
                            gcc is located, user_sources: list (comma separated)
                            of user source files and directories (code, includes),
                            cc_opts: list (comma separated) of extra compiler
                            options, link_opt: list (comma separated) of extra
                            link (dll creation) options, swan_config_begin: data
                            to insert at the beginning of swan_config.h,
                            swan_config_end: data to insert at the end of
                            swan_config.h.

FMU export documentation
------------------------

This section gives the API for the FMU Export.

*Note that the FMU export relies on the* :ref:`ref_generated_code` *API.*

.. autoclass:: FMU_2_Export
    :members: generate build
    :member-order: bysource




