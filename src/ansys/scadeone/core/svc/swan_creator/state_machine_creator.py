# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations
from typing import TYPE_CHECKING, Union, cast

if TYPE_CHECKING:
    from ansys.scadeone.core import swan


class StateMachineFactory:
    """Factory class for state machine."""

    _instance = None
    _parser = None

    def __new__(cls, *args, **kwargs) -> StateMachineFactory:
        if not cls._instance:
            cls._instance = super(StateMachineFactory, cls).__new__(cls)
            from ansys.scadeone.core.model.loader import SwanParser
            from ansys.scadeone.core.common.logger import LOGGER

            cls._instance._parser = SwanParser(LOGGER)  # type: ignore bad-argument-type
        return cls._instance

    def _guard_to_expression(self, guard: swan.Expression | str | None) -> swan.Expression | None:
        """Convert guard to swan.Expression if it is a string. Otherwise, return guard as is."""
        if isinstance(guard, str):
            from ansys.scadeone.core.common.storage import SwanString

            guard = self._parser.expression(SwanString(guard))  # type: ignore missing-attribute
        return guard

    def _action_to_scope(self, action: swan.Scope | str | None) -> swan.Scope:
        """Convert action to swan.Scope if it is a string. Otherwise, return the action as is."""
        from ansys.scadeone.core.swan import Scope

        if isinstance(action, str):
            from ansys.scadeone.core.common.storage import SwanString

            scope_section = self._parser.scope_section(SwanString(action))  # type: ignore missing-attribute
            action = Scope([scope_section] if scope_section else None)
        elif action is None:
            action = Scope()
        return action

    def create_state(
        self, name: str, is_initial: bool = False, is_default: bool = False
    ) -> swan.State:
        """Create a state.

        Parameters
        ----------
        name : str
            The name of the state.
        is_initial : bool, optional
            Whether the state is an initial state, by default False.
        is_default : bool, optional
            Whether the state is a default state, by default False.

        Returns
        -------
        State
            The created state.
        """
        from ansys.scadeone.core.swan import Identifier, State, ScadeOneException

        id_ = Identifier(name)
        if not id_.is_valid:
            raise ScadeOneException(f"Invalid state name: {name}")
        state = State(id=id_, is_initial=is_initial)
        if is_default:
            self._set_default(state)
        return state

    @staticmethod
    def _set_default(state: swan.State) -> None:
        """Set the state as a default state.

        Parameters
        ----------
        state : State
            The state to set as default.
        """
        from ansys.scadeone.core.swan import CGPragma, CGPragmaKind, ScadeOneException

        if not state.is_default:
            default_kind_str = str(CGPragmaKind.DEFAULT)
            if not default_kind_str:
                raise ScadeOneException(
                    "Failed to get the string representation of the default pragma kind."
                )
            pragma = CGPragma(default_kind_str)
            state.pragmas.append(pragma)

    def create_local_variable(self, name: str, var_type: str) -> swan.VarDecl:
        """Create a local variable.

        Parameters
        ----------
        name : str
            The name of the local variable.
        var_type : Type
            The type of the local variable.

        Returns
        -------
        LocalVariable
            The created local variable.
        """
        from ansys.scadeone.core.swan import Identifier, VarDecl, ScadeOneException
        from ansys.scadeone.core.common.storage import SwanString

        id_ = Identifier(name)
        if not id_.is_valid:
            raise ScadeOneException(f"Invalid local variable name: {name}")
        type_decls = self._parser.declaration(SwanString(f"type t0 = {var_type};"))  # type: ignore missing-attribute
        return VarDecl(id=id_, type=type_decls.types[0].definition.type)

    def create_transition(
        self,
        source: swan.State | None,
        target: swan.State,
        priority: int | None = None,
        is_strong: bool = False,
        guard: swan.Expression | str | None = None,
        action: swan.Scope | str | None = None,
    ) -> swan.Transition:
        """Create a transition between two states or between a fork and a state.

        Parameters
        ----------
        source : swan.State | None,
            Source state for the transition. None expected when the source is a swan.Fork.
        target : swan.State
            Target state for the transition.
        priority : int | None, optional
            Transition priority, by default None.
        is_strong : bool, optional
            Whether the transition is strong, by default False.
        guard : swan.Expression | str | None, optional
            Guard expression of the transition. Can be either a Swan expression or a string representing the expression.
        action : swan.Scope | str | None, optional
            Action expression of the transition. Can be either a Swan scope or a string representing the expression.

        Returns
        -------
        Transition
            The created transition.
        """
        from ansys.scadeone.core.swan import (
            Literal,
            Transition,
            State,
            StateRef,
            ScadeOneException,
        )

        # Helper to convert a State into a StateRef
        def _to_state_ref(state: State):
            state_lunum = state._lunum
            state_id = state._id
            if state_lunum:
                return StateRef(lunum=state_lunum)
            elif state_id:
                return StateRef(id=state_id)
            raise ScadeOneException("State must have either an id or a lunum to create a StateRef.")

        tgt = _to_state_ref(target)
        src = _to_state_ref(source) if source is not None else None
        prio_literal = Literal(str(priority)) if priority is not None else None
        guard = self._guard_to_expression(guard)
        scope = self._action_to_scope(action)

        return Transition(
            priority=prio_literal,
            is_strong=is_strong,
            guard=guard,
            action=scope,
            target=tgt,
            source=src,
        )


