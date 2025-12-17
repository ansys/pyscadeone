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
import json
import re
from typing import List, Optional, Union, Dict, cast
from functools import cache
from lark import Lark, Transformer

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.swan.common import Pragma, Lunum, PragmaKey


class CGPragmaKind(Enum):
    """Kind of pragma for Swan CG."""

    #: Probe pragma for local variables ("probe")
    PROBE = auto()
    #: Keep pragma ("keep")
    KEEP = auto()
    #: Default state pragma ("default")
    DEFAULT = auto()
    #: C pragma for constants ("C:const")
    CONST = auto()
    #: C: pragma for scalar values ("C:scalar")
    SCALAR = auto()
    #: C pragma for names ("C:name ID")
    NAME = auto()
    #: C pragma for enum values ("C:enum_val value")
    ENUM_VALUE = auto()
    #: C pragma for type initializers ("C:initializer ID")
    INITIALIZER = auto()
    #: Unknown pragma.
    UNKNOWN = auto()

    @classmethod
    @cache
    def _get_string_map(cls) -> Dict[str, "CGPragmaKind"]:
        """Returns map string => CGPragmaKind."""
        return {
            "probe": cls.PROBE,
            "keep": cls.KEEP,
            "default": cls.DEFAULT,
            "C:const": cls.CONST,
            "C:scalar": cls.SCALAR,
            "C:name": cls.NAME,
            "C:enum_val": cls.ENUM_VALUE,
            "C:initializer": cls.INITIALIZER,
        }

    @classmethod
    @cache
    def _get_enum_map(cls) -> Dict["CGPragmaKind", str]:
        """Returns map string => CGPragmaKind."""
        return {kind: string for string, kind in cls._get_string_map().items()}

    @classmethod
    def from_string(cls, kind_str: str) -> Optional["CGPragmaKind"]:
        """
        Return the CGPragmaKind from a string.

        Parameters
        ----------
        kind_str : str
            The string given.

        Returns
        -------
        Optional[CGPragmaKind]
            The corresponding CGPragmaKind if found, otherwise None.
        """
        return cls._get_string_map().get(kind_str, None)

    @classmethod
    def to_string(cls, kind: "CGPragmaKind") -> Optional[str]:
        """
        Return the string representation of a CGPragmaKind.

        Parameters
        ----------
        kind : CGPragmaKind
            The CGPragmaKind to convert.

        Returns
        -------
        Optional[str]
            The string representation of the CGPragmaKind if found, otherwise None.
        """
        if kind_str := cls._get_enum_map().get(kind, None):
            return kind_str
        return None

    def __str__(self) -> str:
        """Return the string representation of the CGPragmaKind."""
        _kind_str = self.to_string(self)
        return _kind_str if _kind_str else ""


class TestPragmaKind(Enum):
    """Kind of pragma for Under Test."""

    #: Under Test pragma ("under_test")
    UNDER_TEST = "under_test"

    def __str__(self) -> str:
        """Return the string representation of the TestPragmaKind."""
        return self.value

    # TODO: Some Test pragma kinds are not yet implemented (e.g. data_source in VTOLDisplay.swan)
    # In this case, we return the string.
    @classmethod
    def from_string(cls, kind: str) -> Union["TestPragmaKind", str]:
        """
        Return the TestPragmaKind from a string.

        Parameters
        ----------
        kind : str
            The string given.

        Returns
        -------
        Union[TestPragmaKind, str]
            The corresponding TestPragmaKind if found, otherwise the original string.
        """
        for enum_kind in cls:
            if enum_kind.value == kind:
                return enum_kind
        return kind


