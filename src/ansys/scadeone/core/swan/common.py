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

"""
This module contains classes that are used by all the other
language-related modules.

It contains base classes for various language constructs.
"""

from abc import ABC
from collections import namedtuple
from collections.abc import Iterable as abcIterable
from enum import Enum, auto
import re
from typing import Iterable, List, Optional, Tuple, Union, cast

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.interfaces import IModel

Owner = Union["SwanItem", IModel, None]


class SwanItem(ABC):  # numpydoc ignore=PR01
    """Base class for Scade objects."""

    def __init__(self) -> None:
        self._owner = None
        super().__init__()

    @property
    def owner(self) -> Owner:
        """Owner of current Swan construct."""
        return self._owner

    @owner.setter
    def owner(self, owner: Owner) -> None:  # numpydoc ignore=PR01
        """Set the owner of the Swan construct."""
        self._owner = owner

    @staticmethod
    def set_owner(owner: Owner, children: Union["SwanItem", Iterable["SwanItem"], None]) -> None:
        """Helper to set *owner* as the owner of each item in the Iterable *items*.

        Parameters
        ----------
        owner : SwanItem
            Owner of the items.
        children : Union[SwanItem, Iterable[SwanItem], None]
            Items to set owner.
        """
        if isinstance(children, abcIterable):
            for item in children:
                item.owner = owner
        elif children is not None:
            children.owner = owner

    def get_full_path(self) -> str:
        """Full path of the Swan construct.

        This method is implemented by derived classes that correspond to a declaration
        at the module level (such as sensor, type, group, const, operator), or a module itself.

        Returns
        -------
        str
            Path within the owner and name of the Swan construct.

        Raises
        ------
        ScadeOneException
            If the method is not implemented for the current SwanItem type.
        """
        raise ScadeOneException(f"SwanItem.get_full_path(): not implemented for {type(self)}")

    def __str__(self) -> str:
        raise Exception(f"__str__ not implemented for {type(self)}")

    @property
    def is_protected(self) -> bool:
        """Tell if a construct item is syntactically protected with some markup
        and is stored as a string (without the markup)."""
        return False

    @property
    def module(self) -> Union["ModuleBase", None]:
        """Module containing the item.

        Returns:
            ModuleBase: module container, see :py:class:`ModuleBody`
            and :py:class:`ModuleInterface` or None if the object is itself a module.
        """
        if isinstance(self, ModuleBase):
            return None
        if isinstance(self.owner, ModuleBase):
            return self.owner
        if self.owner is not None:
            return cast(SwanItem, self.owner).module
        raise ScadeOneException("owner property is None")

    @property
    def model(self) -> IModel:
        """Return model containing the Swan item."""
        if isinstance(self, ModuleBase):
            module = self
        else:
            module = self.module
        model = module.owner if module is not None else None
        if model is None:
            raise ScadeOneException("Module owner not found")
        return cast(IModel, model)


class PragmaKey(Enum):
    """Class representing pragma keys, supporting both predefined and dynamic keys."""

    SWT = "swt"
    CG = "cg"
    DIAGRAM = "diagram"
    REQUIREMENT = "requirement"
    DOC = "doc"

    def __init__(self, value: str) -> None:
        self._value = value

    def __str__(self) -> str:
        """Return the string representation of the pragma key."""
        return self._value

    @classmethod
    def from_string(cls, key: str) -> Optional["PragmaKey"]:
        """Create a PragmaKey from a string.

        Parameters
        ----------
        key : str
            String representing the pragma key.

        Returns
        -------
        PragmaKey
            Corresponding PragmaKey instance.
        """
        for pragma_key in PragmaKey:
            if pragma_key.value == key:
                return pragma_key
        return None


class Pragma(SwanItem):
    """Pragma structure."""

    def __init__(self, key: PragmaKey | str, data: Optional[str] = None) -> None:
        self._key = key
        self._data = data
        super().__init__()

    @property
    def key(self) -> PragmaKey | str:
        """Return the pragma key."""
        return self._key

    @property
    def data(self) -> Optional[str]:
        """Return the pragma data."""
        return self._data

    def __str__(self) -> str:
        """Return the pragma as a string."""
        if self.data:
            ws = "" if not self.key else " "
            return f"#pragma {self.key}{ws}{self.data} #end"
        kind = getattr(self, "_kind", None)
        kind_str = f" {kind}" if kind else " "
        return f"#pragma {self.key}{kind_str} #end"

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
        res = [pragma for pragma in pragmas if with_key == (pragma.key == key)]
        return res


