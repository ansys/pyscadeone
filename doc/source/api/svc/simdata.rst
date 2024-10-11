.. _sec_simdata:

===================
Simulation Data API
===================

*Simulation Data* format and APIs are intended to be used in the following scopes:  

- Signal Editor: UI for creating and updating a data file made of named and typed elements and associated sequences of values 
- Data Reader operator: set operator outputs with values read in data file
- Simulator: produce simulation trace 
- Trace Viewer: read simulation trace for plotting 
- Trace Converter: convert a simulation trace to a file in former .out format
- User scripting (python): read/write/update simulation data

Covered features
----------------

- Support of ``none`` values, meaning that the value is not defined at a given cycle: 
    - Stimuli operator: value must be defined at first cycle, then a none means that previous value is hold 
    - Simulator trace: none value means that variable clock is false
- Support of all Swan types, imported types (stored as byte array) and combinations of them (esp. native support of Variants & Groups) 
- Variables organized as a tree of <scope>/<scope>/…/<variable>, each scope and variable having an optional Swan kind: sensors, inputs, outputs, probes, assume, guarantee...
- Possibility to specify a *repetition* of the signal or part of it 
- Possibility to open an existing file for modification: elements, types and values 

Design / principles
-------------------

- Binary file format so no value conversion to/from string 
- Values are stored as their binary representation in memory: no structured representation of composite values 
- Values sequences are compressed using zlib 
- No limit on file size (more than 4GB): use of 64 bits positions & C APIs for seek in file
- Entire file content is not loaded in memory when opening: data is read in file only on demand 
- File content is not entirely rewritten on disk when closing: incremental read & write operations 

Performance
-----------

- Appending values to an element: no need to read all values before appending and use of a write cache 
- Updating element: no move of significant data on file 

Example using API simulation data
---------------------------------

.. code:: python

    import ansys.scadeone.core.svc.simdata as sd

    f = sd.create_file("mySimDataFile.sd") # creates a new simulation data file
    
    t_struct1 = sd.create_struct_type([("f1", sd.Bool), ("f2", sd.Int32)], "p1::tStruct1") # creates new structure type
    e_struct1 = f.add_element("eStruct1", t_struct1) # adds element to file
    clock1 = False

    for i in range(10): # number of cycles
        clock1 = not clock1
        e_struct1.append_value([clock1, i + 14]) # adds values to element

    f.close() # closes the file

High-level API
--------------

.. automodule:: ansys.scadeone.core.svc.simdata.csd
    :member-order: bysource

Type Definitions
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