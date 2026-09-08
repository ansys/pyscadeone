Sensor handling
===============

.. currentmodule:: ansys.scadeone.core.swan

Sensors can be defined within a Test module. There are three ways to define the value of a sensor:

- using a **_sensor** *sensor_name* block in a diagram,
- using a *sensor_name := expr* equation in a  **let** scope section,
- or providing a :py:class:`DataSource` with the sensor values. 

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.diagram_creator

To add a **_sensor** *sensor_name* block to a Test module, use the :py:meth:`DiagramCreator.add_set_sensor` method, 
and connect its input to the appropriate expression in the diagram.

.. currentmodule:: ansys.scadeone.core.swan

Sensors found in a data source are automatically connected to their corresponding sensors. 
There is no need to create explicit connections in the diagram.

To add an equation, one must create the equation and add it to a **let** scope section.


SetSensorEquation class
-----------------------
.. autoclass:: SetSensorEquation



SetSensorBlock class
--------------------
.. autoclass:: SetSensorBlock