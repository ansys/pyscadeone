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

"""
This example demonstrates the use of a visitor (see: :ref:`ref_swan_model_visitor`).

The :py:class:`ReferenceVisitor` visitor is used to explore the
"QuadFlightControl" example. This visitor finds for each operator:

- which operators call it
- which operators are called by

The functions :py:func:`caller_stat` and :py:func:`called_stat` print calls information
for a given operator.

Caller stats:

>>> caller_stat('QuadFlightControl::QuadFlightControl')
QuadFlightControl::QuadFlightControl calls:
  QuadFlightControl::MotorControl: called 1 time(s)
  QuadFlightControl::FlightControl: called 1 time(s)

Called stats:

>>> called_stat('QuadUtils::LimiterUnSymmetrical')
QuadUtils::LimiterUnSymmetrical called by:
  QuadFlightControl::MotorControl: called 4 time(s)
  QuadFlightControl::PitchRollFilter: called 1 time(s)

"""

import logging
from pathlib import Path
from typing import cast, Union

from ansys.scadeone.core.scadeone import ScadeOne
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor
import ansys.scadeone.core.swan as swan

# Update according to your installation
s_one_install = Path(r"C:\Scade One")

quad_flight_project = (
    s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
)

app = ScadeOne(install_dir=s_one_install)
model = app.load_project(quad_flight_project).model

model.load_all_modules()

# Logging settings.
logging.basicConfig()
logger = logging.getLogger("visitor")
logger.setLevel(logging.ERROR)
app.logger.logger.setLevel(logging.ERROR)


class ReferenceVisitor(SwanVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._current_op: swan.Operator = None
        self._called = {}
        self._callers = {}

    def get_caller(self, name):
        """Information for calling operator 'name'"""
        return self._callers.get(name, None)

    def get_called(self, name):
        """Information for called operator 'name'"""
        return self._called.get(name, None)

    def visit_Operator(
        self, swan_obj: swan.Operator, owner: Union[swan.Any, None], property: Union[str, None]
    ) -> None:
        self._current_op = swan_obj
        self._callers[swan_obj.get_full_path()] = {}
        super().visit_Operator(swan_obj, owner, property)
        self._current_op = None

    def visit_PathIdOpCall(
        self, swan_obj: swan.PathIdOpCall, owner: Union[swan.Any, None], property: Union[str, None]
    ) -> None:
        if self._current_op is None:
            return
        name = str(swan_obj.path_id)
        op = self._current_op.body.get_declaration(name)
        if op is None:
            logger.debug(f"Declaration of {name} not found")
            return
        self._add_reference(cast(swan.Operator, op).get_full_path())

    def _add_reference(self, called_operator):
        """Add information for 'called_operator' with
        respect to current operator"""
        # calls of used_operator
        current_op_name = self._current_op.get_full_path()
        if called_operator not in self._called:
            self._called[called_operator] = {}
        if current_op_name not in self._called[called_operator]:
            self._called[called_operator][current_op_name] = 0
        self._called[called_operator][current_op_name] += 1
        # calls of current operator
        if called_operator not in self._callers[current_op_name]:
            self._callers[current_op_name][called_operator] = 0
        self._callers[current_op_name][called_operator] += 1


visitor = ReferenceVisitor()
for module in model.modules:
    visitor.visit(module)


def caller_stat(caller):
    """Print which operators are called by 'caller' operator."""
    stat = visitor.get_caller(caller)
    print(f"{caller} calls:")
    for k, v in stat.items():
        print(f"  {k}: called {v} time(s)")


def called_stat(called):
    """Print which operators call 'called' operator."""
    print(f"{called} called by:")
    stat = visitor.get_called(called)
    for k, v in stat.items():
        print(f"  {k}: called {v} time(s)")


if __name__ == "__main__":
    import doctest

    (failure_count, test_count) = doctest.testmod()
    # nothing printed out if success
