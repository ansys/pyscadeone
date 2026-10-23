Formal properties
=================

.. currentmodule:: ansys.scadeone.core.swan

Formal properties are used to specify the properties of an operator body. 
They are used to define the assumptions, guarantees, and assertions of the operator.

.. figure:: formal_props.svg
   :align: center

   Formal properties class diagram

Assume section
--------------

.. autoclass:: AssumeSection
    :exclude-members: to_str

Guarantee section
-----------------

.. autoclass:: GuaranteeSection
    :exclude-members: to_str

Assert section
--------------
.. autoclass:: AssertSection
    :exclude-members: to_str

Assertion class
---------------------

.. autoclass:: Assertion

