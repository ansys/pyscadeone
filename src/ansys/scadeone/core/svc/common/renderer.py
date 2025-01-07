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

# cspell: ignore startuml enduml unmark
# pylint: disable=W0621

"""
This module defines a *Document* concept and render a document.
A Document is composed of DElt instances which consist in:

- printable information (text, newline)
- indentation information
- group or list of DElt
- and the next DElt.

Therefore DElt items form a tree structure:
- sequence of DElt, thanks to the next DElt contained in each DElt
- Structure with the DBlock, which contains DElt.

For instance::

    (
        Hello World !
        Hi there
    )

can be conceptually represented as:

.. uml::

    @startuml
    hide circle
    hide method

    class LPar <<DText>> {
    {field} text: "("
    next
    }

    class indent <<DIndent>> {
    next
    }

    class nl <<DLineBreak>> {
    next
    }

    class list <<DList>> {
    next
    }

    class b1 <<DBlock>> {
    doc
    }

    class hello <<DText>> {
    text: "Hello "
    next
    }
    class world<<DText>> {
    text: "World !"
    }

    class b2 <<DBlock>> {
    doc
    }

    class hi<<DText>> {
    text: "Hi"
    next
    }

    class there <<DText>> {
    text: "there"
    }


    class unindent <<DIndent>> {
    next
    }

    class nl2 <<DLineBreak>> {
    next
    }

    class RPar <<DText>> {
    {field} text: ")"
    }

    hello::next --> world
    b1::doc --> hello
    hi::next --> there
    b2::doc --> hi
    list --> b1
    list --> b2
    together {
       class b1
       class b2
    }

    LPar::next --> indent
    indent::next --> nl
    nl::next --> list
    list::next --> unindent
    unindent --> nl2
    nl2 --> RPar

    @enduml


Methods
-------

The :py:class:`Document` defines the main object. A
document is rendered by a :py:class:`Render`object.

Once a document object is created, several operations are
provided to build the document. Operations are provide as
functions.

String shortcuts can be used as kind of interpreted commands.
A shortcut is prefixed with a **@** character and may
have options separated with **:**

Methods, with their shortcut after the slash are:

text(str)
    Create a text doc element.

indent(), unindent() / i, u
    Add or remove an indentation level. The level of the
    indentation is handle by the render object.

mark(), unmark() / m, M
    Set/unset the next indentation to the column of the last
    rendered document. This can be used to align lines after
    a parenthesis

nl(bool = True) / n
    Insert a line break. It has a boolean option which inserts
    an indentation right after a line break.

    Shortcut is "nl:t" or "nl:f" for True or False

sep(str, bool = False) / s
    Create a new document to be used as a separator for lists.
    The optional boolean inserts a newline with indentation if
    True.

    Shortcut is "@s:<txt>" where txt is the separator. For instance
    "@s:;" defines ";" as a separator. A line break can be added
    line the *nl* command with the syntax "@s:;:t"

block(doc, ...)
    Create a block with the docs given in arguments.
    A block contains the docs, and is itself a doc element.
    It is used to create structure in document.
    A block itself is a document element that can be
    connected to other elements.

doc_list(doc, ..., sep=, start=, last=)
    Create a list of document elements, with a possible
    element separator and start, end separators element.

    Newline can be handled by the separator element.
    A list is itself a document element that can be
    connected to other elements


Note: as *nl* and *sep* commands may generate an indentation,
the *indent* must be called before, as it "pushes" the new
indentation.

Document element can be added to the main document using '<<'.
The '<<' operator adds the document element and returns the
main document. The argument can be a string, a shortcut, or
an other document element:
Example:

>>> doc = Document()
>>> x = doc << "Hello" << " " << "world"
>>> x == doc
True

A document element has also a '<<' operator which set
the argument as next element and return it (different from
*Document.<<()*). Arguments are DElt only

>>> h = text("Hello")
>>> w = text("World")
>>> d = h << w
>>> d == w
True

Document rendering:

>>> import sys
>>> r = Renderer(sys.stdout)
>>> r.render(doc)
Hello world

Examples
--------

Creation of a document. We use "@m" and "@M" to mark
specific indentation after '('. The "@s" separator is
is used with and without newline:

>>> def build_doc():
...   doc = Document()
...   doc << "node"
...   doc << " " << "Op" << "(" << "@m"
...   doc << doc_list("1", "2", "3", sep="@s:;:t", start="/* in */") << ")"
...   doc << "@M" << "@i" << "@n" << "return (" << "@m"
...   io = [
...      block("a", ": ", "T", ";"),
...      block("b", ": ", "T", ";"),
...   ]
...   doc << doc_list(*io, sep="@n") << ")" << "@M" << "@u" << "@n"
...   doc << "{" << "@i" << "@n"
...   doc << "let" << "@m" << "@n"
...   doc << "/* hello */" << "@n"
...   doc << "/* world */" << "@M"
...   doc << "@u" << "@n" << "}" << "@n"
...   return doc

Rendering:
>>> Renderer(sys.stdout).render(build_doc())
node Op(/* in */1;
        2;
        3)
  return (a: T;
          b: T;)
{
  let
     /* hello */
     /* world */
}

The :py:class:`Renderer` uses a stream as parameter,
which can be a stream buffer, of file, ... It can
be also derived to implement other kind of rendering.
"""  # numpydoc ignore

