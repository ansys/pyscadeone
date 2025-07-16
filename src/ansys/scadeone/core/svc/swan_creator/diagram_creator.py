# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2024 ANSYS, Inc.
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

from typing import TYPE_CHECKING, List, Union, Optional, cast

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.storage import SwanString

if TYPE_CHECKING:
    from ansys.scadeone.core import swan


class DiagramFactory:
    _instance = None

    def __init__(self) -> None:
        from ansys.scadeone.core.model.loader import SwanParser

        self._parser = SwanParser(LOGGER)

    def __new__(cls, *args, **kwargs) -> "DiagramFactory":
        if not cls._instance:
            cls._instance = super(DiagramFactory, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def create_block(diagram: "swan.Diagram", instance: "swan.Operator") -> "swan.Block":
        """Create a call operator block.

        Parameters
        ----------
        diagram: Diagram
            Diagram where the block will be added.
        instance: Operator
            Operator instance. A **use** directive may be required in the *diagram*'s module to
            resolve the operator module.

        Returns
        -------
        Block
            Block object

        Raises
        ------
        ScadeOneException
            If the operator does not have a module or if the diagram does not have a module.
        """
        from ansys.scadeone.core.swan import Block, PathIdOpCall
        from ansys.scadeone.core.model import Model

        path_id = Model.get_path_in_module(instance, diagram.module)
        path_id_op_call = PathIdOpCall(path_id, [], [])
        return Block(path_id_op_call)

    @staticmethod
    def create_def_block(instance: "swan.VarDecl") -> "swan.DefBlock":
        """Create a definition block from a variable declaration."""
        from ansys.scadeone.core.swan import DefBlock, EquationLHS, LHSItem

        item = LHSItem(instance.id)
        eq = EquationLHS([item])
        return DefBlock(eq)

    @staticmethod
    def create_expr_block(
        diagram: "swan.Diagram", declaration: "swan.Declaration"
    ) -> "swan.ExprBlock":
        """Create an expression block from a variable declaration."""
        from ansys.scadeone.core.swan import ExprBlock, PathIdExpr, ConstDecl, VarDecl, SensorDecl
        from ansys.scadeone.core.model import Model

        if not isinstance(declaration, (ConstDecl, VarDecl, SensorDecl)):
            raise ScadeOneException("declaration must be a constant, variable or sensor object")
        path_id = Model.get_path_in_module(declaration, diagram.module)
        path_id_expr = PathIdExpr(path_id)
        return ExprBlock(path_id_expr)

    @staticmethod
    def create_bar() -> "swan.Bar":
        """Create a group."""
        from ansys.scadeone.core.swan import Bar

        return Bar()

    def create_wire(
        self,
        source: Union["swan.DiagramObject", tuple["swan.DiagramObject", str]],
        targets: Union[List["swan.DiagramObject"], List[tuple["swan.DiagramObject", str]]],
    ) -> "swan.Wire":
        """Create a wire between a source block and one or more targets block
        with or without group declarations."""
        from ansys.scadeone.core.swan import Connection, PortExpr, Wire

        source_obj, source_adp = self._split_wire_end(source)
        source_port_expr = PortExpr(source_obj.lunum)
        source_conn = Connection(source_port_expr, source_adp)
        target_conns = []
        for target in targets:
            target_obj, target_adp = self._split_wire_end(target)
            target_port_expr = PortExpr(target_obj.lunum)
            target_conns.append(Connection(target_port_expr, target_adp))
        return Wire(source_conn, target_conns)

    def _split_wire_end(
        self, end: Union["swan.DiagramObject", tuple["swan.DiagramObject", str]]
    ) -> tuple["swan.DiagramObject", "swan.GroupAdaptation"]:
        """Return a tuple containing the diagram object and the group adaptation
        of a wire source or target"""
        if isinstance(end, tuple):
            end_obj = end[0]
            end_adp = self._parse_group_adaptation(end[1])
        else:
            end_obj = end
            end_adp = None
        return end_obj, end_adp

    def _parse_group_adaptation(self, adp: str) -> "swan.GroupAdaptation":
        """Convert a group adaptation expression into a GroupAdaptation object."""
        from ansys.scadeone.core.swan import Diagram, Wire

        swan_code = f"diagram (#0 wire #1 .({adp}) => #2)"
        diag_str = SwanString(swan_code, "new_op")
        diag = cast(Diagram, self._parser.scope_section(diag_str))
        wire = cast(Wire, diag.objects[0])
        return wire.source.adaptation


class DiagramAdder:
    def __init__(self, owner: "swan.Diagram") -> None:
        self._owner = owner
        self._lunum = -1

    def add_block(self, block: "swan.Block") -> None:
        """Add a block to the diagram."""
        self._add_diagram_object(block)

    def add_def_block(self, def_block: "swan.DefBlock") -> None:
        """Add a definition block to the diagram."""
        self._add_diagram_object(def_block)

    def add_expr_block(self, expr_block: "swan.ExprBlock") -> None:
        """Add an expression block to the diagram."""
        self._add_diagram_object(expr_block)

    def add_bar(self, bar: "swan.Bar") -> None:
        """Add a group to the diagram."""
        self._add_diagram_object(bar)

    def _check_for_wire(self, wire: "swan.Wire") -> Optional["swan.Wire"]:
        # Check if wire is already in the diagram with the same source characteristics
        from ansys.scadeone.core.swan import Wire

        source_lunum = wire.source.port.lunum.value
        source_adaptation = wire.source.adaptation
        # look for candidate wires with the same source lunum
        candidates = [obj for obj in self._owner.objects if isinstance(obj, Wire)]

        def _check(w: "swan.Wire") -> bool:
            same_lunum = source_lunum == w.source.port.lunum.value
            same_adaptation = source_adaptation == w.source.adaptation
            return same_lunum and same_adaptation

        wires = list(filter(_check, candidates))
        if len(wires) == 0:
            return None
        return wires[0]

    def add_wire(self, wire: "swan.Wire") -> "swan.Wire":
        """Add a wire to the diagram."""
        if existing_wire := self._check_for_wire(wire):
            # Check if the wire is already in the diagram with the same source
            # and add the target to the existing wire
            existing_wire.targets.extend(wire.targets)
            return existing_wire

        # No candidate wires found, add the wire to the diagram
        self._add_diagram_object(wire)
        return wire

    def _add_diagram_object(self, object: "swan.DiagramObject") -> None:
        """Add a diagram object to the diagram."""
        from ansys.scadeone.core.swan import Lunum

        self._generate_next_lunum()
        object._lunum = Lunum(f"#{self._lunum}")
        self._lunum += 1
        object.owner = self._owner
        if not self._owner._objects:
            self._owner._objects = [object]
        else:
            self._owner._objects.append(object)

    def _generate_next_lunum(self) -> None:
        """Generate the next lunum for the diagram objects."""
        if not self._lunum == -1:
            return
        if not self._owner._objects:
            self._lunum = 0
        else:
            self._lunum = max([int(obj.lunum.value[1:]) for obj in self._owner._objects]) + 1


class DiagramCreator:
    def __init__(self) -> None:
        self._diagram_adder = DiagramAdder(self)

    def add_block(self, instance: "swan.Operator") -> "swan.Block":
        """Add an operator call to the operator.

        Parameters
        ----------
        instance: Operator
            Operator instance.

        Returns
        -------
        Block
            Block object.
        """
        block = DiagramFactory().create_block(self, instance)
        self._diagram_adder.add_block(block)
        return block

    def add_def_block(self, variable: "swan.VarDecl") -> "swan.DefBlock":
        """Add a definition block to the operator.

        Parameters
        ----------
        variable: VarDecl
            Local, input or output variable.

        Returns
        -------
        DefBlock
            DefBlock object.
        """
        def_block = DiagramFactory().create_def_block(variable)
        self._diagram_adder.add_def_block(def_block)
        return def_block

    def add_expr_block(self, declaration: "swan.Declaration") -> "swan.ExprBlock":
        """Add an expression block to the operator.

        Parameters
        ----------
        declaration: Declaration
            Local or output variable.

        Returns
        -------
        ExprBlock
            ExprBlock object.
        """
        expr_block = DiagramFactory().create_expr_block(self, declaration)
        self._diagram_adder.add_expr_block(expr_block)
        return expr_block

    def add_bar(self) -> "swan.Bar":
        """Add a bar to the operator.

        Returns
        -------
            Bar
                Bar object.
        """
        bar = DiagramFactory().create_bar()
        self._diagram_adder.add_bar(bar)
        return bar

    def connect(
        self,
        source: Union["swan.DiagramObject", tuple["swan.DiagramObject", str]],
        targets: Union[
            "swan.DiagramObject",
            tuple["swan.DiagramObject", str],
            List["swan.DiagramObject"],
            List[tuple["swan.DiagramObject", str]],
        ],
    ) -> "swan.Wire":
        """Connect a block to one or more blocks.

        Parameters
        ----------
        source: DiagramObject
            Block object.
        targets: Union[DiagramObject, List[DiagramObject]]
            A block object or a list of block objects.

        Returns
        -------
        Wire
            Wire object that connects the blocks.
        """
        if not isinstance(targets, list):
            targets = [targets]
        wire = DiagramFactory().create_wire(source, targets)
        added_wire = self._diagram_adder.add_wire(wire)
        return added_wire