class HasPragma(SwanItem):  # numpydoc ignore=PR01
    """Base class for objects with pragmas."""

    def __init__(self, pragmas: Optional[List[Pragma]] = None) -> None:
        super().__init__()
        self._pragmas = pragmas if pragmas is not None else []
        SwanItem.set_owner(self, self._pragmas)

    @property
    def pragmas(self) -> List[Pragma]:
        """List of pragmas."""
        return self._pragmas

    def add_pragmas(self, *pragmas) -> None:
        """Add one or more pragmas to the current object."""
        self._pragmas.extend(pragmas)
        SwanItem.set_owner(self, pragmas)


class ModuleBase(HasPragma):  # numpydoc ignore=PR01
    """Base class for modules."""

    def __init__(self, pragmas: Optional[List[Pragma]] = None) -> None:
        super().__init__(pragmas)

    def get_use_directive(self, module_name: str) -> Optional["UseDirective"]:  # noqa: F821 # type: ignore
        assert False

    def get_declaration(self, name: str, local_only: bool = False) -> Optional["Declaration"]:
        assert False

    @property
    def is_interface(self) -> bool:
        """True when module is an interface."""
        return False

    @property
    def is_body(self) -> bool:
        """True when module is a body."""
        return False


# ========================================================
# Miscellaneous general definitions
# Type for parsing an integer from a string.
# See class Numeric RE
IntegerTuple = namedtuple(
    "IntegerTuple",
    ["value", "is_bin", "is_oct", "is_hex", "is_dec", "is_signed", "size"],
)

# for parsing a float from a string
# see class Numeric RE
FloatTuple = namedtuple("FloatTuple", ["value", "mantissa", "exp", "size"])


