.. _ref_test_module_ex:

Test module
===========
This section presents how to create a Test module and add it into the Swan project using the Python API. In the example below, the project includes two modules: a module body and a Test module.

.. note:: 
    Project dependencies are not supported yet. You should add the dependencies manually.
    
.. currentmodule:: ansys.scadeone.core


Create a Test module
--------------------
Using the :py:class:`ScadeOne` class, create a new project:

.. literalinclude:: test_module.py
    :start-at: from ansys.scadeone.core
    :end-at: project = 

Once the project is created, add a module body:

.. literalinclude:: test_module.py
    :lines: 43

Update the module body by adding a textual operator definition:

.. literalinclude:: test_module.py
    :lines: 34-46

After creating the project, also add a Test module:

.. literalinclude:: test_module.py
    :lines: 48-49


Once the Test module is created, add a set sensor, an operator under test, a data source, an oracle and connections between blocks,
as shown in the following diagram:

.. figure:: images/test_module.png

The corresponding code is:

.. literalinclude:: test_module.py
    :lines: 51-80

Finally, save the project, and look at the generated code:

.. literalinclude:: test_module.py
    :lines: 83-88
    
Complete example
----------------

This is the complete script presenting a Scade One model creation.

.. literalinclude:: test_module.py
    :lines: 23-88
