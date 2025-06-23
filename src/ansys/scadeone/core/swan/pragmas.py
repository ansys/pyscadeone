# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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
from enum import Enum, auto
from functools import cached_property
import json
import re
from typing import TYPE_CHECKING, List, Optional, Union, cast

from lark import Lark, Transformer

if TYPE_CHECKING:
    from ansys.scadeone.core.swan import Lunum


class PragmaBase:
    """Base class for objects with pragmas."""

    def __init__(self, pragmas: Optional[List["Pragma"]] = None) -> None:
        self._pragmas = pragmas if pragmas else []

    @property
    def pragmas(self) -> List["Pragma"]:
        """List of pragmas."""
        return self._pragmas

    def pragmas_str(self) -> str:
        """Return a string with all pragmas."""
        pragmas = " ".join(str(p) for p in self.pragmas)
        return pragmas


class Pragma:
    """Pragma structure."""

    def __init__(self, pragma: str) -> None:
        self._pragma = pragma

    @property
    def pragma(self) -> str:
        """Return full pragma string."""
        return self._pragma

    @cached_property
    def diagram(self) -> "DiagramPragma":
        """Return the pragma diagram."""
        parser = PragmaParser()
        parser.parse(self._pragma)
        return parser.diagram

    @staticmethod
    def filter(pragmas: List["Pragma"], key: str, with_key: bool = True) -> List["Pragma"]:
        """Filters a list of pragmas with/without a given key.

        Parameters
        ----------
        pragmas : List[Pragma]
            List of pragmas.
        key : str
            Key to filter.
        with_key : bool, optional
            If True, return pragmas with the given key, otherwise without the key, by default True.

        Returns
        -------
        List[Pragma]
            List of pragmas with the given key.
        """
        res = []
        for p in pragmas:
            m = PragmaParser.extract(p.pragma)
            if m and (with_key == (m[0] == key)):
                res.append(p)
        return res

    def __str__(self) -> str:
        return self._pragma


class DiagramPragma:
    """The diagram information of a graphical object."""

    def __init__(self) -> None:
        self._coordinates = None
        self._size = None
        self._direction = None
        self._orientation = None
        self._wire_info = None
        self._arrow_info = None

    @property
    def coordinates(self) -> "Coordinates":
        """Return the diagram coordinates."""
        return self._coordinates

    @property
    def size(self) -> "Size":
        """Return the diagram size."""
        return self._size

    @property
    def direction(self) -> "Direction":
        """Return the diagram direction."""
        return self._direction

    @property
    def orientation(self) -> "Orientation":
        """Return the diagram orientation."""
        return self._orientation

    @property
    def wire_info(self) -> "PathInfo":
        """Return the diagram wire info."""
        return self._wire_info

    @property
    def arrow_info(self) -> "PathInfo":
        """Return the diagram arrow info."""
        return self._arrow_info

    def __str__(self):
        params = []
        if self._coordinates:
            params.append(f'"xy":"{self._coordinates}"')
        if self._size:
            params.append(f'"wh":"{self._size}"')
        if self._direction:
            params.append(f'"dir":"{self._direction}"')
        if self._orientation:
            params.append(f'"orient":"{self._orientation}"')
        if self._wire_info:
            params.append(f'"wp":"{self._wire_info}"')
        if self._arrow_info:
            params.append(f'"tp":"{self._arrow_info}"')
        if len(params) == 0:
            return ""
        return f"{{{','.join(params)}}}"


def _create_parser(grammar: str, start: str, transformer: Transformer) -> Lark:
    """Create a Lark parser with the given grammar, start and transformer. LALR parser is used."""
    return Lark(grammar, start=start, parser="lalr", transformer=transformer)


class PragmaParser:
    """Parser for pragma.

    This is the list of supported pragmas:
    - diagram
    """

    PragmaRE = re.compile(r"#pragma\s+(?P<key>\w+)\s(?P<val>.*)#end", re.DOTALL)
    _instance = None

    def __init__(self) -> None:
        self._diagram = None

    def __new__(cls, *args, **kwargs) -> "PragmaParser":
        if not cls._instance:
            cls._instance = super(PragmaParser, cls).__new__(cls)
        return cls._instance

    @property
    def diagram(self) -> "DiagramPragma":
        """Return the diagram pragma."""
        return self._diagram

    def parse(self, pragma: str) -> None:
        """Parse pragma.
        This is the list of supported pragmas:
        - diagram

        Parameters
        ----------
            pragma : str
                Pragma string defined in SO-SRS-001 V2.1, section 1.2.5, [S1-203]
        """
        if not pragma:
            return
        pragma_tuple = self.extract(pragma)
        if not pragma_tuple:
            return
        key, value = pragma_tuple
        if key == "diagram":
            self._diagram = DiagramPragmaParser().parse(value)
            if self._diagram and not self._diagram.direction:
                self._diagram._direction = Direction(DirectionType.NORTH_EAST)

    @staticmethod
    def extract(pragma: str) -> Union[tuple[str, str], None]:
        """Extract pragma information as a tuple
        if pragma is valid, namely: #pragma key value#end.

        Returns
        -------
            tuple | None
                The Tuple (*pragma name*, *pragma value*) if pragma is valid, None else.
        """
        m = PragmaParser.PragmaRE.match(pragma)
        if not m:
            return None
        return m["key"], m["val"].strip()


