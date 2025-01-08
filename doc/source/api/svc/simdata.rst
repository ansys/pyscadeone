.. _ref_sim_data:

===============
Simulation data
===============

Simulation data files are used to represent sequences of values:

- they are the outputs of simulation jobs;
- they can be used in test harnesses, in *data source* and *oracle* blocks, to be used respectively as inputs and expected values.

This library allows to read and edit simulation data files. Look for *simulation data* in Scade One documentation.

Covered features
----------------

* Support of ``none`` values, meaning that the value is not defined at a given cycle:

  * Stimuli operator: a value must be defined at first cycle, for next steps the ``none`` type means that a previous value is held.
  * Simulator trace: a ``none`` value means that the variable clock is false.

* Support of all Swan types, imported types (stored as a byte array) and combinations of them (native support of Variants & Groups).

  * Data support: structure, table (when the table size is a static constant), enum, string.
  * Limitations: partial data is not supported. All values of a complex type must be given.

* The variables are organized as a tree of <scope>/<scope>/…/<variable>, each scope and variable has an optional Swan kind: sensors, inputs, outputs, probes, assume, guarantee and so on.
* Possibility to specify a *repetition* of a signal or part of it. 
* Possibility to open an existing file for modification: elements, types and values.

Design principles
-----------------

- A file of binary format does not allow a value conversion to or from string. 
- The values are stored as their binary representation in memory: no structured representation of composite values.
- The values sequences are compressed using the zlib data-compression library.
- The file size has no limit (more than 4 GB): use of 64 bits positions and C APIs for seek in file.
- The entire file content is not loaded in memory when opening: the data is read in file only on demand. 
- The file content is not entirely rewritten on disk when closing: incremental read and write operations. 

Performance
-----------

- Appending values to an element: no need to read all the values before appending and use of a write cache. 
- Updating element: no move of significant data in file.

Example using API simulation data
---------------------------------

.. code:: python

    import ansys.scadeone.core.svc.simdata as sd

    f = sd.create_file("mySimDataFile.sd") # creates a new simulation data file
    
    t_struct1 = sd.create_struct_type([("f1", sd.Bool), ("f2", sd.Int32)], "p1::tStruct1") # creates a new structure type
    e_struct1 = f.add_element("eStruct1", t_struct1) # adds an element to the file
    clock1 = False

    for i in range(10): # number of cycles
        clock1 = not clock1
        e_struct1.append_value([clock1, i + 14]) # adds values to the element

    f.close() # closes the file

Simulation data file preview command line
-----------------------------------------

The **pyscadeone** :ref:`ref_cli` is used, in combination with the *simdata* and *-show* arguments, to preview 
the content of a data file with .SD extension in a text editor, without opening the Scade One tool or Signal Editor.

.. code:: bash

    # View content of a .SD file as a text
    pyscadeone simdata --show some_file.sd > some_file.txt
    notepad some_file.txt # opens the file in notepad, or vi editor and so on


High-level API
--------------

.. automodule:: ansys.scadeone.core.svc.simdata.csd
    :member-order: bysource

Type definitions
----------------

Predefined swan types that shall be used for creation of
simple elements or user types definitions

=== =======
Id  Type       
=== =======
0   Char
3   Bool
4   Int8
5   Int16
6   Int32
7   Int64
8   UInt8
9   UInt32
10  UInt32
11  UInt64
12  Float32
13  Float64
=== =======

Using a predefined type (float 32 here) for new element and custom user type

.. code:: python
    
    import ansys.scadeone.core.svc.simdata as sd

    my_file = sd.create_file("mySimDataFile.sd")

    my_element1 = my_file.add_element("myElement", sd.Float32)

    my_array_type = sd.create_array_type(sd.Float32, [3, 4], "my2DArrayType")
    my_element2 = my_file.add_element("my2DArrayElement", my_array_type)

.. automodule:: ansys.scadeone.core.svc.simdata.defs