class StateMachineItemAdder:
    """Class for adding state machine items (State or Transition) to the state machine.

    Parameters
    ----------
    owner : StateMachine
        The state machine to which the states will be added.
    """

    def __init__(self, owner: swan.StateMachine) -> None:
        self._owner = owner

    def add_state_machine_item(self, sm_item: swan.StateMachineItem) -> None:
        """Add a state machine item to the state machine.

        Parameters
        ----------
        sm_item : StateMachineItem
            The state machine item to add to the state machine.
        """
        from ansys.scadeone.core.swan import LunumManager, State, Transition, ScadeOneException

        if isinstance(sm_item, State):
            lnum_manager = LunumManager.get_lunum_manager(self._owner)
            if not lnum_manager:
                raise ScadeOneException(
                    f"Lunum manager not found for the state machine '{self._owner.get_full_path()}'."
                )
            sm_item._lunum = lnum_manager.get_next_lunum()
        elif isinstance(sm_item, Transition):
            # Transition from Fork must not be added in the StateMachine items list
            # Moreover, the transition ownership will be set in the Fork constructor (done in a second step just after)
            if sm_item.source is None:
                return

        if self._owner._items:
            self._owner._items.append(sm_item)
        else:
            self._owner._items = [sm_item]
        sm_item._owner = self._owner

    def remove_state_machine_item(self, sm_item: swan.StateMachineItem) -> None:
        """Remove a state machine item from the state machine.

        Parameters
        ----------
            sm_item : StateMachineItem
                 The state machine item to remove from the state machine.
        """

        if self._owner._items:
            self._owner._items.remove(sm_item)
        sm_item._owner = None


