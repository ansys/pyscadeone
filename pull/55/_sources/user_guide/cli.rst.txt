.. _ref_cli:

======================
Command line interface
======================

The PyScadeOne library has a command line tool, which is automatically installed
in the **Scripts** directory of the Python (virtual or not) installation folder. Ensure that
this **Scripts** folder is in your PATH environment variable.

The tool is named **pyscadeone**, and it has the following sub-commands and options: 

Sub-commands:     
  - **pycodewrap**     generates Scade One wrapper in Python, see :ref:`ref_python_wrapper`.
  - **simdata**        shows :ref:`ref_sim_data` files (in combination with --show).
  - **job**            list or run Scade One jobs. 

Use ``pyscadeone command --help`` for a specific *command* help.

Options:
  -h, --help       Shows help message and exits. 
  --version        Shows pyscadeone version.
  --formats        Shows supported formats: Swan language, simulation data, test results, etc.
  --log DIR        Specifies the directory path where the pyscadeone.log file is stored. Current path is used when no DIR value provided.
  -v, --verbosity  Activates verbose mode. Several occurrences increase verbosity level.

Installation path handling
--------------------------

Some features rely on tools in the Scade One installation folder, like the code generator.
When such feature is used, one must specify the path to the Scade One installation folder.
Possible ways to specify the installation path are:

Installation
  The installed PyScadeOne is configured with the proper installation path.

Environment variable
  The ``SCADE_ONE_INSTALL_DIR`` environment variable is used to define the installation folder.
  It overrides the installation path configured in the PyScadeOne installation.

Option
  Commands may have an option to specify the installation folder. The option supersedes other possibilities.

Note that in a script using the PyScadeOne library, the installation path is given, if necessary, 
when instantiating a :py:class:`ansys.scadeone.core.ScadeOne` object.
