# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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
from typing import List, Optional, Union

import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes

from .expressions import Literal, Pattern


class LHSItem(common.SwanItem):  # numpydoc ignore=PR01
    """Defines an item on the left-hand side of an equation, an ID, or underscore '_'.

    Parameters
    ----------
    id : Identifier (optional)
        Identifier or None for underscore value.
    """

    def __init__(self, id: Union[common.Identifier, str] = None) -> None:
        super().__init__()
        self._id = id

    @property
    def id(self) -> Union[common.Identifier, None]:
        """Returns id value or None."""
        return self._id

    @property
    def is_underscore(self) -> bool:
        """True when LHSItem is '_'."""
        return self._id is None

    def __str__(self) -> str:
        return str(self.id) if self.id else "_"


class EquationLHS(common.SwanItem):  # numpydoc ignore=PR01
    """Equation left-hand side part:

    *lhs* ::= ( ) | *lhs_item* {{ , *lhs_item* }} [[ , .. ]]

    """

    def __init__(self, lhs_items: List[LHSItem], is_partial_lhs: Optional[bool] = False) -> None:
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

    def __str__(self) -> str:
        if len(self.lhs_items):
            items = ", ".join([str(item) for item in self.lhs_items])
            if self.is_partial_lhs:
                items += ", .."
        else:
            items = "()"
        return items