class StateMachineCreator:
    """Class for adding state machine content."""

    def __init__(self) -> None:
        self._state_machine_item_adder = StateMachineItemAdder(self)  # type: ignore bad-argument-type

    def add_state(
        self, name: str, is_initial: bool = False, is_default: bool = False
    ) -> swan.State:
        """Add a state to the state machine.

        Parameters
        ----------
        name : str
            The name of the state.
        is_initial : Optional[bool], optional
            Whether the state is an initial state, by default False.
        is_default : Optional[bool], optional
            Whether the state is a default state, by default False.

        Returns
        -------
        State
            The created state.
        """
        from ansys.scadeone.core.swan import ScadeOneException

        if not name:
            raise ScadeOneException("State name is required.")
        state = StateMachineFactory().create_state(name, is_initial, is_default)
        self._state_machine_item_adder.add_state_machine_item(state)
        return state

    def add_strong_transition(
        self,
        source: swan.State,
        target: swan.State,
        priority: int | None = None,
        guard: swan.Expression | str = "true",
        action: swan.Scope | str | None = None,
    ) -> swan.Transition:
        """Add a strong transition between states.

        The created transition declaration is added to :py:attr:`StateMachine.transition_decls<ansys.scadeone.core.swan.StateMachine.transition_decls>`
        property of the state machine.


        Parameters
        ----------
        source : swan.State
            The state from which the transition starts.
        target : swan.State
            The state to which the transition goes.
        priority : Optional[int], optional
            The transition priority when several transitions have the same source state.
        guard : Union[swan.Expression | str], optional
            Expression representing the guard condition.
            Can be either a :py:class:`swan.Expression<ansys.scadeone.core.swan.Expression>` or a string.
            Default value is the :py:class:`swan.BooleanLiteral<ansys.scadeone.core.swan.BooleanLiteral>` true.
        action : Optional[swan.Scope | str], optional
            Expression representing the action to trigger.
            Can be either a :py:class:`swan.Scope<ansys.scadeone.core.swan.Scope>` or a string.

        Returns
        -------
        Transition
            The created transition.
        """
        return self._add_transition(source, target, True, priority, guard, action)

    def add_weak_transition(
        self,
        source: swan.State,
        target: swan.State,
        priority: int | None = None,
        guard: swan.Expression | str = "true",
        action: swan.Scope | str | None = None,
    ) -> swan.Transition:
        """Add a weak transition between states.

        The created transition declaration is added to :py:attr:`StateMachine.transition_decls<ansys.scadeone.core.swan.StateMachine.transition_decls>`
        property of the state machine.

        Parameters
        ----------
        source : swan.State
            The state from which the transition starts.
        target : swan.State
            The state to which the transition goes.
        priority : Optional[int], optional
            The transition priority when several transitions have the same source state.
        guard : Union[swan.Expression | str], optional
            Expression representing the guard condition.
            Can be either a :py:class:`swan.Expression<ansys.scadeone.core.swan.Expression>` or a string.
            Default value is the :py:class:`swan.BooleanLiteral<ansys.scadeone.core.swan.BooleanLiteral>` true.
        action : Optional[swan.Scope | str], optional
            Expression representing the action to trigger.
            Can be either a :py:class:`swan.Scope<ansys.scadeone.core.swan.Scope>` or a string.

        Returns
        -------
        Transition
            The created transition.
        """
        return self._add_transition(source, target, False, priority, guard, action)

    def _add_transition(
        self,
        source: swan.State | None,
        target: swan.State,
        is_strong: bool,
        priority: int | None,
        guard: swan.Expression | str,
        action: swan.Scope | str | None,
    ) -> swan.Transition:
        transition = StateMachineFactory().create_transition(
            source, target, priority, is_strong, guard, action
        )
        self._state_machine_item_adder.add_state_machine_item(transition)
        return transition

    def remove_transition(self, transition: swan.Transition) -> None:
        """Remove a transition from its owner.

        Parameters
        ----------
        transition : Transition
            The transition to remove.
        """
        self._state_machine_item_adder.remove_state_machine_item(transition)


class LocalVariableAdder:
    """Class for adding local variables to the state machine.

    Parameters
    ----------
    owner : State
        The state to which the local variables will be added.
    """

    def __init__(self, owner: swan.State) -> None:
        self._owner = owner

    def add_local_variable(self, var: swan.VarDecl) -> None:
        """Add a local variable to the state's diagram.

        Parameters
        ----------
        var : LocalVariable
            The local variable to add to the state's diagram.
        """
        from ansys.scadeone.core.swan import (
            Scope,
            Diagram,
            SectionObject,
            VarSection,
            ScadeOneException,
        )

        # If state has not diagram yet, create a diagram and add it to the state body.
        if not self._owner.body or not self._owner.body.sections:
            new_diag = Diagram()
            scope = Scope([new_diag])
            scope.owner = self._owner
            self._owner._body = scope
        diag = next(filter(lambda sec: isinstance(sec, Diagram), self._owner.body.sections), None)
        if not diag:
            raise ScadeOneException("Failed to find the diagram in the state body.")
        diag = cast(Diagram, diag)
        sec_objs = [obj for obj in diag.objects if isinstance(obj, SectionObject)]
        if not sec_objs:
            var_sec = VarSection([var])
            sec_obj = SectionObject(var_sec)
            sec_obj.owner = diag
            diag.objects.append(sec_obj)
        else:
            sec_obj = sec_objs[0]
        if isinstance(sec_obj.section, VarSection) and not any(
            filter(lambda var_: var_ == var, sec_obj.section.var_decls)
        ):
            sec_obj.section.var_decls.append(var)
        var._owner = sec_obj