class CGPragma(Pragma):
    """Pragma for Swan code generator."""

    CGPragmaRE = re.compile((r"(?P<kind>[\w:]+)(?:\s+(?P<value>.*))?"))

    def __init__(self, data: str) -> None:
        super().__init__(PragmaKey.CG, data)
        m = self.CGPragmaRE.match(data)
        if not m:
            raise ScadeOneException(f"Invalid CG pragma format: {data}")
        self._kind = CGPragmaKind.from_string(m["kind"])
        if self._kind is None:
            self._value = data
        else:
            self._value = m["value"] if m["value"] else None

    @property
    def kind(self) -> CGPragmaKind:
        """Return the pragma kind.

        According to the kind call the appropriate method to get the value if any."""
        return cast(CGPragmaKind, self._kind)

    def get_enum_value(self) -> Optional[str]:
        """Return the enum value if the pragma is an enum value."""
        if self.kind != CGPragmaKind.ENUM_VALUE:
            return None
        return self._value

    def get_initializer(self) -> Optional[str]:
        """Return the initializer if the pragma is an initializer."""
        if self.kind != CGPragmaKind.INITIALIZER:
            return None
        return self._value

    def get_name(self) -> Optional[str]:
        """Return the name if the pragma is a name."""
        if self.kind != CGPragmaKind.NAME:
            return None
        return self._value


class TestPragma(Pragma):
    """Pragma used to mark an instance operator as being under test in a test harness."""

    def __init__(self, kind: TestPragmaKind | str) -> None:
        super().__init__(PragmaKey.SWT)
        self._kind = kind

    @property
    def kind(self) -> TestPragmaKind | str:
        """Return the pragma kind.

        According to the kind call the appropriate method to get the value if any."""
        return self._kind


# ==========================
# Classes for diagram pragma
# ==========================
class DiagramPragma(Pragma):
    """The diagram information of a graphical object."""

    def __init__(self) -> None:
        super().__init__(PragmaKey.DIAGRAM)
        self._coordinates = None
        self._size = None
        self._direction = None
        self._orientation = None
        self._wire_path_info = None
        self._transition_path_info = None
        self._is_detached = False

    @property
    def coordinates(self) -> Optional["Coordinates"]:
        """Return the diagram coordinates."""
        return self._coordinates

    @property
    def size(self) -> Optional["Size"]:
        """Return the diagram size."""
        return self._size

    @property
    def direction(self) -> Optional["Direction"]:
        """Return the diagram direction."""
        return self._direction

    @property
    def default_direction(self) -> "Direction":
        """Return the default diagram direction (North-East)."""
        return Direction(DirectionType.NORTH_EAST)

    @property
    def orientation(self) -> Optional["Orientation"]:
        """Return the diagram orientation."""
        return self._orientation

    @property
    def wire_path_info(self) -> Optional["PathInfo"]:
        """Return the diagram wire info."""
        return self._wire_path_info

    @property
    def transition_path_info(self) -> Optional["PathInfo"]:
        """Return the diagram arrow info."""
        return self._transition_path_info

    @property
    def is_detached(self) -> bool:
        """Return whether the diagram is *detached* (content not displayed)."""
        return self._is_detached

    @property
    def data(self) -> str:
        """Return a string representation of a property given."""
        if self._is_detached:
            return "detached"
        params = []
        if self._coordinates:
            params.append(f'"xy":"{self._coordinates}"')
        if self._size:
            params.append(f'"wh":"{self._size}"')
        if self._direction:
            params.append(f'"dir":"{self._direction}"')
        if self._orientation:
            params.append(f'"orient":"{self._orientation}"')
        if self._wire_path_info:
            params.append(f'"wp":"{self._wire_path_info}"')
        if self._transition_path_info:
            params.append(f'"tp":"{self._transition_path_info}"')
        return f"{{{','.join(params)}}}"


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

    def __init__(self, position: Position, value: int) -> None:
        self._position = position
        self._value = value

    @property
    def position(self) -> Position:
        """Return the coordinate position (absolute or relative)."""
        return self._position

    @property
    def value(self) -> int:
        """Return the coordinate value."""
        return self._value

    def __str__(self) -> str:
        """Return the string representation of Coordinate."""
        return f"{self._position.name}:{self._value}"