class ExprEquation(common.Equation):  # numpydoc ignore=PR01
    """Flows definition using an expression:

    *equation* ::= *lhs* [luid] = *expr*"""

    def __init__(
        self, lhs: EquationLHS, expr: common.Expression, luid: Optional[common.Luid] = None
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

    def __str__(self) -> str:
        luid = f"{self.luid} " if self.luid else ""
        return f"{self.lhs} {luid}= {self.expr};"


# Definition by cases: state machines and activate if/when
# ========================================================
class DefByCase(common.Equation, ABC):  # numpydoc ignore=PR01
    """Base class for state machine and active if/when equations."""

    def __init__(
        self,
        lhs: Optional[EquationLHS] = None,
        name: Optional[common.Luid] = None,
        is_equation: bool = False,
    ) -> None:
        common.Equation().__init__()
        self._lhs = lhs
        self._name = name
        self._is_equation = is_equation

    @property
    def lhs(self) -> Union[EquationLHS, None]:
        """Left-hand side of the equation, may be None."""
        return self._lhs

    @property
    def name(self) -> Union[common.Luid, None]:
        """Return name or None if no name."""
        return self._name

    @property
    def is_equation(self) -> bool:
        """True when the object is an equation."""
        return self._is_equation

    def lhs_str(self) -> str:
        if self.lhs:
            return f"{self.lhs} : "
        return ""


# State Machines
# ============================================================


class StateMachineItem(common.SwanItem, ABC):  # numpydoc ignore=PR01
    """Base class for state machine items (states and transitions)."""

    def __init__(self) -> None:
        common.SwanItem().__init__()


class StateRef(common.SwanItem):  # numpydoc ignore=PR01
    """State identification:

    *state_ref* ::= ID | LUNUM

    The class is also used for transition declaration or target
    (**restart**/**resume**) where one has either an ID or a LUNUM.
    """

    def __init__(
        self, lunum: Optional[common.Lunum] = None, id: Optional[common.Identifier] = None
    ) -> None:
        super().__init__()
        self._lunum = lunum
        self._id = id

    @property
    def lunum(self) -> Union[common.Luid, None]:
        """Lunum part, possible None."""
        return self._lunum

    @property
    def id(self) -> Union[common.Identifier, None]:
        """Id part, possible None."""
        return self._id

    def __str__(self) -> str:
        if self.lunum:
            return str(self.lunum)
        return str(self.id)


class Fork(common.SwanItem):  # numpydoc ignore=PR01
    """Base class for fork-related classes."""

    def __init__(self) -> None:
        super().__init__()


class Target(common.SwanItem):  # numpydoc ignore=PR01
    """Arrow target as a state reference and kind."""

    def __init__(self, target: StateRef, is_resume: Optional[bool] = False) -> None:
        super().__init__()
        self._is_resume = is_resume
        self._target = target

    @property
    def is_resume(self) -> bool:
        """True when is **resume**, else **restart**."""
        return self._is_resume

    @property
    def is_restart(self) -> bool:
        """True when is **restart**, else **resume**."""
        return not self.is_resume

    @property
    def target(self) -> StateRef:
        """Target reference"""
        return self._target

    def __str__(self):
        kind = "restart" if self.is_restart else "resume"
        return f"{kind} {self.target}"


class Arrow(common.SwanItem):  # numpydoc ignore=PR01
    """Encode an arrow, with or without guard:

    | *guarded_arrow* ::= ( *expr* ) *arrow*
    | *arrow* ::= [[ *scope* ]] (( *target* | *fork* ))
    """

    def __init__(
        self,
        guard: Union[common.Expression, None],
        action: Union[scopes.Scope, None],
        target: Optional[Target] = None,
        fork: Optional[Fork] = None,
    ) -> None:
        super().__init__()
        self._guard = guard
        self._action = action
        self._target = target
        self._fork = fork

    @property
    def guard(self) -> Union[scopes.Scope, None]:
        """Arrow guard or None."""
        return self._guard

    @property
    def action(self) -> Union[scopes.Scope, None]:
        """Arrow action or None."""
        return self._action

    @property
    def target(self) -> Union[Target, None]:
        """Arrow target."""
        return self._target

    @property
    def fork(self) -> Union[Fork, None]:
        """Arrow fork."""
        return self._fork

    @property
    def is_valid(self):
        "Check whether the arrow has a target or a fork."
        return bool(self.target) != bool(self.fork)

    def __str__(self):
        arrow = []
        if self.guard:
            arrow.append(f"({self.guard})")
        if self.action:
            arrow.append(f"{self.action}")
        if self.target:
            arrow.append(str(self.target))
        else:
            arrow.append(str(self.fork))
        return " ".join(arrow)


class ForkTree(Fork):  # numpydoc ignore=PR01
    """Fork as a tree of arrows:

    | *fork* ::= **if** *guarded_arrow*
    |        {{ **elsif** *guarded_arrow* }}
    |        [[ **else** *arrow* ]]
    |        **end**
    """

    def __init__(
        self,
        if_arrow: Arrow,
        elsif_arrows: Optional[List[Arrow]] = None,
        else_arrow: Optional[Arrow] = None,
    ):
        super().__init__()
        self._if_arrow = if_arrow
        self._elsif_arrows = elsif_arrows if elsif_arrows else []
        self._else_arrow = else_arrow

    @property
    def if_arrow(self) -> Arrow:
        """Start arrow."""
        return self._if_arrow

    @property
    def elsif_arrows(self) -> List[Arrow]:
        """Elsif arrows list."""
        return self._elsif_arrows

    @property
    def else_arrow(self) -> Union[Arrow, None]:
        """Else arrow."""
        return self._else_arrow

    def __str__(self) -> str:
        fork = f"if {self.if_arrow}"
        if self.elsif_arrows:
            elsif = "\n".join(f"elsif {arrow}" for arrow in self.elsif_arrows)
            fork += f"\n{elsif}"
        if self.else_arrow:
            fork += f"\nelse {self.else_arrow}"
        return f"{fork} end"


class ForkWithPriority(common.SwanItem):  # numpydoc ignore=PR01
    """Fork as a priority fork declaration:

    | *fork_priority* ::= *priority* **if** *guarded_arrow*
    |                  | *priority **else** *arrow*
    """

    def __init__(self, priority: Union[Literal, None], arrow: Arrow, is_if_arrow: bool) -> None:
        super().__init__()
        self._priority = priority
        self._arrow = arrow
        self._is_if_arrow = is_if_arrow

    @property
    def priority(self) -> Union[Literal, None]:
        """Fork priority."""
        return self._priority

    @property
    def arrow(self) -> Arrow:
        """For arrow."""
        return self._arrow

    @property
    def is_if_arrow(self) -> bool:
        """True when fork is *priority* **if** *guarded_arrow*,
        False if fork is *priority* **else** *arrow*.
        """
        return self._is_if_arrow

    @property
    def is_valid(self) -> bool:
        """Check if fork is either an **if** with a *guarded_arrow*, or
        an **else** with an *arrow*."""
        if self.is_if_arrow:
            return self.arrow.guard is not None
        return self.arrow.guard is None

    def __str__(self) -> str:
        kind = "if" if self.is_if_arrow else "else"
        priority = str(self.priority) if self.priority else " "
        return f":{priority}: {kind} {self.arrow}"


class ForkPriorityList(Fork):  # numpydoc ignore=PR01
    """List of :py:class:`ForkWithPriority`.

    *fork* ::=  {{ *fork_priority* }} **end**
    """

    def __init__(self, prio_forks: List[ForkWithPriority]) -> None:
        super().__init__()
        self._prio_forks = prio_forks

    @property
    def prio_forks(self) -> List[ForkWithPriority]:
        """List of fork with priority."""
        return self._prio_forks

    def __str__(self) -> str:
        forks = "\n".join([str(fork) for fork in self.prio_forks])
        return f"{forks} end" if forks else "end"


class Transition(common.SwanItem, common.PragmaBase):  # numpydoc ignore=PR01
    """State machine transition:

    | *transition* ::= **if** *guarded_arrow* ;
    |              | [[ *scope* ]] *target* ;

    """

    def __init__(self, arrow: Arrow, pragmas: Optional[List[common.Pragma]] = None) -> None:
        common.SwanItem.__init__(self)
        common.PragmaBase.__init__(self, pragmas)
        self._arrow = arrow

    @property
    def arrow(self) -> Arrow:
        """Transition arrow."""
        return self._arrow

    @property
    def is_guarded(self) -> bool:
        """True when arrow is guarded."""
        return self.arrow.guard is not None

    def __str__(self) -> str:
        pragmas = self.pragma_str()
        if pragmas:
            pragmas = " " + pragmas
        if self.is_guarded:
            return f"if {self.arrow}{pragmas};"
        return f"{self.arrow}{pragmas};"


class TransitionDecl(StateMachineItem):  # numpydoc ignore=PR01
    """Declaration of state machine transition:

    | *transition_decl* ::= *priority* [[ *state_ref* ]]
    |                      (( **unless** | **until** )) *transition*
    | *priority* ::= : [[ INTEGER ]] :

    """

    def __init__(
        self,
        priority: Union[Literal, None],
        transition: Transition,
        is_strong: bool,
        state_ref: StateRef,
    ) -> None:
        super().__init__()
        self._priority = priority
        self._transition = transition
        self._is_strong = is_strong
        self._state_ref = state_ref
        transition.owner = self

    @property
    def priority(self) -> Union[Literal, None]:
        """Transition priority."""
        return self._priority

    @property
    def transition(self) -> Transition:
        """Transition data."""
        return self._transition

    @property
    def is_strong(self) -> bool:
        """True when strong transition, else weak transition."""
        return self._is_strong

    @property
    def state_ref(self) -> StateRef:
        return self._state_ref

    def __str__(self) -> str:
        ref = self.state_ref
        kind = "unless" if self.is_strong else "until"
        priority = str(self.priority) if self.priority else " "
        return f":{priority}: {ref} {kind} {self.transition}"


class State(StateMachineItem, common.PragmaBase):  # numpydoc ignore=PR01
    """State definition."""

    def __init__(
        self,
        id: Optional[common.Identifier] = None,
        lunum: Optional[common.Lunum] = None,
        strong_transitions: Optional[List[Transition]] = None,
        sections: Optional[List[scopes.ScopeSection]] = None,
        weak_transitions: Optional[List[Transition]] = None,
        is_initial: Optional[bool] = False,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        StateMachineItem.__init__(self)
        common.PragmaBase.__init__(self, pragmas)
        self._id = id
        self._lunum = lunum
        self._strong_transitions = strong_transitions if strong_transitions else []
        self._sections = sections if sections else []
        self._weak_transitions = weak_transitions if weak_transitions else []
        self._is_initial = is_initial
        common.SwanItem.set_owner(self, self._strong_transitions)
        common.SwanItem.set_owner(self, self._weak_transitions)
        common.SwanItem.set_owner(self, sections)

    @property
    def id(self) -> Union[common.Identifier, None]:
        return self._id

    @property
    def lunum(self) -> Union[common.Lunum, None]:
        return self._lunum

    @property
    def strong_transitions(self) -> List[Transition]:
        return self._strong_transitions

    @property
    def has_strong_transition(self) -> bool:
        """True when state has strong transitions."""
        return True if self.strong_transitions else False

    @property
    def sections(self) -> List[scopes.ScopeSection]:
        return self._sections

    @property
    def has_body(self) -> bool:
        """True when state has a body, namely scope sections."""
        return True if self.sections else False

    @property
    def weak_transitions(self) -> List[Transition]:
        return self._weak_transitions

    @property
    def has_weak_transition(self) -> bool:
        """True when state has weak transitions."""
        return True if self.weak_transitions else False

    @property
    def is_initial(self) -> Optional[bool]:
        return self._is_initial

    def __str__(self) -> str:
        decl = "initial state" if self.is_initial else "state"
        if self.lunum:
            decl += f" {self.lunum}"
        if self.id:
            decl += f" {self.id}"
        decl += self.pragma_str()
        decl += ":"

        def str_of_transition(transitions, keyword):
            if transitions:
                text = "\n".join([str(transition) for transition in transitions])
                return f"\n{keyword}\n{text}"
            return ""

        strong = str_of_transition(self.strong_transitions, "unless")
        weak = str_of_transition(self.weak_transitions, "until")
        if self.sections:
            body = "\n" + "\n".join([str(section) for section in self.sections])
        else:
            body = ""
        state = f"{decl}{strong}{body}{weak}"
        return state


class StateMachine(DefByCase):  # numpydoc ignore=PR01
    """State machine definition."""

    def __init__(
        self,
        lhs: Optional[EquationLHS] = None,
        items: Optional[List[StateMachineItem]] = None,
        name: Optional[common.Luid] = None,
        is_equation: bool = False,
    ) -> None:
        super().__init__(lhs, name, is_equation)
        self._items = items if items else []
        common.SwanItem.set_owner(self, self._items)

    @property
    def items(self) -> List[StateMachineItem]:
        """Transitions and states of the state machine."""
        return self._items

    def __str__(self) -> str:
        name = f" {self.name}" if self.name else ""
        lhs = self.lhs_str()
        automaton = f"{lhs}automaton{name}"
        if self.items:
            items = "\n".join([str(item) for item in self.items])
            automaton += "\n" + items
        if self.is_equation:
            automaton += ";"
        return automaton


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

    @property
    def condition(self) -> Union[common.Expression, None]:
        """Branch condition, None for **else** branch."""
        return self._condition

    @property
    def branch(self) -> IfteBranch:
        """Branch activation branch."""
        return self._branch

    def to_str(self, index: int) -> str:
        if index == 0:
            return f"if {self.condition} then {self.branch}"
        if self.condition:
            return f"elsif {self.condition} then {self.branch}"
        return f"else {self.branch}"


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
            non_cond = list(filter(lambda x: x.condition is None, [self.branches[1:-1]]))
            if non_cond:
                return False
        return True

    def __str__(self) -> str:
        branches = [branch.to_str(index) for (index, branch) in enumerate(self.branches)]
        return "\n".join(branches)


class IfteDataDef(IfteBranch):  # numpydoc ignore=PR01
    """
    *ifte_branch* of an **activate if** as a data definition. See :py:class:`ActivateIf`.

    *ifte_branch* ::= *data_def*
    """

    def __init__(self, data_def: Union[common.Equation, scopes.Scope]) -> None:
        super().__init__()
        self._data_def = data_def

    @property
    def data_def(self) -> Union[common.Equation, scopes.Scope]:
        return self._data_def

    def __str__(self) -> str:
        return str(self.data_def)


class IfteIfActivation(IfteBranch):  # numpydoc ignore=PR01
    """
    *ifte_branch* of an **activate if** as an *if_activation*. See :py:class:`ActivateIf`.

    *ifte_branch* ::= *if_activation*
    """

    def __init__(self, if_activation: IfActivation) -> None:
        super().__init__()
        self._if_activation = if_activation

    @property
    def if_activation(self) -> IfActivation:
        """If activation."""
        return self._if_activation

    def __str__(self) -> str:
        return str(self.if_activation)


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
        name: Optional[common.Luid] = None,
        is_equation: bool = False,
    ) -> None:
        super().__init__(lhs, name, is_equation)
        self._if_activation = if_activation
        if_activation.owner = self

    @property
    def if_activation(self) -> IfActivation:
        """Activation branch of **activate**."""
        return self._if_activation

    def __str__(self) -> str:
        luid = f" {self.name}" if self.name else ""
        lhs = self.lhs_str()
        activate = f"{lhs}activate{luid}\n{self.if_activation}"
        if self.is_equation:
            activate += ";"
        return activate


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

    @property
    def pattern(self) -> Pattern:
        """Branch pattern."""
        return self._pattern

    @property
    def data_def(self) -> Union[common.Equation, scopes.Scope]:
        """Branch data definition."""
        return self._data_def

    def __str__(self) -> str:
        return f"| {self.pattern} : {self.data_def}"


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
        name: Optional[str] = None,
        is_equation: bool = False,
    ) -> None:
        super().__init__(lhs, name, is_equation)
        self._condition = condition
        self._branches = branches
        condition.owner = self
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

    def __str__(self) -> str:
        luid = f" {self.name}" if self.name else ""
        lhs = self.lhs_str()
        branches = "\n".join([str(branch) for branch in self.branches])
        activate = f"{lhs}activate{luid} when {self.condition} match\n{branches}"
        if self.is_equation:
            activate += ";"
        return activate
