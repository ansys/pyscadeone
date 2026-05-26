State machines
==============

.. currentmodule:: ansys.scadeone.core.swan

The Swan language has the notion of a state machine, represented by the :py:class:`StateMachine` class. A state machine is composed of:

- states, represented by the :py:class:`State` class;
- transitions between states, represented by the :py:class:`Transition` class;
- forks, represented by the :py:class:`Fork` class, which are used to split transitions into several branches.


The figure :numref:`fig_states_and_transitions` shows the classes hierarchy and the relationships between these classes.

.. figure:: states_and_transitions.svg
    :name: fig_states_and_transitions

    States and transition declarations

.. note::

    The Swan language has two syntaxes for defining transitions:

    * Inline transitions: defined directly within the state definition. This syntax is used to defined an automaton within a **let** section.
    * Separate transition declarations: defined outside the state, referencing the state by its ID. This syntax is used to define a state machine within 
      a diagram, using a :py:class:`StateMachineBlock` within a :ref:`ref_diagram`.

The two notations are abstracted, and the :py:class:`Transition` class represents both notations. The :py:attr:`Transition.is_transition_decl` property
 indicates whether the transition is a separate declaration (`is_transition_decl=True`) or an inline transition.

In addition a transition can be:

- between two states, which a direct transition; 
- a part of a transition starting from a state and going to fork, which can split into several branches. 

The :py:class:`Transition` class represents either a direct state-to-state transition or any part when there are forks.


State machine
-------------

.. autoclass:: StateMachine


States
------

A state may have a body, as a scope and may have transitions as :py:class:`Transition` objects. In that case,
transitions belongs to the strong or weak lists.

.. autoclass:: State


Transitions
-----------

A transition gathers the following information:

- its priority, 
- whether it is a strong or weak transition;
- a guard condition, represented by a :py:class:`common.Expression` object;
- an action, represented by a :py:class:`scopes.Scope` object;
- its target, which can be either a :py:class:`State` or a :py:class:`Fork` object.
- if target is a state, whether it is a **resume** or **restart** transition (see :py:attr:`Transition.is_resume`).

The priority and the kind of transition (strong or weak) are defined for the whole transition, or for the start branch in case of a fork.


.. autoclass:: Transition 

Reference to states
^^^^^^^^^^^^^^^^^^^

Transitions reference their source and target states using :py:class:`StateRef` objects as internal information to defined start and end states.
The actual state can be accessed using the :py:attr:`Transition.head` and :py:attr:`Transition.tail` properties, which resolve the references.

.. autoclass:: StateRef



Forks
-----

Forks are transitions that split into several branches. Each branch is represented by a :py:class:`Transition` object,
and the fork itself is represented by a :py:class:`Fork` object.

.. autoclass:: Fork

