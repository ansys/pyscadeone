.. _diagram_nav_ex:

Diagram Navigation
==================
In this section, we present how we can navigate in an operator diagram. We start giving the basic methods to move
through a diagram and we finish by a simple navigation between two objects using these methods.

We use the same ``QuadFlightControl`` example. To setup the example see 
:ref:`QuadFlightControl python setup`.

Then we get the operator:

.. literalinclude:: quad_flight_control.py
    :lines: 40-48

Diagram Block
-------------
The operator's diagram block can be accessed with the :py:attr:`ansys.scadeone.core.swan.Operator.diagrams` property.

.. literalinclude:: quad_flight_control.py
    :lines: 50


Once we have the **MotorControl** diagram block, we can get the list of diagram objects (blocks, wires, ...) and the
connections between them (sources or targets). The figure below presents those blocks for our example:

.. figure:: images/block_sources_targets.png

Diagram Objects
---------------
To get the source and target objects, we need to get the diagram objects using the
:py:attr:`ansys.scadeone.core.swan.Diagram.objects` property. We can filter by :py:class:`ansys.scadeone.core.swan.Block`
to get the blocks list.

.. literalinclude:: quad_flight_control.py
    :lines: 53


Sources and Targets
-------------------
Using the **MotorControl** diagram block, we can get the operator's sources using the
:py:attr:`ansys.scadeone.core.swan.DiagramObject.sources` property:

.. literalinclude:: quad_flight_control.py
    :lines: 55-61

We can also get the operator's targets using the
:py:attr:`ansys.scadeone.core.swan.DiagramObject.targets` property:

.. literalinclude:: quad_flight_control.py
    :lines: 63-64


Navigate from Input to Output
-----------------------------
We can navigate inside the **MotorControl** operator selecting a starting and an ending point.
We take **attitudeCmd** input as starting point and we navigate through the wires to get the blocks on the route
until we arrive at the ending point, **rotorCmd**.

.. figure:: images/input_output_navigation.png

First, we get the **attitudeCmd** input with its fields.

.. literalinclude:: quad_flight_control.py
    :lines: 105-114


Once we have the input, we can move to the next object diagram using
the :py:attr:`ansys.scadeone.core.swan.DiagramObject.targets` property.
For each object diagram target, we can move to the
next object, and so on until we arrive at the output. For each move, we can save the navigated object.

.. literalinclude:: quad_flight_control.py
    :lines: 117-130

Complete Example
________________

This is the complete script for the diagram navigation section, with print of results.

.. literalinclude:: quad_flight_control.py