class SwanRE:  # numpydoc ignore=PR01
    """Container of compiled regular expressions. These expressions can be matched with
    some strings. Some regular expressions use groups to extract parts.

    Attributes:

    TypedInteger: regular expressions for integers with post type (_i, _ui).
             Integer part is in the *value* group, type in the *type* group,
             and size in the *size* group.

    TypeFloat: regular expression for floats with post type (_f).
           Mantissa is in the *mantissa* group, exponent in the *exp* group,
           type in the *type* group, and size in the *size* group.

    """

    def __init__(self) -> None:
        # Hide default init with kwargs and args (introspection)
        pass

    TypedInteger = re.compile(
        r"""^
    (?P<value>                    # value group
     (?:0b[01]+)                  # binary
    |(?:0o[0-7]+)                 # octal
    |(?:0x[0-9a-fA-F]+)           # hexadecimal
    |(?:\d+))                     # decimal
    (?:(?P<type>_ui|_i)(?P<size>8|16|32|64))? # type group & size
    $""",
        re.VERBOSE,
    )

    TypedFloat = re.compile(
        r"""^
    (?P<value>                              # float part
    (?P<mantissa>(?:\d+\.\d*)|(?:\d*\.\d+))  # mantissa
    (?:[eE](?P<exp>[+-]?\d+))?)              # exponent
    (?:_f(?P<size>32|64))?                   # size
    $""",
        re.VERBOSE,
    )

    @classmethod
    def parse_integer(cls, string: str, minus: bool = False) -> Union[IntegerTuple, None]:
        """Matches a string representing an integer and returns
        a description of that integer as an IntegerTuple.

        Parameters
        ----------
        string : str
            String representing an integer, with or without type information.
        minus : bool
            True when the value is preceded with a '-' minus operator.

        Returns
        -------
        IntegerTuple or None
            If the string value matches SwanRE.TypedInteger pattern, an
            IntegerTuple is returned. It is a namedtuple with fields:

            - *value*: computed value
            - *is_bin*, *is_oct*, *is_hex*, *is_dec*: flags set according to found type
            - *is_signed*: True when integer is signed
            - *size*: the size part

            Note: if there is no type information, type is _i32.
        """
        m = cls.TypedInteger.match(string)
        if not m:
            return None
        is_bin = m["value"].startswith("0b")
        is_oct = m["value"].startswith("0o")
        is_hex = m["value"].startswith("0x")
        is_dec = not (is_bin or is_oct or is_hex)
        if m["type"]:
            assert not (minus and m["type"] == "_ui")
            is_signed = m["type"] == "_i" or minus
            size = int(m["size"])
        else:
            is_signed = True
            size = 32

        value = m["value"]
        if is_dec:
            value = int(value)
        elif is_bin:
            value = int(value[2:], 2)
        elif is_oct:
            value = int(value[2:], 8)
        else:  # is_hex
            value = int(value[2:], 16)
        if minus:
            value = -value
        return IntegerTuple(value, is_bin, is_oct, is_hex, is_dec, is_signed, size)

    @classmethod
    def is_integer(cls, string: str) -> bool:
        """Check whether a string is a Swan integer.

        Parameters
        ----------
        string : str
            Integer value, as decimal, bin, octal, or hexadecimal, with
            or without type information.

        Returns
        -------
        bool
            True when string is an integer.
        """
        return cls.parse_integer(string) is not None

    @classmethod
    def parse_float(cls, string: str, minus: bool = False) -> Union[FloatTuple, None]:
        """Match a string representing a float and return
        a description of that float as a FloatTuple.

        Parameters
        ----------
        string : str
            String representing a float, with or without type information.
        minus : bool
            True when the value is preceded with a '-' minus operator.

        Returns
        -------
        FloatTuple or None
            If the string value matches SwanRE.TypedFloat pattern, a
            FloatTuple is returned. It is a namedtuple with fields:

            - *value*: computed value
            - *mantissa*: the mantissa part
            - *exp*: the exponent part
            - *size*: the size part

            Note: if there is no type information, type is _f32.
        """
        m = cls.TypedFloat.match(string)
        if not m:
            return None

        mantissa = m["mantissa"]
        exp = int(m["exp"]) if m["exp"] else 1
        size = int(m["size"]) if m["size"] else 32
        # We should use numpy for float32 / float64
        value = -float(m["value"]) if minus else float(m["value"])
        return FloatTuple(value, mantissa, exp, size)

    @classmethod
    def is_float(cls, string: str) -> bool:
        """Check whether a string is a Swan integer.

        Parameters
        ----------
        string : str
            Integer value, as decimal, bin, octal, or hexadecimal, with
            or without type information.

        Returns
        -------
        bool
            True when string is an integer.
        """
        return cls.parse_float(string) is not None

    @classmethod
    def is_numeric(cls, string: str) -> bool:
        """Check whether a string is a Swan numeric value,
        that is, an integer of float value.

        Parameters
        ----------
        string : str
            String to check.

        Returns
        -------
        bool
            True if string is a Swan numeric value.
        """
        return cls.is_integer(string) or cls.is_float(string)

    CharRe = re.compile(r"'.'|'\\x[0-9a-fA-F]{2}'")

    @classmethod
    def is_char(cls, string: str) -> bool:
        """Check whether a string is a Swan char value.

        Parameters
        ----------
        string : str
            String to check.

        Returns
        -------
        bool
            True if string is a Swan char value.
        """
        return cls.CharRe.match(string) is not None

    BoolRe = re.compile("(?:true|false)$")

    @classmethod
    def is_bool(cls, string: str) -> bool:
        """Check whether a string is a Swan boolean value.

        Parameters
        ----------
        string : str
            String to check.

        Returns
        -------
        bool
            True if string is a Swan char value
        """
        return cls.BoolRe.match(string) is not None


class Markup:  # numpydoc ignore=PR01
    """Class defining the markups used by the Swan serialization."""

    def __init__(self) -> None:
        # avoid the generic version with args and kwargs (introspection)
        pass

    NoMarkup = ""
    #: General syntax error.
    Syntax = "syntax"
    #: Incorrect variable declaration.
    Var = "var"
    #: Incorrect group declaration.
    Group = "group"
    #: Incorrect sensor declaration.
    Sensor = "sensor"
    #: Incorrect const declaration.
    Const = "const"
    #: Incorrect type declaration.
    Type = "type"
    #: Incorrect use declaration.
    Use = "use"
    #: Incorrect operator declaration in interface. Actually, "signature" is used.
    Signature = "signature"
    #: Textual operator or generic operator content. The content is re-parsed by the API.
    Text = "text"
    #: Textual operator with syntax error.
    SyntaxText = "syntax_text"
    #: Empty instance block body. This is an invalid construct, but it is needed for the editor.
    Empty = "empty"
    #: Protected instance id.
    Luid = "luid"
    #: Operator expression. Specific markup for the editor. The content is re-parsed by the API.
    OpExpr = "op_expr"
    #: Incorrect forward dimension.
    Dim = "dim"

    @staticmethod
    def to_str(text: str, is_protected: bool = True, markup: Optional[str] = None) -> str:
        """Return *text* as the protected string ``{markup%text%markup}`` if required.

        Parameters
        ----------
        text : str
            Text to protect
        is_protected : bool, optional
            True when text shall be protected, by default True
        markup : str, optional
            Markup to use, by default None, resulting in using Markup.Syntax

        Returns
        -------
        str
            Protected string *{markup%text%markup}* if is_protected is True, else *text*.
        """
        if not is_protected:
            return text
        if markup is None:
            markup = Markup.Syntax
        return f"{{{markup}%{text}%{markup}}}"


