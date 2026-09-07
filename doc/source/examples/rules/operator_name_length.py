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

from ansys.scadeone.core import swan
from ansys.scadeone.core.svc.metrics_rules.rules import Rule, RuleSeverity, RuleResult, RuleStatus


class OperatorNamePathLength(Rule):
    def __init__(
        self,
        id: str = "SCADEONE_R001",
        label: str = "Operator Name Path Length Check",
        description: str = "This rule checks that the full path of an operator declaration does not exceed a certain length.",
        category: str = "Naming",
        severity: RuleSeverity = RuleSeverity.MANDATORY,
        types: list[type[swan.SwanItem]] | None = [swan.OperatorDeclarationDefinitionBase],
        parameters: str = "max=50",
    ):
        super().__init__(
            id=id,
            label=label,
            category=category,
            severity=severity,
            types=types,
            description=description,
            parameters=parameters,
        )

    def on_check(self, item: swan.SwanItem) -> RuleResult:
        if not self.parameters:
            return RuleResult(
                status=RuleStatus.ERROR, message="Maximum length of operator namepath is required."
            )
        max_len = self._parse_parameters()
        if len(item.get_full_path()) > max_len:
            return RuleResult(RuleStatus.FAILED, "Operator path length exceeds maximum.")
        return RuleResult(RuleStatus.OK)

    def _parse_parameters(self):
        try:
            key, value = self.parameters.split("=")
            if key.strip() != "max":
                raise ValueError("Invalid parameter key. Expected 'max'.")
            return int(value.strip())
        except Exception as e:
            raise ValueError(
                f"Invalid parameters format: {self.parameters}. Expected format: 'max=<int>'. Error: {e}"
            )