from enum import Enum, auto
import re
from typing import Any, Optional, Union, IO
from typing_extensions import Self

from ansys.scadeone.core.common.exception import ScadeOneException


class DElt:
    """Document base class."""

    def __init__(self) -> None:
        self._next: Optional[Self] = None

    def cons(self, doc: Self) -> Self:
        """Add next element and return it."""
        self._next = doc
        return doc

    @property
    def next(self) -> Union[Self, None]:
        """Return the next element."""
        if self._next == self:
            raise ScadeOneException(f"Document connected to itself: {repr(self)}")
        return self._next

    def __lshift__(self, doc) -> Self:
        """Add doc as next element and return it."""
        doc = to_doc(doc)
        return self.cons(doc)


class DText(DElt):
    """Class to store a simple text."""

    def __init__(self, string: str) -> None:
        super().__init__()
        self._string = string

    @property
    def string(self) -> str:
        """Return the text string."""
        return self._string


class DBlock(DElt):
    """Class to store a block of documents (sequence of documents)."""

    def __init__(self, doc: Optional[DElt] = None) -> None:
        super().__init__()
        self._first = doc if doc else DElt()
        self._end = self._first

    @property
    def doc(self) -> DElt:
        """Return the first document of the block."""
        return self._first

    def __lshift__(self, doc) -> Self:
        """Add doc to the end of the block and return the block."""
        doc = to_doc(doc)
        self._end = self._end.cons(doc)
        return self


class DLineBreak(DElt):
    """Class to store a line break."""

    def __init__(self, with_indent=True) -> None:
        super().__init__()
        self._with_indent = with_indent

    @property
    def with_indent(self) -> bool:
        """Return True if indentation is added after the line break."""
        return self._with_indent


class EIndentation(Enum):
    """Kind of indentation."""

    #: No indentation
    NOTHING = auto()
    #: Start new indentation
    INDENT = auto()
    #: End last indentation, including mark
    UNINDENT = auto()
    #: Mark last column for indentation
    MARK = auto()


class DIndent(DElt):
    """Class to store an indentation."""

    def __init__(self, indent: EIndentation) -> None:
        super().__init__()
        self._indent = indent

    @property
    def indent(self) -> EIndentation:
        """Return the kind of indentation."""
        return self._indent