class NumericKind(Enum):  # numpydoc ignore=PR01
    """Numeric kinds for generic type constraints."""

    # pylint: disable=invalid-name
    #: *numeric*
    Numeric = auto()
    #: *integer*
    Integer = auto()
    #: *signed*
    Signed = auto()
    #: *unsigned*
    Unsigned = auto()
    #: *float*
    Float = auto()

    @staticmethod
    def to_str(value: "NumericKind") -> str:
        return value.name.lower()


# ========================================================
# Common Constructs, used by other constructs


class Identifier(SwanItem):  # numpydoc ignore=PR01
    """Class for identifier.

    An Identifier can be invalid if it was protected while saving it
    for some reason. In that case, the property *_is_valid_* is set to True.

    Parameters
    ----------
    value : str
        Identifier string.
    comment : str, optional
        Comment, can be multiline, by default None.
    is_name : bool, optional
        True when Identifier is a name, aka. 'Identifier.
    """

    IdentifierRE = re.compile(r"^[a-zA-Z]\w*$", re.ASCII)

    def __init__(
        self,
        value: str,
        comment: str = "",
        is_name: bool = False,
    ) -> None:
        super().__init__()
        self._value = value
        self._comment = comment
        self._is_name = is_name

    @property
    def is_valid(self) -> bool:
        """Return true when Identifier is valid."""
        if Identifier.IdentifierRE.match(self._value) is not None:
            return True
        # Not a valid Identifier from regexp, check for special ones.
        if self._value in ("_stop_condition", "_current_cycle"):
            return True
        # definitively wrong...
        return False

    @property
    def is_protected(self) -> bool:
        """Tell if a construct item is syntactically protected with some markup
        and is stored as a string (without the markup).

        There is no specific derived class for protected Identifier, hence it is handled at by the Identifier
        class itself:

        - with the *is_valid* property: when false, the Identifier should be protected.
        - with the *is_protected* property: when true, the Identifier should be protected.

        The two properties are complementary.

        The *__str__* method returns the Identifier value, with a protection markup when needed.
        """
        return not self.is_valid

    @property
    def value(self) -> str:
        """Identifier as a string."""
        return f"'{self._value}" if self._is_name else self._value

    @property
    def is_name(self) -> bool:
        """Return true when Identifier is a name."""
        return self._is_name

    @property
    def comment(self) -> str:
        """Comment part string."""
        return self._comment

    def __str__(self) -> str:
        """Generate a string representation of the Identifier."""
        value = self.value if self.is_valid else Markup.to_str(self.value)
        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value and self.is_name == other.is_name

    def __hash__(self) -> int:
        return hash((self.value, self.is_name))


