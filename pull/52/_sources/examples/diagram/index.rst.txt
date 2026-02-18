.. _diagram_nav_ex:

Diagram navigation
==================

This section presents navigation in an operator diagram, which means how to find the sources of an diagram block
(the blocks that are connected to its inputs) and the targets (the blocks that are connected to its outputs).

The section starts giving the basic methods to move through a diagram and finishes by a simple 
navigation between two objects using these methods.

The ``QuadFlightControl`` example is used. To setup the example see 
:ref:`ref_QuadFlightControl_python_setup`.

The operator is first retrieved from the module:

.. literalinclude:: quad_flight_control.py
    :start-after: Step 1
    :end-before: Step 2

Diagram block
-------------

The operator's diagram block can be accessed with the :py:attr:`ansys.scadeone.core.swan.OperatorDefinition.diagrams` property.

.. literalinclude:: quad_flight_control.py
    :start-after: Step 2
    :end-at: diag =


From the **MotorControl** diagram block, one can get the list of diagram objects (blocks, wires, etc.) and the
connections between them (sources or targets). The figure below presents those blocks for the example:

.. figure:: images/block_sources_targets.png

Diagram objects
---------------
To get the source and target objects, one need to get the diagram objects using the
:py:attr:`ansys.scadeone.core.swan.Diagram.objects` property. One can filter by :py:class:`ansys.scadeone.core.swan.Block`
to get the blocks list.

.. literalinclude:: quad_flight_control.py
    :start-after: Step 3
    :end-at: blocks = list


Sources and targets
-------------------
Using the **MotorControl** diagram block, one can get the operator's sources using the
:py:attr:`ansys.scadeone.core.swan.DiagramObject.sources` property:

.. literalinclude:: quad_flight_control.py
    :start-after: Step 4
    :end-at: sources = 

One can also get the operator's targets using the
:py:attr:`ansys.scadeone.core.swan.DiagramObject.targets` property:

.. literalinclude:: quad_flight_control.py
    :start-after: Step 5
    :end-at: targets =


Navigate from Input to Output
-----------------------------
One can navigate inside the **MotorControl** operator selecting a starting and an ending point.
One takes **attitudeCmd** input as starting point and one navigates through the wires to get the blocks on the route
until one arrives at the ending point, **rotorCmd**.

.. figure:: images/input_output_navigation.png

First, the **MotoControl** operator is selected, then its **$Control** sub-diagram is extracted.

.. literalinclude:: quad_flight_control.py
    :start-at: # Get the 'MotorControl' operator
    :end-at: control_diag =

Then, one gets the **attitudeCmd** input with its fields, that is to say, expression
blocks using **attitudeCmd** are selected as starting blocks.

.. literalinclude:: quad_flight_control.py
    :start-at: def input_filter
    :end-at: attitude_cmd_fields =


Once one has the inputs, one can move to the next object diagram using
the :py:attr:`ansys.scadeone.core.swan.DiagramObject.targets` property.
For each object diagram target, one can move to the
next object, and so on until one arrives at the output. For each move, one can save the navigated object.

.. literalinclude:: quad_flight_control.py
    :start-at: def contains_output
    :end-at: attitude_cmd_fields =

Complete example
----------------

This is the complete script for the diagram navigation section, with print of results.

.. literalinclude:: quad_flight_control.py