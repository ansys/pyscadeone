Data source
===========

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.diagram_creator

A data source is a particular node used to produce flows from the content of a simulation data (`*.sd`).
The simulation data file is given by a key in the project :ref:`ref_resources`.
The data source exposes the signals in the data source as outputs.


To include a data source in a test harness, use the :py:meth:`DiagramCreator.add_data_source()` method.

.. currentmodule:: ansys.scadeone.core.swan

DataSource class
----------------
.. autoclass:: DataSource