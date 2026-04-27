Test harness
============

.. currentmodule:: ansys.scadeone.core.swan


A test harness is a particular operator that can be declared only in a test module `(*.swant)` and with the following specificities:

- It has no declared I/Os.
- It has one implicit input `_current_cycle: uint64`; intended to contain the current cycle counter.
- It has one implicit output `_stop_condition: bool default=false`; when it's True, intended to indicate that the execution can be suspended or stopped.
- It cannot be instantiated.
- It must provide definitions for all sensors used in its cone of influence.

.. currentmodule:: ansys.scadeone.core.svc.swan_creator.module_creator

To include a test harness in a Test module, use the :py:meth:`TestModuleCreator.add_test_harness()` method.

.. currentmodule:: ansys.scadeone.core.swan

TestHarness class
-----------------

.. figure:: diagram.svg

   Diagram class diagram for Test harness

.. autoclass:: TestHarness
    :exclude-members: add_input, add_output, add_diagram