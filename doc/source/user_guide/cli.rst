.. _ref_cli:

======================
Command line interface
======================

The PyScadeOne library has a command line tool, which is automatically installed
in the ``Scripts`` directory of the Python installation folder. Ensure that
this ``Scripts`` folder is in your PATH environment variable.

The name of the tool is **pyscadeone**. It has the following sub-commands and options: 

Sub-commands:     
  - ``fmu``            generates an FMU. For more information, see :ref:`ref_fmu_export`.
  - ``script``         executes given script or module. 
  - ``simdata``        shows :ref:`ref_sim_data` files (in combination with --show).

Use ``pyscadeone <command> --help`` for a specific *<command>* help.

Options:
  -h, --help       Shows help message and exits 
  --version        Shows pyscadeone version
  --formats        Shows supported formats
  -v, --verbosity  Activates verbose mode. Several occurrences increase verbosity level
