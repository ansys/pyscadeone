
.. currentmodule:: ansys.scadeone.core.svc.generated_code

==============
Generated code
==============

This section describes how to access generated code data from model elements using 
a Code Generation job (see :ref:`ref_generated_code`).

The same ``QuadFlightControl`` example is used. To setup the example see 
:ref:`QuadFlightControl python setup`.

The generated code related package is required:

.. code-block:: python

    from ansys.scadeone.core.svc.generated_code import GeneratedCode

The example uses the code generation job named `CodeGen` for which
a :py:class:`GeneratedCode` object is created:
    
.. literalinclude:: quad_flight_control.py
    :lines: 17-22

Before being able to manipulate the generated code data, it is necessary to check that 
the *CodeGen* job executed (this is done from the Scade One IDE).

To check that the job has been executed, use the :py:attr:`GeneratedCode.is_code_generated` property. 

.. literalinclude:: quad_flight_control.py
    :lines: 24-26

Model operators
---------------

The list of operators as they are defined in the model can be retrieved using the :py:meth:`GeneratedCode.get_model_operators` method:

.. literalinclude:: quad_flight_control.py
    :lines: 28-30

A given operator can also be retrieved by its model path using 
the :py:meth:`GeneratedCode.get_model_operator` method.

The monomorphic instances of polymorphic operators can be retrieved using 
the :py:meth:`GeneratedCode.get_model_monomorphic_instance` 
and :py:meth:`GeneratedCode.get_model_monomorphic_instances` methods:

.. literalinclude:: quad_flight_control.py
    :lines: 32-34

Get generated code from model operators
---------------------------------------

The *ModelOperator* object gives access to the different associated generated functions 
(for example the cycle function or the init function)

For example, to get the cycle function of the root operator:

.. literalinclude:: quad_flight_control.py
    :lines: 36-41

To directly get the parameters of the cycle function:

.. literalinclude:: quad_flight_control.py
    :lines: 43-47	

To get the list of inputs and outputs with the name of the associated parameters in the cycle function:

.. literalinclude:: quad_flight_control.py
    :lines: 49-61	