class Coordinates:
    """*Coordinates* define a horizontal (*x*) and a vertical (*y*) position of a graphical object.

    *Coordinates* are specified as:

    .. code-block:: ebnf

        xy = COORD ";" COORD

    where:

    - :code:`COORD`: Coordinate *x* or *y* (see :py:class:`Coordinate`)

    *Coordinates* are used to define the position of the diagram object, states or Active if/when blocks.
    """

    def __init__(self, x: Optional[Coordinate] = None, y: Optional[Coordinate] = None) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> Union[Coordinate, None]:
        """Return the *x* coordinate."""
        return self._x

    @property
    def y(self) -> Union[Coordinate, None]:
        """Return the *y* coordinate."""
        return self._y

    def __str__(self) -> str:
        """Return the string representation of Coordinates."""
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


class Size:
    """Size of a graphical object.

    Size is defined as

    .. code-block:: ebnf

        wh = width ";" height

    where:

    - :code:`width`: Width value
    - :code:`height`: Height value

    Size is used to define the size of the diagram object,
    states, active if/when blocks or automaton. If omitted, the default size of the object is used.
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

    def __str__(self) -> str:
        """Return the string representation of Size."""
        return f"{self._width};{self._height}"


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


class Direction:
    """The direction of the diagram object.

    *Direction* is defined as

    .. code-block:: ebnf

        dir = dir_val

    where :code:`dir_val` is defined in :py:class:`DirectionType`.

    *Direction* is used to define the direction of predefined operator and block with text (Expr, Def, Instance, Equation).
    """

    def __init__(self, value: DirectionType) -> None:
        self._value = value

    @property
    def value(self) -> DirectionType:
        """Return the direction value."""
        return self._value

    def __str__(self) -> str:
        """Return the string representation of Direction."""
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


class Orientation:
    """Text content orientation.

    *Orientation* is defined as

    .. code-block:: ebnf

        orient = orient_val

    where :code:`orient_val` is defined in :py:class:`OrientationType`.

    *Orientation* is used to define the text content orientation of the diagram object.
    """

    def __init__(self, value: OrientationType) -> None:
        self._value = value

    @property
    def value(self) -> OrientationType:
        """Return the orientation value."""
        return self._value

    def __str__(self) -> str:
        """Return the string representation of Orientation."""
        if self._value is None:
            return ""
        return self._value.value


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

        path_info = path_anchor path

    :code:`path_anchor` is defined in :py:class:`PathAnchor`.

    :code:`path` is defined in :py:class:`PathPart`.
    """

    def __init__(self, path_anchor: "PathAnchor", path: "PathPart") -> None:
        self._path_anchor = path_anchor
        self._path = path

    @property
    def path_anchor(self) -> "PathAnchor":
        """Return the wire anchor."""
        return self._path_anchor

    @property
    def path(self) -> "PathPart":
        """Return the path."""
        return self._path

    def __str__(self) -> str:
        """Return the string representation of PathInfo."""
        return f"{self._path_anchor} {self._path}"


