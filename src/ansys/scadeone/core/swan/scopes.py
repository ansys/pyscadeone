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


from typing import TYPE_CHECKING, Any, List, Optional

from .common import SwanItem, PragmaBase, Pragma

if TYPE_CHECKING:
    from .namespace import ScopeNamespace  # noqa: F401


class Scope(SwanItem, PragmaBase):  # numpydoc ignore=PR01
    """Scope definition:

    | *data_def* ::= *scope*
    | *scope* ::= { {{*scope_section*}} }"""

    def __init__(
        self, sections: List["ScopeSection"], pragmas: Optional[List[Pragma]] = None
    ) -> None:
        SwanItem.__init__(self)
        PragmaBase.__init__(self, pragmas)
        self._sections = sections
        self._pragmas = pragmas
        self.set_owner(self, self._sections)

    @property
    def sections(self) -> List["ScopeSection"]:
        """Scope sections."""
        return self._sections

    def get_declaration(self, name: str):
        """Returns the type, global, operator or variable declaration searching by namespace."""
        from ansys.scadeone.core.swan.namespace import ScopeNamespace

        ns = ScopeNamespace(self)
        return ns.get_declaration(name)

    def __str__(self) -> str:
        sections = "\n".join([str(section) for section in self.sections])
        return f"{{\n{sections}\n}}"


class ScopeSection(SwanItem):  # numpydoc ignore=PR01
    """Base class for scopes."""

    def __init__(self) -> None:
        super().__init__()
        self._is_text = False

    @property
    def is_text(self) -> bool:
        """True when section is given from {text%...%text} markup."""
        return self._is_text

    @is_text.setter
    def is_text(self, text_flag: bool):
        self._is_text = text_flag

    def get_declaration(self, name: str):
        from ansys.scadeone.core.swan.namespace import ScopeNamespace

        ns = ScopeNamespace(self)
        return ns.get_declaration(name)

    @classmethod
    def to_str(cls, section: str, items: List[Any], end: Optional[str] = ";") -> str:
        """Print *section* name with its list of *items*, one per line,
        ended with *sep* string."""
        item_str = "\n".join([f"    {item}{end}" for item in items])
        return f"{section}\n{item_str}"
