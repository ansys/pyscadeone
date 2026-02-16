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

import os
import platform
from typing import Optional, Any
from string import Template
import shutil
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor, Owner, OwnerProperty
import ansys.scadeone.core.swan as Swan

if platform.system() == "Windows":
    Path("C:/Tmp").mkdir(exist_ok=True)
    tmp_dir = Path("C:/Tmp")
else:
    tmp_dir = Path("/tmp")


def log_diff(
    *, expected: str, actual: str, prefix: str = "diff", ext: str = ".txt", winmerge: bool = False
):
    """Save expected and actual values to files for comparison.

    Files are:
     - C:/Tmp/{prefix}_expected{ext}
     - C:/Tmp/{prefix}_actual{ext}

     Parameters
     ----------
     expected : str
         Expected value.
     actual : str
         Actual value from the test.
     prefix : str optional
         Prefix for the file names.
         Used to distinguish between different tests.
     ext : str, optional
         Generated files extensions by default ".txt"
    """
    if expected == actual:
        return
    actual_path = Path(f"{tmp_dir}/{prefix}_actual{ext}")
    expected_path = Path(f"{tmp_dir}/{prefix}_expected{ext}")
    expected_path.write_text(expected)
    actual_path.write_text(actual)
    if winmerge:
        try:
            subprocess.run(
                ["WinMergeU", "/e", "/s", "/u", str(expected_path), str(actual_path)],
                check=True,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "WinMerge not found. Please install WinMerge to use this feature."
            ) from e


def clear_directory(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


def versioned_swan_str(swan: str, origin: str, is_test_module: bool = False) -> SwanString:
    """Generate SwanString with version from swan code.

    Parameters
    ----------
    swan : str
        The Swan code to be processed.
    origin : str
        The origin of the Swan code  for information purposes.
    is_test_module : bool, optional
        True if the SwanString is for a test module, by default False.

    Returns
    -------
    SwanString
        The generated SwanString with version information.
    """
    return SwanString(gen_swan_version(is_test_module) + "\n" + swan, origin)


class XMLVisitor(SwanVisitor):
    """Visitor for XML representation of Swan AST.

    Usage:

        visitor = XMLVisitor()
        res = visitor.xml_string(swan_obj)
        visitor.visit(swan_obj)
        print(visitor.buffer)
    """

    node_template = Template('<node name="$name"$value owner="$owner" property="$property"$end>\n')
    end_template = "</node>\n"

    def __init__(self) -> None:
        super().__init__()
        self._owners: dict[str, ET.Element] = {}

    def xml_string(self, swan_obj: Swan.SwanItem) -> str:
        """Get XML representation of Swan object.

        Parameters
        ----------
        swan_obj : S.SwanItem
            The Swan object to be visited.

        Returns
        -------
        str
            The XML representation of the Swan object.
        """
        self._owners = {"None": ET.Element("Root")}
        self.visit(swan_obj)
        swan_xml = self._owners["None"][0]
        ET.indent(swan_xml, space="  ")
        return ET.tostring(swan_xml, encoding="unicode")

    @staticmethod
    def base_class(obj: Optional[Swan.SwanItem]) -> str:
        if obj is None:
            return "None"
        return obj.__class__.__name__.split(".")[-1]

    @staticmethod
    def owner_hash(owner: Optional[Swan.SwanItem]) -> str:
        if owner is None:
            return "None"
        return str(id(owner))

    def update_tree(
        self, swan_obj: Swan.SwanItem | None, elt: ET.Element, owner: Swan.SwanItem | None
    ) -> None:
        # Add element to tree under its owner
        owner_id = self.owner_hash(owner)
        if owner_id not in self._owners:
            raise ValueError(f"Owner id {owner_id} not found in owners")
        self._owners[owner_id].append(elt)
        # Case of leaves we do not keep track as owners
        if swan_obj is not None:
            self._owners[self.owner_hash(swan_obj)] = elt

    def visit_SwanItem(
        self, swan_obj: Swan.SwanItem, owner: Swan.SwanItem | None, owner_property: str | None
    ) -> None:
        elt = ET.Element(
            self.base_class(swan_obj),
            {
                "owner": self.base_class(owner),
                "property": owner_property if owner_property else "None",
            },
        )
        self.update_tree(swan_obj, elt, owner)

    def _visit(
        self, swan_obj: Swan.SwanItem, owner: Swan.SwanItem | None, owner_property: str | None
    ) -> None:
        super()._visit(swan_obj, owner, owner_property)

    def visit_builtin(
        self,
        object: Any,
        owner: Owner,
        owner_property: str | None,
    ) -> None:
        """Default visitor for builtin value of type `str`, `bool`, `int` or `float`."""
        elt = ET.Element(
            "builtin",
            {
                "owner": self.base_class(owner),
                "property": owner_property if owner_property else "None",
                "value": str(object),
            },
        )
        self.update_tree(None, elt, owner)

    def visit_Pragma(
        self,
        swan_obj: Swan.Pragma,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default Pragma visitor method."""
        elt = ET.Element(
            "Pragma",
            {
                "owner": self.base_class(owner),
                "property": owner_property if owner_property else "None",
            },
        )
        elt.text = str(swan_obj)
        self.update_tree(swan_obj, elt, owner)

    def visit_enum(self, swan_obj: Any, owner: Owner, owner_property: OwnerProperty) -> None:
        """Default visitor for enum values."""
        elt = ET.Element(
            self.base_class(swan_obj),
            {
                "owner": self.base_class(owner),
                "property": owner_property if owner_property else "None",
                "value": swan_obj.__class__.to_str(swan_obj),
            },
        )
        self.update_tree(None, elt, owner)

    def visit_BinaryOp(
        self,
        swan_obj: Swan.BinaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        self.visit_enum(swan_obj, owner, owner_property)

    def visit_GroupOperation(
        self,
        swan_obj: Swan.GroupOperation,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        self.visit_enum(swan_obj, owner, owner_property)

    def visit_IteratorKind(
        self,
        swan_obj: Swan.IteratorKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        self.visit_enum(swan_obj, owner, owner_property)

    def visit_NaryOp(
        self,
        swan_obj: Swan.NaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        self.visit_enum(swan_obj, owner, owner_property)

    def visit_NumericKind(
        self,
        swan_obj: Swan.NumericKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        self.visit_enum(swan_obj, owner, owner_property)

    def visit_UnaryOp(
        self,
        swan_obj: Swan.UnaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        self.visit_enum(swan_obj, owner, owner_property)


def swan_to_xml(swan: Swan.SwanItem) -> str:
    """Convert Swan object to XML string.

    Parameters
    ----------
    swan : S.SwanItem
        The Swan object to be converted.

    Returns
    -------
    str
        The XML representation of the Swan object.
    """
    visitor = XMLVisitor()
    return visitor.xml_string(swan)
