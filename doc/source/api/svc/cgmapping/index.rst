.. _ref_cgmapping:

======================
Code generator mapping
======================

.. currentmodule:: ansys.scadeone.core.svc.cgmapping

The code generator mapping API allows to explore and query the relationship
between Swan model elements and their generated C code counterparts.

This API can be used after executing a Code Generation job in Scade One.
It needs the generated JSON mapping data file named ``cg_map.json``.

The latter file contains three sections:

- **model**: Elements from the Swan language (operators, types, constants, sensors, etc.)
- **code**: Generated C code elements (functions, types, variables, etc.)
- **mapping**: Associations between model and code items with optional roles

Modules of interest
===================

.. toctree::
   :maxdepth: 2

   model
   code
   cgmapping

Getting started
===============

Loading mapping data
---------------------

The main entry point is the :py:class:`~cgmapping.CGMapping` class. You can load mapping data from
a JSON file or dictionary:

.. code:: python

   from ansys.scadeone.core.svc.cgmapping import CGMapping
   
   # Load from JSON file
   mapping = CGMapping.from_file("path/to/cg_map.json")

Basic information
-----------------

Once loaded, you can get basic information about the mapping:

.. code:: python

   # Get statistics about loaded data
   stats = mapping.get_statistics()
   print(f"Model items: {stats['model_items']}")
   print(f"Code items: {stats['code_items']}")
   print(f"Mappings: {stats['mappings']}")
   
   # Get format version
   print(f"Format version: {mapping.version}")

Querying model elements
=======================

Finding model elements
-----------------------

You can search for model elements using various methods:

.. code:: python

   # Find model elements by their path
   operators = mapping.get_model_by_path("MyPackage::MyOperator")
   
   # Find model elements by name
   items = mapping.get_model_by_name("MyOperator")

Specialized model queries
--------------------------

The API provides specialized methods for common model element types:

.. code:: python

   # Get all operators
   all_operators = mapping.get_all_operators()
   
   # Get only root operators
   root_operators = mapping.get_root_operators()
   
   # Get all constants
   constants = mapping.get_all_constants()
   
   # Get all sensors
   sensors = mapping.get_all_sensors()
   
   # Get all types
   types = mapping.get_all_types()

Working with operators
----------------------

.. code:: python

   operators = mapping.get_model_by_name("FlightController")
   for operator in operators:

       # Operator attributes
       print(f"Operator path: {operator.path}")
       print(f"Is root: {operator.root}")
       print(f"Is expanded: {operator.expanded}")
       for input in operator.inputs:
           print(f"  Input: {input.name}")
       
       # Specialized method access
       cycle_method = operator.get_cycle()
       init_method = operator.get_init()
       reset_method = operator.get_reset()
       
       # Access to operator metadata
       function_name = operator.get_function_name()
       header_file = operator.get_header_name()
       
       # Context and structure access
       context_type = operator.get_context_type()
       global_context = operator.get_global_context()
       input_struct = operator.get_input_struct_type()
       obs_struct = operator.get_obs_struct_type()


Using model elements
--------------------

.. currentmodule:: ansys.scadeone.core.svc.cgmapping.model

All model elements inherit from :py:class:`ModelElement`, which provides
the :py:meth:`~ModelElement.get_generated_element` method to access their generated code counterpart:

.. code:: python

   # Get all generated code elements for an operator
   code_items = operator.get_generated_element()
   print(f"Operator generates {len(code_items)} code elements")
   
   # Get specific code elements using specialized helpers
   cycle_fn = operator.get_cycle()
   if cycle_fn:
       print(f"Cycle method: {cycle_fn.name}")
   
   reset_fn = operator.get_reset()
   if reset_fn:
       print(f"Reset method: {reset_fn.name}")

Querying code elements
======================

.. currentmodule:: ansys.scadeone.core.svc.cgmapping.code

Finding code elements
---------------------

Similar to model elements, you can search for code elements:

.. code:: python

   # Find code elements by name
   functions = mapping.get_code_by_name("FlightController_cycle")
   
   # Get all code containers (files)
   containers = mapping.get_all_code_containers()
   for container in containers:
       print(f"Interface file: {container.interface_file}")
       if container.implementation_file:
           print(f"Implementation file: {container.implementation_file}")

.. note:: See :ref:`ref_code_container` for more details on code containers.

Working with code elements
--------------------------

Code elements represent various C constructs:

.. code:: python

   # Example with a C function
   functions = mapping.get_code_by_name("my_function")
   if functions:
       function = functions[0]
       print(f"Function name: {function.name}")
       print(f"Return type ID: {function.return_type}")
       print(f"Parameters: {len(function.parameters)}")
       
       for param in function.parameters:
           print(f"  - {param.name}: type {param.type}")

Using code elements
-------------------

All code elements inherit from :py:class:`CodeElement`, which provides
the :py:meth:`~CodeElement.get_model_element` method to access the associated model element that generated them:

.. code:: python

    # Get the model element that generated this code
    model_item = function.get_model_element()
   
    print(f"Generated from: {type(model_item).__name__}")
    if hasattr(model_item, 'path'):
        print(f"  Path: {model_item.path}")

Bidirectional mapping
=====================

Forward mapping (model → code)
-------------------------------

Get generated code from model elements:

.. code:: python

    code_items = model_element.get_generated_element()
    cycle_function = model_element.get_cycle()

Reverse mapping (code → model)
-------------------------------

Find which model element generated specific code:

.. code:: python

    model_item = code_element.get_model_element()

Use cases
=========

Complete working example
------------------------

For a comprehensive use case demonstrating the mapping API,
here is a complete working example:

.. literalinclude:: cg_mapping_demo.py
   :language: python
   :linenos:
   :lines: 30-