# Document creation functions
CmdRe = re.compile("^(?P<c>@[a-zA-Z]+)(?P<a>(?::[^:])*)")
Cmd = {
    "@i": "indent",
    "@u": "unindent",
    "@m": "mark",
    "@M": "unmark",
    "@n": "nl",
    "@s": "sep",
}


def fix_arg(arg):
    """Transform arg into bool, int or keep it"""
    if arg == "t":
        return True
    if arg == "f":
        return False
    if isinstance(arg, int):
        return int(arg)
    return arg


def cmd(arg):
    """Check if arg is a document manipulation string command
    and returns its result if it is the case, else None."""
    if not isinstance(arg, str):
        return None
    m = CmdRe.match(arg)
    if not m:
        return None
    if m["c"] not in Cmd:
        return None
    func = Cmd[m["c"]]
    # first item will always be empty.
    args = m["a"].split(":")[1:]
    args = [fix_arg(arg) for arg in args]
    return func(*args)


def to_doc(arg) -> DElt:
    """Create a DElt:
    - If arg is already a DElt, return it
    - If arg is a shortcut, returns command
    - Else return a text()."""
    if isinstance(arg, DElt):
        return arg
    res = cmd(arg)
    if res:
        return res
    return text(arg if arg else "")


def text(txt: str) -> DElt:
    """Create a DText from txt. No command processing"""
    return DText(txt)


def nl(with_indent: bool = True):
    """Add a new line. If `with_indent is True,
    indentation is added beginning of next line."""
    return DLineBreak(with_indent)


def indent() -> DElt:
    """Add an indentation. Indentation is set by Render."""
    return DIndent(EIndentation.INDENT)


def unindent() -> DElt:
    """Back to previous indentation. Indentation is set by Render."""
    return DIndent(EIndentation.UNINDENT)


def mark() -> DElt:
    """Mark last column as reference for indentation.

    Indented new lines use column-spaces. Column depends on
    latest rendered document."""
    return DIndent(EIndentation.MARK)


def unmark() -> DElt:
    """Remove previous mark"""
    return DIndent(EIndentation.UNINDENT)


def block(first: DElt, *args) -> DElt:
    """Create a block of n-documents. A block is assimilated
    as a single document. Each internal document are rendered in sequence.
    """
    first = to_doc(first)
    current_doc = first
    for doc in args:
        doc = to_doc(doc)
        current_doc.cons(doc)
        current_doc = doc
    return DBlock(first)


def doc_list(
    doc,
    *args,
    sep: Optional[Any] = None,
    start: Optional[Any] = None,
    last: Optional[Any] = None,
) -> DElt:
    """Build a list of documents.

    Args:
        doc (Any): first document, followed by any number of documents
        sep (Optional[Any], optional): separator. Defaults to None.
        start (Optional[Any], optional): document at beginning of list.
        Defaults to None.
        last (Optional[Any], optional): document at end of list.
        Defaults to None.

    Returns:
        Document: _description_
    """
    _current_doc = to_doc(doc)
    if start:
        _first = to_doc(start)
        _first.cons(_current_doc)
    else:
        _first = _current_doc
    _sep = to_doc(sep)
    for _arg in args:
        _doc = to_doc(_arg)
        if sep:
            _current_doc = _current_doc.cons(DBlock(_sep))
        _current_doc = _current_doc.cons(_doc)
    if last:
        _current_doc.cons(to_doc(last))
    return DBlock(_first)


def sep(char: str, newline: bool = False) -> DElt:
    """Helper to create a document separator (comma, semi-col, ...)."""
    doc = text(char)
    if not newline:
        return doc
    doc.cons(nl(True))
    return DBlock(doc)


# Fix function references
for k, v in Cmd.items():
    Cmd[k] = globals()[v]


class Document(DBlock):
    """Document object.

    A document object contains the starting DElt and has the '<<' method.

    *a_doc* << *d_elt* => add *d_elt* and returns *a_doc*."""

    def __init__(self) -> None:
        super().__init__(DElt())

    @property
    def start_doc(self):
        """Return the first document."""
        return self.doc

    @property
    def end_doc(self):
        """Return the last document."""
        return self._end