class PathAnchor:
    """*Path anchor* is the starting or ending point of a path.

    *Path anchor* is defined as:

    .. code-block:: ebnf

        path_anchor = LUNUM
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
        coordinates: Optional[Coordinates] = None,
    ) -> None:
        self._lunum = lunum
        self._coordinates = coordinates

    @property
    def lunum(self) -> Optional["Lunum"]:
        """Return the LUNUM."""
        return self._lunum

    @property
    def coordinates(self) -> Optional[Coordinates]:
        """Return the coordinates."""
        return self._coordinates

    def __str__(self) -> str:
        """Return the string representation of PathAnchor."""
        wire_anchor = []
        if self._coordinates:
            wire_anchor.append(str(self._coordinates))
        if self._lunum:
            wire_anchor.append(str(self._lunum))
        if len(wire_anchor) == 0:
            return ""
        return "|".join(wire_anchor)


class Move:
    """This class manages the *moves* along wire and transition paths.

    A *move* is defined as:

    .. code-block:: ebnf

        move_coordinates = COORD | coordinates

    for a *move* along a wire path and a transition path, and is defined as:

    .. code-block:: ebnf

        move_and_fork_coordinates = (COORD | coordinates) '|' coordinates

    for a *move* along a transition path with a fork. The coordinates before the pipe symbol ('|')
    represent the move, and the coordinates after the pipe symbol represent the fork point.
    """

    def __init__(
        self,
        coordinates: "Coordinates",
        fork_coordinates: Optional[Coordinates] = None,
    ) -> None:
        self._coordinates = coordinates
        self._fork_coordinates = fork_coordinates

    @property
    def coordinates(self) -> "Coordinates":
        """Return the coordinates."""
        return self._coordinates

    @property
    def fork_coordinates(self) -> Optional[Coordinates]:
        """Return the fork coordinates. Only applies to transitions."""
        return self._fork_coordinates

    def __str__(self) -> str:
        """Return the string representation of Move."""
        if not self._fork_coordinates:
            return str(self._coordinates)
        return f"{self._coordinates}|{self._fork_coordinates}"


class PathPart:
    """The PathPart represents a segment of a path after the anchor or in branch.

    The path part is defined as:

    .. code-block:: ebnf

        path = {move} path_anchor
             | {move} branch

    *{move}* means zero or more moves.
    where:

    - :code:`move` is defined in :py:class:`Move`
    - :code:`path_anchor` is defined in :py:class:`PathAnchor`
    - :code:`branch` is defined in :py:class:`Branch`
    """

    def __init__(
        self,
        moves: Optional[List[Move]] = None,
        path_anchor: Optional[PathAnchor] = None,
        branches: Optional["Branches"] = None,
    ) -> None:
        self._moves = moves
        self._path_anchor = path_anchor
        self._branches = branches

    @property
    def moves(self) -> Optional[List[Move]]:
        """Return the moves."""
        return self._moves

    @property
    def path_anchor(self) -> Optional[PathAnchor]:
        """Return the wire anchor."""
        return self._path_anchor

    @property
    def branches(self) -> Union["Branches", None]:
        """Return the branch."""
        return self._branches

    def __str__(self) -> str:
        """Return the string representation of PathPart."""
        path = " ".join(str(move) for move in self.moves) if self.moves else ""
        if self._path_anchor:
            if path:
                path += " "
            path += str(self._path_anchor)
        if self._branches:
            path += str(self._branches)
        return path


class Branches:
    """Branch is the graphic path followed by the wire or transition when there are multiple paths.

    Branch is defined as:

    .. code-block:: ebnf

        branch = '[' path_list ']';
        path_list = path
                  | path_list ',' path

    where:

    - :code:`path`: path part (see :py:class:`PathPart`)
    """

    def __init__(self, path_list: List[PathPart]) -> None:
        self._path_list = path_list

    @property
    def path_list(self) -> List[PathPart]:
        """Return the path list."""
        return self._path_list

    def __str__(self) -> str:
        """Return the string representation of Branches."""
        path_list_str = [str(path) for path in self.path_list]
        if len(path_list_str) == 0:
            return ""
        list_str = ", ".join(path_list_str)
        return f"[{list_str}]"


# ==========================
# Classes for pragma parsing
# ==========================


def _create_parser(grammar: str, start: str, transformer: Transformer) -> Lark:
    """Create a Lark parser with the given grammar, start and transformer. LALR parser is used."""
    return Lark(grammar, start=start, parser="lalr", transformer=transformer)


# Diagram-related parser


class DiagramPragmaParser:
    """Parser for diagram pragma."""

    _instance = None

    def __new__(cls, *args, **kwargs) -> "DiagramPragmaParser":
        if not cls._instance:
            cls._instance = super(DiagramPragmaParser, cls).__new__(cls)
            cls._instance._coordinates_parser = cls._create_coordinate_parser()
            cls._instance._size_parser = cls._create_size_parser()
            cls._instance._direction_parser = cls._create_direction_parser()
            cls._instance._orientation_parser = cls._create_orientation_parser()
            cls._instance._path_info_parser = cls._create_path_info_parser()
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
        Path info is defined as "path_anchor path" where:

        - path_anchor: LUNUM
                    | COORD '|' LUNUM
                    | coordinates '|' LUNUM
                    | coordinates
        - path: moves path_anchor
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
                    path_info: path_anchor path
                    path_anchor: LUNUM
                        | (x | y | coordinates) "|" LUNUM
                        | coordinates
                    path: move* path_anchor | move* branch
                    coordinates: x ";" y
                    x: (absolute_horizontal | relative_horizontal) SIGNED_INT
                    y: (absolute_vertical | relative_vertical) SIGNED_INT
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
            This is a string that contains either a JSON expression with the following properties:

            - "xy": Coordinates
            - "wh": Size
            - "dir": Direction
            - "orient": Orientation
            - "wp": Wire path
            - "tp": Transition path

            or a string that contains "detached" to indicate that the diagram content
            should not be displayed.

            Each property's value is parsed by the corresponding parser.

        Returns
        -------
        DiagramPragma | None
            The parsed pragma diagram or None if params is empty.
        """
        if not params:
            return None
        # Check if params is "detached"
        if params == "detached":
            pragma_diag = DiagramPragma()
            pragma_diag._is_detached = True
            return pragma_diag
        # otherwise, parse the JSON expression
        try:
            params = json.loads(params)
        except json.JSONDecodeError:
            return None
        if not isinstance(params, dict):
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
            pragma_diag._wire_path_info = cast(PathInfo, self._path_info_parser.parse(params["wp"]))
        if "tp" in params:
            pragma_diag._transition_path_info = cast(
                PathInfo, self._path_info_parser.parse(params["tp"])
            )
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
    def x(items) -> Coordinate:
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
    def y(items) -> Coordinate:
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
    def path_anchor(items) -> "PathAnchor":
        """Return the wire anchor.

        Parameters
        ----------
        items : list
            List of items. This list could contain two items:
            - The LUNUM
            - The coordinates

        Returns
        -------
        PathAnchor
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
        return PathAnchor(lunum, coordinates)

    @staticmethod
    def path(items) -> "PathPart":
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
        PathPart
            The object wire path.
        """
        moves = items[:-1] if isinstance(items[0], Move) else None
        path_anchor = items[-1] if isinstance(items[-1], PathAnchor) else None
        branches = items[-1] if isinstance(items[-1], Branches) else None
        return PathPart(moves, path_anchor, branches)

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
    def x(items) -> tuple[str, Coordinate]:
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
    def y(items) -> tuple[str, Coordinate]:
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
        if isinstance(items[0], tuple):
            # simple COORD
            if items[0][0] == "x":
                coordinates = Coordinates(items[0][1], None)
            else:
                coordinates = Coordinates(None, items[0][1])
            return Move(coordinates)
        elif isinstance(items[0], Coordinates):
            # coordinates
            return Move(items[0])
        elif isinstance(items[0], Move):
            # fork coordinates
            return items[0]

    @staticmethod
    def fork_coordinates(items) -> "Move":
        """Return the coordinates with fork coordinates.

        fork_coordinates: (x | y | coordinates) '|' coordinates

        Parameters
        ----------
        items : list
            List of items. This list only contains two items:
            - The coordinates
            - The fork coordinates

        Returns
        -------
        Move
            The object move with fork coordinates.
        """
        return Move(items[0], items[1])

    @staticmethod
    def branch(items) -> "Branches":
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
        return Branches(items[0])

    @staticmethod
    def path_list(items) -> List["PathPart"]:
        """Return the path list.

        path_list: (path ',')* path

        Parameters
        ----------
        items : list
            List of items. This list contains the path list.

        Returns
        -------
        List[PathPart]
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


class DocumentationPragma(Pragma):
    """Documentation pragma."""

    def __init__(self, data: str) -> None:
        super().__init__(PragmaKey.DOC, data)

    @property
    def text(self) -> str:
        """Return the documentation text.

        Returns
        -------
        str
            The documentation text.
        """
        return cast(str, self._data)


class TraceabilityPragma(Pragma):
    """Traceability pragma."""

    def __init__(self, data: str) -> None:
        super().__init__(PragmaKey.REQUIREMENT, data)

    @property
    def reference(self) -> str:
        """Return the traceability reference.

        Returns
        -------
        str
            The traceability reference.
        """
        return cast(str, self._data)


# ==========================
# General pragma parser
# ==========================
class PragmaParser:
    """Parser for pragma.

    This is the list of supported pragmas:
    - diagram
    """

    PragmaRE = re.compile(r"^#pragma(?P<content>.*)#end$", re.DOTALL)
    PragmaContentRE = re.compile(r"^(?P<key>\s*\S+)(?P<val>.*?)$", re.DOTALL)
    _instance = None

    def __new__(cls, *args, **kwargs) -> "PragmaParser":
        if not cls._instance:
            cls._instance = super(PragmaParser, cls).__new__(cls)
        return cls._instance

    def parse(self, pragma: str) -> Optional[Pragma]:
        """Parse pragma.

        Parameters
        ----------
        pragma : str
            Pragma string defined in SO-SRS-001 V2.1, section 1.2.5, [S1-203]

        Returns
        -------
        Pragma | None
            The parsed pragma or None if the pragma is not valid or not supported.
        """
        if not pragma:
            return None

        pragma_tuple = self.extract(pragma)
        if not pragma_tuple:
            return None
        raw_key, value = pragma_tuple
        key = PragmaKey.from_string(raw_key.strip())
        if key == PragmaKey.DIAGRAM:
            if diagram_pragma := DiagramPragmaParser().parse(value):
                return diagram_pragma
            return Pragma(PragmaKey.DIAGRAM, value)
        if key == PragmaKey.CG:
            return CGPragma(value.strip())
        if key == PragmaKey.SWT:
            return TestPragma(TestPragmaKind.from_string(value.strip()))
        if key == PragmaKey.DOC:
            return DocumentationPragma(value)
        if key == PragmaKey.REQUIREMENT:
            return TraceabilityPragma(value)
        return Pragma(raw_key, value)

    @staticmethod
    def extract(pragma: str) -> Union[tuple[str, str], None]:
        """Extract pragma information as a tuple
        if pragma is valid, namely: #pragma key value? #end.

        Fist white space before the key and the value is removed, as the last before the #end.

        Parameters
        ----------
        pragma : str
            Pragma information string.

        Returns
        -------
        tuple | None
            The Tuple (*pragma name*, *pragma value*) if pragma is valid, None else.
        """
        #  get the pragma content
        m = PragmaParser.PragmaRE.match(pragma)
        if not m:
            return None
        content = m["content"]
        # get the pragma key and value
        m = PragmaParser.PragmaContentRE.match(content)
        if not m:
            # pragma without key and value,
            if content and content[0] == " ":
                content = content[1:]
            if content and content[-1] == " ":
                content = content[:-1]
            return content, ""
        val = m["val"]
        # strip leading and trailing spaces if any
        if val and val[0] == " ":
            val = val[1:]
        if val and val[-1] == " ":
            val = val[:-1]
        key = m["key"]
        if key and key[0] == " ":
            key = key[1:]
        return key, val
