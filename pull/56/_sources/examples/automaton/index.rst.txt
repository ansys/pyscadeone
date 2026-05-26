.. _ref_automaton_example:


Automaton navigation
====================

.. currentmodule:: ansys.scadeone.core.swan

This section presents navigation in a state machine, which means how to find states, transitions, forks,
and how to explore the state machine structure.

Given a Swan project with the operator `point` declared with the following interface:

.. code::

    node point (u: bool;
                d: bool;
                r: bool;
                l: bool;
                unlock: bool;)
      returns (x: int32 last = 0;
               y: int32 last = 0;)

and with the behavior defined by the state machine:

.. figure:: statemachine.png
   :align: center


The following code gets the automaton:

.. literalinclude:: statemachine.py
    :start-after: # Load project
    :end-at: position_automaton = 


Get the initial state
---------------------

The initial state of the state machine can be accessed using the :py:attr:`StateMachine.initial_state` property:
and is the **Stop** state in this example.

.. literalinclude:: statemachine.py
    :start-after: # Get initial Stop state
    :end-at: stop_state =


Get target states from a specific state
---------------------------------------

The following code gets all direct target states reachable from the **Stop** state:

.. literalinclude:: statemachine.py
    :start-after: # Get target states from Stop state
    :end-at: assert target_ids


Explore state transitions
-------------------------

Out-going transitions of the **Stop** state are explored, going through forks if any, 
and a `dot graph <https://graphviz.org/docs/layouts/dot/>`_ is generated.

.. literalinclude:: statemachine.py
    :start-after: # Explore all transitions from Stop state
    :end-at:     d.extend(fork.transitions)

The generated graph is:

.. code:: 

    digraph G {
        Stop [label="Stop[#1]"]
        Up [label="Up[#3]"]
        Down [label="Down[#5]"]
        Left [label="Left[#7]"]
        Right [label="Right[#9]"]
        Center [label="Center[#11]"]
        Stop -> fork  [label="unlock\n<strong>"]
        Stop -> Center  [label="c\n<strong>"]
        fork -> Up  [label="u\n<restart>"]
        fork -> Down  [label="d\n<restart>"]
        fork -> Left  [label="l\n<restart>"]
        fork -> Right  [label="r\n<restart>"]
    }

This code can be visualized using any online graphviz viewer. The result is:

.. image:: statemachine_dot.png
   :align: center
   :alt: State machine graph

Get a specific state by its name
--------------------------------

The following code gets a specific state by its name:

.. literalinclude:: statemachine.py
    :start-after: # Get a specific state by its name
    :end-at: assert str(down_state.id) == "Down"

Accessing transition details
----------------------------

The following code shows how to access transition details such as its source (tail),
destination (head), and guard condition.

.. literalinclude:: statemachine.py
    :start-after: # Transition access


Complete example
-----------------

.. literalinclude:: statemachine.py