class Renderer:
    """Rendering class.

    Render a document on a stream. The stream can be a file, a buffer, ...
    The rendering is done by calling the render method which applies to
    a specific DElt.

    """

    def __init__(
        self,
        stream: Optional[IO] = None,
        indent: Optional[int] = 2,
        initial_indent: Optional[int] = 0,
    ):
        """
        Args:
            stream (io.IO): Output stream
            indent (int, optional): default indentation. Defaults to 2.
            initial_indent (int, optional): initial indentation. Defaults to 0.
        """
        self._indent = indent
        self._initial_indent = initial_indent
        self._col = 0
        self._line = 0
        self._indent_stack = [initial_indent]
        self._stream = stream

    def set_stream(self, stream: IO):
        """Set the stream to render on."""
        self._stream = stream

    @property
    def lines(self) -> int:
        """Current line number"""
        return self._line

    @property
    def default_indent(self):
        """Default indent, as given in constructor."""
        return self._indent

    @property
    def curr_indent(self):
        """Current indent"""
        if self._indent_stack:
            return self._indent_stack[-1]
        raise ScadeOneException("Render.indent: empty stack")

    def render(self, doc: Document):
        """Render a document on the stream.

        Parameters
        ----------
        doc : Document
            Document to render

        Raises
        ------
        ScadeOneException
            Raised if there is no stream to render on, or an error is raised
        """
        if not self._stream:
            raise ScadeOneException("No stream to render on")
        if not isinstance(doc, Document):
            raise ScadeOneException("Renderer: Document expected")
        try:
            self._render(doc.start_doc)
        except Exception as e:
            raise ScadeOneException("Error during rendering") from e

    def _write(self, obj: Any):
        """Write obj on stream. str(obj) shall be a string without newlines"""
        text = str(obj)
        assert text.find("\n") == -1
        self._col += len(text)
        self._stream.write(text)  # type: ignore # (stream is IO)

    def _nl(self, with_indent: bool):
        self._stream.write("\n")  # type: ignore # (stream is IO)
        self._line += 1
        self._col = 0
        if with_indent:
            self._write(" " * self.curr_indent)

    def _push_indent(self):
        indent = self.curr_indent + self.default_indent
        self._indent_stack.append(indent)

    def _pop_indent(self):
        try:
            self._indent_stack.pop()
        except Exception:  # pylint: disable=broad-except
            self._indent_stack = [self._initial_indent]

    def _push_mark(self):
        self._indent_stack.append(self._col)

    def _render(self, doc: DElt):
        class_name = doc.__class__.__name__
        func = getattr(self, f"_render_{class_name}", self._render_NoFunc)
        func(doc)

    def _render_NoFunc(self, doc):  # pylint: disable=C0103
        class_name = doc.__class__.__name__
        raise ScadeOneException(f"Render._render_{class_name}() does not exist")

    def _render_DElt(self, doc: DElt):  # pylint: disable=C0103
        if doc.next:
            self._render(doc.next)

    def _render_DText(self, doc: DText):  # pylint: disable=C0103
        self._write(doc.string)
        self._render_DElt(doc)

    def _render_DBlock(self, doc: DBlock):  # pylint: disable=C0103
        self._render(doc.doc)
        self._render_DElt(doc)

    def _render_DLineBreak(self, doc: DLineBreak):  # pylint: disable=C0103
        self._nl(doc.with_indent)
        self._render_DElt(doc)

    def _render_DIndent(self, doc: DIndent):  # pylint: disable=C0103
        if doc.indent is EIndentation.INDENT:
            self._push_indent()
        elif doc.indent is EIndentation.UNINDENT:
            self._pop_indent()
        elif doc.indent is EIndentation.MARK:
            self._push_mark()
        self._render_DElt(doc)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
