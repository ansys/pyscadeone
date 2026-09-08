CGMapping
=========

.. currentmodule:: ansys.scadeone.core.svc.cgmapping.cgmapping

Entry point
-----------

The :py:class:`CGMapping` class provides the entry point to the Code Generator (CG) mapping information.
Use the :py:meth:`~CGMapping.from_file` method to create an instance
of :py:class:`CGMapping` from a CG mapping file (`cg_map.json`).

.. code:: python

    from ansys.scadeone.core.svc.cgmapping import CGMapping
    cg_mapping = CGMapping.from_file("path/to/cg_map.json")

Helpful methods
---------------

**Model queries**

- :py:meth:`~CGMapping.get_model_by_path` - Get model items by full path.
- :py:meth:`~CGMapping.get_model_by_name` - Get model items by name.
- :py:meth:`~CGMapping.get_all_operators` - Get all operators (including monomorphized ones).
- :py:meth:`~CGMapping.get_root_operators` - Get operators marked as root.
- :py:meth:`~CGMapping.get_all_constants` - Get all constants.
- :py:meth:`~CGMapping.get_all_sensors` - Get all sensors.
- :py:meth:`~CGMapping.get_all_types` - Get all type declarations.

**Code queries**

- :py:meth:`~CGMapping.get_code_by_name` - Get code items by name.
- :py:meth:`~CGMapping.get_all_code_containers` - Get all code containers.

**Mapping queries**

- :py:meth:`~ansys.scadeone.core.svc.cgmapping.model.ModelElement.get_generated_element` - Get the generated element associated to a model item.
- :py:meth:`~ansys.scadeone.core.svc.cgmapping.code.CodeElement.get_model_element` - Get the model element associated to a code item.

**Statistics**

- :py:meth:`~CGMapping.get_statistics` - Get some statistics on loaded mapping data.

API Documentation
-----------------

.. automodule:: ansys.scadeone.core.svc.cgmapping.cgmapping