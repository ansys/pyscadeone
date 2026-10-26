Oracle
======

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.diagram_creator

An oracle is a particular node used by the test environment to compare flows to expected values in a simulation data file (`*.sd`).
The oracle uses a key to reference the simulation data file in the project :ref:`ref_resources`.
Signals defined in the simulation data file are used as inputs of the oracle.


To include an oracle in a test harness, use the :py:meth:`DiagramCreator.add_oracle()` method.

Oracle class
------------
.. autoclass:: ansys.scadeone.core.swan.Oracle