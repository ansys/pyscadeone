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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.scadeone.core import swan


class LetAdder:
    """Class for adding and removing automata from a let section."""

    def __init__(self, owner: swan.LetSection) -> None:
        self._owner = owner

    def add_automaton(self, automaton: swan.StateMachine) -> None:
        """Add the provided automate to the let section.

        Parameters
        ----------
            automaton : StateMachine
                 The automaton to add as equation.
        """
        automaton.owner = self._owner
        equations = self._owner.equations
        if not equations:
            equations = [automaton]
        else:
            equations.append(automaton)

    def remove_automaton(self, name: str) -> None:
        """Remove from the let section the automaton matching the provided name.

        Parameters
        ----------
            name : str
                 The name of the automaton to remove.

        Raises
        ------
        ScadeOneException
            If no automaton with the provided name exists or if the let section has no automaton as equations.
        """
        from ansys.scadeone.core.swan import StateMachine, ScadeOneException

        equations = self._owner.equations
        all_fsm = [eq for eq in equations if isinstance(eq, StateMachine)]
        state_machine = next((sm for sm in all_fsm if sm._luid and sm._luid.value == name), None)
        if state_machine:
            equations.remove(state_machine)
            state_machine._owner = None
        elif all_fsm:
            raise ScadeOneException(f"Automaton {name} not found.")
        else:
            raise ScadeOneException("No automaton in this let section.")


class LetCreator:
    """Creator class for adding and removing automaton from a LetSection."""

    def __init__(self) -> None:
        self._let_adder = LetAdder(self)  # type: ignore bad-argument-type

    def add_automaton(
        self,
        name: str | None = None,
        lhs: list[swan.LHSItem | str] | None = None,
        is_partial: bool = False,
    ) -> swan.StateMachine:
        """Create and add an automaton as equation of the LetSection.

        Parameters
        ----------
        name : str, optional
            The optional name of the automaton to create.
        lhs : List[swan.LHSItem | str] | None, optional
            List of LHS (left-hand side) items or None. Can be provided as string list for convenience.
        is_partial : bool, optional
            Flag indicating whether the LHS equation is partial or complete. Default is False.

        Returns
        -------
        StateMachine
            The created automaton.
        """
        from ansys.scadeone.core.swan import StateMachine, Identifier, EquationLHS, LHSItem, Luid

        if lhs is not None:
            lhs_items = []
            for item in lhs:
                if isinstance(item, str):
                    uuid = Identifier(item) if item != "_" else None
                    lhs_items.append(LHSItem(uuid))
                else:
                    lhs_items.append(item)
            equation_lhs = EquationLHS(lhs_items, is_partial)
        else:
            equation_lhs = None

        fsm = StateMachine(luid=Luid(name) if name else None, lhs=equation_lhs)
        self._let_adder.add_automaton(fsm)
        return fsm

    def remove_automaton(self, name: str) -> None:
        """Remove by name an automaton from the LetSection.

        Parameters
        ----------
            name : str
                 The name of the automaton to remove.

        Raises
        ------
        ValueError
            If the automaton name is not defined.
        """
        if name:
            self._let_adder.remove_automaton(name)
        else:
            raise ValueError("Automaton name is not defined")
