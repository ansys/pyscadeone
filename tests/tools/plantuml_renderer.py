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

from typing import Any, Callable, Optional
import os
from io import StringIO
from pathlib import Path
import subprocess
from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.svc.common.renderer as R


# This module provides a PlantUML renderer for ScadeOne documents.
# It allows rendering of ScadeOne DElt documents into PlantUML format.
# to find out problem in the rendering process.
# You can set the environment variable PLANTUML_JAR or
# Usage:
# with proper number of dots in the import path:
# import sys
# sys.path.append("C:/path/to/pyscadone")
# from tests.tools.plantuml_renderer import to_puml
# to_puml(doc, out_dir="C:/Tmp", note="This is a note for the diagram")


class PumlRenderer:
    PlantUMLJAR = os.getenv("PLANTUML_JAR", "C:/Program Files/PlantUML/plantuml.jar")

    def __init__(self, note: str) -> None:
        self._buffer: StringIO = StringIO()
        self._content: StringIO = StringIO()
        self._rendered = {}
        self._links = []
        self.note = note

    def render(self, doc: R.DElt) -> str:
        self._buffer.write("@startuml\n")
        if self.note:
            self._buffer.write(f"note as UserNote\n{self.note}\nend note\n")
        text = R.Renderer(stream=self._content)
        tmp_doc = R.Document()
        tmp_doc << doc
        text.render(tmp_doc, error_ok=True)
        self._buffer.write(f'note as Content\n"{self._content.getvalue()}"\nend note\n')
        self._render(doc)
        self._buffer.write("\n" + "\n".join(self._links) + "\n")
        self._buffer.write("@enduml\n")
        return self._buffer.getvalue()

    def _render(self, doc: R.DElt) -> None:
        def _get_render_fn(doc) -> Callable[[R.Renderer, R.DElt], None]:
            "Auxiliary function to get the render function, which is a method of the Renderer class"
            class_name = doc.__class__.__name__
            func = getattr(self, f"_render_{class_name}", self._render_NoFunc)
            return func

        _current_doc = doc
        while _current_doc:
            _id = id(_current_doc)
            if _id in self._rendered:
                self._buffer.write(f"' {_id} already rendered\n")
                continue
            self._rendered[_id] = True
            func = _get_render_fn(_current_doc)
            func(_current_doc)
            if _current_doc.next is not None:
                self._links.append(f"{id(_current_doc)} --> {id(_current_doc.next)} : next")
            _current_doc = _current_doc.next

    def _render_NoFunc(self, doc) -> None:  # pylint: disable=C0103
        class_name = doc.__class__.__name__
        raise ScadeOneException(f"Render._render_{class_name}() does not exist")

    def _add_field(self, obj: R.DElt, field: str, value: Any) -> None:
        """Add a field to the object representation."""
        self._buffer.write(f"{id(obj)} : {field} = {value}\n")

    def _render_DElt(self, doc: R.DElt) -> None:
        self._buffer.write(f"object {id(doc)}\n")
        self._add_field(doc, "type", doc.__class__.__name__)

    def _render_DText(self, doc: R.DText) -> None:
        self._render_DElt(doc)
        self._add_field(doc, "text", f'"{doc.string}"')

    def _render_DLineBreak(self, doc: R.DLineBreak) -> None:
        self._render_DElt(doc)

    def _render_DIndent(self, doc: R.DIndent) -> None:
        self._render_DElt(doc)
        self._add_field(doc, "indent", doc.indent.name)

    def _render_DBlock(self, doc: R.DBlock) -> None:
        self._render_DElt(doc)
        self._add_field(doc, "doc", id(doc.doc))
        self._links.append(f"{id(doc)} --> {id(doc.doc)} : doc")
        self._render(doc.doc)


def to_puml(doc: R.DElt, out_dir: Optional[str] = None, note: Optional[str] = None) -> None:
    """Render aR. DElt document to a PlantUML file.
    The document is saved in the specified output directory
    as a PlantUML file with a name based on the document's ID.

    Parameters
    ----------
    doc :R. DElt
        document to render.
    note : str
        Note to add to the PlantUML file.
    out_dir : str
        Output directory where the PlantUML file will be saved.
    """
    _out_dir = Path(out_dir) if out_dir else Path("C:/Tmp")
    _out_dir.mkdir(parents=True, exist_ok=True)
    puml = PumlRenderer(note)
    content = puml.render(doc)
    puml = _out_dir / f"ObjectDiagram_{id(doc)}.puml"
    puml.write_text(content, encoding="utf-8")
    if Path(PumlRenderer.PlantUMLJAR).is_file():
        subprocess.run(
            ["java", "-jar", str(PumlRenderer.PlantUMLJAR), str(puml)],
            check=True,
        )


PumlRenderer.PlantUMLJAR = r"C:\Program Files\PlantUML\plantuml-mit-1.2025.2.jar"
