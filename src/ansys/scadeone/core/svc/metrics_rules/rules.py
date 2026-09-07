# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Type

from ansys.scadeone.core.model import Model
from ansys.scadeone.core.swan import SwanItem

from ansys.scadeone.core.svc.metrics_rules.common import Check


class RuleStatus(Enum):
    """Possible status values for a rule check"""

    #: The rule check succeeded.
    OK = auto()
    #: The rule check failed.
    FAILED = auto()
    #: An error occurred during the rule check.
    ERROR = auto()
    #: The rule does not apply to the checked object.
    NA = auto()


class RuleSeverity(Enum):
    """Possible severity values"""

    #: The rule is mandatory. If it fails, the model is not compliant with the rule set.
    MANDATORY = auto()
    #: The rule is recommended. If it fails, the model is compliant with the rule set,
    #: but it is recommended to fix it.
    REQUIRED = auto()
    #: The rule is advisory. If it fails, the model is compliant with the rule set,
    #: but it is recommended to fix it if possible.
    ADVISORY = auto()


@dataclass
class RuleResult:
    """
    Represents the result of a rule check.

    Attributes
    ----------
    status : RuleStatus
        The status of the rule check (OK, FAILED, ERROR, NA).
    message : str
        An message describing the result. By default, the message is set to an empty string.
    """

    status: RuleStatus
    message: str | None = None


class Rule(Check, ABC):
    """
    The Rule class is a representation of a Rule of the Scade One Rules Checker.
    A derived class adds a new Rule to the tool.
    """

    def __init__(
        self,
        id: str,
        label: str,
        category: str,
        severity: RuleSeverity,
        types: list[Type[SwanItem]] | None = None,
        description: str = "",
        parameters: str = "",
    ):
        """
        Registers a new rule to the Scade One Rules checker tool

        Parameters
        ----------
        id: str
            The unique identifier of the rule
        label: str
            The name of the rule
        category: str
            The name of the category to which the rule belongs
        severity: RuleSeverity
            The severity of the rule
        types: list[Type[SwanItem]]
            A list of Scade One classes. The rule is checked for each item which is an instance of those classes,
            or of one of their derived classes. If not provided, the rule is checked for all items.
        description: str, optional
            A text describing the rule.
        parameters: str, optional
            A text describing the parameters of the rule, if any.
        """
        super().__init__(
            id=id, label=label, category=category, types=types, description=description
        )
        self.severity = severity
        self.message = ""
        self.parameters = parameters

    def on_start(self, model: Model) -> RuleResult:
        """
        Called before any call to on_check or before_checking_subtree is done. Not called if no item matches the rule.

        Parameters
        ----------
        model: Model
            The model on which rules are checked

        Returns
        -------
        RuleResult
            RuleStatus.OK, or RuleStatus.ERROR if an error occurred, leading the whole Rules Checker computation
            to fail.
        """
        return RuleResult(RuleStatus.OK)

    def before_checking_subtree(self, item: SwanItem) -> RuleResult:
        """
        Called after 'on_start' and before 'on_check'. First 'before_checking_subtree' is called for that item, then
        recursively for each item it contains. Finally on_check is called on the item to return the rule check result.
        There is no default implementation provided but implementers must return either Rule.OK, or Rule.ERROR if an
        error occurred, leading the whole Rules checker computation to fail.

        Parameters
        ----------
        item: SwanItem
            The Swan item on which the rule is applicable or a direct or indirect sub-element it contains

        Returns
        -------
        RuleResult
            RuleStatus.OK, or RuleStatus.ERROR if an error occurred, leading the whole Rules checker
            computation to fail.

        Raises
        ------
        NotImplementedError
            If the method is not redefined by the derived class.
        """
        raise NotImplementedError("No default implementation")

    def on_check(self, item: SwanItem) -> RuleResult:
        """
        Checks whether the rule succeeds.
        Returns RuleStatus.OK if the rule succeeds, Rule.FAILED if the rule fails,

        Parameters
        ----------
        item: SwanItem
                The Swan item on which the rule is checked

        Returns
        -------
        RuleResult
                RuleStatus.OK if the rule succeeds, RuleStatus.FAILED if the rule fails, RuleStatus.NO_RULE if the rule
                does not apply to the item, and Rule.ERROR if an error occurred, leading the whole Rules checker
                computation to fail.
        """
        return RuleResult(RuleStatus.OK)

    def after_checking_subtree(self, item: SwanItem) -> RuleResult:
        """
        Called after 'on_check' (independently of its result) and before 'on_stop'. This method is called from the item
        and recursively called for all sub-elements it contains directly or indirectly. There is no default implementation
        provided but implementers are invited to return Rule.OK, or Rule.ERROR if an error occurred, leading the whole
        Rules checker computation to fail.

        Parameters
        ----------
        item: SwanItem
            The Swan item on which the rule has been applied or a direct or indirect sub-element it contains

        Returns
        -------
        RuleResult
            RuleStatus.OK, or RuleStatus.ERROR if an error occurred, leading the whole Rules checker
            computation to fail.

        Raises
        ------
        NotImplementedError
            If the method is not redefined by the derived class.
        """
        raise NotImplementedError("No default implementation")

    def on_stop(self) -> RuleResult:
        """
        Called once all checks have been done. Not called if no item matches the rule.

        Returns
        -------
        RuleResult
            RuleStatus.OK, or RuleStatus.ERROR if an error occurred, leading the whole Rules checker
            computation to fail.
        """
        return RuleResult(RuleStatus.OK)
