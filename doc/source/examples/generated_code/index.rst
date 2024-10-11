.. _GeneratedCode Example:

.. currentmodule:: ansys.scadeone.core.svc.generated_code

==============
Generated Code
==============

In this section, we present how we can access generated code data from model elements using a Code Generation job (see :ref:`Generated Code`).

We use the same ``QuadFlightControl`` example. To setup the example see 
:ref:`QuadFlightControl python setup`.

In addition, we import the generated code related package:

.. code-block:: python

    from ansys.scadeone.core.svc.generated_code import GeneratedCode

For that example, we rely on the code generation job named `CodeGen`.
We first create a :py:class:`GeneratedCode` object for this job:
    
.. literalinclude:: quad_flight_control.py
    :lines: 17-22

Before being able to manipulate the generated code data, we need to have the *CodeGen* job executed (this is done from
the Scade One IDE).

To check that the job has been executed, use the :py:attr:`GeneratedCode.is_code_generated` property. 

.. literalinclude:: quad_flight_control.py
    :lines: 24-26

Model operators
---------------

The list of operators as they are defined in the model can be retrieved using the :py:meth:`GeneratedCode.get_model_operators` method:

.. literalinclude:: quad_flight_control.py
    :lines: 28-30

A given operator can also be retrieved by its model pathname using 
the :py:meth:`GeneratedCode.get_model_operator` method.

The monomorphic instances of polymorphic operators can be retrieved using 
the :py:meth:`GeneratedCode.get_model_monomorphic_instance` 
and :py:meth:`GeneratedCode.get_model_monomorphic_instances` methods:

.. literalinclude:: quad_flight_control.py
    :lines: 32-34

Get generated code from model operators
---------------------------------------

The *ModelOperator* object gives access to the different associated generated functions (eg cycle function, init function)

For example, to get the cycle function of the root operator:

.. literalinclude:: quad_flight_control.py
    :lines: 36-41

To directly get the parameters of the cycle function:

.. literalinclude:: quad_flight_control.py
    :lines: 43-47	

To get the list of inputs and outputs with the name of the associated parameters in the cycle function:

.. literalinclude:: quad_flight_control.py
    :lines: 49-61	











