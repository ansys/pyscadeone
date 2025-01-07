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

from typing_extensions import Self

from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes

from .equations import EquationLHS, DefByCase, StateMachine, ActivateIf, ActivateWhen
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
        locals: Optional[List[Self]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        common.SwanItem.__init__(self)
        common.PragmaBase.__init__(self, pragmas)
        self._lunum = lunum
        self._luid = luid
        self._locals = locals if locals else []

    @property
    def lunum(self) -> Union[common.Lunum, None]:
        """Lunum of object, or None if no Lunum."""
        return self._lunum

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Luid of object, or None if no Luid."""
        return self._luid

    @property
    def locals(self) -> List[Self]:
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
        diagram = cast(Diagram, self.owner)
        return diagram.get_block_sources(self)

    @property
    def targets(
        self,
    ) -> List[tuple["DiagramObject", GroupAdaptation, GroupAdaptation]]:
        """Return a list of all diagram objects that are targets of current diagram object.

        A list item is a tuple of target object and the source and target adaptations used
        for connection if any.
        """
        diagram = cast(Diagram, self.owner)
        return diagram.get_block_targets(self)

    def to_str(self) -> str:
        """String representation. Must be overridden by subclasses."""
        raise ScadeOneException("DiagramObject.to_str() call")

    def __str__(self):
        luid = f"{self.luid} " if self.luid else ""
        lunum = f"{self.lunum} " if self.lunum else ""
        locals_ = "\n".join([str(obj) for obj in self.locals])
        if locals_:
            locals_ = f"\nwhere\n{locals_}"
        pragmas = self.pragma_str()
        if pragmas:
            pragmas = f" {pragmas}"
        return f"({lunum}{luid}{self.to_str()}{locals_}{pragmas})"


class Diagram(scopes.ScopeSection):  # numpydoc ignore=PR01
    """Class for a **diagram** construct."""

    def __init__(self, objects: List[DiagramObject]) -> None:
        super().__init__()
        self._objects = objects
        self._diag_nav = None
        common.SwanItem.set_owner(self, objects)

    @property
    def objects(self) -> List[DiagramObject]:
        """Diagram objects."""
        return self._objects

    def __str__(self):
        objects = "\n".join([str(obj) for obj in self.objects])
        return f"diagram\n{objects}" if objects else "diagram"

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
        locals: Optional[List[Self]] = None,
        pragmas: Optional[List[common.Pragma]] = None,
    ) -> None:
        super().__init__(lunum, luid, locals, pragmas)
        self._expr = expr

    @property
    def expr(self) -> common.Expression:
        """Block expression."""
        return self._expr

    def to_str(self) -> str:
        """Expr to string."""
        return f"expr {self.expr}"


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
    def is_protected(self):
        """True when definition is syntactically incorrect and protected."""
        return self._is_protected

    def to_str(self) -> str:
        """Def to string."""
        return f"def {self.lhs}"


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
    def is_protected(self):
        """True when called operator is defined as a string."""
        return isinstance(self.instance, common.ProtectedItem)

    def to_str(self) -> str:
        """Block to string."""
        if self.is_protected:
            return f"block {self.instance}"

        return f"block {self.instance}"


class Connection(common.SwanItem):  # numpydoc ignore=PR01
    """Wire connection for a source or for targets:

    - *connection* ::= *port* [[ *group_adaptation* ]] | ()

    If both *port* and *adaptation* are None, then it corresponds to the '()' form.

    Connection is not valid if only *adaptation* is given. This is checked
    with the *_is_valid()_* method.
    """

    def __init__(
        self, port: Optional[PortExpr] = None, adaptation: Optional[GroupAdaptation] = None
    ) -> None:
        super().__init__()
        self._port = port
        self._adaptation = adaptation

    @property
    def port(self) -> Union[PortExpr, None]:
        """Returns the port of the connection."""
        return self._port

    @property
    def adaptation(self) -> Union[GroupAdaptation, None]:
        """Returns the adaptation of the port of the connection."""
        return self._adaptation

    @property
    def is_valid(self) -> bool:
        """True when the connection either () or *port* [*adaptation*]."""
        return (self.port is not None) or (self.adaptation is None)

    @property
    def is_connected(self) -> bool:
        """True when connected to some port."""
        return self.is_valid and (self.port is not None)

    def __str__(self) -> str:
        if self.is_connected:
            conn = str(self.port)
            if self.adaptation:
                conn += f" {self.adaptation}"
        else:
            conn = "()"
        return conn


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
        raise ScadeOneException("Wire.sources call")

    def to_str(self) -> str:
        """Wire to string."""
        targets = ", ".join([str(conn) for conn in self.targets])
        return f"wire {self.source} => {targets}"


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
    def to_str(value: Self):
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

    def to_str(self) -> str:
        """Group to string."""
        return f"group {GroupOperation.to_str(self.operation)}"


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

    def to_str(self) -> str:
        """Section to string."""
        return str(self.section)


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
        raise ScadeOneException("SectionBlock.sources() call")

    @property
    def targets(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a *def-by-case* block."""
        raise ScadeOneException("SectionBlock.targets() call")

    def to_str(self) -> str:
        """Section to string."""
        return str(self._def_by_case)


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
    ) -> tuple[DiagramObject, GroupAdaptation, Union[List[GroupAdaptation], None]]:
        """Getting source block and adaptations of a wire."""
        block = self.get_block(wire.source.port.lunum)
        from_block_adaptation = wire.source.adaptation
        to_block_adaptations = list(map(lambda target: target.adaptation, wire.targets))
        if len(to_block_adaptations) == 1 and to_block_adaptations[0] is None:
            to_block_adaptations = None
        return block, from_block_adaptation, to_block_adaptations

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
        """A list of block sources of a Diagram Object."""
        if len(obj.locals) != 0:
            locals = [local.lunum for local in obj.locals]
            targets = []
            for lunum in locals:
                targets.extend(self.with_target(lunum))
        else:
            targets = self.with_target(obj.lunum)
        sources = [self.get_wire_source(wire) for wire in targets]
        return sources

    def get_block_targets(
        self, obj: DiagramObject
    ) -> List[tuple[DiagramObject, GroupAdaptation, GroupAdaptation]]:
        """A list of targets block of a Diagram Object."""
        targets = []
        for wire in self.with_source(obj.lunum):
            targets.extend(self.get_wire_targets(wire))
        return targets

    def consolidate(self):
        """Retrieves wire sources, wire targets and blocks from the Diagram Object."""

        def explore_object(obj: DiagramObject):
            if isinstance(obj, SectionBlock) or isinstance(obj, DefByCaseBlockBase):
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
