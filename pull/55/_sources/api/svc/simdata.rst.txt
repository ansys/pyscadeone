.. _ref_sim_data:

===============
Simulation data
===============

.. currentmodule:: ansys.scadeone.core.svc.simdata

Simulation data files are used to represent sequences of values:

- they are the outputs of simulation jobs;
- they can be used in test harnesses:

  * in *data source* blocks, to feed the input flows of the operator instance to test
  * in *oracle* blocks, to store expected output values to compare with the actual values in model test execution

This library allows to read and edit simulation data files. Look for *simulation data* in the Scade One documentation.

Covered features
================

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

- The values are stored as their binary representation in memory: no structured representation of composite values.
- The values sequences are compressed using the zlib data-compression library.
- The file size has no limit (more than 4 GB): use of 64-bits positions and C APIs for seek in file.
- The entire file content is not loaded in memory when opening: the data is read in file only on demand. 
- The file content is not entirely rewritten on disk when closing: incremental read and write operations. 

Performance
-----------

- Appending values to an element: no need to read all the values before appending and use of a write cache. 
- Updating element: no move of significant data in file.

Examples
========

Simulation data file preview command line
-----------------------------------------

The **pyscadeone** :ref:`ref_cli` is used, in combination with the *simdata* and *-show* arguments, to preview 
the content of a data file with .SD extension in a text editor, without opening the Scade One tool or the Signal Editor.

.. code:: bash

    # View content of a .SD file as a text
    pyscadeone simdata --show some_file.sd > some_file.txt
    notepad some_file.txt # opens the file in notepad, or vi editor and so on

Create a structure type data
----------------------------

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

Create a variant type data
--------------------------

.. code:: python

    import ansys.scadeone.core.svc.simdata as sd

    f = sd.create_file("mySimDataFile.sd") # creates a new simulation data file
    
    variant_type2 = sd.create_variant_type([("speedLimitStart", sd.Int32), ("speedLimitEnd", None)], "MyModule::SpeedLimit") # creates a new variant type
    variant_type1 = sd.create_variant_type([("tsBool", sd.Bool), ("tsNone", None), ("tsSome", variant_type2)], "MyModule::Variant") # creates a new variant type with an inserted variant subtype
    variant_element = f.add_element("inputVariant", variant_type1) # adds an element to the file

    variant_element.append_values_sequence([("tsNone")]) # fills with values                  
    variant_element.append_values_sequence([("tsBool", True)])
    variant_element.append_values_sequence([("tsSome", ("speedLimitStart", 147))])
    variant_element.append_values_sequence([("tsSome", ("speedLimitEnd"))])
    variant_element.append_values_sequence([("tsNone")])

    f.close() # closes the file


Create a group type data
------------------------  

A group is a composite type that contains child elements. Each child element can be of any type, including another group.
The Simdata representation of a group is a container used to organize related elements together. The :py:class:`Element`
representing the group has the name of the group itself, but does not hold values; its child elements do.

The group representation is flattened: child elements are represented as individual elements in the simulation data file.
Child elements are identified by their path in the group hierarchy, using positions and names.

Suppose one defines a group type in Swan as follows: `group MyGroup = (int32, bool, b:((x:float32, y:float32), int32))` 
in the module interface `MyModule`. The code to create a simulation data file with this group type is:

.. code:: python

    import ansys.scadeone.core.svc.simdata as sd

    f = sd.create_file("mySimDataFile.sd") # creates a new simulation data file
    group_element = f.add_element("inputGroup", group_expr="MyModule::MyGroup")
    child_1 = group_element.add_child_element(".(.1)", sd.Int32, sd.ElementKind.GROUP_ITEM)
    child_2 = group_element.add_child_element(".(.2)", sd.Bool, sd.ElementKind.GROUP_ITEM)
    child_b1_b_1_x = group_element.add_child_element(
        ".(.b.1.x)", sd.Float32, sd.ElementKind.GROUP_ITEM
    )
    child_b1_b_1_y = group_element.add_child_element(
        ".(.b.1.y)", sd.Float32, sd.ElementKind.GROUP_ITEM
    )
    child_b1_b_2 = group_element.add_child_element(
        ".(.b.2)", sd.Int32, sd.ElementKind.GROUP_ITEM
    )

    child_1.append_values_sequence([1, 1, 1, 2, 3, 4])
    child_b1_b_1_x.append_values_sequence([0.1, 0.1, 0.1, 0.2, 2.3, 2.4])
    child_b1_b_1_y.append_values_sequence([2.5, 2.5, 2.5, 2.6, 2.7, 2.8])
    child_b1_b_2.append_values_sequence([10, 11, 12, 12, 12, 12])
    child_2.append_values_sequence([False, True, False, True, False, True])

    f.close()

The content of the file can be visualized:

.. code:: shell

    $ pyscadeone simdata --show mySimDataFile.sd
    *** Elements:
    inputGroup: 
        GROUP_ITEM .(.1): int32: 1 | 1 | 1 | 2 | 3 | 4 |
        GROUP_ITEM .(.2): bool: false | true | false | true | false | true |
        GROUP_ITEM .(.b.1.x): float32: 0.1 | 0.1 | 0.1 | 0.2 | 2.3 | 2.4 |
        GROUP_ITEM .(.b.1.y): float32: 2.5 | 2.5 | 2.5 | 2.6 | 2.7 | 2.8 |
        GROUP_ITEM .(.b.2): int32: 10 | 11 | 12 | 12 | 12 | 12 |

In the Scade One Signal Editor, the group is represented as:

.. image:: simdata_group.png
   :alt: Signal Editor view of a group type
   :align: center
   :width: 60%

High-level API
==============


High-level functions
--------------------

The following functions are used to create or open a simulation data file, 
and to create user types definitions for elements, which can be then be filled with values
from Python values.

.. autofunction:: open_file
.. autofunction:: create_file
.. autofunction:: edit_file
.. autofunction:: create_array_type
.. autofunction:: create_struct_type
.. autofunction:: create_enum_type
.. autofunction:: create_variant_type
.. autofunction:: create_imported_type

High-level classes
------------------

Following classes are used to manipulate simulation data files and their content:

- :py:class:`File` is returned by :py:func:`open_file`, :py:func:`create_file` and :py:func:`edit_file`.

- :py:class:`Element` is created by :py:meth:`File.add_element` or :py:meth:`Element.add_child_element`.

.. autoclass:: File

.. autoclass:: Element


Type definitions
================ 

Simulation values have types, defined in Swan language. Types can be predefined (native) or user-defined.
In the latter case, the type must be created before creating an element of this type.

Values are passed to the API as Python values, and converted to the proper binary representation of the Swan type.
Scalar types are mapped to Python built-in types, composite types are mapped to Python lists or tuples. 
For arrays one can use :py:func:`numpy.array` function.

Predefined types
----------------

Predefined swan types that shall be used for creation of
simple elements or user types definitions

=========  =======
Swan type  SD Type       
=========  =======
char       Char
bool       Bool
int8       Int8
int16      Int16
int32      Int32
int64      Int64
uint8      UInt8
uint16     UInt16
uint32     UInt32
uint64     UInt64
float32    Float32
float64    Float64
=========  =======


Example of using a predefined type (float 32 here) for new element and a custom user type:

.. code:: python
    
    import ansys.scadeone.core.svc.simdata as sd

    my_file = sd.create_file("mySimDataFile.sd")
    # Predefined type
    my_element1 = my_file.add_element("myElement", sd.Float32)
    # User defined type: 2D array of float32
    my_array_type = sd.create_array_type(sd.Float32, [3, 4], "my2DArrayType")
    my_element2 = my_file.add_element("my2DArrayElement", my_array_type)

Type-related classes
--------------------

.. automodule:: ansys.scadeone.core.svc.simdata.defs
    :exclude-members: ElementBase, FileBase