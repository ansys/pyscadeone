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

import pytest
import test_tools

from ansys.scadeone.core import ScadeOneException
from ansys.scadeone.core.swan import LHSItem, Identifier
from ansys.scadeone.core.svc import swan_printer as printer


@pytest.fixture
def let_section(parser):
    code = test_tools.versioned_swan_str(
        """
            node operator0 (a: int32; b: int32)
              returns (c: int16)
              {
                let c = (a:>int16) * 256 + (b:>int16);
              }
            """,
        "module0",
    )
    body = parser.module_body(code)
    op0 = body.operator_definitions[0]
    return op0.body.sections[0]


@pytest.fixture
def let_section_with_automata(parser):
    code = test_tools.versioned_swan_str(
        """
            node operator0 (a: int32; b: int32)
              returns (c: int16)
              {
                let c = (a:>int16) * 64;
                 automaton $a0;
                 _, .. : automaton $a1;
                 foo, bar, joe, _, .. : automaton $a2;
                 () : automaton $a3;
              }
            """,
        "module0",
    )
    body = parser.module_body(code)
    op0 = body.operator_definitions[0]
    return op0.body.sections[0]


class TestLetCreator:
    def test_add_automaton_with_default(self, let_section) -> None:
        automaton = let_section.add_automaton()
        assert not automaton.luid
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   automaton;"
        assert output == oracle

    def test_add_automaton_without_lhs(self, let_section) -> None:
        automaton = let_section.add_automaton("automaton0")
        assert automaton.luid.value == "automaton0"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   automaton $automaton0;"
        assert output == oracle

    def test_add_automaton_without_lhs_and_partial(self, let_section) -> None:
        automaton = let_section.add_automaton(
            "automaton0", is_partial=True
        )  # is_partial has no effect in this test
        assert automaton.luid.value == "automaton0"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   automaton $automaton0;"
        assert output == oracle

    def test_add_automaton_with_empty_lhs(self, let_section) -> None:
        automaton = let_section.add_automaton("automaton1", [])
        assert automaton.luid.value == "automaton1"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   () : automaton $automaton1;"
        assert output == oracle

    def test_add_automaton_with_empty_lhs_and_partial(self, let_section) -> None:
        automaton = let_section.add_automaton(
            "automaton1", [], True
        )  # is_partial has no effect in this test
        assert automaton.luid.value == "automaton1"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   () : automaton $automaton1;"
        assert output == oracle

    @pytest.mark.parametrize("lhs_item", [["_"], [LHSItem(None)]])
    def test_add_automaton_with_only_underscore_lhs(self, let_section, lhs_item) -> None:
        automaton = let_section.add_automaton("automaton2", lhs_item)
        assert automaton.luid.value == "automaton2"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   _ : automaton $automaton2;"
        assert output == oracle

    @pytest.mark.parametrize("lhs_item", [["_"], [LHSItem(None)]])
    def test_add_automaton_with_only_partial_underscore_lhs(self, let_section, lhs_item) -> None:
        automaton = let_section.add_automaton("automaton2", lhs_item, True)
        assert automaton.luid.value == "automaton2"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   _, .. : automaton $automaton2;"
        assert output == oracle

    @pytest.mark.parametrize(
        "lhs_item",
        [
            ["foo", "bar", "_", "joe"],
            [
                LHSItem(Identifier("foo")),
                LHSItem(Identifier("bar")),
                LHSItem(None),
                LHSItem(Identifier("joe")),
            ],
            [LHSItem(Identifier("foo")), "bar", "_", LHSItem(Identifier("joe"))],  # mix
        ],
    )
    def test_add_automaton_with_lhs(self, let_section, lhs_item) -> None:
        automaton = let_section.add_automaton("automaton3", lhs_item)
        assert automaton.luid.value == "automaton3"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   foo, bar, _, joe : automaton $automaton3;"
        assert output == oracle

    @pytest.mark.parametrize(
        "lhs_item",
        [
            ["_", "foo", "bar", "joe"],
            [
                LHSItem(None),
                LHSItem(Identifier("foo")),
                LHSItem(Identifier("bar")),
                LHSItem(Identifier("joe")),
            ],
            ["_", LHSItem(Identifier("foo")), "bar", LHSItem(Identifier("joe"))],  # mix
        ],
    )
    def test_add_automaton_with_partial_lhs(self, let_section, lhs_item) -> None:
        automaton = let_section.add_automaton("automaton3", lhs_item, True)
        assert automaton.luid.value == "automaton3"
        assert len(let_section.equations) == 2
        output = printer.swan_to_str(let_section)
        oracle = "let\n   c = (a :> int16) * 256 + (b :> int16);\n   _, foo, bar, joe, .. : automaton $automaton3;"
        assert output == oracle

    def test_remove_automaton(self, let_section_with_automata) -> None:
        assert len(let_section_with_automata.equations) == 5
        let_section_with_automata.remove_automaton("a0")
        let_section_with_automata.remove_automaton("a1")
        let_section_with_automata.remove_automaton("a2")
        let_section_with_automata.remove_automaton("a3")
        assert len(let_section_with_automata.equations) == 1

    def test_remove_automaton_with_undefined_name(self, let_section_with_automata) -> None:
        with pytest.raises(ValueError) as e:
            let_section_with_automata.remove_automaton(None)
        assert len(e.value.args) == 1
        assert "Automaton name is not defined" == str(e.value.args[0])

    def test_remove_automaton_when_nothing_to_remove(self, let_section) -> None:
        with pytest.raises(ScadeOneException) as e:
            let_section.remove_automaton("a1")
        assert len(e.value.args) == 1
        assert "No automaton in this let section." == str(e.value.args[0])

    def test_remove_not_existing_automaton(self, let_section_with_automata) -> None:
        with pytest.raises(ScadeOneException) as e:
            let_section_with_automata.remove_automaton("not_existing")
        assert len(e.value.args) == 1
        assert "Automaton not_existing not found." == str(e.value.args[0])

    def test_remove_automaton_when_anonymous_automaton_exists(
        self, let_section_with_automata
    ) -> None:
        # extra automaton without name arg
        let_section_with_automata.add_automaton()
        assert len(let_section_with_automata.equations) == 6
        let_section_with_automata.remove_automaton("a0")
        assert len(let_section_with_automata.equations) == 5
