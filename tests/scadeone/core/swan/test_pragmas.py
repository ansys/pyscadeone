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

import pytest

from ansys.scadeone.core.swan import Pragma
from ansys.scadeone.core.swan.pragmas import (
    DiagramPragmaParser,
    Coordinates,
    Coordinate,
    Position,
)


class TestPragmas:
    def test_pragma_filter(self):
        pragma1 = Pragma('#pragma diagram {"xy":"h-36150;v54737"} #end')
        pragma2 = Pragma('#pragma diagram {"xy":"h-36150;v54737"} #end')
        pragmas = [pragma1, pragma2]
        assert len(Pragma.filter(pragmas, "diagram")) == 2

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            (
                '#pragma diagram {"xy":"h-36150;v54737","wh":"16000;3200","dir":"nw","orient":"H"} #end',
                '{"xy":"h-36150;v54737","wh":"16000;3200","dir":"nw","orient":"H"}',
            ),
            (
                '#pragma diagram {"wp":"v15505|#1376 h14300[#1379, v13695 #6]"} #end',
                '{"dir":"ne","wp":"v15505|#1376 h14300 [#1379, v13695 #6]"}',
            ),
        ],
    )
    def test_diagram_pragma(self, pragma_str, expected):
        pragma = Pragma(pragma_str)
        assert str(pragma) == pragma_str
        assert str(pragma.diagram) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            ('{"xy":"h-36150;v54737"}', "h-36150;v54737"),
            ('{"xy":"H-36150;v54737"}', "H-36150;v54737"),
            ('{"xy":"h-36150;V54737"}', "h-36150;V54737"),
            ('{"xy":"H-36150;V54737"}', "H-36150;V54737"),
        ],
    )
    def test_coordinates_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.coordinates) == expected

    def test_size_parser(self):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse('{"wh":"16000;3200"}')
        assert str(pragma_diag.size) == "16000;3200"

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            ('{"dir":"ne"}', "ne"),
            ('{"dir":"nw"}', "nw"),
            ('{"dir":"es"}', "es"),
            ('{"dir":"en"}', "en"),
            ('{"dir":"se"}', "se"),
            ('{"dir":"sw"}', "sw"),
            ('{"dir":"ws"}', "ws"),
            ('{"dir":"wn"}', "wn"),
        ],
    )
    def test_direction_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.direction) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            ('{"orient":"H"}', "H"),
            ('{"orient":"V"}', "V"),
        ],
    )
    def test_orientation_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.orientation) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            (
                '{"wp":"v15505|#1376 h14300 [#1379, v13695 #6]"}',
                "v15505|#1376 h14300 [#1379, v13695 #6]",
            ),
            (
                '{"wp": "#1322 h-7267 [v11635 [v11635 [v16560 [#1078, v-6410 #1070], #8], #1302], #4]"}',
                "#1322 h-7267 [v11635 [v11635 [v16560 [#1078, v-6410 #1070], #8], #1302], #4]",
            ),
        ],
    )
    def test_wire_info_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.wire_info) == expected

    @pytest.mark.parametrize(
        "pragma_str, expected",
        [
            (
                '{"tp":"h20000;v50|#0 h500 h5781;v10600 h0;v-2000|h-2900;v15925 h2000;v0 h5621 h-20000;v7600|#1"}',
                "h20000;v50|#0 h500 h5781;v10600 h0;v-2000|h-2900;v15925 h2000;v0 h5621 h-20000;v7600|#1",
            )
        ],
    )
    def test_arrow_info_parser(self, pragma_str, expected):
        parser = DiagramPragmaParser()
        pragma_diag = parser.parse(pragma_str)
        assert str(pragma_diag.arrow_info) == expected


class TestCoordinates:
    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (
                Coordinate(Position.RELATIVE, 10),
                Coordinate(Position.ABSOLUTE, -20),
                "h10;V-20",
            ),
            (None, Coordinate(Position.ABSOLUTE, -20), "V-20"),
            (Coordinate(Position.RELATIVE, 10), None, "h10"),
            (None, None, ""),
        ],
    )
    def test_str(self, x, y, expected):
        coordinates = Coordinates(x, y)
        assert str(coordinates) == expected
