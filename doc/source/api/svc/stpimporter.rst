.. _sec_sd_converter:

========================
SCADE Suite STP Importer
========================

The **stpimporter** command allows to turn sets of SSS test files defined 
in a SCADE Test STP document into simulation data files.
It is used as a command line, installed along with **pyscadone**:

.. code:: bash

    $ stpimporter stpfile sprojfile

See `Command Line <stp_importer_cli>`_ section for details.

Inputs
------

In order to start a conversion, the user shall provide:

- A procedure file (.stp) that has at least one record of SSS file(s) defined
- A record name (only if not all the records are to be converted)
- The associated Swan project (.sproj)

Outputs
-------

For each desired record of SSS files, the converter produces two files:

- One file ``name.sd`` setting all the input flows of the operator defined
  in the test, including used sensors, for the tests execution in each cycle.
- One file ``name_checks.sd`` for the tests verifications (checks) of outputs.

*name* corresponds to the record name in procedure file.

All the files are created in a folder which name matches the respective procedure element 
name in STP file. Folder is eventually created if not existing.

In addition, the ``stpimporter.log`` file is created in the folder where the command is launched.

This file notifies which variables or commands were not converted into simulation data,
and provides the full readable content of every generated simulation data file.

Supported features
------------------

- For every record, **stpimporter** parses any inits, preambles and scenarios
- For every flow, it looks for its corresponding type in the swan files based on **module::operator/name**
- Supported types:
    - bool
    - int8, int16, int32, int64
    - uint8, uint16, uint32, uint64
    - float32, float64
    - char
    - enums
    - structures
    - arrays
    - combination of the above
- **SSM::check** with optional *sustain* parameter - Assert equality for N cycles or *forever*. *real* option is ignored.
- **SSM::alias** - Any alias use will be replaced by the original variable name.
- **SSM::cycle** [n] - Add *n* (default 1) occurrences to each variable value.
- **SSM::alias_value** - Any alias use will be replaced by the value. 
  A value can contain other alias values.
- Use of *None* sequences - whenever a variable is not defined at a cycle.
- Values completion - fills all elements so that their number of values are equal.

Limitations
-----------

Multiple features offered by SSS files are not supported in Simulation Data.
Those will be ignored and reported in the logs.

- Any SSM commands that are not supported are ignored.
- *operator* attribute **must** be defined in stp file and be the same as the operator 
  in the .sss files.
- Input values:
    - Partial inputs are not supported. Ex: "(1, ,2)" meaning second value should be the
      the last given value.
    - **All** inputs must be initialized. There is default value like QTE does.
- Types:
    - Only numerical constants are evaluated to determine array sizes. 
      There is no evaluation of static expressions. 
    - Enumeration values set with a pragma are not supported 
      (Ex: given *enum {#pragma cg enum_val 6#end Red, Green, Blue}* a *6* in .sss 
      is not recognized as a valid enum value).
    - Imported types are not supported.
    - NaN, +Inf, -Inf are not supported.
    - **?** value is not supported.
- Checks not supported:
    - Tolerance (SSM::tolerance or *real* argument of SSM::check)
    - Probes are not taken into account (SSM::check).
    - Check of parts of a complex type (SSM::check with paths, indexes, occurrences, ...)
    - Complex checks (ranges, *lambda* expressions, ...)
    - Images checks (SSM::check image)
- CSV files - only SSS files are converted
- *None* and values cannot be mixed in the same sequence for structures and arrays.


.. _stp_importer_cli:

Command line
------------

The **stpimporter** command is installed in the ``Scripts`` folder of the Python installation directory
where *pyscadeone* is installed. The command line is as follows:

positional arguments:
  - ``stp_path``              STP file path
  - ``sproj_path``            Associated Swan project path

options:
  -h, --help            show this help message and exit
  -r RECORD_NAME, --record_name RECORD_NAME
                        Specific record name
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        Use specific directory
  -s S_ONE_INSTALL, --s_one_install S_ONE_INSTALL
                        Scade One installation path
  -v, --verbose_sd      Print exported sd files
  -R ROOT, --root ROOT  Specify root operator (override STP information)
  -n RENAMINGS, --renamings RENAMINGS 
                        Renaming log file from Scade Suite importer
  --no_gc               Disable garbage collection
		
The *--renamings* option specifies the path to the renaming log file 
from the SCADE Suite importer, usually named *renamings.log*. This file contains the renamings
performed by the SCADE Suite in case of packages within packages and declarations at top-level
out ouf any packages. This file is **mandatory** for **stpimporter** command in these cases
to correctly convert the SSS files with the proper names.