class PathIdentifier(SwanItem):  # numpydoc ignore=PR01
    """Class for path identifiers, i.e: P1::Id.

    The class manipulates the PathIdentifier as separate items.

    If the original path was protected (given as a string), the property *is_valid*
    is False, and the path is considered to be a single string and *is_protected* is True.

    path_id argument is:

    - a list of identifiers, for a valid path.
    - a string if the path was protected.
    """

    def __init__(self, path_id: Union[List[Identifier], str]) -> None:
        super().__init__()
        self._path_id = path_id
        if not isinstance(self._path_id, str):
            SwanItem.set_owner(self, self._path_id)
        self._is_valid = isinstance(path_id, list) and all(id.is_valid for id in path_id)

    def __eq__(self, other) -> bool:
        # Compare the two objects
        if not isinstance(other, PathIdentifier):
            return False

        # Compare path_id attributes, maybe it is a List[Identifier] or a string
        if isinstance(self.path_id, list) and isinstance(other.path_id, list):
            return self.as_string == other.as_string
        return self.path_id == other.path_id

    def __hash__(self) -> int:
        # Compute hash based on path_id
        if isinstance(self.path_id, list):
            # Convert list to tuple for hashing
            return hash(tuple(self.path_id))
        return hash(self.path_id)

    @staticmethod
    def from_string(path: str) -> "PathIdentifier":
        """Create a PathIdentifier from a string.

        Parameters
        ----------
        path : str
            String containing the path identifier.

        Returns
        -------
        PathIdentifier
            PathIdentifier instance.
        """
        return PathIdentifier([Identifier(p) for p in path.split("::") if p])

    @staticmethod
    def from_identifier(id: Identifier) -> "PathIdentifier":
        """Create a PathIdentifier from an Identifier.

        Parameters
        ----------
        id : Identifier
            Identifier to create the PathIdentifier from.

        Returns
        -------
        PathIdentifier
            PathIdentifier instance.
        """
        return PathIdentifier([id])

    @staticmethod
    def split(path: str) -> Tuple[str, str]:
        """Split a path into **path**::**name**.

        Parameters
        ----------
        path : str
            Path string.

        Returns
        -------
        Tuple[str, str]
            **path**, **name**.
        """
        parts = path.replace(" ", "").split("::")
        if len(parts) == 1:
            return "", parts[0]
        return "::".join(parts[:-1]), parts[-1]

    # id { :: id} * regexp, with spaces included
    PathIdentifierRe = re.compile(
        r"""^[a-zA-Z]\w*   # identifier
        (?:\s*::\s*[a-zA-Z]\w*)*  # sequence of ('-' identifier)
        $""",
        re.ASCII | re.VERBOSE,
    )

    @classmethod
    def is_valid_path(cls, path: str) -> bool:
        """Check if *path* is a valid path identifier, i.e.
        *id {:: id}*, with possible spaces around '::'.

        Parameters
        ----------
        path : str
            String containing the path identifier.

        Returns
        -------
        bool
            True when path is valid.
        """
        return cls.PathIdentifierRe.match(path) is not None

    # id { - id} * regexp, with no spaces
    FilePathIdentifierRE = re.compile(
        r"""^[a-zA-Z]\w*   # identifier
        (?:-[a-zA-Z]\w*)*  # sequence of ('-' identifier)
        $""",
        re.ASCII | re.VERBOSE,
    )

    @classmethod
    def is_valid_file_path(cls, path: str) -> bool:
        """Check if *path* is a valid file path identifier, i.e.
        *id {- id}*, with no possible spaces around '-'.

        The path string is the basename of a module or an instance file.

        Parameters
        ----------
        path : str
            String containing the path identifier.

        Returns
        -------
        bool
            True when path is valid.
        """
        return cls.FilePathIdentifierRE.match(path) is not None

    @property
    def is_valid(self) -> bool:
        """True when path is a sequence of Identifier."""
        return self._is_valid

    @property
    def is_protected(self) -> bool:
        """True when path is from a protected source, i.e., a string."""
        return not self.is_valid

    @property
    def path_id(self) -> Union[List[Identifier], str]:
        """PathId as a list of Identifier, or a string if protected."""
        return self._path_id

    @property
    def as_string(self) -> str:
        """Compute name by joining name parts with '::'."""
        if self.is_protected:
            return str(self.path_id)
        return "::".join(cast(Identifier, p).value for p in self.path_id)

    def __str__(self) -> str:
        """Generate string representation of the PathIdentifier. Pragmas are not included."""
        return self.as_string


class ModuleItem(SwanItem):  # numpydoc ignore=PR01
    """Base class for module body item or module interface item."""

    def __init__(self) -> None:
        super().__init__()


