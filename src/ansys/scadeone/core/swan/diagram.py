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

# pylint: too-many-arguments

from collections import defaultdict
from enum import Enum, auto
from typing import List, Optional, Union, cast

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.svc.swan_creator.diagram_creator import DiagramCreator
import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes

from .equations import ActivateIf, ActivateWhen, DefByCase, EquationLHS, StateMachine
from .expressions import GroupAdaptation, PortExpr
from .instances import OperatorBase, OperatorExpression


class DiagramObject(common.SwanItem, common.PragmaBase):  # numpydoc ignore=PR01
    """Base class for diagram objects.

    *object* ::= ( [[ *lunum* ]] [[ *luid* ]] *description* [[ *local_objects* ]] )

    Parameters
    ----------
    lunum: Lunum (optional)
        Object local unique number within the current operator.

    luid: Luid (optional)
        Object local unique identifier within the current operator.

    locals: list DiagramObject
        List of local objects associated with the object.
        If locals is None, an empty list is created.
    """

    def __init__(
        self,
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
        locals: Optional[List["DiagramObject"]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        common.SwanItem.__init__(self)
        common.PragmaBase.__init__(self, pragmas)
        self._lunum = lunum
        self._luid = luid
        self._locals = locals if locals else []
        common.SwanItem.set_owner(self, self._locals)

    @property
    def lunum(self) -> Union[common.Lunum, None]:
        """Lunum of object, or None if no Lunum."""
        return self._lunum

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Luid of object, or None if no Luid."""
        return self._luid

    @property
    def locals(self) -> List["DiagramObject"]:
        """Local objects of object."""
        return self._locals

    @property
    def sources(
        self,
    ) -> List[tuple["DiagramObject", GroupAdaptation, Union[List[GroupAdaptation], None]]]:
        """Return a list of all diagram objects that are sources of current diagram object.
        A list item is a tuple of source object and the source and target adaptations used
        for connection if any.
        """
        diagram = self._get_diagram(self.owner)
        return diagram.get_block_sources(self)

    @property
    def targets(
        self,
    ) -> List[tuple["DiagramObject", GroupAdaptation, GroupAdaptation]]:
        """Return a list of all diagram objects that are targets of current diagram object.
        A list item is a tuple of target object and the source and target adaptations used
        for connection if any.
        """
        diagram = self._get_diagram(self.owner)
        return diagram.get_block_targets(self)

    def _get_diagram(self, diag_obj: "DiagramObject") -> "Diagram":
        """Get the diagram from a diagram object."""
        if isinstance(diag_obj, Diagram):
            return diag_obj
        return self._get_diagram(diag_obj.owner)


class Diagram(scopes.ScopeSection, DiagramCreator):  # numpydoc ignore=PR01
    """Class for a **diagram** construct."""

    def __init__(self, objects: List[DiagramObject] = None) -> None:
        super().__init__()
        if objects is None:
            self._objects = []
        else:
            self._objects = objects
        self._diag_nav = None
        common.SwanItem.set_owner(self, objects)

    @property
    def objects(self) -> List[DiagramObject]:
        """Diagram objects."""
        return self._objects

    def get_block_sources(
        self, obj: DiagramObject
    ) -> List[tuple[DiagramObject, Optional[GroupAdaptation], Optional[GroupAdaptation]]]:
        """Return a list of all diagram objects that are sources of current diagram.
        A list item is a tuple of source object and the source and target adaptations used
        for connection if any.
        """
        if self._diag_nav is None:
            self._consolidate()
        return self._diag_nav.get_block_sources(obj)

    def get_block_targets(
        self, obj: DiagramObject
    ) -> List[tuple[DiagramObject, Optional[GroupAdaptation], Optional[GroupAdaptation]]]:
        """Return a list of all diagram objects that are targets of current diagram.
        A list item is a tuple of source object and the source and target adaptations used
        for connection if any.
        """
        if self._diag_nav is None:
            self._consolidate()
        return self._diag_nav.get_block_targets(obj)

    def _consolidate(self) -> None:
        # Retrieves wire sources, wire targets and blocks from the Diagram Object. Internal method.
        self._diag_nav = DiagramNavigation(self)
        self._diag_nav.consolidate()


# Diagram object descriptions
# ------------------------------------------------------------


class ExprBlock(DiagramObject):  # numpydoc ignore=PR01
    """Expression block:

    - *object* ::= ( [[ *lunum* ]] [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **expr** *expr*
    """

    def __init__(
        self,
        expr: common.Expression,
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
        locals: Optional[List["DiagramObject"]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(lunum, luid, locals, pragmas)
        self._expr = expr

    @property
    def expr(self) -> common.Expression:
        """Block expression."""
        return self._expr


class DefBlock(DiagramObject):  # numpydoc ignore=PR01
    """Definition block:

    - *object* ::= ( [[ *lunum* ]]  [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **def** *lhs*
    - *description* ::= **def** {syntax% text %syntax}

    The *is_protected* property returns True when the definition is
    protected with a markup.
    """

    def __init__(
        self,
        lhs: Union[EquationLHS, common.ProtectedItem],
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(lunum, luid, locals, pragmas)
        self._lhs = lhs
        self._is_protected = isinstance(lhs, str)

    @property
    def lhs(self) -> Union[EquationLHS, common.ProtectedItem]:
        """Returned defined flows."""
        return self._lhs

    @property
    def is_protected(self) -> bool:
        """True when definition is syntactically incorrect and protected."""
        return self._is_protected


class Block(DiagramObject):  # numpydoc ignore=PR01
    """Generic block:

    - *object* ::= ( [[ *lunum* ]] [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **block**  (*operator* | *op_expr* )
    - *description* ::= **block** {syntax% text %syntax}

    The *is_protected* property returns True when the block definition
    is protected with a markup.
    """

    def __init__(
        self,
        instance: Union[OperatorBase, OperatorExpression, common.ProtectedItem],
        lunum: Optional[common.Lunum] = None,
        luid: Optional[common.Luid] = None,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(lunum, luid, locals, pragmas)
        self._instance = instance

    @property
    def instance(self) -> Union[OperatorBase, OperatorExpression, common.ProtectedItem]:
        """Called instance as an Operator, or an OperatorExpression or a protected string."""
        return self._instance

    @property
    def is_protected(self) -> bool:
        """True when called operator is defined as a string."""
        return isinstance(self.instance, common.ProtectedItem)


class Connection(common.SwanItem):  # numpydoc ignore=PR01
    """Wire connection for a source or for targets:

    - *connection* ::= *port* [[ *group_adaptation* ]] | ()

    If both *port* and *adaptation* are None, then it corresponds to the '()' form.

    Connection is not valid if only *adaptation* is given. This is checked
    with the *_is_valid()_* method.
    """

    def __init__(
        self,
        port: Optional[PortExpr] = None,
        adaptation: Optional[GroupAdaptation] = None,
    ) -> None:
        super().__init__()
        self._port = port
        self._adaptation = adaptation

    @property
    def port(self) -> Union[PortExpr, None]:
        """Return the port of the connection."""
        return self._port

    @property
    def adaptation(self) -> Union[GroupAdaptation, None]:
        """Return the adaptation of the port of the connection."""
        return self._adaptation

    @property
    def is_valid(self) -> bool:
        """True when the connection either () or *port* [*adaptation*]."""
        return (self.port is not None) or (self.adaptation is None)

    @property
    def is_connected(self) -> bool:
        """True when connected to some port."""
        return self.is_valid and (self.port is not None)


class Wire(DiagramObject):  # numpydoc ignore=PR01
    """Wire definition:

    - *object* ::= ( [[ *lunum* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **wire** *connection* => *connection* {{ , *connection* }}

    A **wire** *must* have a least one target.
    """

    def __init__(
        self,
        source: Connection,
        targets: List[Connection],
        lunum: Optional[common.Lunum] = None,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(lunum, None, locals, pragmas)
        self._source = source
        self._targets = targets

    @property
    def source(self) -> Connection:
        """Wire source."""
        return self._source

    @property
    def targets(self) -> List[Connection]:
        """Wire targets."""
        return self._targets

    @property
    def has_target(self) -> bool:
        """Return True when wire as at least one target."""
        return len(self.targets) > 0

    @property
    def sources(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a Wire"""
        raise ScadeOneException("Wire.sources() call")


class GroupOperation(Enum):  # numpydoc ignore=PR01
    """Operation on groups."""

    # pylint: disable=invalid-name

    #: No operation on group
    NoOp = auto()

    #: **byname** operation (keep named items)
    ByName = auto()

    #: **bypos** operation (keep positional items)
    ByPos = auto()

    #: Normalization operation (positional, then named items)
    Normalize = auto()

    @staticmethod
    def to_str(value: "GroupOperation"):
        """Group Enum to string."""
        if value == GroupOperation.NoOp:
            return ""
        if value == GroupOperation.Normalize:
            return "()"
        return value.name.lower()


class Bar(DiagramObject):  # numpydoc ignore=PR01
    """Bar (group/ungroup constructor block):

    - *object* ::= ( [[ *lunum* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **group** [[*group_operation*]]
    - *group_operation* ::= () | **byname** | **bypos**
    """

    def __init__(
        self,
        operation: Optional[GroupOperation] = GroupOperation.NoOp,
        lunum: Optional[common.Lunum] = None,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(lunum, None, locals, pragmas)
        self._operation = operation

    @property
    def operation(self) -> GroupOperation:
        """Group operation."""
        return self._operation


class SectionBlock(DiagramObject):  # numpydoc ignore=PR01
    """Section block definition:

    - *object* ::= ( *description* [[ *local_objects* ]] )
    - *description* ::= *scope_section*

    """

    def __init__(
        self,
        section: scopes.ScopeSection,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(locals=locals, pragmas=pragmas)
        self._section = section
        common.SwanItem.set_owner(self, section)

    @property
    def section(self) -> scopes.ScopeSection:
        """Section object of diagram object."""
        return self._section

    @property
    def sources(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a SectionBlock"""
        raise ScadeOneException("SectionBlock.sources() call")

    @property
    def targets(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a SectionBlock"""
        raise ScadeOneException("SectionBlock.targets() call")


class DefByCaseBlockBase(DiagramObject):  # numpydoc ignore=PR01
    """Def-by-case graphical definition (automaton or activate if/when):

    - *object* ::= ( *description* [[ *local_objects* ]] )
    - *description* ::= *def_by_case*

    This class is a base class for StateMachineBlock, ActivateIfBlock and ActivateWhenBlock
    and is used as a proxy to the internal DefByCase object.

    """

    def __init__(
        self,
        def_by_case: DefByCase,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(locals=locals, pragmas=pragmas)
        self._def_by_case = def_by_case
        common.SwanItem.set_owner(self, def_by_case)

    @property
    def def_by_case(self) -> DefByCase:
        """Def-by-case object."""
        return self._def_by_case

    def __getattr__(self, name: str):
        """Proxy to the DefByCase object."""
        return getattr(self._def_by_case, name)

    @property
    def sources(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a *def-by-case* block."""
        raise ScadeOneException("DefByCaseBlockBase.sources() call")

    @property
    def targets(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a *def-by-case* block."""
        raise ScadeOneException("DefByCaseBlockBase.targets() call")


class StateMachineBlock(DefByCaseBlockBase):  # numpydoc ignore=PR01
    """State machine block definition:

    - *object* ::= ( *description* [[ *local_objects* ]] )
    - *description* ::= *[lhs :] state_machine*

    A *StateMachineBlock* is a proxy to the internal :py:class:`StateMachine` object, therefore
    the methods and properties of the *StateMachine* object can be accessed directly.
    """

    def __init__(
        self,
        def_by_case: StateMachine,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(def_by_case, locals, pragmas)

    @property
    def state_machine(self) -> StateMachine:
        """State machine object."""
        return self.def_by_case


class ActivateIfBlock(DefByCaseBlockBase):  # numpydoc ignore=PR01
    """Activate-if block definition:

    - *object* ::= ( *description* [[ *local_objects* ]] )
    - *description* ::= *[lhs :] activate [[ luid ]] if_activation*

    A *ActivateIF* is a proxy to the internal :py:class:`ActivateIf` object, therefore
    the methods and properties of the *ActivateIf* object can be accessed directly.

    """

    def __init__(
        self,
        def_by_case: ActivateIf,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(def_by_case, locals, pragmas)

    @property
    def activate_if(self) -> ActivateIf:
        """Activate if object."""
        return self.def_by_case


class ActivateWhenBlock(DefByCaseBlockBase):  # numpydoc ignore=PR01
    """Activate-when block definition:

    - *object* ::= ( *description* [[ *local_objects* ]] )
    - *description* ::= *[lhs :] activate [[ luid ]] when_activation*

    A *ActivateIF* is a proxy to the internal :py:class:`ActivateWhen` object, therefore
    the methods and properties of the *ActivateIf* object can be accessed directly.

    """

    def __init__(
        self,
        def_by_case: ActivateWhen,
        locals: Optional[List[DiagramObject]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(def_by_case, locals, pragmas)

    @property
    def activate_when(self) -> ActivateWhen:
        """Activate when object."""
        return self.def_by_case


# Diagram navigation
# ------------------------------------------------------------


class DiagramNavigation:
    """Class handling navigation through Diagram objects.

    Parameters
    ----------
    diagram: Diagram
        Diagram object to navigate.
    """

    def __init__(self, diagram: Diagram) -> None:
        self._block_table = {}
        self._wires_of_target = defaultdict(list)
        self._wires_of_source = defaultdict(list)
        self._diagram = diagram

    def get_block(self, lunum: common.Lunum) -> Block:
        """Getting specific block."""
        return self._block_table[lunum.value]

    def with_source(self, lunum: common.Lunum) -> List[Wire]:
        """Returning list of wires that have a specific source."""
        return self._wires_of_source[lunum.value]

    def with_target(self, lunum: common.Lunum) -> List[Wire]:
        """Returning list of wires that have a specific target."""
        return self._wires_of_target[lunum.value]

    def get_wire_source(
        self, wire: Wire
    ) -> tuple[
        DiagramObject,
        GroupAdaptation,
        Union[List[tuple[DiagramObject, GroupAdaptation]], None],
    ]:
        """Get source block and adaptations of a wire. Also get the list of target blocks and adaptations."""
        from_block = self.get_block(wire.source.port.lunum)
        from_block_adaptation = wire.source.adaptation
        to_blocks = []
        for target in wire.targets:
            to_block = self.get_block(target.port.lunum)
            to_blocks.append((to_block, target.adaptation))
        return from_block, from_block_adaptation, to_blocks if to_blocks else None

    def get_wire_targets(
        self, wire: Wire
    ) -> List[tuple[DiagramObject, GroupAdaptation, GroupAdaptation]]:
        """Getting a list of targets block and adaptations of a wire."""
        list_targets = []
        from_block_adaptation = wire.source.adaptation
        for target in wire.targets:
            block = self.get_block(target.port.lunum)
            to_block_adaptation = target.adaptation
            list_targets.append((block, from_block_adaptation, to_block_adaptation))
        return list_targets

    def get_block_sources(
        self, obj: DiagramObject
    ) -> List[tuple[DiagramObject, GroupAdaptation, Union[List[GroupAdaptation], None]]]:
        """A block sources list of a Diagram Object."""
        if len(obj.locals) != 0:
            locals = [local.lunum for local in obj.locals]
            target_wires = []
            for lunum in locals:
                target_wires.extend(self.with_target(lunum))
        else:
            target_wires = self.with_target(obj.lunum)
        sources = [self.get_wire_source(wire) for wire in target_wires]
        return self._filter_sources(obj, sources)

    def _filter_sources(
        self,
        obj: DiagramObject,
        sources: List[
            tuple[
                DiagramObject,
                GroupAdaptation,
                Optional[tuple[DiagramObject, GroupAdaptation]],
            ]
        ],
    ) -> List[tuple[DiagramObject, GroupAdaptation, Union[List[GroupAdaptation], None]]]:
        """Filter sources (object, adaptation) of a given diagram object."""
        sources_dict = {}
        for source in sources:
            target_obj_adps = self._filter_target_blocks(source[2], obj)
            for target_obj_adp in target_obj_adps:
                # Stock a source (object, adaptation) and the corresponding target adaptations
                source_obj_adp = (source[0], source[1])
                if not sources_dict.get(source_obj_adp):
                    sources_dict[source_obj_adp] = {}
                    if target_obj_adp[1]:
                        sources_dict[source_obj_adp] = {target_obj_adp[1]}
                elif target_obj_adp[1]:
                    sources_dict[source_obj_adp].add(target_obj_adp[1])
        obj_sources = []
        # Convert the (source, target adaptations) dictionary
        # to a list of tuples: (source_block, source_adaptation, targets)
        for source_obj_adp, target_adps in sources_dict.items():
            obj_sources.append(
                (
                    source_obj_adp[0],
                    source_obj_adp[1],
                    list(target_adps) if target_adps else None,
                )
            )
        return obj_sources

    @staticmethod
    def _filter_target_blocks(
        target_obj_adps: Optional[List[tuple[DiagramObject, GroupAdaptation]]], obj
    ) -> List[tuple[DiagramObject, GroupAdaptation]]:
        """Filter target objects and adaptations of a given diagram object."""
        if not target_obj_adps:
            return []
        filtered_target_obj_adps = []
        for target_obj_adp in target_obj_adps:
            if target_obj_adp[0].locals:
                for local in target_obj_adp[0].locals:
                    if local.lunum == obj.lunum:
                        filtered_target_obj_adps.append((local, None))
            if target_obj_adp[0].lunum == obj.lunum:
                filtered_target_obj_adps.append(target_obj_adp)
        return filtered_target_obj_adps

    def get_block_targets(
        self, obj: DiagramObject
    ) -> List[tuple[DiagramObject, GroupAdaptation, GroupAdaptation]]:
        """A list of targets block of a Diagram Object."""
        lunum = obj.lunum
        if not isinstance(obj.owner, Diagram):
            lunum = obj.owner.lunum
        if not lunum:
            raise ScadeOneException(
                "Cannot get targets of a block without a locally unique number (LUNUM)"
            )
        targets = []
        for wire in self.with_source(lunum):
            targets.extend(self.get_wire_targets(wire))
        return targets

    def consolidate(self):
        """Retrieve wire sources, wire targets and blocks from the Diagram Object."""

        def explore_object(obj: DiagramObject):
            if isinstance(obj, (SectionBlock, DefByCaseBlockBase)):
                return
            if isinstance(obj, Wire):
                # process targets
                # _wire_of_target: table which stores wires from
                # target block found in wire
                wire = cast(Wire, obj)
                for target in wire.targets:
                    if not target.is_connected:
                        continue
                    if target.port.is_self:
                        continue
                    self._wires_of_target[target.port.lunum.value].append(wire)
                # process source
                # _wire_of_source: table which stores wires from
                # source block found in wire
                if wire.source.is_connected and not wire.source.port.is_self:
                    self._wires_of_source[wire.source.port.lunum.value].append(wire)
            else:
                lunum = obj.lunum
                if lunum is None:
                    return
                self._block_table[lunum.value] = obj
                for local in obj.locals:
                    self._block_table[local.lunum.value] = obj

        for obj in self._diagram.objects:
            explore_object(obj)
