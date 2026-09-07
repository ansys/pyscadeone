.. _ref_rules_example:

.. currentmodule:: ansys.scadeone.rulechecker.core.svc.metrics_rules.rules

Rules checker
=============

This section provides an example of how to define a rule using the base class :py:class:`Rule`. The example rule checks
if the operators' pathname exceeds a certain threshold in a Scade One project.

.. literalinclude:: operator_name_length.py
    :start-after: # SOFTWARE.