class Declaration(HasPragma):  # numpydoc ignore=PR01
    """Base class for declarations."""

    def __init__(self, id: Identifier, pragmas: Optional[List[Pragma]] = None) -> None:
        super().__init__(pragmas)
        self._id = id
        SwanItem.set_owner(self, self._id)

    @property
    def id(self) -> Identifier:
        """Language item identifier."""
        return self._id

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        if self.owner is None:
            raise ScadeOneException("No owner")
        path = cast(SwanItem, self.owner).get_full_path()
        id_str = self.id.value
        return f"{path}::{id_str}"

    @property
    def has_definition(self) -> bool:
        """True if declaration has a definition part."""
        raise ScadeOneException("has_definition property not implemented for " + str(type(self)))

    @property
    def is_external(self) -> bool:
        """True if declaration has no definition.

        Check if there is no alternative declaration in the module (interface or body).
        Warn if any, and raise an error if inconsistent.
        """
        if (module := self.module) is None:
            raise ScadeOneException(f"No module for declaration {self.id.value}")
        # alternative declaration in interface or in body, if any
        other_decl = None
        if module.is_interface:
            # look in body for alternative declaration, if any
            if (
                (mod := module.body())  # type: ignore
                and (decl := mod.get_declaration(self.id.value, local_only=True))
                and isinstance(decl, type(self))
            ):
                other_decl = decl
        else:
            # in a body, look in interface for alternative declaration, if any
            if (
                (mod := module.interface())  # type: ignore
                and (decl := mod.get_declaration(self.id.value, local_only=True))
                and isinstance(decl, type(self))
            ):
                other_decl = decl
        if other_decl is not None:
            # declaration is in both interface and body, warn if same declaration kind (no check about definition itself!)
            # error if inconsistent declaration *and* definition
            # No other checks are done.
            LOGGER.warning(
                f"Declaration {self.id.value} is declared in interface and body of module {module.get_full_path()}."
            )
            if self.has_definition != other_decl.has_definition:
                raise ScadeOneException(
                    f"Inconsistent `is_external` declaration for {self.id.value} in interface and body of module {module.get_full_path()}."
                )
        return not (self.has_definition)

    @property
    def is_public(self) -> bool:
        """True if declaration is public.

        A declaration is public if:

        - it is declared in a module interface,
        - or it is declared in a module body, but the module has no interface.

        A declaration is private if it is declared in a module body, and the module has an interface,
        and there is no declaration with the same name in the module interface.

        If declared in both a module interface and body, the declaration is considered as public,
        but a warning is issued.

        """
        # Proceed with simple checks.
        # Other cases, like multiple declarations of same object
        # or another object kind with same name is not handled.
        if (module := self.module) is None:
            raise ScadeOneException(f"No module for declaration {self.id.value}")

        elif module.is_interface:
            # default to public, but check and warn for declaration in body (only check done)
            if (
                (body := module.body())  # type: ignore
                and (decl := body.get_declaration(self.id.value, local_only=True))
                and isinstance(decl, type(self))
            ):
                LOGGER.warning(
                    f"Declaration {self.id.value} is declared in interface and body of module {module.get_full_path()}."
                )
            return True
        else:  # module body
            if (interface := module.interface()) is None:  # type: ignore
                # no interface, so all declarations are public.
                return True
            # module has an interface
            if (decl := interface.get_declaration(self.id.value, local_only=True)) and isinstance(
                decl, type(self)
            ):
                # declaration is in interface, warn if same declaration. No other checks are done.
                LOGGER.warning(
                    f"Declaration {self.id.value} is declared in interface and body of module {module.get_full_path()}."
                )
                return True
            else:
                # declaration is not in interface, so it is private.
                return False


class Expression(HasPragma):  # numpydoc ignore=PR01
    """Base class for expressions."""

    def __init__(self) -> None:
        HasPragma.__init__(self)

    def set_pragmas(self, pragmas: List[Pragma]) -> None:
        """Set pragmas for the equation."""
        self._pragmas = pragmas
        SwanItem.set_owner(self, self._pragmas)


