# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# cSpell:ignore prio
# pylint: disable=too-many-arguments

from abc import ABC
from typing import List, Optional, Union, Set, cast
from collections import deque
from collections.abc import Generator
from functools import cache

from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes
from ansys.scadeone.core.swan.pragmas import CGPragma, CGPragmaKind

from .expressions import Literal, Pattern


class LHSItem(common.SwanItem):  # numpydoc ignore=PR01
    """Defines an item on the left-hand side of an equation, an ID, or underscore '_'.

    Parameters
    ----------
    id : Identifier (optional)
        Identifier or None for underscore value.
    """

    def __init__(self, id: Optional[common.Identifier] = None) -> None:
        super().__init__()
        self._id = id

    @property
    def id(self) -> Optional[common.Identifier]:
        """Returns id value or None."""
        return self._id

    @property
    def is_underscore(self) -> bool:
        """True when LHSItem is '_'."""
        return self._id is None


class EquationLHS(common.SwanItem):  # numpydoc ignore=PR01
    """Equation left-hand side part:

    *lhs* ::= ( ) | *lhs_item* {{ , *lhs_item* }} [[ , .. ]]

    """

    def __init__(self, lhs_items: List[LHSItem], is_partial_lhs: bool = False) -> None:
        super().__init__()
        self._lhs_items = lhs_items
        self._is_partial_lhs = is_partial_lhs

    @property
    def is_partial_lhs(self) -> bool:
        """True when lhs list is partial (syntax: final '..' not in the list."""
        return self._is_partial_lhs

    @property
    def lhs_items(self) -> List[LHSItem]:
        """Return left-hand side list."""
        return self._lhs_items


class ExprEquation(common.Equation):  # numpydoc ignore=PR01
    """Flows definition using an expression:

    *equation* ::= *lhs* [luid] = *expr*"""

    def __init__(
        self,
        lhs: EquationLHS,
        expr: common.Expression,
        luid: Optional[common.Luid] = None,
    ) -> None:
        super().__init__()
        self._lhs = lhs
        self._expr = expr
        self._luid = luid
        common.SwanItem.set_owner(self, expr)

    @property
    def lhs(self) -> EquationLHS:
        """Left-hand side of the equation."""
        return self._lhs

    @property
    def expr(self) -> common.Expression:
        """Equation expression."""
        return self._expr

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Equation LUID."""
        return self._luid


# Definition by cases: state machines and activate if/when
# ========================================================
class DefByCase(common.Equation, ABC):  # numpydoc ignore=PR01
    """Base class for state machine and active if/when equations."""

    def __init__(
        self,
        lhs: Optional[EquationLHS] = None,
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
    ) -> None:
        common.Equation.__init__(self)
        self._lhs = lhs
        self._lunum = lunum
        self._luid = luid

    @property
    def lhs(self) -> Union[EquationLHS, None]:
        """Left-hand side of the equation, may be None."""
        return self._lhs

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Return luid or None if no luid."""
        return self._luid

    @property
    def lunum(self) -> Union[common.Lunum, None]:
        """Return lunum or None if no lunum."""
        return self._lunum

    @property
    def pragmas(self) -> List[common.Pragma]:
        """Pragmas associated to this Def by case."""
        if isinstance(self.owner, common.HasPragma):
            return self.owner.pragmas
        return []


# State Machines
# ============================================================


class StateRef(common.SwanItem):
    """Reference to a state in a state machine.

    This class is used to reference a state in a state machine, either by its identifier or its lunum.
    It also includes a flag to indicate whether the state should be resumed or restarted.

    Parameters
    ----------
    id : Optional[common.Identifier]
        The identifier of the state. Default is None.
    lunum : Optional[common.Lunum]
        The lunum of the state. Default is None.

    Raises
    ------
    ScadeOneException
        If both `id` and `lunum` are None, or if both are provided.

    """

    def __init__(
        self,
        id: Optional[common.Identifier] = None,
        lunum: Optional[common.Lunum] = None,
    ) -> None:
        super().__init__()
        if id is None and lunum is None:
            raise ScadeOneException("StateRef must have either an id or a lunum.")
        if id is not None and lunum is not None:
            raise ScadeOneException("StateRef cannot have both an id and a lunum.")
        self._id = id
        self._lunum = lunum

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, StateRef):
            return False
        return self.id == getattr(value, "id", None) and self.lunum == getattr(value, "lunum", None)

    def __hash__(self) -> int:
        return hash((self.id.value if self.id else None, self.lunum.value if self.lunum else None))

    @property
    def id(self) -> Union[common.Identifier, None]:
        """State identifier, or None if lunum is used."""
        return self._id

    @property
    def lunum(self) -> Union[common.Lunum, None]:
        """State lunum, or None if identifier is used."""
        return self._lunum


