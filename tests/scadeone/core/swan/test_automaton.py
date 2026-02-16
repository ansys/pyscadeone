# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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
Tests of automaton features
"""

# cSpell: ignore keepends Decel

from typing import cast
from pathlib import Path
import logging
import pytest
import difflib

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model.loader import SwanParser
from ansys.scadeone.core.model.model import Model
import ansys.scadeone.core.swan as Swan
from ansys.scadeone.core.common.storage import SwanString
from tools.utils import swan_to_xml, log_diff  # noqa: F401

logging.basicConfig(level=logging.DEBUG)

parser = SwanParser(logging.getLogger("pyofast"))


@pytest.fixture(scope="session")
def position_model(app: ScadeOne) -> Model:
    project = app.load_project(TestAutomaton.PositionProject)
    assert project is not None
    return app.model


class TestAutomaton:
    PositionProject = "examples/models/Position/Position.sproj"

    @staticmethod
    def _get_position_automaton(model: Model) -> Swan.StateMachine:
        assert model is not None
        root = model.operator_definitions[0]
        diagram = root.diagrams[0]
        automaton = cast(Swan.StateMachineBlock, diagram.objects[0]).state_machine
        assert automaton is not None
        return automaton

    def test_position_load(self, position_model: Model, tmp_path: Path) -> None:
        """Basic automaton test on Position model"""
        automaton = TestAutomaton._get_position_automaton(position_model)
        xml_str = swan_to_xml(automaton)
        (tmp_path / "position_automaton.xml").write_text(xml_str, encoding="utf-8")

        stop = automaton.get_state("Stop")
        assert stop is not None
        assert stop.weak_transitions is not None
        assert len(stop.weak_transitions) == 0
        assert stop.strong_transitions is not None
        assert len(stop.strong_transitions) == 2

        targets = stop.get_targets()
        assert {str(t.id) for t in targets} == {"Up", "Down", "Left", "Right", "Center"}

    def test_position_print(self, position_model: Model, tmp_path: Path) -> None:
        """Print automaton to text file"""
        automaton = TestAutomaton._get_position_automaton(position_model)
        text_str = Swan.swan_to_str(cast(Swan.SwanItem, automaton.owner))
        # Check differences with original file
        # In original file, the let statement is in one line, while here it is split in multiple lines.
        source = Path(TestAutomaton.PositionProject).parent / "assets/Point.swan"
        original_lines = [line[4:] for line in source.read_text().splitlines()][11:68]
        diff = difflib.unified_diff(
            original_lines,
            text_str.splitlines(),
            n=0,
            lineterm="",
        )
        diff_text = "\n".join(list(diff)[3:])
        # log_diff(actual=text_str, expected=original_lines, winmerge=False)
        assert (
            diff_text
            == "-      (let x = 0; y = 0;\n+      (let\n+          x = 0;\n+          y = 0;"
        ), "Unexpected difference in printed automaton."

    CC_text = """\
node CruiseControl (On: bool;
                    Off: bool;
                    Resume: bool;
                    Set: bool;
                    QuickAccel: bool;
                    QuickDecel: bool;
                    Accel: tPercent;
                    Brake: tPercent;
                    Speed: tSpeed;)
  returns (CruiseSpeed: tSpeed default = ZEROSPEED;
           ThrottleCmd: tPercent default = Accel;
           CruiseState: TCruiseState default = OFF;)
{
  let automaton $SM1
        initial state Off :
          unless
          if (On)
          restart Enabled;
        state Enabled :
          unless
          if (Off)
          restart Off;
          var
             local_CruiseSpeed: tSpeed;
             tmp_: tSpeed;
          let
             automaton $SM2
               initial state Active :
                 unless
                 if (FloatGT (Brake, PEDALSMIN, TOL))
                 restart Interrupt;
                 var
                    StdbyCondition: bool;
                 let
                    automaton $SM3
                      initial state On :
                        unless
                        if (StdbyCondition)
                        restart StandBy;
                        let
                           ThrottleCmd = CruiseRegulation (local_CruiseSpeed, Speed);
                           CruiseState = ON;
                      state StandBy :
                        unless
                        if (not StdbyCondition)
                        restart On;
                        let CruiseState = STDBY;;
                    StdbyCondition = FloatGT (Speed, SPEEDREGMAX, TOL) or FloatGT (Accel, PEDALSMIN, TOL) or FloatLT (Speed, SPEEDMIN, TOL);
               state Interrupt :
                 unless
                 if (Resume)
                 restart Active;
                 let CruiseState = INT;;
             CruiseSpeed = tmp_;
             tmp_ = CruiseSpeedMgt (Set, QuickAccel, QuickDecel, Speed);
             local_CruiseSpeed = tmp_;;
}
"""

    def test_cc(self, tmp_path):
        code = SwanString(self.CC_text, "CC text")
        swan_obj = parser.operator_decl_or_def(code)
        assert swan_obj is not None
        res = Swan.swan_to_str(swan_obj)
        if res != self.CC_text:
            log_diff(actual=res, expected=self.CC_text, winmerge=False)
            assert False, "set log_merge=True in log_diff() to see differences."