class TypeExpression(SwanItem):  # numpydoc ignore=PR01
    """Base class for type expressions."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def is_predefined(self) -> bool:
        """True if type expression is a predefined type."""
        return False


class GroupTypeExpression(SwanItem):  # numpydoc ignore=PR01
    """Base class for group type expressions."""

    def __init__(self) -> None:
        super().__init__()


class Luid(SwanItem):  # numpydoc ignore=PR01
    """Class for LUID support.
    The '$' prefix is not saved (potentially removed at creation)."""

    LuidRE = re.compile(r"^\$?[a-zA-Z]\w*$", re.ASCII)

    def __init__(self, value: str) -> None:
        super().__init__()
        self._luid = value[1:] if value and value[0] == "$" else value

    @property
    def value(self) -> str:
        """Luid value."""
        return self._luid

    def as_luid(self) -> str:
        """Luid value with '$' prefix. Equivalent to str(luid)."""
        return f"${self.value}"

    @staticmethod
    def is_valid(luid: str) -> bool:  # numpydoc ignore=PR01
        """True when a luid is a valid LUID."""
        return Luid.LuidRE.match(luid) is not None

    def __str__(self) -> str:
        return self.as_luid()


class Lunum(SwanItem):  # numpydoc ignore=PR01
    """Class for LUNUM support: '#' is part of the LUNUM."""

    LunumRE = re.compile(r"^\#\d+$", re.ASCII)

    def __init__(self, value: str) -> None:
        super().__init__()
        self._luid = value

    @property
    def value(self) -> str:
        """Luid value as a string."""
        return self._luid

    @staticmethod
    def is_valid(lunum: str) -> bool:  # numpydoc ignore=PR01
        """True when a lunum is a valid LUNUM."""
        return Lunum.LunumRE.match(lunum) is not None

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Lunum):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class LunumManager:
    """Manage local unique numbers (lunum) for diagram objects."""

    def __init__(self):
        self._lunums = set()

    @staticmethod
    def int_of_lunum(lunum: Lunum) -> int:
        """Convert a Lunum to an integer.
        Returns -1 if invalid, or cannot be converted to an integer (too large)"""
        if lunum.is_valid(lunum.value):
            try:
                return int(lunum.value[1:])  # remove '#' from lunum value
            except ValueError:
                return -1
        return -1

    @staticmethod
    def get_lunum_manager(obj: SwanItem | None) -> Optional["LunumManager"]:
        """Get the LunumManager of an object, if any."""
        if manager := getattr(obj, "_lunum_manager", None):
            return cast(LunumManager, manager)
        if obj and obj.owner:
            return LunumManager.get_lunum_manager(cast(SwanItem, obj.owner))
        return None

    def set_lunums(self, lunums: Iterable[Lunum]):
        """Store lunums, discarding invalid ones (-1) and converting to integers."""
        self._lunums = set(
            li for li in (LunumManager.int_of_lunum(lu) for lu in lunums) if li != -1
        )

    def get_next_lunum(self) -> Lunum:
        """Get the next unique local Lunum."""
        missing = 0
        while missing in self._lunums:
            missing += 1
        self._lunums.add(missing)
        return Lunum(f"#{missing}")


class Variable(SwanItem):  # numpydoc ignore=PR01
    """Base class for Variable and ProtectedVariable."""

    def __init__(self) -> None:
        super().__init__()


class Equation(HasPragma):  # numpydoc ignore=PR01
    """Base class for equations."""

    def __init__(self) -> None:
        HasPragma.__init__(self)

    def set_pragmas(self, pragmas: List[Pragma]) -> None:
        """Set pragmas for the equation."""
        self._pragmas = pragmas
        SwanItem.set_owner(self, self._pragmas)


# =============================================
# Protected Items
# =============================================


class ProtectedItem(SwanItem):  # numpydoc ignore=PR01
    """Base class for protected data. A protected data
    is a piece of Swan code enclosed between markups, mostly to store
    syntactically incorrect code. A protected data is enclosed within the pair
    ``{markup%`` .. ``%markup}``, where *markup* is defined by the
    regular expression: ['a'-'z' 'A'-'Z' 0-9 _]*.

    See :py:class:`Markup` for existing markups.
    """

    def __init__(self, data: str = "", markup: str = Markup.Syntax) -> None:
        super().__init__()
        self._markup = markup
        self._data = data

    @property
    def is_protected(self) -> bool:
        """Tell if item is syntactically protected and provided as a string."""
        return True

    def has_markup(self, markup: str) -> bool:
        """Check if protected data has the specified *markup*.

        Parameters
        ----------
        markup : str
            String markup.

        Returns
        -------
        result: bool
            True when instance markup is same as parameter.
        """
        return self._markup == markup

    @property
    def data(self) -> str:
        """Protected data between markups.

        Returns
        -------
        str
            Protected data.
        """
        return self._data

    @property
    def markup(self) -> str:
        """Protection markup.

        Returns
        -------
        str
            Markup string.
        """
        return self._markup

    def __str__(self) -> str:
        """Generate a string representation of the protected data."""
        return Markup.to_str(self.data, markup=self.markup)