class DiagramPragmaParser:
    """Parser for diagram pragma.
    The different parsers implement SO-SRS-001 V2.1, section 5.5: Graphical Information
    """

    _instance = None

    def __init__(self) -> None:
        self._coordinates_parser = self._create_coordinate_parser()
        self._size_parser = self._create_size_parser()
        self._direction_parser = self._create_direction_parser()
        self._orientation_parser = self._create_orientation_parser()
        self._path_info_parser = self._create_path_info_parser()

    def __new__(cls, *args, **kwargs) -> "DiagramPragmaParser":
        if not cls._instance:
            cls._instance = super(DiagramPragmaParser, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def _create_coordinate_parser() -> Lark:
        """Create the parser for coordinates.
        Coordinates are defined as "[Hh]x;[Vv]y" where:

        - H,V: Absolute position
        - h,v: Relative position
        - x,y: Coordinate values

        Returns
        -------
        Lark
            A coordinates' parser.
        """
        grammar = r"""
                    coordinates: x ";" y
                    x: horizontal number
                    y: vertical number
                    horizontal: absolute_horizontal | relative_horizontal
                    vertical: absolute_vertical | relative_vertical
                    absolute_horizontal: "H"
                    relative_horizontal: "h"
                    absolute_vertical: "V"
                    relative_vertical: "v"
                    number: /-?\d+/
                    %import common.WS
                    %ignore WS
                    """
        return _create_parser(grammar, start="coordinates", transformer=CoordinateTransformer())

    @staticmethod
    def _create_size_parser() -> Lark:
        """Create the parser for size.
        Size is defined as "width;height" where:

        - width: Width value
        - height: Height value

        Returns
        -------
        Lark
            A size parser.
        """
        grammar = r"""
                    size: width ";" height
                    width: number
                    height: number
                    number: /-?\d+/
                    %import common.WS
                    %ignore WS
                    """
        return _create_parser(grammar, start="size", transformer=SizeTransformer())

    @staticmethod
    def _create_direction_parser() -> Lark:
        """Create the parser for a direction.
        Direction is defined as "ne|nw|es|en|se|sw|ws|wn" where:

        - ne: North east
        - nw: North west
        - es: East south
        - en: East north
        - se: South east
        - sw: South west
        - ws: West south
        - wn: West north

        Returns
        -------
        Lark
            A direction parser.
        """
        grammar = r"""
                    direction: north_east | north_west | east_south | east_north | south_east | south_west | west_south | west_north
                    north_east: "ne"
                    north_west: "nw"
                    east_south: "es"
                    east_north: "en"
                    south_east: "se"
                    south_west: "sw"
                    west_south: "ws"
                    west_north: "wn"
                    %import common.WS
                    %ignore WS
                    """
        return _create_parser(grammar, start="direction", transformer=DirectionTransformer())

    @staticmethod
    def _create_orientation_parser() -> Lark:
        """Create the parser for orientation.
        Orientation is defined as "H|V" where:

        - H: Horizontal
        - V: Vertical

        Returns
        -------
        Lark
            An orientation parser.
        """
        grammar = r"""
                    orientation: horizontal | vertical
                    horizontal: "H"
                    vertical: "V"
                    %import common.WS
                    %ignore WS
                    """
        return _create_parser(grammar, start="orientation", transformer=OrientationTransformer())

    @staticmethod
    def _create_path_info_parser() -> Lark:
        """Create the parser for path info.
        Path info is defined as "w_anchor path" where:

        - w_anchor: LUNUM
                    | COORD '|' LUNUM
                    | coordinates '|' LUNUM
                    | coordinates
        - path: moves w_anchor
                | moves branch
        - moves: /* empty */
                | moves move
        - move: COORD
                | COORD '|' coordinates
                | coordinates '|' coordinates
                | coordinates
        - coordinates: x ';' y
        - branch: '[' path_list ']'
        - path_list: path_list ',' path

        Returns
        -------
        Lark
            A path info parser.
        """
        grammar = r"""
                    path_info: w_anchor path
                    w_anchor: LUNUM
                        | (x | y | coordinates) "|" LUNUM
                        | coordinates
                    path: move* w_anchor | move* branch
                    coordinates: x ";" y
                    x: absolute_horizontal | relative_horizontal SIGNED_INT
                    y: absolute_vertical | relative_vertical SIGNED_INT
                    absolute_horizontal: "H"
                    relative_horizontal: "h"
                    absolute_vertical: "V"
                    relative_vertical: "v"
                    move: (x | y | coordinates)
                        | fork_coordinates
                    fork_coordinates: (x | y | coordinates) "|" coordinates
                    branch: "[" path_list "]"
                    path_list: (path ",")* path
                    LUNUM: "#" DIGIT10+
                    DIGIT10: /[0-9]/
                    %import common.WS
                    %import common.SIGNED_INT
                    %ignore WS
                    """
        return _create_parser(grammar, start="path_info", transformer=PathInfoTransformer())

    def parse(self, params: str) -> Union["DiagramPragma", None]:
        """Parse pragma diagram.

        Parameters
        ----------
            params : str
                Pragma diagram parameters.
                This is a string that contains a JSON expression with the following properties:

                - "xy": Coordinates
                - "wh": Size
                - "dir": Direction
                - "orient": Orientation
                - "wp": Wire path
                - "tp": Arrow path

            Each property's value is parsed by the corresponding parser.

        Returns
        -------
            DiagramPragma | None
                The parsed pragma diagram or None if params is empty.
        """
        if not params:
            return None
        params = json.loads(params)
        if not isinstance(params, dict):
            from ansys.scadeone.core import ScadeOneException

            raise ScadeOneException(f"Pragma diagram must be a dictionary: {params}")
        pragma_diag = DiagramPragma()
        if "xy" in params:
            pragma_diag._coordinates = cast(
                Coordinates, self._coordinates_parser.parse(params["xy"])
            )
        if "wh" in params:
            pragma_diag._size = cast(Size, self._size_parser.parse(params["wh"]))
        if "dir" in params:
            pragma_diag._direction = cast(Direction, self._direction_parser.parse(params["dir"]))
        if "orient" in params:
            pragma_diag._orientation = cast(
                Orientation, self._orientation_parser.parse(params["orient"])
            )
        if "wp" in params:
            pragma_diag._wire_info = cast(PathInfo, self._path_info_parser.parse(params["wp"]))
        if "tp" in params:
            pragma_diag._arrow_info = cast(PathInfo, self._path_info_parser.parse(params["tp"]))
        return pragma_diag


class CoordinateTransformer(Transformer):
    """Coordinate transformer.
    Transform the parser tree into Coordinates."""

    @staticmethod
    def coordinates(items) -> "Coordinates":
        """Return the coordinates.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The x coordinate
            - The y coordinate

        Returns
        -------
        Coordinates
            The object coordinates (diagram object, states or Active if/when blocks).
        """
        return Coordinates(items[0], items[1])

    @staticmethod
    def x(items) -> "Coordinate":
        """Return the *x* coordinate.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The position of the x coordinate
            - The value of the x coordinate

        Returns
        -------
        Coordinate
            The x coordinate.
        """
        return Coordinate(items[0], items[1])

    @staticmethod
    def y(items) -> "Coordinate":
        """Return the *y* coordinate.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The position of the y coordinate
            - The value of the y coordinate

        Returns
        -------
        Coordinate
            The y coordinate.
        """
        return Coordinate(items[0], items[1])

    @staticmethod
    def horizontal(items) -> "Position":
        """Return the horizontal position.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The horizontal position (absolute or relative)

        Returns
        -------
        Position
            The horizontal position (absolute or relative).
        """
        return items[0]

    @staticmethod
    def vertical(items) -> "Position":
        """Return the vertical position.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The vertical position (absolute or relative)

        Returns
        -------
        Position
            The vertical position (absolute or relative).
        """
        return items[0]

    @staticmethod
    def absolute_horizontal(items) -> "Position":
        """Return an absolute position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects an absolute position for x.

        Returns
        -------
        Position
            Absolute x position.
        """
        return Position.ABSOLUTE

    @staticmethod
    def relative_horizontal(items) -> "Position":
        """Return a relative position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects a relative position for x.

        Returns
        -------
        Position
            Relative x position.
        """
        return Position.RELATIVE

    @staticmethod
    def absolute_vertical(items) -> "Position":
        """Return an absolute position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects an absolute position for y.

        Returns
        -------
        Position
            Absolute y position.
        """
        return Position.ABSOLUTE

    @staticmethod
    def relative_vertical(items) -> "Position":
        """Return a relative position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects a relative position for y.

        Returns
        -------
        Position
            Relative y position.
        """
        return Position.RELATIVE

    @staticmethod
    def number(items) -> int:
        """Return the coordinate value.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The coordinate value

        Returns
        -------
        int
            The coordinate value.
        """
        return int(items[0].value)


class SizeTransformer(Transformer):
    """Size transformer.
    Transform the parser tree into Size."""

    @staticmethod
    def size(items) -> "Size":
        """Return the size.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The width
            - The height

        Returns
        -------
        Size
            The object size.
        """
        return Size(items[0], items[1])

    @staticmethod
    def width(items) -> int:
        """Return the width.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The width value

        Returns
        -------
        int
            The object width value.
        """
        return items[0]

    @staticmethod
    def height(items) -> int:
        """Return the height.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The height value

        Returns
        -------
        int
            The object height value.
        """
        return items[0]

    @staticmethod
    def number(items) -> int:
        """Return the size value.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The size value

        Returns
        -------
        int
            The object size value.
        """
        return int(items[0].value)


class DirectionTransformer(Transformer):
    """Direction transformer.
    Transforms the parser tree into Direction."""

    @staticmethod
    def direction(items) -> "Direction":
        """Return the direction.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The direction value

        Returns
        -------
        Direction
            The object direction.
        """
        return Direction(items[0])

    @staticmethod
    def north_east(items) -> "DirectionType":
        """Return the north-east direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the north-east direction.

        Returns
        -------
        DirectionType
            The north-east direction
        """
        return DirectionType.NORTH_EAST

    @staticmethod
    def north_west(items) -> "DirectionType":
        """Return the north-west direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the north-west direction.

        Returns
        -------
        DirectionType
            The north-west direction
        """
        return DirectionType.NORTH_WEST

    @staticmethod
    def east_south(items) -> "DirectionType":
        """Return the east-south direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the east-south direction.

        Returns
        -------
        DirectionType
            The east-south direction
        """
        return DirectionType.EAST_SOUTH

    @staticmethod
    def east_north(items) -> "DirectionType":
        """Return the east-north direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the east-north direction.

        Returns
        -------
        DirectionType
            The east-north direction
        """
        return DirectionType.EAST_NORTH

    @staticmethod
    def south_east(items) -> "DirectionType":
        """Return the south-east direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the south-east direction.

        Returns
        -------
        DirectionType
            The south-east direction
        """
        return DirectionType.SOUTH_EAST

    @staticmethod
    def south_west(items) -> "DirectionType":
        """Return the south-west direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the south-west direction.

        Returns
        -------
        DirectionType
            The south-west direction
        """
        return DirectionType.SOUTH_WEST

    @staticmethod
    def west_south(items) -> "DirectionType":
        """Return the west-south direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the west-south direction.

        Returns
        -------
        DirectionType
            The west-south direction
        """
        return DirectionType.WEST_SOUTH

    @staticmethod
    def west_north(items) -> "DirectionType":
        """Return the west-north direction.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the west-north direction.

        Returns
        -------
        DirectionType
            The west-north direction
        """
        return DirectionType.WEST_NORTH


class OrientationTransformer(Transformer):
    """Orientation transformer.
    Transforms the parser tree into Orientation."""

    @staticmethod
    def orientation(items) -> "Orientation":
        """Return the orientation.

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The orientation value

        Returns
        -------
        Orientation
            The object orientation.
        """
        return Orientation(items[0])

    @staticmethod
    def horizontal(items) -> "OrientationType":
        """Return the horizontal orientation.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the horizontal orientation.

        Returns
        -------
        OrientationType
            The horizontal orientation
        """
        return OrientationType.HORIZONTAL

    @staticmethod
    def vertical(items) -> "OrientationType":
        """Return the vertical orientation.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects the vertical orientation.

        Returns
        -------
        OrientationType
            The vertical orientation
        """
        return OrientationType.VERTICAL


class PathInfoTransformer(Transformer):
    """Transforms the parser tree into PathInfo."""

    @staticmethod
    def path_info(items) -> "PathInfo":
        """Return the path info.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The wire anchor
            - The path

        Returns
        -------
        PathInfo
            The object path info.
        """
        return PathInfo(items[0], items[1])

    @staticmethod
    def w_anchor(items) -> "WireAnchor":
        """Return the wire anchor.

        Parameters
        ----------
        items : list
            List of items. This list could contain two items:
            - The LUNUM
            - The coordinates

        Returns
        -------
        WireAnchor
            The object wire anchor.
        """
        from ansys.scadeone.core.swan import Lunum

        lunum = None
        coordinates = None
        for item in items:
            if isinstance(item, Lunum):
                lunum = item
            elif isinstance(item, tuple):
                if item[0] == "x":
                    coordinates = Coordinates(item[1], None)
                else:
                    coordinates = Coordinates(None, item[1])
            elif isinstance(item, Coordinates):
                coordinates = item
        return WireAnchor(lunum, coordinates)

    @staticmethod
    def path(items) -> "WirePath":
        """Return the wire path.

        Parameters
        ----------
        items : list
            List of items. This list could contain three items:
            - The moves
            - The wire anchor
            - The branch

        Returns
        -------
        WirePath
            The object wire path.
        """
        moves = None
        w_anchor = None
        branch = None
        for item in items:
            if isinstance(item, Move):
                if not moves:
                    moves = []
                moves.append(item)
            if isinstance(item, WireAnchor):
                w_anchor = item
            if isinstance(item, Branch):
                branch = item
        return WirePath(moves, w_anchor, branch)

    @staticmethod
    def coordinates(items) -> "Coordinates":
        """Return the coordinates.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The *x* coordinate
            - The *y* coordinate

        Returns
        -------
        Coordinates
            The object coordinates.
        """
        return Coordinates(items[0][1], items[1][1])

    @staticmethod
    def x(items) -> tuple[str, "Coordinate"]:
        """Return the *x* coordinate.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The *x* position
            - The *x* value

        Returns
        -------
        tuple
            The *x* coordinate. The tuple is used to identify the *x* or *y* coordinate.
        """
        return "x", Coordinate(items[0], items[1].value)

    @staticmethod
    def y(items) -> tuple[str, "Coordinate"]:
        """Return the *y* coordinate.

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The *y* position
            - The *y* value

        Returns
        -------
        tuple
            The *y* coordinate. The tuple is used to identify the *x* or *y* coordinate.
        """
        return "y", Coordinate(items[0], items[1].value)

    @staticmethod
    def absolute_horizontal(items) -> "Position":
        """Return an absolute position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects an absolute position for *x*.

        Returns
        -------
        Position
            *x* is in absolute position.
        """
        return Position.ABSOLUTE

    @staticmethod
    def relative_horizontal(items) -> "Position":
        """Return a relative position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects a relative position for *x*.

        Returns
        -------
        Position
            *x* is in relative position.
        """
        return Position.RELATIVE

    @staticmethod
    def absolute_vertical(items) -> "Position":
        """Return an absolute position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects an absolute position for *y*.

        Returns
        -------
        Position
            *y* is in absolute position.
        """
        return Position.ABSOLUTE

    @staticmethod
    def relative_vertical(items) -> "Position":
        """Return a relative position.

        Parameters
        ----------
        items : list
            List of items. It's not used but needed for the parser.
            When the parser calls this method, it expects a relative position for *y*.

        Returns
        -------
        Position
            *y* is in relative position.
        """
        return Position.RELATIVE

    @staticmethod
    def move(items) -> "Move":
        """Returns the move.

        move: (x | y | coordinates) '|' coordinates

        Parameters
        ----------
        items : list
            List of items. This list only contains an item:
            - tuple: The *x* or *y* coordinate
            - The coordinates
            - The coordinates with fork coordinates

        Returns
        -------
        Move
            The object move.
        """
        move_coordinates = None
        if isinstance(items[0], tuple):
            if items[0][0] == "x":
                coordinates = Coordinates(items[0][1], None)
            else:
                coordinates = Coordinates(None, items[0][1])
            move_coordinates = MoveCoordinates(coordinates)
        elif isinstance(items[0], Coordinates):
            move_coordinates = MoveCoordinates(items[0])
        elif isinstance(items[0], MoveCoordinates):
            move_coordinates = items[0]
        return Move(move_coordinates)

    @staticmethod
    def fork_coordinates(items) -> "MoveCoordinates":
        """Return the coordinates with fork coordinates.

        fork_coordinates: (x | y | coordinates) '|' coordinates

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The coordinates
            - The fork coordinates
        """
        return MoveCoordinates(items[0], items[1])

    @staticmethod
    def branch(items) -> "Branch":
        """Return the branch.

        branch: '[' path_list ']'

        Parameters
        ----------
        items : list
            List of items. This list only contains one item:
            - The path list

        Returns
        -------
        Branch
            The object branch.
        """
        return Branch(items[0])

    @staticmethod
    def path_list(items) -> List["WirePath"]:
        """Return the path list.

        path_list: (path ',')* path

        Parameters
        ----------
        items : list
            List of items. This list contains the path list.

        Returns
        -------
        List[WirePath]
            The object path list.
        """
        return items

    @staticmethod
    def LUNUM(item) -> "Lunum":
        """Return the *LUNUM*.

        Parameters
        ----------
        item : str
            The *LUNUM* value.

        Returns
        -------
        Lunum
            The object *LUNUM*.
        """
        from ansys.scadeone.core.swan import Lunum

        return Lunum(item.value)

    @staticmethod
    def DIGIT10(item) -> str:
        """Return the *LUNUM* number.

        Parameters
        ----------
        item : str
            The *LUNUM* number.

        Returns
        -------
        str
            The object *LUNUM* number.
        """
        return item.value


class Coordinates:
    """*Coordinates* define a horizontal (*x*) and a vertical (*y*) position of a graphical object.

    *Coordinates* are specified as:

    .. code-block:: ebnf

        xy = COORD ";" COORD

    where:

    - :code:`COORD`: Coordinate *x* or *y* (see :py:class:`Coordinate`)

    *Coordinates* are used to define the position of the diagram object, states or Active if/when blocks.
    """

    def __init__(self, x: Optional["Coordinate"] = None, y: Optional["Coordinate"] = None) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> Union["Coordinate", None]:
        """Return the *x* coordinate."""
        return self._x

    @property
    def y(self) -> Union["Coordinate", None]:
        """Return the *y* coordinate."""
        return self._y

    def __str__(self) -> str:
        coordinates = []
        if self._x:
            position_str = "H" if self._x.position == Position.ABSOLUTE else "h"
            coordinates.append(f"{position_str}{self._x.value}")
        if self._y:
            position_str = "V" if self._y.position == Position.ABSOLUTE else "v"
            coordinates.append(f"{position_str}{self._y.value}")
        if len(coordinates) == 0:
            return ""
        return ";".join(coordinates)


class Coordinate:
    """*Coordinate* defines a horizontal (*x*) or vertical (*y*) position of a graphical object.

    *Coordinate* is defined as:

    .. code-block:: ebnf

        xy = ("H" | "h")x ";" ("V" | "v")y

    - :code:`("H" | "h")` or :code:`("V" | "v")`: Absolute or relative position (see :py:class:`Position`)
    - :code:`x` or :code:`y`: Coordinate value

    The relative coordinate values are computed from:

    - the center of the parent block
    - wire and transition: the center of the source/target, or the previous coordinate
    """

    def __init__(self, position: "Position", value: int) -> None:
        self._position = position
        self._value = value

    @property
    def position(self) -> "Position":
        """Return the coordinate position (absolute or relative)."""
        return self._position

    @property
    def value(self) -> int:
        """Return the coordinate value."""
        return self._value

    def __str__(self):
        return f"{self._position.name}:{self._value}"


class Position(Enum):
    """Position of a coordinate.

    .. code-block:: ebnf

        xy = ("H" | "h")x ";" ("V" | "v")y

    - :code:`H`, :code:`V`: Absolute position
    - :code:`h`, :code:`v`: Relative position
    """

    #: Absolute position.
    ABSOLUTE = auto()

    #: Relative position.
    RELATIVE = auto()


class Size:
    """Size of a graphical object.

    Size is defined as

    .. code-block:: ebnf

        wh = width ";" height

    where:

    - :code:`width`: Width value
    - :code:`height`: Height value

    Size is used to define the size of the diagram object,
    states, active if/when blocks or automaton.
    """

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        """Return the object width."""
        return self._width

    @property
    def height(self) -> int:
        """Return the object height."""
        return self._height

    def __str__(self):
        return f"{self._width};{self._height}"


class Direction:
    """The direction of the diagram object.

    *Direction* is defined as

    .. code-block:: ebnf

        dir = dir_val

    where :code:`dir_val` is defined in :py:class:`DirectionType`.

    *Direction* is used to define the direction of predefined operator and block with text (Expr, Def, Instance, Equation).
    """

    def __init__(self, value: "DirectionType") -> None:
        self._value = value

    @property
    def value(self) -> "DirectionType":
        """Return the direction value."""
        return self._value

    def __str__(self):
        return self._value.value


class DirectionType(Enum):
    """The direction value of a diagram object.

    The direction value is defined as

    .. code-block:: ebnf

        dir_val = ne|nw|es|en|se|sw|ws|wn

    where:

    - :code:`ne`: North-East
    - :code:`nw`: North-West
    - :code:`es`: East-South
    - :code:`en`: East-North
    - :code:`se`: South-East
    - :code:`sw`: South-West
    - :code:`ws`: West-South
    - :code:`wn`: West-North

    The direction value is read as: the first direction is at the top of the graphical object,
    and the second direction is the right side of the graphical object.

    The default direction is North-East:
        - West corresponding to inputs,
        - East corresponding to outputs.
    """

    #: North-East direction. Default direction (inputs are on the left, outputs are on the right).
    NORTH_EAST = "ne"

    #: North-West direction. From the default direction, a horizontal flip is applied,
    #: or a 180° rotation and a vertical flip are applied
    #: (inputs are on the right and outputs are on the left).
    NORTH_WEST = "nw"

    #: East-South direction. From the default direction, a 90° left rotation is applied
    #: (inputs are at the bottom and outputs are at the top).
    EAST_SOUTH = "es"

    #: East-North direction. From the default direction, a 90° left rotation and a horizontal flip are applied
    #: (inputs are at the bottom and outputs are at the top).
    EAST_NORTH = "en"

    #: South east direction. From the default direction, a vertical flip is applied
    #: (inputs are on the left and outputs are on the right).
    SOUTH_EAST = "se"

    #: South-West direction. From the default direction, a 180° rotation is applied
    #: (inputs are on the right and outputs are on the left).
    SOUTH_WEST = "sw"

    #: West-South direction. From the default direction, a 90° right rotation and a horizontal flip are applied
    #: (inputs are at the top and outputs are at the bottom).
    WEST_SOUTH = "ws"

    #: West-North direction. From the default direction a 90° right rotation is applied
    #: (inputs are at the top and outputs are at the bottom).
    WEST_NORTH = "wn"


class Orientation:
    """Text content orientation.

    *Orientation* is defined as

    .. code-block:: ebnf

        orient = orient_val

    where :code:`orient_val` is defined in :py:class:`OrientationType`.

    *Orientation* is used to define the text content orientation of the diagram object.
    """

    def __init__(self, value: "OrientationType") -> None:
        self._value = value

    @property
    def value(self) -> "OrientationType":
        """Return the orientation value."""
        return self._value

    def __str__(self):
        if self._value is None:
            return ""
        return self._value.value


class OrientationType(Enum):
    """Text content orientation value.

    The orientation value is defined as:

    .. code-block:: ebnf

        orient_val = "H"|"V"

    where:

    - :code:`H`: Horizontal orientation
    - :code:`V`: Vertical orientation
    """

    #: Horizontal orientation.
    HORIZONTAL = "H"

    #: Vertical orientation.
    VERTICAL = "V"


class PathInfo:
    """The wire or transition path between two objects.
    The path is defined by a list of moves.

    The wire and transition paths are defined as:

    - Wire

    .. code-block:: ebnf

        wp = path_info

    - Transition

    .. code-block:: ebnf

        tp = path_info

    where:

    .. code-block:: ebnf

        path_info = w_anchor path

    :code:`w_anchor` is defined in :py:class:`WireAnchor`.

    :code:`path` is defined in :py:class:`WirePath`.
    """

    def __init__(self, w_anchor: "WireAnchor", path: "WirePath") -> None:
        self._w_anchor = w_anchor
        self._path = path

    @property
    def w_anchor(self) -> "WireAnchor":
        """Return the wire anchor."""
        return self._w_anchor

    @property
    def path(self) -> "WirePath":
        """Return the path."""
        return self._path

    def __str__(self):
        return f"{self._w_anchor} {self._path}"


class WireAnchor:
    """*Wire anchor* is the starting or ending point of a path.

    *Wire anchor* is defined as:

    .. code-block:: ebnf

        w_anchor = LUNUM
            | COORD '|' LUNUM (* connection to a group-related block *)
            | coordinates '|' LUNUM (* coordinates of a starting/ending point of a transition for a state *)
            | coordinates (* unconnected point as a pair of COORD. *)

    where:

    - :code:`LUNUM`: The graphical object identifier (see :py:class:`Lunum`)
    - :code:`COORD`: Coordinate *x* or *y* (see :py:class:`Coordinate`)
    - :code:`coordinates`: Coordinates (*x*;*y*) (see :py:class:`Coordinates`)
    """

    def __init__(
        self,
        lunum: Optional["Lunum"] = None,
        coordinates: Optional["Coordinates"] = None,
    ) -> None:
        self._lunum = lunum
        self._coordinates = coordinates

    @property
    def lunum(self) -> "Lunum":
        """Return the LUNUM."""
        return self._lunum

    @property
    def coordinates(self) -> Union["Coordinates", None]:
        """Return the coordinates."""
        return self._coordinates

    def __str__(self):
        wire_anchor = []
        if self._coordinates:
            wire_anchor.append(str(self._coordinates))
        if self._lunum:
            wire_anchor.append(str(self._lunum))
        if len(wire_anchor) == 0:
            return ""
        return "|".join(wire_anchor)


class WirePath:
    """The wire path structure.

    Wire path is defined as:

    .. code-block:: ebnf

        path = {move} w_anchor
                | {move} branch

    *{move}* means zero or more moves.
    where:

    - :code:`move` is defined in :py:class:`Move`
    - :code:`w_anchor` is defined in :py:class:`WireAnchor`
    - :code:`branch` is defined in :py:class:`Branch`
    """

    def __init__(
        self,
        moves: Optional[List["Move"]] = None,
        w_anchor: Optional["WireAnchor"] = None,
        branch: Optional["Branch"] = None,
    ) -> None:
        self._moves = moves
        self._w_anchor = w_anchor
        self._branch = branch

    @property
    def moves(self) -> Union[List["Move"], None]:
        """Return the moves."""
        return self._moves

    @property
    def w_anchor(self) -> Union["WireAnchor", None]:
        """Return the wire anchor."""
        return self._w_anchor

    @property
    def branch(self) -> Union["Branch", None]:
        """Return the branch."""
        return self._branch

    def __str__(self) -> str:
        branch_str = []
        if self._moves:
            for move in self._moves:
                branch_str.append(str(move))
        if self._w_anchor:
            branch_str.append(str(self._w_anchor))
        if self._branch:
            branch_str.append(str(self._branch))
        if len(branch_str) == 0:
            return ""
        return " ".join(branch_str)


class Move:
    """Movement of a wire or transition.

    Move is defined as:

    .. Code-block:: ebnf

        Move = move_coordinates

    Where:

    - :code:`move_coordinates`: Move coordinates (see :py:class:`MoveCoordinates`)
    """

    def __init__(self, coordinates: Optional["MoveCoordinates"] = None) -> None:
        self._coordinates = coordinates

    @property
    def coordinates(self) -> Union["MoveCoordinates", None]:
        """Return the coordinates."""
        return self._coordinates

    def __str__(self) -> str:
        if not self._coordinates:
            return ""
        return str(self._coordinates)


class MoveCoordinates:
    """*Move coordinates* manages the movement among coordinates of wires and transitions.

    *Wire coordinates* are defined as:

    .. code-block:: ebnf

        wire_coordinates = COORD | coordinates

    and *transition coordinates* are defined as:

    .. code-block:: ebnf

        transition_coordinates = (COORD | coordinates) '|' coordinates

    Thus, joining both definitions, *move coordinates* is defined as:

    .. code-block:: ebnf

        move_coordinates = (COORD | coordinates) '|' coordinates
    """

    def __init__(
        self,
        coordinates: "Coordinates",
        fork_coordinates: Optional["Coordinates"] = None,
    ) -> None:
        self._coordinates = coordinates
        self._fork_coordinates = fork_coordinates

    @property
    def coordinates(self) -> "Coordinates":
        """Return the coordinates."""
        return self._coordinates

    @property
    def fork_coordinates(self) -> Union["Coordinates", None]:
        """Return the fork coordinates. Only applies to transitions."""
        return self._fork_coordinates

    def __str__(self):
        if not self._fork_coordinates:
            return str(self._coordinates)
        return f"{self._coordinates}|{self._fork_coordinates}"


class Branch:
    """Branch is the graphic path followed by the wire or transition.

    Branch is defined as:

    .. code-block:: ebnf

        branch = '[' path_list ']';
        path_list = path
            | path_list ',' path

    where:

    - :code:`path`: Wire path (see :py:class:`WirePath`)
    """

    def __init__(self, path_list: List["WirePath"]) -> None:
        self._path_list = path_list

    @property
    def path_list(self) -> List["WirePath"]:
        """Return the path list."""
        return self._path_list

    def __str__(self):
        path_list_str = []
        for path in self._path_list:
            path_list_str.append(str(path))
        if len(path_list_str) == 0:
            return ""
        list_str = ", ".join(path_list_str)
        return f"[{list_str}]"
