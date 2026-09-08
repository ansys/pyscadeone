Model section items
===================

.. currentmodule:: ansys.scadeone.core.svc.cgmapping.model

ModelElement subclasses
-----------------------

Each model section item is represented by one of the following classes, which all inherit from :py:class:`ModelElement`,
thus provide the :py:meth:`~ModelElement.get_generated_element` method to access the associated generated C element. (see :doc:`code`)

**Type Definitions**

- :py:class:`ModelPredefinedType` - Predefined type
- :py:class:`ModelArray` - Array type definition
- :py:class:`ModelStruct` - Structure type definition
- :py:class:`ModelStructField` - Field within a structure
- :py:class:`ModelEnum` - Enumeration type definition
- :py:class:`ModelEnumValue` - Value within an enumeration
- :py:class:`ModelVariant` - Variant type definition
- :py:class:`ModelVariantConstructor` - Constructor within a variant
- :py:class:`ModelNamedType` - Named type (user-defined type reference)

**Operators and Instances**

- :py:class:`ModelOperator` - Operator declaration
- :py:class:`ModelMonoOperator` - Monomorphized operator
- :py:class:`ModelOperatorInstance` - Instance of an operator
- :py:class:`ModelLoopInstance` - Loop instance

**Variables and Parameters**

- :py:class:`ModelVariable` - Input/output variable
- :py:class:`ModelVariablesGroup` - Group of variables
- :py:class:`ModelMonoVariable` - Monomorphized variable
- :py:class:`ModelTypeParameter` - Type parameter for monomorphization
- :py:class:`ModelSizeParameter` - Size parameter for monomorphization

**Constants, Sensors, and Probes**

- :py:class:`ModelConstant` - Constant value
- :py:class:`ModelSensor` - Sensor element
- :py:class:`ModelProbe` - Probe element
- :py:class:`ModelProbesGroup` - Group of probes

Model groups
------------

Some model items can be returned as groups (:py:class:`ModelGroup`) of said items.
These items are:

- Flows :py:class:`ModelVariable`, found in :py:class:`ModelOperator` inputs and outputs, returned as :py:class:`ModelVariablesGroup`
- Probes :py:class:`ModelProbe`, found in :py:class:`ModelOperator`, :py:class:`ModelMonoOperator`, :py:class:`ModelLoopInstance` and :py:class:`ModelOperatorInstance`, returned as :py:class:`ModelProbesGroup`

These groups possess a common identifier: respectively name and path for variables and probes.
Both possess an attribute `projections` which is a list of all their respective items, represented
as projections.
A projection is a list of strings or integers which represent the location of the item in the group hierarchy.
Integers are used for positional (location in current level) and strings are used for labels
(element name or sub-group name).

Groups cannot use the method :py:meth:`~ModelElement.get_generated_element` (it will return None), they must use :py:meth:`~ModelGroup.get_generated_group_elements` instead.
However, each of a group's projections can use the method :py:meth:`~ModelElement.get_generated_element` normally.

======================= ==================================== ========================================
Group                   Flows                                Probes
======================= ==================================== ========================================
Found in attributes     inputs and outputs                   probes
From elements           :py:class:`ModelOperator`            :py:class:`ModelOperator`
                                                             :py:class:`ModelMonoOperator`
                                                             :py:class:`ModelLoopInstance`
                                                             :py:class:`ModelOperatorInstance`
Instead of              :py:class:`ModelVariable`            :py:class:`ModelProbe`
Group type              :py:class:`ModelVariablesGroup`      :py:class:`ModelProbesGroup`
Group attributes        name (str)                           path (str) and 
                                                             kind (:py:class:`ProbeKind`)
Group projections       :py:class:`ModelGroupProjection`     :py:class:`ModelGroupProjection`
======================= ==================================== ========================================

To get flattened flows and probes instead of groups, :py:meth:`ModelOperator.get_flat_inputs`,
:py:meth:`ModelOperator.get_flat_outputs` and :py:meth:`HasProbesMixin.get_flat_probes` can be used.

API Documentation
-----------------

.. automodule:: ansys.scadeone.core.svc.cgmapping.model
   :members:
   :no-inherited-members: