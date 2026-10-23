.. _ref_jobs:

============
Project jobs
============

Overview
========

Project jobs can be loaded, edited, and executed.
A job execution requires Scade One to be installed as it uses the *job launcher* executable from Scade One tools.

Example
=======

Following example shows how to load a job from a project, edit its parameters, save, and execute it.

The result of a job execution is represented by a :py:class:`JobResult` object.

.. code:: python
    
    from ansys.scadeone.core.job import JobLauncher, Job, JobType

    s_one_install = "C:/Scade One"
    app = ScadeOne(install_dir=s_one_install)

    project = app.load_project(sproj_path)

    # Get all the jobs of a project or get a specific job from its name
    jobs = project.load_jobs()
    job = project.get_job("TestExecutionJob0")

    # Edit the job, save and execute it
    job.input_paths = ["assets/testEnumsModule.swant"]
    job.properties.test_harness = "testEnumsModule::harness_Operator2forEnums"
    job.properties.use_cycle_time = True
    job.cycle_time = 25  # .properties is not necessary
    
    job.save()
    result = job.run()
    if result.code == 0:
        print("Execution successful!")
    else:
        print(f"Execution failed. Error: {result.message})


Job parameters
==============

Every :py:class:`Job` is represented by the following parameters:

============ ============= =======================================================
Attribute    Type          Description
============ ============= =======================================================
version      str           Job version
kind         JobType       Job type (code generation, simulation, etc.)
properties   JobProperties Parameters specific to the job type
input_paths  list[str]     List of paths to be used as input for the job execution
============ ============= =======================================================

Parameters of :py:class:`JobProperties` depend on the :py:class:`Job` type (code generation, simulation, test execution or model check):

======================= ===== ======= ========== ======== =====
Attribute               Type  CodeGen Simulation TestExec Check
======================= ===== ======= ========== ======== =====
root_declarations       list  x       x          x        x
name                    str   x       x          x        x
custom_arguments        str   x       x          x        x
expansion               enum* x
expansion_exp           str   x
expansion_no_exp        str   x
name_length             int   x
keep_assume             str   x
globals_prefix          str   x
use_macros              bool  x
static_locals           bool  x
max_function_parameters int   x
probes                  bool  x
file_scenario           str           x
simulation_input_type   str           x
test_harness            str           x          x
test_result_file        str                      x
use_cycle_time          bool          x
cycle_time              int           x
======================= ===== ======= ========== ======== =====

\*`Expansion` is an attribute that can only have specific values: see :py:class:`ExpansionMode`


Classes
=======

Main classes related to project jobs are listed below. For more details, see the class documentation.

.. currentmodule:: ansys.scadeone.core.job 

.. autosummary::
    :signatures: none

   Job
   JobType
   CodeGenerationJob
   SimulationJob
   TestExecutionJob
   ModelCheckJob
   JobResult
   ExpansionMode

Class details
-------------

This section lists all the classes related to project jobs with their full documentation.

.. automodule:: ansys.scadeone.core.job
    :member-order: bysource


