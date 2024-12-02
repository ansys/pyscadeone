.. _ref_sd_converter:

========================
SCADE Suite STP Importer
========================

The **stpimporter** command allows to turn sets of SSS scenarios defined 
in a SCADE Test STP test procedure into simulation data files.
It is used as a command line, installed along with **pyscadone**:

.. code:: bash

  $ stpimporter stpfile sprojfile

See `Command Line <stp_importer_cli_>`_ section for details.

Inputs
------

To start a conversion, the user shall provide:

- A procedure file (.STP) that has at least one record of the defined SSS file(s).
- A record name (only if not all the records should be converted).
- The associated Scade One project (.SPROJ).

Outputs
-------

For each desired record, the importer produces two files:

- One file ``name.sd`` setting all the input flows of the operator defined
  in the test, including used sensors, for the tests execution in each cycle
- One file ``name_checks.sd`` for the checks of outputs.

The *name* corresponds to the record name in the procedure file.

All the files are created in a folder which name matches the respective procedure element 
name in the STP file. A folder is eventually created if not existing.

The ``stpimporter.log`` file is created in the folder where the command is launched.
This file notifies which variables or commands are not converted into simulation data,
and provides the full readable content of every generated simulation data file.

Supported features
------------------

* For every record, **stpimporter** parses any inits, preambles and scenarios.
* For every flow, it looks for its corresponding type in the Swan files based on **module::operator/name**.
* Supported types:

  * bool
  * int8, int16, int32, int64
  * uint8, uint16, uint32, uint64
  * float32, float64
  * char
  * enums
  * structures
  * arrays
  * combination of the above

* The **SSM::check** command with optional *sustain* parameter

  * Asserts equality for N cycles or *forever*. The *real* option is ignored.

* The **SSM::alias** command

  * Replaces any alias use by the original variable name.

* The **SSM::cycle** [n] command

  * Adds *n* (default 1) occurrences to each variable value.

* The **SSM::alias_value** command

  * Replaces any alias use by a value. A value can contain other alias values.

* The use of *None* sequences - whenever a variable is not defined at a cycle.
* The generated sequences have all the same number of values. 
  They are eventually completed if the .SSS scenario does not contain enough values for some signals.

Limitations
-----------

Multiple features offered by SSS files are not supported in Simulation Data.
Those will be ignored and reported in the logs:

* Any SSM commands that are not supported are ignored.
* The *operator* attribute **must** be defined in STP file and be the same as the operator 
  in the .SSS files.
* Input values:

  * Partial inputs are not supported. The example "(1, ,2)" means that the second value should be the last given value.
  * **All** inputs must be initialized. There is no default value like QTE does.

* Types:

  * Only numerical constants are evaluated to determine array sizes. There is no evaluation of static expressions
  * Enumeration values set with a pragma are not supported. For example, given *enum {#pragma cg enum_val 6#end Red, Green, Blue}* a *6* in .SSS is not recognized as a valid enum value
  * Imported types are not supported
  * NaN, +Inf, -Inf are not supported
  * **?** value is not supported.

* Checks not supported:

  * Tolerance (SSM::tolerance or *real* argument of SSM::check)
  * Probes are not taken into account (SSM::check)
  * Check of parts of a complex type (SSM::check with paths, indexes, occurrences, ...)
  * Complex checks (ranges, *lambda* expressions, ...)
  * Images checks (SSM::check image).

* CSV files - only SSS files are converted.
* The *None* values cannot be mixed with actual values in the same sequence for structures and arrays.


.. _stp_importer_cli:

Command line
------------

The **stpimporter** command is installed in the ``Scripts`` folder of the Python installation directory
where the *pyscadeone* library is installed. The command line is as follows:

positional arguments:
  - ``stp_path``              STP file path
  - ``sproj_path``            Associated Swan project path

options:
  -h, --help            Show this help message and exit
  -r RECORD_NAME, --record_name RECORD_NAME
                        Specific record name
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        Use specific output directory
  -s S_ONE_INSTALL, --s_one_install S_ONE_INSTALL
                        Scade One installation path
  -v, --verbose_sd      Print exported SD files
  -R ROOT, --root ROOT  Specify root operator (override STP information)
  -n RENAMINGS, --renamings RENAMINGS 
                        Renaming log file from Scade Suite importer
  --no_gc               Disable garbage collection
		
The *--renamings* option specifies the path to the renaming log file 
from the SCADE Suite importer, usually named *renamings.log*. This file contains the renamings
performed by the SCADE Suite importer in case of packages within packages and declarations at top-level
out ouf any packages. This file is **mandatory** for **stpimporter** command in these cases
to correctly convert the SSS files with the proper names.