class StateMachineItem(common.HasPragma):
    """Base class for state machine items, states and transitions.

    Parameters
    ----------
    pragmas : Optional[List[common.Pragma]], optional
        List of pragmas associated with the item, None if not set, by default None.
    """

    def __init__(self, pragmas: Optional[List[common.Pragma]] = None) -> None:
        super().__init__(pragmas)


class Transition(StateMachineItem):  # numpydoc ignore=PR01
    """Transition definition between states or forks.

    A transition can be between two states, or from a state to a fork,
    or from a fork to a state. The Transition class represents all these cases,
    including the case with a guard or not, a source state or not (for transition declarations),
    a priority or not, and a resume or restart type.


    Parameters
    ----------
    priority : Optional[Literal]
        Transition priority, None if not set.
    is_strong : bool
        True if the transition is strong, False if weak.
    guard : Optional[common.Expression]
        Transition guard, None if not set.
    action : Optional[scopes.Scope]
        Transition action, None if not set.
    target : Union[StateRef, Fork]
        Transition target, either a StateRef or a Fork.
    source : Optional[StateRef], optional
        Transition source, None if not set (for transition declarations), by default None.
    is_resume : bool, optional
        True if the transition is a resume transition, False if restart, by default False.
        Only applies to transitions to a state.
    pragmas : Optional[List[common.Pragma]], optional
        List of pragmas associated with the transition, None if not set. Apply to the transition itself,
        either a state-to-state or state-to-fork transition, by default None.
    """

    def __init__(
        self,
        priority: Optional[Literal],
        is_strong: bool,
        guard: Optional[common.Expression],
        action: Optional[scopes.Scope],
        target: Union[StateRef, "Fork"],
        source: Optional[StateRef] = None,
        is_resume: bool = False,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(pragmas)
        self._priority = priority
        self._guard = guard
        self._action = action
        self._target = target
        self._source = source
        self._is_strong = is_strong
        self._is_resume = is_resume
        # ownership
        if guard:
            common.SwanItem.set_owner(self, guard)
        if action:
            common.SwanItem.set_owner(self, action)
        if source:
            common.SwanItem.set_owner(self, source)
        common.SwanItem.set_owner(self, target)

    @staticmethod
    def sort_key(transition: "Transition") -> Union[int, float]:
        """Key function to sort transitions by priority, with None as lowest priority.
        This key can be used in sort() or sorted() functions."""
        try:
            return int(transition.priority.value)  # type: ignore
        except (ValueError, TypeError):
            return float("inf")

    @property
    def is_transition_decl(self) -> bool:
        """True when the transition is a source (whole state-to-state transition, or state-to-fork transition)."""
        return self._source is not None

    @property
    def guard(self) -> Union[common.Expression, None]:
        """Transition guard or None. Apply to transition start, or to *else* branch of a fork."""
        return self._guard

    @property
    def is_guarded(self) -> bool:
        "Check whether the transition has a guard."
        return self.guard is not None

    @property
    def action(self) -> Union[scopes.Scope, None]:
        """Transition action or None."""
        return self._action

    @property
    def priority(self) -> Union[Literal, None]:
        """Transition priority or None."""
        return self._priority

    @property
    def is_strong(self) -> bool:
        """True when the transition is strong, False when weak."""
        return self._is_strong

    @property
    def source(self) -> Union[StateRef, None]:
        """Transition source, either a StateRef (transition declaration), or None.
        Consider using :py:attr:`Transition.tail` property to get the actual source."""
        return self._source

    @property
    def target(self) -> Union[StateRef, "Fork"]:
        """Transition target, either a StateRef, or a Fork.
        Consider using :py:attr:`Transition.head` property to get the actual target."""
        return self._target

    @property
    def is_resume(self) -> bool:
        """True when the transition is a **resume** transition, False when **restart**."""
        return self._is_resume

    @property
    def tail(self) -> Union["State", "Fork"]:
        """Transition source, either a State or a Fork."""
        match self.owner:
            case StateMachine() as sm:
                if self.source is None:
                    raise ScadeOneException("Transition source is None, cannot resolve tail state.")
                if source := sm.get_state(self.source):
                    return source
                raise ScadeOneException("Transition source state not found.")
            case State() as state:
                return state
            case Fork() as fork:
                return fork
            case _:
                raise ScadeOneException("Transition source is neither a State nor a Fork.")

    @property
    def head(self) -> Union["State", "Fork"]:
        """Transition target, either a State or a Fork.

        Raises
        ------
        ScadeOneException
            If the target is a StateRef and the actual State cannot be found.
        """
        if isinstance(self.target, Fork):
            return self.target
        automaton = self.owner
        while automaton and not isinstance(automaton, StateMachine):
            automaton = cast(common.SwanItem, automaton).owner
        if not automaton or not isinstance(automaton, StateMachine):
            raise ScadeOneException("Transition target cannot be resolved, no parent StateMachine.")
        target = automaton.get_state(self.target)
        if not target:
            raise ScadeOneException(f"Transition target state not found: {self.target}.")
        return target


class Fork(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for fork-related classes.
    Transitions are ordered by priority, with the first transition having the highest priority.

    If the latest transition has None guard, it is the *else* branch.
    """

    def __init__(self, transitions: List[Transition]) -> None:
        super().__init__()
        self._transitions = transitions
        common.SwanItem.set_owner(self, transitions)

    @property
    def transitions(self) -> List[Transition]:
        """List of transitions, sorted by priority.

        .. note::

           A new list is returned, modifying it does not change the state.
           Use *self._transitions* to modify the internal list.
        """
        return sorted(self._transitions, key=Transition.sort_key)

    @property
    def from_transition(self) -> "Transition":
        """Return the transition owning this fork."""
        match self.owner:
            case Transition() as transition:
                return transition
            case _:
                raise ScadeOneException("Fork owner is not a Transition.")


class State(StateMachineItem):  # numpydoc ignore=PR01
    """State definition.

    .. note::

       Syntactically, state transitions can be defined either in the state declaration, or in the automaton as
       separate items. Transitions defined in the state declaration are stored within the state, using the
       :py:attr:`State.in_state_strong_transition_decls` and :py:attr:`State.in_state_weak_transition_decls` properties.
       These properties are used to preserve the original Swan description.

    Consider using instead the :py:attr:`State.strong_transitions` and :py:attr:`State.weak_transitions` properties.
    They return the list of all strong and weak transitions, respectively. They combine the transitions defined
    in the state declaration, and the transitions defined in the automaton with this state as source.

    Parameters
    ----------

    id : Optional[common.Identifier]
        State identifier, None if not set.
    lunum : Optional[common.Lunum]
        State lunum, None if not set.
    in_state_strong_transition_decls : Optional[List[Transition]]
        List of strong transitions, None if not set. These are the transitions found in the state declaration.
        They are kept to preserve the original Swan description.
    body : Optional[scopes.Scope]
        Body of the state as a Scope, None if not set. Note that syntactically, the body is a list of :py:class:`Section`.
    in_state_weak_transition_decls : Optional[List[Transition]]
        List of weak transitions, None if not set. These are the transitions that are found in the state declaration.
        They are kept to preserve the original Swan description.
    is_initial : bool
        True if the state is the initial state.
    """

    def __init__(
        self,
        id: Optional[common.Identifier] = None,
        lunum: Optional[common.Lunum] = None,
        in_state_strong_transition_decls: Optional[List[Transition]] = None,
        body: Optional[scopes.Scope] = None,
        in_state_weak_transition_decls: Optional[List[Transition]] = None,
        is_initial: bool = False,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(pragmas)
        self._id = id
        self._lunum = lunum
        self._strong_transitions = (
            in_state_strong_transition_decls if in_state_strong_transition_decls else []
        )
        self._body = body if body else scopes.Scope()
        self._weak_transitions = (
            in_state_weak_transition_decls if in_state_weak_transition_decls else []
        )
        self._is_initial = is_initial
        common.SwanItem.set_owner(self, self._strong_transitions)
        common.SwanItem.set_owner(self, self._weak_transitions)
        common.SwanItem.set_owner(self, self._body)

    @property
    def id(self) -> Union[common.Identifier, None]:
        """State ID."""
        return self._id

    @property
    def lunum(self) -> Union[common.Lunum, None]:
        return self._lunum

    @property
    def in_state_strong_transition_decls(self) -> List[Transition]:
        """List of strong transitions defined **in** the state declaration.

        Consider using :py:attr:`State.strong_transitions` property to get the list of all strong transitions
        (defined in the state and/or defined in the automaton with this state as source)."""
        return self._strong_transitions

    @property
    def in_state_weak_transition_decls(self) -> List[Transition]:
        """List of weak transitions defined **in** the state declaration.

        Consider using :py:attr:`State.weak_transitions` property to get the list of all weak transitions
        (defined in the state and/or defined in the automaton with this state as target)."""
        return self._weak_transitions

    def _get_transitions(self, is_strong: bool) -> Generator[Transition, None, None]:
        """Return the list of transitions, strong or weak from the containing automaton."""
        for transition in cast(StateMachine, self.owner).transition_decls:
            if transition.is_strong != is_strong:
                continue
            if not transition.source:
                raise ScadeOneException("Transition declaration with undefined source state.")
            # a StateRef can have either id or lunum
            state_ref = StateRef(lunum=self.lunum) if self.lunum else StateRef(id=self.id)
            if transition.source == state_ref:
                yield transition

    @property
    def strong_transitions(self) -> List[Transition]:
        """List of strong transitions, sorted by priority. It combines:

        - transitions defined in the state declaration,
        - transitions declared outside of states with this state as source.

        .. note::

           Adding or removing transitions from this list does not change the state transitions.
           Use :py:attr:`State.in_state_strong_transition_decls` to modify the list of strong
           transitions defined within the state, or changes the automaton's transitions for this state.
        """
        transitions = self._strong_transitions.copy()
        transitions.extend(self._get_transitions(is_strong=True))
        transitions.sort(key=Transition.sort_key)
        return transitions

    @property
    def body(self) -> scopes.Scope:
        """Body of state as a Scope."""
        return self._body

    @property
    def weak_transitions(self) -> List[Transition]:
        """List of weak transitions, sorted by priority. It combines:

        - transitions defined in the state declaration,
        - transitions declared outside of states with this state as target.

        .. note::

           Adding or removing transitions from this list does not change the state transitions.
           Use :py:attr:`State.in_state_weak_transition_decls` to modify the list of weak transitions defined within
           the state, or changes the automaton's transitions for this state.
        """
        transitions = self._weak_transitions.copy()
        transitions.extend(self._get_transitions(is_strong=False))
        transitions.sort(key=Transition.sort_key)
        return transitions

    @property
    def is_initial(self) -> bool:
        """True when state is initial."""
        return self._is_initial

    def get_targets(self) -> Set["State"]:
        """Get direct target states of the state.

        Returns
        -------
        set[State]
            A set of target State objects.
        """

        d = deque(self.strong_transitions + self.weak_transitions)
        targets = set()
        while d:
            transition = d.popleft()
            match transition.head:
                case State() as target_state:
                    targets.add(target_state)
                case Fork() as fork:
                    d.extend(fork.transitions)

        return targets


class StateMachine(DefByCase):  # numpydoc ignore=PR01
    """State machine definition.

    A state machine contains states and transition declarations defined as *items*.

    Consider using :py:attr:`StateMachine.states` and :py:attr:`StateMachine.transition_decls`
    properties to get the list of states and transition declarations.
    """

    def __init__(
        self,
        lhs: Optional[EquationLHS] = None,
        items: Optional[List[StateMachineItem]] = None,
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
    ) -> None:
        super().__init__(lhs, lunum, luid)
        self._items = items if items else []
        common.SwanItem.set_owner(self, self._items)

    @property
    def items(self) -> List[StateMachineItem]:
        """List of states and transition declarations in declaration order.

        Consider using :py:attr:`StateMachine.states` and :py:attr:`StateMachine.transition_decls`
        properties to get the list of states and transition declarations."""
        return self._items

    @property
    def states(self) -> List[State]:
        """Transitions and states of the state machine."""
        return [item for item in self._items if isinstance(item, State)]

    @property
    def transition_decls(self) -> List[Transition]:
        """List of transition declarations, defined in the automaton (not in a state)."""
        return [item for item in self._items if isinstance(item, Transition)]

    @property
    def initial_state(self) -> List[State]:
        """Return the initial state, or None if no initial state.
        There should be only one initial state, but this is not checked is there are multiple initial states."""
        return [state for state in self.states if state.is_initial]

    @property
    def default_state(self) -> List[State]:
        """Return the default state, or None if no default state.
        The default state is marked with dedicated pragma."""

        def is_default(state: State) -> bool:
            return any(
                isinstance(pragma, CGPragma) and pragma.kind == CGPragmaKind.DEFAULT
                for pragma in state.pragmas
            )

        return [state for state in self.states if is_default(state)]

    @property
    def all_transitions(self) -> List[Transition]:
        """Return all transitions, strong and weak, of all states."""
        transitions = []
        for state in self.states:
            transitions.extend(state.strong_transitions)
            transitions.extend(state.weak_transitions)
        return transitions

    @cache
    def get_state(
        self, state_id: Union[str, common.Identifier, common.Lunum, StateRef]
    ) -> Union[State, None]:
        """
        Retrieve a state object matching the given identifier or lunum.

        Parameters
        ----------
        state_id : Union[str, Identifier, Lunum, StateRef]
            The identifier or lunum to match against the states.
            If a string is provided, it is treated as an identifier.
            If a StateRef is provided, identifier or lunum are used for matching (lunum has priority if both are set).

        Returns
        -------
        State or None
            The state object that matches the given identifier or lunum, or None if no match is found.

        Raises
        ------
        ScadeOneException
            If `ident` type is not supported.
        """
        match state_id:
            case str() as id_str:
                states = [state for state in self.states if state.id and str(state.id) == id_str]
            case common.Identifier() as state_id:
                states = [state for state in self.states if state.id == state_id]
            case common.Lunum() as lunum:
                states = [state for state in self.states if state.lunum == lunum]
            case StateRef(id=id_, lunum=lunum):
                # lunum or id_ can be None, but not both
                states = [
                    state
                    for state in self.states
                    if (lunum and state.lunum == lunum) or (id_ and state.id == id_)
                ]
            case _:
                raise ScadeOneException("State identifier must be either an Identifier or a Lunum.")
        if states:
            return states[0]
        return None


#
# Activates
# ============================================================

# Activate If
# ------------------------------------------------------------


class IfteBranch(common.SwanItem):  # numpydoc ignore=PR01
    """
    Base class for :py:class:`IfteDataDef` and :py:class:`IfteIfActivation` classes.

    | ifte_branch ::= data_def
    |             | if_activation
    """

    def __init__(self) -> None:
        super().__init__()


class IfActivationBranch(common.SwanItem):  # numpydoc ignore=PR01
    """Stores a branch of an *if_activation*.

    A branch is:

    - **if** *expr* **then** *ifte_branch*, or
    - **elsif** *expr* **then** *ifte_branch*, or
    - **else** *ifte_branch*

    """

    def __init__(self, condition: Union[common.Expression, None], branch: IfteBranch) -> None:
        super().__init__()
        self._condition = condition
        self._branch = branch
        common.SwanItem.set_owner(self, branch)
        common.SwanItem.set_owner(self, condition)

    @property
    def condition(self) -> Union[common.Expression, None]:
        """Branch condition, None for **else** branch."""
        return self._condition

    @property
    def branch(self) -> IfteBranch:
        """Branch activation branch."""
        return self._branch


class IfActivation(common.SwanItem):  # numpydoc ignore=PR01
    """
    List of *if_activation* branches as a list of :py:class:`IfActivationBranch`.

    | *if_activation* ::= **if** *expr* **then** *ifte_branch*
    |                     {{ **elsif** *expr* **then** *ifte_branch* }}
    |                     **else** *ifte_branch*
    """

    def __init__(self, branches: List[IfActivationBranch]) -> None:
        super().__init__()
        self._branches = branches
        common.SwanItem.set_owner(self, branches)

    @property
    def branches(self) -> List[IfActivationBranch]:
        """Return branches of *if_activation*.
        There must be at least two branches, the **if** and the **else** branches."""
        return self._branches

    @property
    def is_valid(self) -> bool:
        """Activation branches must be at least **if** and **else**, and *elsif* has a condition."""
        if len(self.branches) < 2:
            return False
        if self.branches[0].condition is None:
            return False
        if self.branches[-1].condition is None:
            return False
        # check all elsif as non None condition
        if len(self.branches) > 2:
            non_cond = list(filter(lambda x: x.condition is None, self.branches[1:-1]))
            if non_cond:
                return False
        return True


class IfteDataDef(IfteBranch):  # numpydoc ignore=PR01
    """
    *ifte_branch* of an **activate if** as a data definition. See :py:class:`ActivateIf`.

    *ifte_branch* ::= *data_def*
    """

    def __init__(self, data_def: Union[common.Equation, scopes.Scope]) -> None:
        super().__init__()
        self._data_def = data_def
        common.SwanItem.set_owner(self, data_def)

    @property
    def data_def(self) -> Union[common.Equation, scopes.Scope]:
        return self._data_def


class IfteIfActivation(IfteBranch):  # numpydoc ignore=PR01
    """
    *ifte_branch* of an **activate if** as an *if_activation*. See :py:class:`ActivateIf`.

    *ifte_branch* ::= *if_activation*
    """

    def __init__(self, if_activation: IfActivation) -> None:
        super().__init__()
        self._if_activation = if_activation
        common.SwanItem.set_owner(self, if_activation)

    @property
    def if_activation(self) -> IfActivation:
        """If activation."""
        return self._if_activation


class ActivateIf(DefByCase):  # numpydoc ignore=PR01
    """Activate if operator definition:

    | *select_activation* ::= **activate** [[ LUID ]] *if_activation*
    | *if_activation* ::= **if** *expr* **then** *ifte_branch*
    |                     {{ **elsif** *expr* **then** *ifte_branch* }}
    |                     **else** *ifte_branch*
    | *ifte_branch* ::= *data_def* | *if_activation*
    """

    def __init__(
        self,
        if_activation: IfActivation,
        lhs: Optional[EquationLHS] = None,
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
    ) -> None:
        super().__init__(lhs, lunum, luid)
        self._if_activation = if_activation
        common.SwanItem.set_owner(self, if_activation)

    @property
    def if_activation(self) -> IfActivation:
        """Activation branch of **activate**."""
        return self._if_activation


# Activate When
# ------------------------------------------------------------
class ActivateWhenBranch(common.SwanItem):  # numpydoc ignore=PR01
    """Stores a branch of a *match_activation*.

    A branch is:
    **|** *pattern_with_capture* : *data_def*

    """

    def __init__(self, pattern: Pattern, data_def: Union[common.Equation, scopes.Scope]) -> None:
        super().__init__()
        self._pattern = pattern
        self._data_def = data_def
        common.SwanItem.set_owner(self, pattern)
        common.SwanItem.set_owner(self, data_def)

    @property
    def pattern(self) -> Pattern:
        """Branch pattern."""
        return self._pattern

    @property
    def data_def(self) -> Union[common.Equation, scopes.Scope]:
        """Branch data definition."""
        return self._data_def


class ActivateWhen(DefByCase):  # numpydoc ignore=PR01
    """Activate when operator definition.

    There must be at least one branch.
    This can be checked with the *is_valid()* method.

    | *select_activation* ::= *activate* [[ LUID ]] *match_activation*
    | *match_activation* ::= **when** *expr* **match**
    |                      {{ | *pattern_with_capture* : *data_def* }}+
    """

    def __init__(
        self,
        condition: common.Expression,
        branches: List[ActivateWhenBranch],
        lhs: Optional[EquationLHS] = None,
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
    ) -> None:
        super().__init__(lhs, lunum, luid)
        self._condition = condition
        self._branches = branches
        common.SwanItem.set_owner(self, condition)
        common.SwanItem.set_owner(self, branches)

    @property
    def is_valid(self) -> bool:
        """True when there is at least one branch."""
        return len(self.branches) > 0

    @property
    def condition(self) -> common.Expression:
        """Activate when condition."""
        return self._condition

    @property
    def branches(self) -> List[ActivateWhenBranch]:
        """Activate when branches."""
        return self._branches