class StateCreator:
    """Class for adding state content."""

    def __init__(self) -> None:
        self._state_adder = LocalVariableAdder(self)  # type: ignore bad-argument-type

    def add_local_variable(self, name: str, var_type: str) -> swan.VarDecl:
        """Add a local variable to the state's diagram.

        Parameters
        ----------
        name : str
            The name of the local variable.
        var_type : str
            The type of the local variable.

        Returns
        -------
        LocalVariable
            The created local variable.
        """
        from ansys.scadeone.core.swan import ScadeOneException

        if not name:
            raise ScadeOneException("Local variable name cannot be empty.")
        if not var_type:
            raise ScadeOneException("Local variable type cannot be empty.")
        local_var = StateMachineFactory().create_local_variable(name, var_type)
        self._state_adder.add_local_variable(local_var)
        return local_var

    def add_section(self, section: Union[str, swan.Scope]) -> None:
        """Add a section to the state.

        Parameters
        ----------
        section : Scope
            The section to add to the state.
        """
        from ansys.scadeone.core.common.storage import SwanString

        if isinstance(section, str):
            section = StateMachineFactory()._parser.scope_section(SwanString(section))  # type: ignore missing-attribute
        self._body._sections.append(section)  # type: ignore missing-attribute
        section._owner = self._body  # type: ignore missing-attribute


class TransitionCreator:
    """Class for adding fork from a transition."""

    def add_fork(
        self,
        guard: swan.Expression | str = "true",
        action: swan.Scope | str | None = None,
    ) -> tuple[swan.Fork, swan.Transition]:
        """Add a fork to the transition (either between two states or between a fork and a state).

        The target of the transition is modified to point to the future fork.
        The returned fork is created with one default outgoing transition pointing to the original transition target.
        The outgoing transition type (strong or weak) is the same as the original transition type.

        Parameters
        ----------
        guard : Union[swan.Expression | str], optional
            Expression representing the guard condition.
            Can be either a :py:class:`swan.Expression<ansys.scadeone.core.swan.Expression>` or a string.
            Default value is the :py:class:`swan.BooleanLiteral<ansys.scadeone.core.swan.BooleanLiteral>` true.
        action : Optional[swan.Section | str], optional
            Expression representing the action to trigger.
            Can be either a :py:class:`swan.Section<ansys.scadeone.core.swan.Section>` or a string.

        Returns
        -------
        Fork, Transition
            The created fork with one outgoing transition between the fork and the original transition target
        """
        from ansys.scadeone.core.swan import Fork

        # Create an outgoing transition between future fork and target
        outgoing = StateMachineFactory().create_transition(
            None,
            self.head,  # type: ignore missing-attribute
            1,
            self.is_strong,  # type: ignore missing-attribute
            guard,
            action,
        )
        # Create the fork
        fork = Fork([outgoing])

        # Adapt the target of the transition received as argument to point to the fork
        self._target = fork

        # Attach the created fork to the transition used for this operation
        fork.owner = self  # type: ignore bad-argument-type

        return fork, outgoing


class ForkCreator:
    """Class for adding additional outgoing transitions from the fork."""

    def add_fork_transition(
        self,
        target: swan.State,
        priority: int,
        guard: swan.Expression | str = "true",
        action: swan.Scope | str | None = None,
        is_resume: bool = False,
        is_else: bool = False,
    ) -> swan.Transition:
        """Add a new transition starting from the fork to the state provided in argument.

        The transition type (weak or strong) is the same as the incoming transition of the fork.
        To create an **else branch** transition, do not provide any guard condition, use parameter is_else=True and
        invoke this method last after creating all other fork transitions.

        Parameters
        ----------
        target : swan.State
            The state to which the transition goes.
        priority : int
            The transition priority when several transitions have the same source fork.
        guard : Union[swan.Expression | str], optional
            Expression representing the guard condition.
            Can be either a :py:class:`swan.Expression<ansys.scadeone.core.swan.Expression>` or a string.
            Default value is the :py:class:`swan.BooleanLiteral<ansys.scadeone.core.swan.BooleanLiteral>` true.
        action : Optional[swan.Scope | str], optional
            Expression representing the action to trigger.
            Can be either a :py:class:`swan.Scope<ansys.scadeone.core.swan.Scope>` or a string.
        is_resume : bool, optional
            True if the transition is a **resume** transition, False for **restart** transition. Default is False.
        is_else : bool, optional
            True if the transition is an **else branch** transition, False otherwise. Default is False. Note that an else branch transition must not have any guard condition.

        Returns
        -------
        Transition
            The transition starting from the fork to the target state
        """
        is_strong = self.from_transition.is_strong  # type: ignore missing-attribute

        real_guard = None if is_else else guard
        transition = StateMachineFactory().create_transition(
            None, target, priority, is_strong, real_guard, action
        )
        transition._owner = self
        transition._is_resume = is_resume

        self._transitions.append(transition)  # type: ignore missing-attribute

        return transition
