.. _ref_jobs:

Project jobs
============

Project jobs can be loaded, edited, and executed.
A job execution requires Scade One to be installed as it uses the JobLauncher executable from Scade One tools.

Every :py:class:`Job` is represented by the following parameters:

============ =============
Attribute    Type 
============ =============
version      str
kind         JobType
properties   JobProperties
input_paths  list[str]
============ =============

Parameters of :py:class:`JobProperties` depend on the :py:class:`Job` type (code generation, simulation or test execution):

======================= ===== ======= ========== ========
Attribute               Type  CodeGen Simulation TestExec     
======================= ===== ======= ========== ========
root_declarations       list  x       x          x
name                    str   x       x          x
custom_arguments        str   x       x          x
expansion               enum* x       
expansion_exp           str   x
expansion_no_exp        str   x 
short_circuit_operators bool  x 
name_length             int   x 
significance_length     int   x 
keep_assume             str   x 
globals_prefix          str   x 
use_macros              bool  x 
static_locals           bool  x 
file_scenario           str           x
simulation_input_type   str           x
test_harness            str           x          x
test_result_file        str                      x
use_cycle_time          bool          x
cycle_time              int           x
======================= ===== ======= ========== ========

\*`Expansion` is an attribute that can only have specific values: see :py:class:`ExpansionMode`


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

.. automodule:: ansys.scadeone.core.job
    :member-order: bysource