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

# pylint: disable=too-many-lines, pointless-statement

from io import IOBase, StringIO
from typing import Any, List, Optional, Union

import ansys.scadeone.core.svc.common.renderer as R
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor, Owner, OwnerProperty
import ansys.scadeone.core.swan as S
from ansys.scadeone.core.common.versioning import gen_swan_version


class PPrinter(SwanVisitor):
    """
    A class to pretty print Swan declarations.

    See *print* method to print a Swan object to the output stream.
    ...

    Attributes
    ----------
    normalize: bool
        Write each Swan declaration or all declarations per line

    Methods
    -------
    Supported to use for a Swan project:

        - Use clauses declaration
        - Globals declaration:
            + Types declaration
            + Constants declaration
            + Sensors declaration
            + Groups declaration
        - Modules: body and interface declarations
            + User operators declaration: Variable, operators, equations, diagrams, scopes, ...
            + Expressions declaration
        - Signature
        - Project
    """

    __own_property = "visitor"

    def __init__(self, normalize=True) -> None:
        """
        Constructs all the necessary attributes for the PPrinter object

        Parameters
        ----------
        normalize : bool, optional
            Write all the same Swan declarations or each declaration on one line,
            by default True i.e. each Swan declaration per line
        """

        super().__init__()
        self._normalize = normalize

    def print(
        self,
        stream: IOBase,
        swan_obj: Union[S.SwanItem, None],
        render: Optional[R.Renderer] = None,
    ):
        """
        Print a Swan object to the output stream

        Parameters
        ----------
        stream : IOBase
            A file or buffer to which the output will be written.
        swan_obj : S.SwanItem | None
            A Swan object to print. If None, 'None' is rendered.
        render : Optional[R.Renderer], optional
            A renderer to use for printing, by default None.
            If None, a new renderer will be created from R.Renderer class.
        """

        if not swan_obj:
            stream.write("None")
            return
        # Visit Swan object to build document
        self.visit(swan_obj)
        # Write visited Swan code
        doc = R.Document()
        doc << self.pprint_array[self.__own_property]
        if render is None:
            render = R.Renderer(stream)
        else:
            render.set_stream(stream)
        render.render(doc)

    def _decl_formatting(self, data: dict, key: str, prefix: str):
        """
        Update the data stream according to the 'normalize' attribute

        Parameters
        ----------
        data : dict
            Data stream needs to update
        key : str
            Key name to know the updating position in the data stream
        prefix : str
            Prefix of a visited swan declaration syntax
        """

        if data[key]:
            _doc = R.DBlock()
            if self._normalize:
                # Normalized format, one declaration per line
                _doc << prefix << " " << data[key][0] << ";" << "@n"
                for decl in data[key][1:]:
                    _doc << "@n" << prefix << " " << decl << ";" << "@n"
            else:
                # One single declaration
                _doc << prefix << " " << "@m" << data[key][0] << ";"
                for decl in data[key][1:]:
                    _doc << "@n" << decl << ";"
                _doc << "@M"
            _doc << "@n"
        else:
            _doc = R.DText(prefix)
        # Update data stream for declaration property
        data[self.__own_property] = _doc

    @classmethod
    def _update_property(cls, owner: Any, owner_property: str, data: str):
        """
        Update owner's data stream via its property with a data given

        Parameters
        ----------
        owner : Any
            Instance containing owner_property
        owner_property : str
            Property name to know the visit context within the owner.
        data : str
            Data given to update
        """

        if isinstance(owner.pprint_array[owner_property], list):
            owner.pprint_array[owner_property].append(data)
        else:
            owner.pprint_array[owner_property] = data

    @staticmethod
    def _doc_or_list(inp: Union[List, R.DElt]) -> R.DElt:
        """
        Update an input according to its type

        Parameters
        ----------
        inp : Union[List, str]
            Input string or list of string

        Returns
        -------
        R.DElt
            A document
        """

        if isinstance(inp, list):
            _items = [PPrinter._doc_or_list(_it) for _it in inp]
            _rtn = R.doc_list(*_items, sep=", ", start="(", last=")")
        else:
            _rtn = inp
        return _rtn

    @staticmethod
    def _format_list(pref: str, lst: List, end: Optional[str] = ";", single_line=False) -> R.DBlock:
        """
        Format each elem with adding a given separation at the end

        Parameters
        ----------
        pref : str
            A given prefix or keyword
        lst : List
            A given list
        end : Optional[str], optional
            A given separation, by default ";"
        single_line : bool, optional
            True if the content shall not be indented on separate lines

        Returns
        -------
        R.DBlock
            A document block
        """

        _decl = R.DBlock()
        _decl << pref
        if lst:
            if single_line:
                _decl << " "
            else:
                _decl << "@m" << "@n"
            _decl << R.doc_list(*[item << end for item in lst], sep="@n")
            if not single_line:
                _decl << "@M"
        return _decl

    def visit(self, swan_obj: S.Declaration):
        """
        Visit method - Pretty prints a Swan declaration to data stream

        Parameters
        ----------
        swan_obj : S.Declaration
            a visited Swan object, it's a Declaration instance
        """

        # Initialize data stream for Swan declaration.
        self.pprint_array = {self.__own_property: None}
        # Visit Swan declaration.
        self._visit(swan_obj, self, self.__own_property)

    def visit_ActivateClock(
        self,
        swan_obj: S.ActivateClock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateClock visitor

        Parameters
        ----------
        swan_obj : S.ActivateClock
            Visited Swan object, it's a ActivateClock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "clock": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.clock, swan_obj, "clock")
        _decl = R.DBlock()
        _decl << "activate "
        _decl << swan_obj.pprint_array["operator"]
        _decl << " every "
        _decl << swan_obj.pprint_array["clock"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ActivateIf(
        self,
        swan_obj: S.ActivateIf,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateIf visitor

        Parameters
        ----------
        swan_obj : S.ActivateIf
            Visited Swan object, it's a ActivateIf instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"if_activation": None, "name": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << "activate"
        if swan_obj.name:
            self._visit(swan_obj.name, swan_obj, "name")
            _decl << " " << swan_obj.pprint_array["name"]
        self._visit(swan_obj.if_activation, swan_obj, "if_activation")
        _decl << "@i" << "@n"
        _decl << swan_obj.pprint_array["if_activation"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, owner_property)
        _decl << "@u"

    def visit_ActivateIfBlock(
        self,
        swan_obj: S.ActivateIfBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateIf Block visitor

        Parameters
        ----------
        swan_obj : S.ActivateIfBlock
            Visited Swan object, it's a ActivateIfBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_DefByCaseBlockBase(swan_obj, owner, owner_property)

    def visit_ActivateEvery(
        self,
        swan_obj: S.ActivateEvery,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateEvery visitor

        Parameters
        ----------
        swan_obj : S.ActivateEvery
            Visited Swan object, it's a ActivateEvery instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "condition": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.condition, swan_obj, "condition")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << "activate "
        _decl << swan_obj.pprint_array["operator"]
        _decl << " every "
        _decl << swan_obj.pprint_array["condition"]
        if swan_obj.is_last:
            _decl << " last "
        else:
            _decl << " default "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ActivateWhen(
        self,
        swan_obj: S.ActivateWhen,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateWhen visitor

        Parameters
        ----------
        swan_obj : S.ActivateWhen
            Visited Swan object, it's a ActivateWhen instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"condition": None, "branches": [], "name": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << "activate"
        if swan_obj.name:
            self._visit(swan_obj.name, swan_obj, "name")
            _decl << " " << swan_obj.pprint_array["name"]
        _decl << " when "
        self._visit(swan_obj.condition, swan_obj, "condition")
        _decl << swan_obj.pprint_array["condition"]
        _decl << " match"
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")
        if swan_obj.pprint_array["branches"]:
            _decl << "@n"
            _decl << R.doc_list(*swan_obj.pprint_array["branches"], sep="@n")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, owner_property)

    def visit_ActivateWhenBlock(
        self,
        swan_obj: S.ActivateWhenBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateWhen Block visitor

        Parameters
        ----------
        swan_obj : S.ActivateWhenBlock
            Visited Swan object, it's a ActivateWhenBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_DefByCaseBlockBase(swan_obj, owner, owner_property)

    def visit_ActivateWhenBranch(
        self,
        swan_obj: S.ActivateWhenBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateWhen Branch visitor

        Parameters
        ----------
        swan_obj : S.ActivateWhenBranch
            Visited Swan object, it's a ActivateWhenBranch instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"pattern": None, "data_def": None}
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        self._visit(swan_obj.data_def, swan_obj, "data_def")
        _decl = R.DBlock()
        _decl << "| "
        _decl << swan_obj.pprint_array["pattern"]
        _decl << " : "
        _decl << swan_obj.pprint_array["data_def"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_AnonymousOperatorWithDataDefinition(
        self,
        swan_obj: S.AnonymousOperatorWithDataDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Anonymous Operator With Data Definition visitor

        Parameters
        ----------
        swan_obj : S.AnonymousOperatorWithDataDefinition
            Visited Swan object, it's a AnonymousOperatorWithDataDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"inputs": None, "outputs": None, "data_def": None}
        _in = []
        _out = []
        # Visit properties
        _decl = R.DBlock()
        if swan_obj.is_node:
            _decl << "node"
        else:
            _decl << "function"

        for item in swan_obj.inputs:
            self._visit(item, swan_obj, "inputs")
            _in.append(swan_obj.pprint_array["inputs"])
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
            _out.append(swan_obj.pprint_array["outputs"])
        if isinstance(swan_obj.data_def, (S.Equation, S.Scope)):
            self._visit(swan_obj.data_def, swan_obj, "data_def")
        _decl << " (" << R.doc_list(*_in, sep="; ") << ")"
        _decl << " returns "
        _decl << "(" << R.doc_list(*_out, sep="; ") << ") "
        _decl << swan_obj.pprint_array["data_def"]

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_AnonymousOperatorWithExpression(
        self,
        swan_obj: S.AnonymousOperatorWithExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Anonymous Operator With Expression visitor

        Parameters
        ----------
        swan_obj : S.AnonymousOperatorWithExpression
            Visited Swan object, it's a AnonymousOperatorWithExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"params": None, "sections": None, "expr": None}
        _pm = []
        _st = []
        # Visit properties
        _decl = R.DBlock()
        if swan_obj.is_node:
            _decl << "node"
        else:
            _decl << "function"
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")
            _pm.append(swan_obj.pprint_array["params"])
        for item in swan_obj.sections:
            self._visit(item, swan_obj, "sections")
            _st.append(swan_obj.pprint_array["sections"])
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl << " " << R.doc_list(*_pm, sep=", ")
        if _st:
            _decl << " " << R.doc_list(*_st, sep=" ")
        _decl << " => " << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ArrayConstructor(
        self,
        swan_obj: S.ArrayConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Constructor visitor

        Parameters
        ----------
        swan_obj : S.ArrayConstructor
            Visited Swan object, it's a ArrayConstructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        _decl = R.DBlock()
        _decl << "["
        _decl << swan_obj.pprint_array["group"]
        _decl << "]"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ArrayProjection(
        self,
        swan_obj: S.ArrayProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Projection visitor

        Parameters
        ----------
        swan_obj : S.ArrayProjection
            Visited Swan object, it's a ArrayProjection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "index": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.index, swan_obj, "index")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << swan_obj.pprint_array["index"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ArrayRepetition(
        self,
        swan_obj: S.ArrayRepetition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Repetition visitor

        Parameters
        ----------
        swan_obj : S.ArrayRepetition
            Visited Swan object, it's a ArrayRepetition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "size": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.size, swan_obj, "size")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << " ^ "
        _decl << swan_obj.pprint_array["size"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ArrayTypeExpression(
        self,
        swan_obj: S.ArrayTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Type Expression visitor

        Parameters
        ----------
        swan_obj : S.ArrayTypeExpression
            Visited Swan object, it's a ArrayTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type": None, "size": None}

        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        self._visit(swan_obj.size, swan_obj, "size")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["type"]
        _decl << " ^ "
        _decl << swan_obj.pprint_array["size"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Arrow(
        self,
        swan_obj: S.Arrow,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Arrow visitor

        Parameters
        ----------
        swan_obj : S.Arrow
            Visited Swan object, it's a Arrow instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "guard": None,
            "action": None,
            "target": None,
            "fork": None,
        }
        # Visit properties
        _arw = []
        if swan_obj.guard:
            self._visit(swan_obj.guard, swan_obj, "guard")
            _arw.append(R.DBlock() << "(" << swan_obj.pprint_array["guard"] << ")")
        if swan_obj.action:
            self._visit(swan_obj.action, swan_obj, "action")
            _arw.append(swan_obj.pprint_array["action"])
        if swan_obj.target:
            self._visit(swan_obj.target, swan_obj, "target")
            _arw.append(swan_obj.pprint_array["target"])
        if swan_obj.fork:
            self._visit(swan_obj.fork, swan_obj, "fork")
            _arw.append(swan_obj.pprint_array["fork"])
        if _arw:
            owner.pprint_array[owner_property] = R.doc_list(*_arw, sep="@n")

    def visit_AssertSection(
        self,
        swan_obj: S.AssertSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Assert Section visitor

        Parameters
        ----------
        swan_obj : S.AssertSection
            Visited Swan object, it's a AssertSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"assertions": None}
        _ast = []
        # Visit properties
        for item in swan_obj.assertions:
            self._visit(item, swan_obj, "assertions")
            _ast.append(swan_obj.pprint_array["assertions"])
        owner.pprint_array[owner_property] = PPrinter._format_list("assert", _ast)

    def visit_AssumeSection(
        self,
        swan_obj: S.AssumeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Assume Section visitor

        Parameters
        ----------
        swan_obj : S.AssumeSection
            Visited Swan object, it's a AssumeSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"hypotheses": []}
        # Visit properties
        for item in swan_obj.hypotheses:
            self._visit(item, swan_obj, "hypotheses")

        owner.pprint_array[owner_property] = PPrinter._format_list(
            "assume", swan_obj.pprint_array["hypotheses"]
        )

    def visit_Bar(self, swan_obj: S.Bar, owner: Owner, owner_property: OwnerProperty) -> None:
        """
        Bar visitor

        Parameters
        ----------
        swan_obj : S.Bar
            Visited Swan object, it's a Bar instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operation": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << "group"
        if swan_obj.operation:
            self._visit(swan_obj.operation, swan_obj, "operation")
            if swan_obj.operation != S.GroupOperation.NoOp:
                _decl << " "
            _decl << swan_obj.pprint_array["operation"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_BinaryExpr(
        self,
        swan_obj: S.BinaryExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Binary Expression visitor

        Parameters
        ----------
        swan_obj : S.BinaryExpr
            Visited Swan object, it's a BinaryExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "left": None, "right": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.left, swan_obj, "left")
        self._visit(swan_obj.right, swan_obj, "right")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["left"]
        _decl << " "
        _decl << swan_obj.pprint_array["operator"]
        _decl << " "
        _decl << swan_obj.pprint_array["right"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_BinaryOp(
        self,
        swan_obj: S.BinaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        Binary Operator visitor

        Parameters
        ----------
        swan_obj : S.BinaryOp
            Visited Swan object, it's a BinaryOp instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(S.BinaryOp.to_str(swan_obj))

    def visit_Block(
        self,
        swan_obj: S.Block,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Block visitor

        Parameters
        ----------
        swan_obj : S.Block
            Visited Swan object, it's a Block instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"instance": None, "instance_luid": None}
        # Visit properties
        self._visit(swan_obj.instance, swan_obj, "instance")

        _decl = R.DBlock()
        _decl << "block "
        _decl << swan_obj.pprint_array["instance"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_BoolPattern(
        self,
        swan_obj: S.BoolPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Bool Pattern visitor

        Parameters
        ----------
        swan_obj : S.BoolPattern
            Visited Swan object, it's a BoolPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(str(swan_obj))

    def visit_BoolType(
        self,
        swan_obj: S.BoolType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Bool Type visitor

        Parameters
        ----------
        swan_obj : S.BoolType
            Visited Swan object, it's a BoolType instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_CaseBranch(
        self,
        swan_obj: S.CaseBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Case Branch visitor

        Parameters
        ----------
        swan_obj : S.CaseBranch
            Visited Swan object, it's a CaseBranch instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"pattern": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << " | "
        _decl << swan_obj.pprint_array["pattern"]
        _decl << ": "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_CaseExpr(
        self,
        swan_obj: S.CaseExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Case Expression visitor

        Parameters
        ----------
        swan_obj : S.CaseExpr
            Visited Swan object, it's a CaseExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "branches": []}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")

        _decl = R.DBlock()
        _decl << "(case "
        _decl << swan_obj.pprint_array["expr"]
        _decl << " of"
        _decl << R.doc_list(*swan_obj.pprint_array["branches"], sep="")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_CharType(
        self,
        swan_obj: S.CharType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Char Type visitor

        Parameters
        ----------
        swan_obj : S.CharType
            Visited Swan object, it's a CharType instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_CharPattern(
        self,
        swan_obj: S.CharPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Character Pattern visitor

        Parameters
        ----------
        swan_obj : S.CharPattern
            Visited Swan object, it's a CharPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(str(swan_obj))

    def visit_ClockExpr(
        self,
        swan_obj: S.ClockExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Clock Expression visitor

        Parameters
        ----------
        swan_obj : S.ClockExpr
            Visited Swan object, it's a ClockExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "is_not": None, "pattern": None}

        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _decl = R.DBlock()
        if swan_obj.pattern:
            self._visit(swan_obj.pattern, swan_obj, "pattern")
            _decl << "("
            _decl << swan_obj.pprint_array["id"]
            _decl << " match "
            _decl << swan_obj.pprint_array["pattern"]
            _decl << ")"
        elif swan_obj.is_not:
            self.visit_builtin(swan_obj.is_not, swan_obj, "is_not")
            _decl << "not "
            _decl << swan_obj.pprint_array["id"]
        else:
            _decl << swan_obj.pprint_array["id"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Connection(
        self,
        swan_obj: S.Connection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Connection visitor

        Parameters
        ----------
        swan_obj : S.Connection
            Visited Swan object, it's a Connection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        swan_obj.pprint_array = {"port": None, "adaptation": None}
        # Visit properties
        if swan_obj.port:
            self._visit(swan_obj.port, swan_obj, "port")
        if swan_obj.adaptation:
            self._visit(swan_obj.adaptation, swan_obj, "adaptation")
        _decl = R.DBlock()
        if swan_obj.is_connected:
            _decl << swan_obj.pprint_array["port"]
            if swan_obj.adaptation:
                _decl << " "
                _decl << swan_obj.pprint_array["adaptation"]
        else:
            _decl << "()"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ConstDecl(
        self,
        swan_obj: S.ConstDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a constant declaration
        Syntax: const {{ const_decl ; }}
                const_decl ::= id : type_expr [[ = expr ]] | id = expr

        Parameters
        ----------
        swan_obj : S.ConstDecl
            Visited Swan object, it's a ConstantDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "type": None, "value": None}
        # Visit parent class
        super().visit_ConstDecl(swan_obj, owner, owner_property)
        # Visit properties
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.pprint_array["type"]:
            _decl << ": " << swan_obj.pprint_array["type"]
        if swan_obj.pprint_array["value"]:
            _decl << " = " << swan_obj.pprint_array["value"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_ConstDeclarations(
        self,
        swan_obj: S.ConstDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of constant declarations

        Parameters
        ----------
        swan_obj : S.ConstDeclarations
            Visited Swan object, it's a ConstDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"constants": []}
        # Visit parent class
        super().visit_ConstDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "constants", "const")
        owner.pprint_array[owner_property] = swan_obj.pprint_array[self.__own_property]

    def visit_DefaultPattern(
        self,
        swan_obj: S.DefaultPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Default Pattern visitor

        Parameters
        ----------
        swan_obj : S.DefaultPattern
            Visited Swan object, it's a DefaultPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.DText(str(swan_obj))

    def visit_DefBlock(
        self,
        swan_obj: S.DefBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Def Block visitor

        Parameters
        ----------
        swan_obj : S.DefBlock
            Visited Swan object, it's a DefBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None}

        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        _decl = R.DBlock()
        _decl << "def "
        _decl << swan_obj.pprint_array["lhs"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_DefByCase(
        self,
        swan_obj: S.DefByCase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        DefByCase visitor

        Parameters
        ----------
        swan_obj : S.DefByCase
            Visited Swan object, it's a DefByCase instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None, "name": None}
        _decl = R.DBlock()
        # Visit properties
        if swan_obj.lhs:
            self._visit(swan_obj.lhs, swan_obj, "lhs")
            _decl << swan_obj.pprint_array["lhs"] << " : "
        _decl << owner.pprint_array[owner_property]
        if swan_obj.is_equation:
            _decl << ";"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_DefByCaseBlockBase(
        self,
        swan_obj: S.DefByCaseBlockBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        DefByCase Block Base visitor

        Parameters
        ----------
        swan_obj : S.DefByCaseBlockBase
            Visited Swan object, it's a DefByCaseBlockBase instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"def_by_case": None}
        # Visit properties
        self._visit(swan_obj.def_by_case, swan_obj, "def_by_case")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["def_by_case"]
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_Diagram(
        self,
        swan_obj: S.Diagram,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Diagram visitor

        Parameters
        ----------
        swan_obj : S.Diagram
            Visited Swan object, it's a Diagram instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"objects": None}
        _decl = R.DBlock() << "@i"
        _decl << "diagram"
        _objs = []
        iterator = iter(swan_obj.objects)
        wires_section = None
        while True:
            try:
                item = next(iterator)
                if wires_section is None:
                    # First item defines first section
                    wires_section = isinstance(item, S.Wire)
                elif wires_section != isinstance(item, S.Wire):
                    # Entering or leaving wires section: must add line break
                    wires_section = not wires_section
                    _decl << "@n"
                    _decl << R.doc_list(*_objs, sep="@n") << "@n"
                    _objs.clear()
                self._visit(item, swan_obj, "objects")
                _objs.append(swan_obj.pprint_array["objects"])
            except StopIteration:
                _decl << "@n"
                _decl << R.doc_list(*_objs, sep="@n")
                _decl << "@u"
                break

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        if isinstance(owner, PPrinter):
            del swan_obj.pprint_array

    def visit_DiagramObject(
        self,
        swan_obj: S.DiagramObject,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Diagram Object visitor

        Parameters
        ----------
        swan_obj : S.DiagramObject
            Visited Swan object, it's a DiagramObject instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lunum": None, "luid": None, "locals": None}
        _decl = R.DBlock()
        _decl << "("
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _decl << swan_obj.pprint_array["lunum"]
            _decl << " "
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _decl << swan_obj.pprint_array["luid"]
            _decl << " "
        _decl << owner.pprint_array[owner_property]
        if swan_obj.locals:
            _lc = []
            for item in swan_obj.locals:
                self._visit(item, swan_obj, "locals")
                _lc.append(swan_obj.pprint_array["locals"])
            if _lc:
                _decl << "@i" << "@n" << "where" << "@i" << "@n"
                _decl << R.doc_list(*_lc, sep="@n") << "@u" << "@u"
        if swan_obj.pragmas:
            # Add pragmas for diagram object
            swan_obj.pprint_array = {"pragmas": None}
            _pgm = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgm.append(swan_obj.pprint_array["pragmas"])
            if _pgm:
                _decl << "@n"
                _decl << R.doc_list(*_pgm, sep=" ")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_EmitSection(
        self,
        swan_obj: S.EmitSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Emit Section visitor

        Parameters
        ----------
        swan_obj : S.EmitSection
            Visited Swan object, it's a EmitSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"emissions": []}
        # Visit properties
        for item in swan_obj.emissions:
            self._visit(item, swan_obj, "emissions")

        owner.pprint_array[owner_property] = PPrinter._format_list(
            "emit", swan_obj.pprint_array["emissions"]
        )

    def visit_EmissionBody(
        self,
        swan_obj: S.EmissionBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Emission Body visitor

        Parameters
        ----------
        swan_obj : S.EmissionBody
            Visited Swan object, it's a EmissionBody instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"flows": None, "condition": None, "luid": None}
        _fls = []
        # Visit properties
        _decl = R.DBlock()
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _decl << swan_obj.pprint_array["luid"]
            _decl << " "
        for item in swan_obj.flows:
            self._visit(item, swan_obj, "flows")
            _fls.append(swan_obj.pprint_array["flows"])
        _decl << R.doc_list(*_fls, sep=", ")
        if swan_obj.condition:
            self._visit(swan_obj.condition, swan_obj, "condition")
            _decl << " if "
            _decl << swan_obj.pprint_array["condition"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_EnumTypeDefinition(
        self,
        swan_obj: S.EnumTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Enumeration Type Definition visitor

        Parameters
        ----------
        swan_obj : S.EnumTypeDefinition
            Visited Swan object, it's a EnumTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"tags": []}
        # Visit properties
        for itm in swan_obj.tags:
            self._visit(itm, swan_obj, "tags")
        _decl = R.DBlock()
        _decl << "enum "
        _decl << R.doc_list(*swan_obj.pprint_array["tags"], sep=", ", start="{", last="}")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_EquationLHS(
        self,
        swan_obj: S.EquationLHS,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Equation LHS visitor

        Parameters
        ----------
        swan_obj : S.EquationLHS
            Visited Swan object, it's a EquationLHS instance
        owner : Owner
            Owner of the property, 'None' for the root visited object
        property : Union[str, None]
            Property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs_items": None}
        _lms = []
        # Visit properties
        for item in swan_obj.lhs_items:
            self._visit(item, swan_obj, "lhs_items")
            _lms.append(swan_obj.pprint_array["lhs_items"])
        _decl = R.DBlock()
        if _lms:
            _decl << R.doc_list(*_lms, sep=", ")
            if swan_obj.is_partial_lhs:
                _decl << ", .."
        else:
            _decl << "()"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ExprBlock(
        self,
        swan_obj: S.ExprBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Expression Block visitor

        Parameters
        ----------
        swan_obj : S.ExprBlock
            Visited Swan object, it's a ExprBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << "expr "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_ExprEquation(
        self,
        swan_obj: S.ExprEquation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Expression Equation visitor

        Parameters
        ----------
        swan_obj : S.ExprEquation
            Visited Swan object, it's a ExprEquation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None, "expr": None, "luid": None}
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["lhs"]
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _decl << " " << swan_obj.pprint_array["luid"]
        _decl << " = " << swan_obj.pprint_array["expr"] << ";"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ExprTypeDefinition(
        self,
        swan_obj: S.ExprTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Expression Type Definition visitor

        Parameters
        ----------
        swan_obj : S.ExprTypeDefinition
            Visited Swan object, it's a ExprTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type": None}
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["type"]

    def visit_Float32Type(
        self,
        swan_obj: S.Float32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Float32 Type visitor

        Parameters
        ----------
        swan_obj : S.Float32Type
            Visited Swan object, it's a Float32Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Float64Type(
        self,
        swan_obj: S.Float64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Float64 Type visitor

        Parameters
        ----------
        swan_obj : S.Float64Type
            Visited Swan object, it's a Float64Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_ForkPriorityList(
        self,
        swan_obj: S.ForkPriorityList,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Fork Priority List visitor

        Parameters
        ----------
        swan_obj : S.ForkPriorityList
            Visited Swan object, it's a ForkPriorityList instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"prio_forks": []}
        # Visit properties
        for item in swan_obj.prio_forks:
            self._visit(item, swan_obj, "prio_forks")

        _decl = R.DBlock()
        if swan_obj.pprint_array["prio_forks"]:
            _decl << R.doc_list(*swan_obj.pprint_array["prio_forks"], sep="@n")
            _decl << " "
        _decl << "end"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForkTree(
        self,
        swan_obj: S.ForkTree,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ForkTree visitor

        Parameters
        ----------
        swan_obj : S.ForkTree
            Visited Swan object, it's a ForkTree instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "if_arrow": None,
            "elsif_arrows": [],
            "else_arrow": None,
        }
        # Visit properties
        self._visit(swan_obj.if_arrow, swan_obj, "if_arrow")
        _decl = R.DBlock()
        _decl << "if " << swan_obj.pprint_array["if_arrow"]
        if swan_obj.elsif_arrows:
            _ela = []
            for item in swan_obj.elsif_arrows:
                self._visit(item, swan_obj, "elsif_arrows")
                _ela.append(R.DBlock() << "elsif " << swan_obj.pprint_array["elsif_arrows"])
            if _ela:
                _decl << "@n" << R.doc_list(*_ela, sep="@n")
        if swan_obj.else_arrow:
            self._visit(swan_obj.else_arrow, swan_obj, "else_arrow")
            _decl << "@n" << "else " << swan_obj.pprint_array["else_arrow"]
        _decl << " end"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForkWithPriority(
        self,
        swan_obj: S.ForkWithPriority,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Fork With Priority visitor

        Parameters
        ----------
        swan_obj : S.ForkWithPriority
            Visited Swan object, it's a ForkWithPriority instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"priority": None, "arrow": None}
        # Visit properties
        self._visit(swan_obj.arrow, swan_obj, "arrow")
        _decl = R.DBlock()
        _decl << ":"
        if swan_obj.priority:
            self._visit(swan_obj.priority, swan_obj, "priority")
            _decl << swan_obj.pprint_array["priority"]
        else:
            _decl << " "
        _decl << ":" << " "
        if swan_obj.is_if_arrow:
            _decl << "if"
        else:
            _decl << "else"
        _decl << " " << swan_obj.pprint_array["arrow"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Forward(
        self,
        swan_obj: S.Forward,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward visitor

        Parameters
        ----------
        swan_obj : S.Forward
            Visited Swan object, it's a Forward instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "state": None,
            "dimensions": [],
            "body": None,
            "returns": [],
            "luid": None,
        }
        # Visit properties
        self._visit(swan_obj.state, swan_obj, "state")
        for item in swan_obj.dimensions:
            self._visit(item, swan_obj, "dimensions")
        self._visit(swan_obj.body, swan_obj, "body")
        for item in swan_obj.returns:
            self._visit(item, swan_obj, "returns")
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
        _decl = R.DBlock()
        _decl << "forward"
        if swan_obj.luid:
            _decl << " "
            _decl << swan_obj.pprint_array["luid"]
        if swan_obj.state != S.ForwardState.Nothing:
            _decl << " "
            _decl << S.ForwardState.to_str(swan_obj.state)
        if swan_obj.pprint_array["dimensions"]:
            _decl << R.DLineBreak(False)
            _decl << R.doc_list(*swan_obj.pprint_array["dimensions"], sep="@n")
        _decl << R.DLineBreak(False)
        _decl << swan_obj.pprint_array["body"]
        _decl << R.DLineBreak(False)
        _decl << "returns ("
        if swan_obj.pprint_array["returns"]:
            _decl << R.doc_list(*swan_obj.pprint_array["returns"], sep=", ")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_FormalProperty(
        self,
        swan_obj: S.FormalProperty,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Property visitor

        Parameters
        ----------
        swan_obj : S.FormalProperty
            Visited Swan object, it's a FormalProperty instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"luid": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.luid, swan_obj, "luid")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["luid"]
        _decl << ": "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardArrayClause(
        self,
        swan_obj: S.ForwardArrayClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Array Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardArrayClause
            Visited Swan object, it's a ForwardArrayClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"return_clause": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << "["
        if isinstance(swan_obj.return_clause, (S.ForwardItemClause, S.ForwardArrayClause)):
            self._visit(swan_obj.return_clause, swan_obj, "return_clause")
            _decl << swan_obj.pprint_array["return_clause"]
        _decl << "]"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardBody(
        self,
        swan_obj: S.ForwardBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Body visitor

        Parameters
        ----------
        swan_obj : S.ForwardBody
            Visited Swan object, it's a ForwardBody instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"body": None, "unless_expr": None, "until_expr": None}
        _bdy = []
        # Visit properties
        for item in swan_obj.body:
            self._visit(item, swan_obj, "body")
            _bdy.append(swan_obj.pprint_array["body"])
        _decl = R.DBlock()
        if swan_obj.unless_expr:
            self._visit(swan_obj.unless_expr, swan_obj, "unless_expr")
            _decl << "unless "
            _decl << swan_obj.pprint_array["unless_expr"]
            _decl << R.DLineBreak(False)
        if _bdy:
            _decl << R.doc_list(*_bdy, sep=R.DLineBreak(False))
        if swan_obj.until_expr:
            self._visit(swan_obj.until_expr, swan_obj, "until_expr")
            if _bdy:
                _decl << R.DLineBreak(False)
            _decl << "until "
            _decl << swan_obj.pprint_array["until_expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardDim(
        self,
        swan_obj: S.ForwardDim,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Dimension visitor

        Parameters
        ----------
        swan_obj : S.ForwardDim
            Visited Swan object, it's a ForwardDim instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "expr": None,
            "dim_id": None,
            "elems": [],
            "protected": None,
        }
        # Visit properties
        if swan_obj.expr:
            self._visit(swan_obj.expr, swan_obj, "expr")

        if swan_obj.is_protected:
            _decl = R.DText(S.Markup.to_str(swan_obj.value, markup=S.Markup.Dim))
        else:
            _decl = R.DBlock()
            _decl << "<<"
            _decl << swan_obj.pprint_array["expr"]
            _decl << ">>"
            if swan_obj.dim_id or swan_obj.elems:
                _decl << " with "
            if swan_obj.dim_id:
                self._visit(swan_obj.dim_id, swan_obj, "dim_id")
                _decl << "<<"
                _decl << swan_obj.pprint_array["dim_id"]
                _decl << ">> "
            if swan_obj.elems:
                for item in swan_obj.elems:
                    self._visit(item, swan_obj, "elems")
                _decl << R.doc_list(*swan_obj.pprint_array["elems"], sep=" ")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardElement(
        self,
        swan_obj: S.ForwardElement,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Element visitor

        Parameters
        ----------
        swan_obj : S.ForwardElement
            Visited Swan object, it's a ForwardElement instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["lhs"]
        _decl << " = "
        _decl << swan_obj.pprint_array["expr"]
        _decl << ";"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardItemClause(
        self,
        swan_obj: S.ForwardItemClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Item Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardItemClause
            Visited Swan object, it's a ForwardItemClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "last_default": None}
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.last_default:
            self._visit(swan_obj.last_default, swan_obj, "last_default")
            _decl << ": "
            _decl << swan_obj.pprint_array["last_default"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardLastDefault(
        self,
        swan_obj: S.ForwardLastDefault,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Last Default visitor

        Parameters
        ----------
        swan_obj : S.ForwardLastDefault
            Visited Swan object, it's a ForwardLastDefault instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"last": None, "default": None, "shared": None}
        # Visit properties
        _decl = R.DBlock()
        if swan_obj.shared:
            self._visit(swan_obj.shared, swan_obj, "shared")
            _decl << "last = default = "
            _decl << swan_obj.pprint_array["shared"]
        else:
            if swan_obj.last:
                self._visit(swan_obj.last, swan_obj, "last")
                _decl << "last = "
                _decl << swan_obj.pprint_array["last"]
            if swan_obj.last and swan_obj.default:
                _decl << " "
            if swan_obj.default:
                self._visit(swan_obj.default, swan_obj, "default")
                _decl << "default = "
                _decl << swan_obj.pprint_array["default"]

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardLHS(
        self,
        swan_obj: S.ForwardLHS,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward LHS visitor

        Parameters
        ----------
        swan_obj : S.ForwardLHS
            Visited Swan object, it's a ForwardLHS instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None}
        # Visit properties
        if isinstance(swan_obj.lhs, (S.Identifier, S.ForwardLHS)):
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        _decl = R.DBlock()
        if swan_obj.is_id:
            _decl << swan_obj.pprint_array["lhs"]
        else:
            _decl << "["
            _decl << swan_obj.pprint_array["lhs"]
            _decl << "]"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardReturnArrayClause(
        self,
        swan_obj: S.ForwardReturnArrayClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Return Array Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardReturnArrayClause
            Visited Swan object, it's a ForwardReturnArrayClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"array_clause": None, "return_id": None}
        # Visit properties
        self._visit(swan_obj.array_clause, swan_obj, "array_clause")
        _decl = R.DBlock()
        if swan_obj.return_id:
            self._visit(swan_obj.return_id, swan_obj, "return_id")
            _decl << swan_obj.pprint_array["return_id"]
            _decl << " = "
        _decl << swan_obj.pprint_array["array_clause"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardReturnItemClause(
        self,
        swan_obj: S.ForwardReturnItemClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Return Item Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardReturnItemClause
            Visited Swan object, it's a ForwardReturnItemClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"item_clause": None}
        # Visit properties
        self._visit(swan_obj.item_clause, swan_obj, "item_clause")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["item_clause"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ForwardState(
        self,
        swan_obj: S.ForwardState,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward State visitor

        Parameters
        ----------
        swan_obj : S.ForwardState
            Visited Swan object, it's a ForwardState instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(S.ForwardState.to_str(swan_obj))

    def visit_FunctionalUpdate(
        self,
        swan_obj: S.FunctionalUpdate,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Functional Update visitor

        Parameters
        ----------
        swan_obj : S.FunctionalUpdate
            Visited Swan object, it's a FunctionalUpdate instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "modifiers": []}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.modifiers:
            self._visit(item, swan_obj, "modifiers")

        _decl = R.DBlock()
        _decl << "("
        _decl << swan_obj.pprint_array["expr"]
        _decl << " with "
        _decl << R.doc_list(*swan_obj.pprint_array["modifiers"], sep="; ")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Group(
        self,
        swan_obj: S.Group,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group visitor

        Parameters
        ----------
        swan_obj : S.Group
            Visited Swan object, it's a Group instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"items": None}
        _itm = []
        # Visit properties
        for item in swan_obj.items:
            self._visit(item, swan_obj, "items")
            _itm.append(swan_obj.pprint_array["items"])
        _decl = R.DBlock()
        _decl << R.doc_list(*_itm, sep=", ")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GroupAdaptation(
        self,
        swan_obj: S.GroupAdaptation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Adaption visitor

        Parameters
        ----------
        swan_obj : S.GroupAdaptation
            Visited Swan object, it's a GroupAdaptation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"renamings": None}
        _rnm = []
        # Visit properties
        for item in swan_obj.renamings:
            self._visit(item, swan_obj, "renamings")
            _rnm.append(swan_obj.pprint_array["renamings"])
        _decl = R.DBlock()
        _decl << ".("
        if _rnm:
            _decl << R.doc_list(*_rnm, sep=", ")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GroupConstructor(
        self,
        swan_obj: S.GroupConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Constructor visitor

        Parameters
        ----------
        swan_obj : S.GroupConstructor
            Visited Swan object, it's a GroupConstructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        _decl = R.DBlock()
        _decl << "("
        _decl << swan_obj.pprint_array["group"]
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GroupDecl(
        self,
        swan_obj: S.GroupDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a group declaration
        Syntax:
        |    group_decl ::= id = group_type_expr
        |    group_type_expr ::= type_expr
        |       | ( group_type_expr {{ , group_type_expr }} {{ , id : group_type_expr }} )
        |       | ( id : group_type_expr {{ , id : group_type_expr }} )

        Parameters
        ----------
        swan_obj : S.GroupDecl
            Visited Swan object, it's a GroupDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "type": None}
        # Visit parent class
        super().visit_GroupDecl(swan_obj, owner, owner_property)
        # Visit properties
        _decl = R.DBlock()

        _type = PPrinter._doc_or_list(swan_obj.pprint_array["type"])
        _decl << swan_obj.pprint_array["id"] << " = " << _type

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_GroupDeclarations(
        self,
        swan_obj: S.GroupDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of group declarations

        Parameters
        ----------
        swan_obj : S.GroupDeclarations
            Visited Swan object, it's a GroupDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"groups": []}
        # Visit parent class
        super().visit_GroupDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "groups", "group")
        owner.pprint_array[owner_property] = swan_obj.pprint_array[self.__own_property]

    def visit_GroupItem(
        self,
        swan_obj: S.GroupItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Item visitor

        Parameters
        ----------
        swan_obj : S.GroupItem
            Visited Swan object, it's a GroupItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "label": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        if swan_obj.label:
            self._visit(swan_obj.label, swan_obj, "label")
            _decl << swan_obj.pprint_array["label"]
            _decl << ": "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GroupOperation(
        self,
        swan_obj: S.GroupOperation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Operation visitor

        Parameters
        ----------
        swan_obj : S.GroupOperation
            Visited Swan object, it's a GroupOperation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        if swan_obj == S.GroupOperation.Normalize:
            owner.pprint_array[owner_property] = R.text("()")
        elif swan_obj == S.GroupOperation.NoOp:
            owner.pprint_array[owner_property] = R.text("")
        else:
            owner.pprint_array[owner_property] = R.text(S.GroupOperation.to_str(swan_obj))

    def visit_GroupRenaming(
        self,
        swan_obj: S.GroupRenaming,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Renaming visitor

        Parameters
        ----------
        swan_obj : S.GroupRenaming
            Visited Swan object, it's a GroupRenaming instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"source": None, "renaming": None}
        # Visit properties
        _decl = R.DBlock()
        self._visit(swan_obj.source, swan_obj, "source")
        _decl << swan_obj.pprint_array["source"]
        if swan_obj.renaming:
            self._visit(swan_obj.renaming, swan_obj, "renaming")
            _decl << ": "
            _decl << swan_obj.pprint_array["renaming"]
        elif swan_obj.is_shortcut:
            _decl << ":"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GroupProjection(
        self,
        swan_obj: S.GroupProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Projection visitor

        Parameters
        ----------
        swan_obj : S.GroupProjection
            Visited Swan object, it's a GroupProjection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "adaptation": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.adaptation, swan_obj, "adaptation")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << " "
        _decl << swan_obj.pprint_array["adaptation"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GroupTypeExpressionList(
        self,
        swan_obj: S.GroupTypeExpressionList,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group type expression list visitor

        Parameters
        ----------
        swan_obj : S.GroupTypeExpressionList
            Visited Swan object, it's a GroupTypeExpressionList instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"positional": None, "named": None}
        _lst_items = []
        # Visit properties
        for item in swan_obj.positional:
            self._visit(item, swan_obj, "positional")
            _lst_items.append(swan_obj.pprint_array["positional"])
        for item in swan_obj.named:
            self._visit(item, swan_obj, "named")
            _lst_items.append(swan_obj.pprint_array["named"])
        _decl = R.DBlock()
        _decl << "("
        _decl << R.doc_list(*_lst_items, sep=", ")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_GuaranteeSection(
        self,
        swan_obj: S.GuaranteeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Guarantee Section visitor

        Parameters
        ----------
        swan_obj : S.GuaranteeSection
            Visited Swan object, it's a GuaranteeSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"guarantees": None}
        _grt = []
        # Visit properties
        for item in swan_obj.guarantees:
            self._visit(item, swan_obj, "guarantees")
            _grt.append(swan_obj.pprint_array["guarantees"])
        owner.pprint_array[owner_property] = PPrinter._format_list("guarantee", _grt)

    def visit_Identifier(
        self,
        swan_obj: S.Identifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Identifier visitor

        Parameters
        ----------
        swan_obj : S.Identifier
            Visited Swan object, it's a Identifier instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _decl = R.DBlock()
        if swan_obj.pragmas:
            # Init data buffer
            swan_obj.pprint_array = {"pragmas": None}
            _pgm = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgm.append(swan_obj.pprint_array["pragmas"])

            if _pgm:
                _decl << R.doc_list(*_pgm, sep=" ") << " "

        if swan_obj.must_be_protected:
            _decl << R.DText(S.Markup.to_str(swan_obj.value))
        else:
            _decl << R.DText(swan_obj.value)
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_IfActivation(
        self,
        swan_obj: S.IfActivation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        IfActivation visitor

        Parameters
        ----------
        swan_obj : S.IfActivation
            Visited Swan object, it's a IfActivation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"branches": None}
        _brc = []
        # Visit properties
        for idx, item in enumerate(swan_obj.branches):
            self._visit(item, swan_obj, "branches")
            if idx == 0:
                _brc.append(R.DBlock() << "if " << swan_obj.pprint_array["branches"])
            else:
                if item.condition:
                    _brc.append(R.DBlock() << "elsif " << swan_obj.pprint_array["branches"])
                else:
                    _brc.append(swan_obj.pprint_array["branches"])
        _decl = R.DBlock()
        if _brc:
            _decl << R.doc_list(*_brc, sep="@n")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_IfActivationBranch(
        self,
        swan_obj: S.IfActivationBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        IfActivation Branch visitor

        Parameters
        ----------
        swan_obj : S.IfActivationBranch
            Visited Swan object, it's a IfActivationBranch instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"condition": None, "branch": None}
        # Visit properties
        self._visit(swan_obj.branch, swan_obj, "branch")
        _decl = R.DBlock()
        if swan_obj.condition:
            self._visit(swan_obj.condition, swan_obj, "condition")
            _decl << swan_obj.pprint_array["condition"] << "@n"
            _decl << "then" << "@i" << "@n"
            _decl << swan_obj.pprint_array["branch"] << "@u"
        else:
            _decl << "else" << "@i" << "@n" << swan_obj.pprint_array["branch"] << "@u"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_IfteDataDef(
        self,
        swan_obj: S.IfteDataDef,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        IfteDataDef visitor

        Parameters
        ----------
        swan_obj : S.IfteDataDef
            Visited Swan object, it's a IfteDataDef instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"data_def": None}
        # Visit properties
        self._visit(swan_obj.data_def, swan_obj, "data_def")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["data_def"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_IfteExpr(
        self,
        swan_obj: S.IfteExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        If Then Else Expression visitor

        Parameters
        ----------
        swan_obj : S.IfteExpr
            Visited Swan object, it's a IfteExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "cond_expr": None,
            "then_expr": None,
            "else_expr": None,
        }
        # Visit properties
        self._visit(swan_obj.cond_expr, swan_obj, "cond_expr")
        self._visit(swan_obj.then_expr, swan_obj, "then_expr")
        self._visit(swan_obj.else_expr, swan_obj, "else_expr")
        _decl = R.DBlock()
        _decl << "if "
        _decl << swan_obj.pprint_array["cond_expr"]
        _decl << " then "
        _decl << swan_obj.pprint_array["then_expr"]
        _decl << " else "
        _decl << swan_obj.pprint_array["else_expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_IfteIfActivation(
        self,
        swan_obj: S.IfteIfActivation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """IfteIfActivation visitor function. Should be overridden."""
        # Visit properties
        swan_obj.pprint_array = {"if_activation": None}
        self._visit(swan_obj.if_activation, swan_obj, "if_activation")
        PPrinter._update_property(owner, owner_property, swan_obj.pprint_array["if_activation"])

    def visit_Int8Type(
        self,
        swan_obj: S.Int8Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int8 Type visitor

        Parameters
        ----------
        swan_obj : S.Int8Type
            Visited Swan object, it's a Int8Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Int16Type(
        self,
        swan_obj: S.Int16Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int16 Type visitor

        Parameters
        ----------
        swan_obj : S.Int16Type
            Visited Swan object, it's a Int16Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Int32Type(
        self,
        swan_obj: S.Int32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int32 Type visitor

        Parameters
        ----------
        swan_obj : S.Int32Type
            Visited Swan object, it's a Int32Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Int64Type(
        self,
        swan_obj: S.Int64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int64 Type visitor

        Parameters
        ----------
        swan_obj : S.Int64Type
            Visited Swan object, it's a Int64Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_IntPattern(
        self,
        swan_obj: S.IntPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Integer Pattern visitor

        Parameters
        ----------
        swan_obj : S.IntPattern
            Visited Swan object, it's a IntPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(str(swan_obj))

    def visit_Iterator(
        self,
        swan_obj: S.Iterator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Iterator visitor

        Parameters
        ----------
        swan_obj : S.Iterator
            Visited Swan object, it's a Iterator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"kind": None, "operator": None}
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")
        self._visit(swan_obj.operator, swan_obj, "operator")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["kind"]
        _decl << " "
        _decl << swan_obj.pprint_array["operator"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_IteratorKind(
        self,
        swan_obj: S.IteratorKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        Iterator Kind visitor

        Parameters
        ----------
        swan_obj : S.IteratorKind
            Visited Swan object, it's a IteratorKind instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(S.IteratorKind.to_str(swan_obj))

    def visit_LabelOrIndex(
        self,
        swan_obj: S.LabelOrIndex,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Label Or Index visitor

        Parameters
        ----------
        swan_obj : S.LabelOrIndex
            Visited Swan object, it's a LabelOrIndex instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"value": None}
        # Visit properties
        if isinstance(swan_obj.value, (S.Identifier, S.Expression)):
            self._visit(swan_obj.value, swan_obj, "value")
        _decl = R.DBlock()
        if swan_obj.is_label:
            _decl << "."
            _decl << swan_obj.pprint_array["value"]
        else:
            _decl << "["
            _decl << swan_obj.pprint_array["value"]
            _decl << "]"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_LastExpr(
        self,
        swan_obj: S.LastExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Last Expression visitor

        Parameters
        ----------
        swan_obj : S.LastExpr
            Visited Swan object, it's a LastExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None}
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _decl = R.DBlock()
        _decl << "last "
        _decl << swan_obj.pprint_array["id"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_LetSection(
        self,
        swan_obj: S.LetSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Let Section visitor

        Parameters
        ----------
        swan_obj : S.LetSection
            Visited Swan object, it's a LetSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"equations": None}
        _eqt = []
        # Visit properties
        for item in swan_obj.equations:
            self._visit(item, swan_obj, "equations")
            _eqt.append(swan_obj.pprint_array["equations"])
        owner.pprint_array[owner_property] = PPrinter._format_list("let", _eqt, "", True)

    def visit_LHSItem(
        self,
        swan_obj: S.LHSItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        LHS Item visitor

        Parameters
        ----------
        swan_obj : S.LHSItem
            Visited Swan object, it's a LHSItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None}
        # Visit properties
        if isinstance(swan_obj.id, S.Identifier):
            self._visit(swan_obj.id, swan_obj, "id")
            owner.pprint_array[owner_property] = swan_obj.pprint_array["id"]
        else:
            owner.pprint_array[owner_property] = "_"

    def visit_Literal(
        self,
        swan_obj: S.Literal,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Literal visitor

        Parameters
        ----------
        swan_obj : S.Literal
            Visited Swan object, it's a Literal instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(swan_obj.value)

    def visit_Luid(self, swan_obj: S.Luid, owner: Owner, owner_property: OwnerProperty) -> None:
        """
        Luid visitor

        Parameters
        ----------
        swan_obj : S.Luid
            Visited Swan object, it's a Luid instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(str(swan_obj))

    def visit_Lunum(
        self,
        swan_obj: S.Lunum,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Lunum visitor

        Parameters
        ----------
        swan_obj : S.Lunum
            Visited Swan object, it's a Lunum instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(str(swan_obj))

    def visit_Merge(
        self,
        swan_obj: S.Merge,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Merge visitor

        Parameters
        ----------
        swan_obj : S.Merge
            Visited Swan object, it's a Merge instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"params": None}
        _prm = []
        # Visit properties
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")
            _prm.append(swan_obj.pprint_array["params"])
        if _prm:
            _decl = R.DBlock()
            _decl << "merge "
            _decl << R.doc_list(*[R.DBlock() << "(" << itm << ")" for itm in _prm], sep=" ")
            # Update property
            PPrinter._update_property(owner, owner_property, _decl)

    def visit_Modifier(
        self,
        swan_obj: S.Modifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Modifier visitor

        Parameters
        ----------
        swan_obj : S.Modifier
            Visited Swan object, it's a Modifier instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"modifier": None, "expr": None}
        _decl = R.DBlock()
        # Visit properties
        if isinstance(swan_obj.modifier, list):
            _mdp = []
            for item in swan_obj.modifier:
                self._visit(item, swan_obj, "modifier")
                _mdp.append(swan_obj.pprint_array["modifier"])
            _decl << R.doc_list(*_mdp, sep="")
        else:
            _decl << R.DText(S.Markup.to_str(swan_obj.modifier))

        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl << " = " << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Module(
        self,
        swan_obj: S.Module,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Module visitor

        Parameters
        ----------
        swan_obj : S.Module
            Visited Swan object, it's a Module instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"use_directives": [], "declarations": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << R.DText(gen_swan_version()) << "@n"
        if swan_obj.use_directives:
            for item in swan_obj.use_directives:
                self._visit(item, swan_obj, "use_directives")

            if swan_obj.pprint_array["use_directives"]:
                _decl << R.doc_list(
                    *swan_obj.pprint_array["use_directives"], sep=R.DLineBreak(False)
                )
                _decl << R.DLineBreak(False)
        if swan_obj.declarations:
            _dcl = []
            for item in swan_obj.declarations:
                self._visit(item, swan_obj, "declarations")
                _dcl.append(swan_obj.pprint_array["declarations"])
            if _dcl:
                _decl << R.doc_list(*_dcl, sep=R.DLineBreak(False))
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        if isinstance(owner, PPrinter):
            del swan_obj.pprint_array

    def visit_ModuleBody(
        self,
        swan_obj: S.ModuleBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Module Body visitor

        Parameters
        ----------
        swan_obj : S.ModuleBody
            Visited Swan object, it's a ModuleBody instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_Module(swan_obj, owner, owner_property)

    def visit_ModuleInterface(
        self,
        swan_obj: S.ModuleInterface,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Module Interface visitor

        Parameters
        ----------
        swan_obj : S.ModuleInterface
            Visited Swan object, it's a ModuleInterface instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_Module(swan_obj, owner, owner_property)

    def visit_NamedGroupTypeExpression(
        self,
        swan_obj: S.NamedGroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Named Group Type Expression visitor

        Parameters
        ----------
        swan_obj : S.NamedGroupTypeExpression
            Visited Swan object, it's a NamedGroupTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"label": None, "type": None}
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, owner_property)
        # Visit properties
        self._visit(swan_obj.label, swan_obj, "label")
        self._visit(swan_obj.type, swan_obj, "type")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["label"]
        _decl << ": "
        _decl << PPrinter._doc_or_list(swan_obj.pprint_array["type"])
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_NaryOp(
        self,
        swan_obj: S.NaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        NaryOp visitor

        Parameters
        ----------
        swan_obj : S.NaryOp
            Visited Swan object, it's a NaryOp instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        owner.pprint_array[owner_property] = R.text(S.NaryOp.to_str(swan_obj))

    def visit_NAryOperator(
        self,
        swan_obj: S.NAryOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        N-Ary Operator visitor

        Parameters
        ----------
        swan_obj : S.NAryOperator
            Visited Swan object, it's a NAryOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["operator"]

    def visit_NumericCast(
        self,
        swan_obj: S.NumericCast,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Numeric Casting visitor

        Parameters
        ----------
        swan_obj : S.NumericCast
            Visited Swan object, it's a NumericCast instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "type": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.type, swan_obj, "type")
        _decl = R.DBlock()
        _decl << "("
        _decl << swan_obj.pprint_array["expr"]
        _decl << " :> "
        _decl << swan_obj.pprint_array["type"]
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Operator(
        self,
        swan_obj: S.Operator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Operator visitor

        Parameters
        ----------
        swan_obj : S.Operator
            Visited Swan object, it's a Operator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Visit base class(es)
        self.visit_OperatorSignatureBase(swan_obj, owner, owner_property)
        _decl = R.DBlock()

        if swan_obj.is_text:
            _decl << "{text%"
        _decl << owner.pprint_array[owner_property]
        # Init data buffer
        swan_obj.pprint_array = {"body": None}
        # Visit properties
        if isinstance(swan_obj.body, (S.Scope, S.Equation)):
            self._visit(swan_obj.body, swan_obj, "body")
            _decl << "@n"
            if isinstance(swan_obj.body, S.Equation):
                _decl << "  "
            _decl << swan_obj.pprint_array["body"]
        else:
            _decl << ";"
        if swan_obj.is_text:
            _decl << "%text}"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_OperatorBase(
        self,
        swan_obj: S.OperatorBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Operator Base visitor

        Parameters
        ----------
        swan_obj : S.OperatorBase
            Visited Swan object, it's a OperatorBase instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"sizes": None}
        _sz = []
        # Visit properties
        for item in swan_obj.sizes:
            self._visit(item, swan_obj, "sizes")
            _sz.append(swan_obj.pprint_array["sizes"])
        _decl = R.DBlock()
        _decl << owner.pprint_array[owner_property]
        if _sz:
            _decl << " <<"
            _decl << R.doc_list(*_sz, sep=", ")
            _decl << ">>"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_OperatorInstance(
        self,
        swan_obj: S.OperatorInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Operator Instance visitor

        Parameters
        ----------
        swan_obj : S.OperatorInstance
            Visited Swan object, it's a OperatorInstance instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "params": None, "luid": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.params, swan_obj, "params")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["operator"]
        _decl << " "
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _decl << swan_obj.pprint_array["luid"]
            _decl << " "
        _decl << "("
        _decl << swan_obj.pprint_array["params"]
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_OperatorSignatureBase(
        self,
        swan_obj: S.Signature,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Signature visitor

        Parameters
        ----------
        swan_obj : S.Signature
            Visited Swan object, it's a Signature instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "pragmas": None,
            "inputs": None,
            "outputs": None,
            "sizes": None,
            "constraints": None,
            "specialization": None,
        }
        _in = []
        _ou = []
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _decl = R.DBlock()

        if swan_obj.is_text and not isinstance(swan_obj, S.Operator):
            _decl << r"{signature%"

        if swan_obj.is_inlined:
            _decl << "inline "
        if swan_obj.is_node:
            _decl << "node "
        else:
            _decl << "function "
        if swan_obj.pragmas:
            _pgm = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgm.append(swan_obj.pprint_array["pragmas"])
            if _pgm:
                _decl << R.doc_list(*_pgm, sep=" ")
                _decl << " "
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.sizes:
            _sz = []
            for item in swan_obj.sizes:
                self._visit(item, swan_obj, "sizes")
                _sz.append(swan_obj.pprint_array["sizes"])
            if _sz:
                _decl << " <<"
                _decl << R.doc_list(*_sz, sep=", ")
                _decl << ">>"
        for item in swan_obj.inputs:
            self._visit(item, swan_obj, "inputs")
            _in.append(swan_obj.pprint_array["inputs"])
        _decl << " (" << "@i"
        if _in:
            separator = R.doc_list(";", "@n")
            _decl << "@m" << R.doc_list(*_in, sep=separator) << ";" << "@M"
        _decl << ")"
        _decl << R.DLineBreak(True)
        _decl << "returns "
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
            _ou.append(swan_obj.pprint_array["outputs"])
        _decl << "(" << "@m"
        if _ou:
            _decl << R.doc_list(*_ou, sep=R.doc_list(";", "@n")) << ";"
        _decl << ")" << "@M"
        if swan_obj.constraints:
            _ct = []
            for item in swan_obj.constraints:
                self._visit(item, swan_obj, "constraints")
                _ct.append(swan_obj.pprint_array["constraints"])
            if _ct:
                _decl << R.doc_list(*_ct, sep=" ")
        if swan_obj.specialization:
            self._visit(swan_obj.specialization, swan_obj, "specialization")
            if swan_obj.pprint_array["specialization"]:
                _decl << " specialize "
                _decl << swan_obj.pprint_array["specialization"]
        if not isinstance(swan_obj, S.Operator):
            # Case when called as visit base class from Operator
            _decl << ";"
        _decl << "@u"

        if swan_obj.is_text and not isinstance(swan_obj, S.Operator):
            _decl << r"%signature}"

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_OptGroupItem(
        self,
        swan_obj: S.OptGroupItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        OptGroupItem visitor

        Parameters
        ----------
        swan_obj : S.OptGroupItem
            Visited Swan object, it's a OptGroupItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _decl = R.DBlock()
        # Visit properties
        if swan_obj.item:
            # Init data buffer
            swan_obj.pprint_array = {"item": None}
            self._visit(swan_obj.item, swan_obj, "item")
            _decl << swan_obj.pprint_array["item"]
        else:
            _decl << "_"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Partial(
        self,
        swan_obj: S.Partial,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Partial visitor

        Parameters
        ----------
        swan_obj : S.Partial
            Visited Swan object, it's a Partial instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "partial_group": None}
        _pg = []
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        for item in swan_obj.partial_group:
            self._visit(item, swan_obj, "partial_group")
            _pg.append(swan_obj.pprint_array["partial_group"])
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["operator"]
        _decl << " \\ "
        _decl << R.doc_list(*_pg, sep=", ")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_PathIdentifier(
        self,
        swan_obj: S.PathIdentifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Path Identifier visitor

        Parameters
        ----------
        swan_obj : S.PathIdentifier
            Visited Swan object, it's a PathIdentifier instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None, "pragmas": None}
        # Visit properties
        _decl = R.DBlock()
        if swan_obj.pragmas:
            _pgm = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgm.append(swan_obj.pprint_array["pragmas"])

            if _pgm:
                _decl << R.doc_list(*_pgm, sep=" ") << " "

        if swan_obj.is_protected:
            _decl << R.DText(S.Markup.to_str(swan_obj.path_id))
        else:
            _lst = []
            for item in swan_obj.path_id:
                self._visit(item, swan_obj, "path_id")
                _lst.append(swan_obj.pprint_array["path_id"])
            if _lst:
                _decl << R.doc_list(*_lst, sep="::")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_PathIdExpr(
        self,
        swan_obj: S.PathIdExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Path Identifier Expression visitor

        Parameters
        ----------
        swan_obj : S.PathIdExpr
            Visited Swan object, it's a PathIdExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit base class(es)
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["path_id"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_PathIdOpCall(
        self,
        swan_obj: S.PathIdOpCall,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        PathId Operator Call visitor

        Parameters
        ----------
        swan_obj : S.PathIdOpCall
            Visited Swan object, it's a PathIdOpCall instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["path_id"]
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, owner_property)

    def visit_PathIdPattern(
        self,
        swan_obj: S.PathIdPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        PathId Pattern visitor

        Parameters
        ----------
        swan_obj : S.PathIdPattern
            Visited Swan object, it's a PathIdPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["path_id"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_PortExpr(
        self,
        swan_obj: S.PortExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Port Expression visitor

        Parameters
        ----------
        swan_obj : S.PortExpr
            Visited Swan object, it's a PortExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lunum": None, "luid": None}
        _decl = R.DBlock()
        # Visit properties
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _decl << swan_obj.pprint_array["lunum"]
        if swan_obj.is_self:
            _decl << "self"
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _decl << swan_obj.pprint_array["luid"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Pragma(
        self,
        swan_obj: S.Pragma,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pragma visitor

        Parameters
        ----------
        swan_obj : S.Pragma
            Visited Swan object, it's a Pragma instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(swan_obj.pragma)

    def visit_PragmaBase(
        self,
        swan_obj: S.PragmaBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        PragmaBase visitor

        Parameters
        ----------
        swan_obj : S.PragmaBase
            Visited Swan object, it's a PragmaBase instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Visit properties
        if swan_obj.pragmas:
            swan_obj.pprint_array = {"pragmas": None}
            _pgs = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgs.append(swan_obj.pprint_array["pragmas"])
            if _pgs:
                _decl = R.DBlock()
                _decl << R.doc_list(*_pgs, sep=" ")
                # Update property
                PPrinter._update_property(owner, owner_property, _decl)

    def visit_PredefinedType(
        self,
        swan_obj: S.PredefinedType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Predefined Type visitor

        Parameters
        ----------
        swan_obj : S.PredefinedType
            Visited Swan object, it's a PredefinedType instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(swan_obj.name)

    def visit_PrefixOperatorExpression(
        self,
        swan_obj: S.PrefixOperatorExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Prefix Operator Expression visitor

        Parameters
        ----------
        swan_obj : S.PrefixOperatorExpression
            Visited Swan object, it's a PrefixOperatorExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"op_expr": None}
        # Visit properties
        self._visit(swan_obj.op_expr, swan_obj, "op_expr")
        _decl = R.DBlock()
        if swan_obj.is_text:
            _decl << r"{text%"
        elif swan_obj.is_op_expr:
            _decl << r"{op_expr%"
        _decl << "("
        _decl << swan_obj.pprint_array["op_expr"]
        _decl << ")"
        if swan_obj.is_text:
            _decl << r"%text}"
        elif swan_obj.is_op_expr:
            _decl << r"%op_expr}"

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, owner_property)

    def visit_PrefixPrimitive(
        self,
        swan_obj: S.PrefixPrimitive,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Prefix Primitive visitor

        Parameters
        ----------
        swan_obj : S.PrefixPrimitive
            Visited Swan object, it's a PrefixPrimitive instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"kind": None}
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["kind"]
        _decl << owner.pprint_array[owner_property]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, owner_property)

    def visit_PrefixPrimitiveKind(
        self,
        swan_obj: S.PrefixPrimitiveKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        Prefix Primitive Kind visitor

        Parameters
        ----------
        swan_obj : S.PrefixPrimitiveKind
            Visited Swan object, it's a PrefixPrimitiveKind instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(S.PrefixPrimitiveKind.to_str(swan_obj))

    def visit_ProjectionWithDefault(
        self,
        swan_obj: S.ProjectionWithDefault,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Project With Default visitor

        Parameters
        ----------
        swan_obj : S.ProjectionWithDefault
            Visited Swan object, it's a ProjectionWithDefault instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "indices": [], "default": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.indices:
            self._visit(item, swan_obj, "indices")
        self._visit(swan_obj.default, swan_obj, "default")
        _decl = R.DBlock()
        _decl << "("
        _decl << swan_obj.pprint_array["expr"]
        _decl << " . "
        _decl << R.doc_list(*swan_obj.pprint_array["indices"], sep="")
        _decl << " default "
        _decl << swan_obj.pprint_array["default"]
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ProtectedDecl(
        self,
        swan_obj: S.ProtectedDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Declaration visitor

        Parameters
        ----------
        swan_obj : S.ProtectedDecl
            Visited Swan object, it's a ProtectedDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        _decl = R.DBlock()
        if swan_obj.markup:
            _decl << "{"
            _decl << R.DText(swan_obj.markup)
            _decl << "%"
        _dta = [R.DText(_itm) for _itm in swan_obj.data.split("\n")]
        _decl << R.doc_list(*_dta, sep=R.DLineBreak(False))
        if swan_obj.markup:
            _decl << "%"
            _decl << R.DText(swan_obj.markup)
            _decl << "}"
        owner.pprint_array[owner_property] = _decl

    def visit_ProtectedExpr(
        self,
        swan_obj: S.ProtectedExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Expression visitor

        Parameters
        ----------
        swan_obj : S.ProtectedExpr
            Visited Swan object, it's a ProtectedExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, owner_property)

    def visit_ProtectedGroupRenaming(
        self,
        swan_obj: S.ProtectedGroupRenaming,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected GroupRenaming visitor

        Parameters
        ----------
        swan_obj : S.ProtectedGroupRenaming
            Visited Swan object, it's a ProtectedGroupRenaming instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_GroupRenamingBase(swan_obj, owner, owner_property)
        self.visit_ProtectedItem(swan_obj, owner, owner_property)

    def visit_ProtectedItem(
        self,
        swan_obj: S.ProtectedItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Item visitor

        Parameters
        ----------
        swan_obj : S.ProtectedItem
            Visited Swan object, it's a ProtectedItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _decl = R.DBlock()
        _decl << "{" << swan_obj.markup << "%"
        _dta = [R.DText(_itm) for _itm in swan_obj.data.split("\n")]
        _decl << R.doc_list(*_dta, sep=R.DLineBreak(False))
        _decl << "%" << swan_obj.markup << "}"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_ProtectedOpExpr(
        self,
        swan_obj: S.ProtectedOpExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Operator Expression visitor

        Parameters
        ----------
        swan_obj : S.ProtectedOpExpr
            Visited Swan object, it's a ProtectedOpExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, owner_property)

    def visit_ProtectedSection(
        self,
        swan_obj: S.ProtectedSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Section visitor

        Parameters
        ----------
        swan_obj : S.ProtectedSection
            Visited Swan object, it's a ProtectedSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, owner_property)

    def visit_ProtectedVariable(
        self,
        swan_obj: S.ProtectedVariable,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Variable visitor

        Parameters
        ----------
        swan_obj : S.ProtectedVariable
            Visited Swan object, it's a ProtectedVariable instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, owner_property)

    def visit_Restart(
        self,
        swan_obj: S.Restart,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Restart visitor

        Parameters
        ----------
        swan_obj : S.Restart
            Visited Swan object, it's a Restart instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "condition": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.condition, swan_obj, "condition")
        _decl = R.DBlock()
        _decl << "restart "
        _decl << swan_obj.pprint_array["operator"]
        _decl << " every "
        _decl << swan_obj.pprint_array["condition"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Scope(
        self,
        swan_obj: S.Scope,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Scope visitor

        Parameters
        ----------
        swan_obj : S.Scope
            Visited Swan object, it's a Scope instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PragmaBase(swan_obj, owner, owner_property)
        # Init data buffer
        swan_obj.pprint_array = {"sections": None}
        _sc = []
        # Visit properties
        for item in swan_obj.sections:
            self._visit(item, swan_obj, "sections")
            _sc.append(swan_obj.pprint_array["sections"])
        _decl = R.DBlock()
        _decl << "{"
        if _sc:
            _decl << "@i" << "@n"
            _decl << R.doc_list(*_sc, sep="@n") << "@u"
        _decl << "@n"
        if swan_obj.pragmas:
            _decl << owner.pprint_array[owner_property]
        if owner_property == "data_def":
            _decl << "@n" << "}"
        else:
            _decl << "}" << "@n"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Signature(
        self,
        swan_obj: S.Signature,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Signature visitor

        Parameters
        ----------
        swan_obj : S.Signature
            Visited Swan object, it's a Signature instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self.visit_OperatorSignatureBase(swan_obj, owner, owner_property)

    def visit_SizedTypeExpression(
        self,
        swan_obj: S.SizedTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Sized Type Expression visitor

        Parameters
        ----------
        swan_obj : S.SizedTypeExpression
            Visited Swan object, it's a SizedTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"size": None}
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        _decl = R.DBlock()
        if swan_obj.is_signed:
            _decl << "signed "
        else:
            _decl << "unsigned "
        _decl << "<<"
        _decl << swan_obj.pprint_array["size"]
        _decl << ">>"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_SectionBlock(
        self,
        swan_obj: S.SectionBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Section Block visitor

        Parameters
        ----------
        swan_obj : S.SectionBlock
            Visited Swan object, it's a SectionBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"section": None}
        # Visit properties
        self._visit(swan_obj.section, swan_obj, "section")
        if swan_obj.section.is_text:
            _doc = R.DBlock()
            _doc << "{text%"
            _doc << swan_obj.pprint_array["section"]
            _doc << "%text}"
        else:
            _doc = swan_obj.pprint_array["section"]
        owner.pprint_array[owner_property] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_SensorDecl(
        self,
        swan_obj: S.SensorDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a sensor declaration
        Syntax: sensor_decl ::= id : type_expr

        Parameters
        ----------
        swan_obj : S.SensorDecl
            Visited Swan object, it's a SensorDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "type": None,
        }
        # Visit parent class
        super().visit_SensorDecl(swan_obj, owner, owner_property)
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.pprint_array["type"]:
            _decl << ": " << swan_obj.pprint_array["type"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_SensorDeclarations(
        self,
        swan_obj: S.SensorDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of sensor declarations

        Parameters
        ----------
        swan_obj : S.SensorDeclarations
            Visited Swan object, it's a SensorDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"sensors": []}
        # Visit parent class
        super().visit_SensorDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "sensors", "sensor")
        owner.pprint_array[owner_property] = swan_obj.pprint_array[self.__own_property]

    def visit_Slice(
        self,
        swan_obj: S.Slice,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Slice visitor

        Parameters
        ----------
        swan_obj : S.Slice
            Visited Swan object, it's a Slice instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "start": None, "end": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.start, swan_obj, "start")
        self._visit(swan_obj.end, swan_obj, "end")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << "["
        _decl << swan_obj.pprint_array["start"]
        _decl << " .. "
        _decl << swan_obj.pprint_array["end"]
        _decl << "]"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_State(
        self,
        swan_obj: S.State,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        State visitor

        Parameters
        ----------
        swan_obj : S.State
            Visited Swan object, it's a State instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PragmaBase(swan_obj, owner, owner_property)
        _decl = R.DBlock()
        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "lunum": None,
            "strong_transitions": None,
            "sections": None,
            "weak_transitions": None,
        }
        _sts = []
        _sct = []
        _wts = []
        # Visit properties
        if swan_obj.strong_transitions:
            for item in swan_obj.strong_transitions:
                self._visit(item, swan_obj, "strong_transitions")
                _sts.append(swan_obj.pprint_array["strong_transitions"])
        if swan_obj.sections:
            for item in swan_obj.sections:
                self._visit(item, swan_obj, "sections")
                _sct.append(swan_obj.pprint_array["sections"])
        if swan_obj.weak_transitions:
            for item in swan_obj.weak_transitions:
                self._visit(item, swan_obj, "weak_transitions")
                _wts.append(swan_obj.pprint_array["weak_transitions"])
        if swan_obj.is_initial:
            _decl << "initial "
        _decl << "state"
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _decl << " " << swan_obj.pprint_array["lunum"]
        if swan_obj.id:
            self._visit(swan_obj.id, swan_obj, "id")
            _decl << " " << swan_obj.pprint_array["id"]
        if swan_obj.pragmas:
            _decl << "@n"
            _decl << owner.pprint_array[owner_property]
        _decl << " :" << "@i"
        if _sts:
            _decl << "@n" << "unless" << "@n"
            _decl << R.doc_list(*_sts, sep="@n")
        if _sct:
            _decl << "@n"
            _decl << R.doc_list(*_sct, sep="@n")
        if _wts:
            _decl << "@n" << "until" << "@n"
            _decl << R.doc_list(*_wts, sep="@n")
        _decl << "@u"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_StateRef(
        self,
        swan_obj: S.StateRef,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        StateRef visitor

        Parameters
        ----------
        swan_obj : S.StateRef
            Visited Swan object, it's a StateRef instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lunum": None, "id": None}
        _decl = R.DBlock()
        # Visit properties
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _decl << swan_obj.pprint_array["lunum"]
        else:
            self._visit(swan_obj.id, swan_obj, "id")
            _decl << swan_obj.pprint_array["id"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_StateMachine(
        self,
        swan_obj: S.StateMachine,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        State Machine visitor

        Parameters
        ----------
        swan_obj : S.StateMachine
            Visited Swan object, it's a StateMachine instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"items": None, "name": None}
        _it = []
        # Visit properties
        if swan_obj.items:
            for item in swan_obj.items:
                self._visit(item, swan_obj, "items")
                _it.append(swan_obj.pprint_array["items"])
        _decl = R.DBlock()
        _decl << "automaton" << "@i"
        if swan_obj.name:
            self._visit(swan_obj.name, swan_obj, "name")
            _decl << " " << swan_obj.pprint_array["name"]
        if _it:
            _decl << "@n"
            _decl << R.doc_list(*_it, sep="@n")
        _decl << "@u"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, owner_property)

    def visit_StateMachineBlock(
        self,
        swan_obj: S.StateMachineBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        State Machine Block visitor

        Parameters
        ----------
        swan_obj : S.StateMachineBlock
            Visited Swan object, it's a StateMachineBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_DefByCaseBlockBase(swan_obj, owner, owner_property)

    def visit_StructConstructor(
        self,
        swan_obj: S.StructConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Constructor visitor

        Parameters
        ----------
        swan_obj : S.StructConstructor
            Visited Swan object, it's a StructConstructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None, "type": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        _decl = R.DBlock()
        _decl << "{"
        _decl << swan_obj.pprint_array["group"]
        _decl << "}"
        if swan_obj.type:
            self._visit(swan_obj.type, swan_obj, "type")
            _decl << " : "
            _decl << swan_obj.pprint_array["type"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_StructDestructor(
        self,
        swan_obj: S.StructDestructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Destructor visitor

        Parameters
        ----------
        swan_obj : S.StructDestructor
            Visited Swan object, it's a StructDestructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["group"]
        _decl << " group ("
        _decl << swan_obj.pprint_array["expr"]
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_StructField(
        self,
        swan_obj: S.StructField,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Field visitor

        Parameters
        ----------
        swan_obj : S.StructField
            Visited Swan object, it's a StructField instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "type": None}
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        self._visit(swan_obj.type, swan_obj, "type")
        _decl = R.DBlock() << swan_obj.pprint_array["id"] << ": " << swan_obj.pprint_array["type"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_StructProjection(
        self,
        swan_obj: S.StructProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Projection visitor

        Parameters
        ----------
        swan_obj : S.StructProjection
            Visited Swan object, it's a StructProjection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "label": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.label, swan_obj, "label")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << swan_obj.pprint_array["label"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_StructTypeDefinition(
        self,
        swan_obj: S.StructTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Type Definition visitor

        Parameters
        ----------
        swan_obj : S.StructTypeDefinition
            Visited Swan object, it's a StructTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"fields": []}
        # Visit properties
        for item in swan_obj.fields:
            self._visit(item, swan_obj, "fields")

        _decl = R.DBlock() << "{" << R.doc_list(*swan_obj.pprint_array["fields"], sep=", ") << "}"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Target(
        self,
        swan_obj: S.Target,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Target visitor

        Parameters
        ----------
        swan_obj : S.Target
            Visited Swan object, it's a Target instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"target": None}
        # Visit properties
        self._visit(swan_obj.target, swan_obj, "target")
        _decl = R.DBlock()
        if swan_obj.is_restart:
            _decl << "restart"
        else:
            _decl << "resume"
        _decl << " " << swan_obj.pprint_array["target"]
        _decl << "@n"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Transition(
        self,
        swan_obj: S.Transition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Transition visitor

        Parameters
        ----------
        swan_obj : S.Transition
            Visited Swan object, it's a Transition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PragmaBase(swan_obj, owner, owner_property)
        # Init data buffer
        swan_obj.pprint_array = {"arrow": None}
        # Visit properties
        self._visit(swan_obj.arrow, swan_obj, "arrow")
        _decl = R.DBlock()
        if swan_obj.is_guarded:
            _decl << "if "
        _decl << swan_obj.pprint_array["arrow"]
        if swan_obj.pragmas:
            _decl << owner.pprint_array[owner_property]
        _decl << ";"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_TransitionDecl(
        self,
        swan_obj: S.TransitionDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        TransitionDecl visitor

        Parameters
        ----------
        swan_obj : S.TransitionDecl
            Visited Swan object, it's a TransitionDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "priority": None,
            "transition": None,
            "state_ref": None,
        }
        # Visit properties
        self._visit(swan_obj.transition, swan_obj, "transition")
        self._visit(swan_obj.state_ref, swan_obj, "state_ref")

        _decl = R.DBlock()
        _decl << ":"
        if swan_obj.priority:
            self._visit(swan_obj.priority, swan_obj, "priority")
            _decl << swan_obj.pprint_array["priority"]
        else:
            _decl << " "
        _decl << ":"
        _decl << " " << swan_obj.pprint_array["state_ref"]
        if swan_obj.is_strong:
            _decl << " unless"
        else:
            _decl << " until"
        _decl << " " << swan_obj.pprint_array["transition"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Transpose(
        self,
        swan_obj: S.Transpose,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Transpose visitor

        Parameters
        ----------
        swan_obj : S.Transpose
            Visited Swan object, it's a Transpose instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        _decl = R.DBlock()
        if swan_obj.params:
            _decl << " {"
            if isinstance(swan_obj.params, list):
                _pm = []
                for item in swan_obj.params:
                    _pm.append(R.text(item))
                if _pm:
                    _decl << R.doc_list(*_pm, sep=", ")
            elif SwanVisitor._is_builtin(swan_obj.params):
                _decl << R.text(swan_obj.params)
            _decl << "}"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_PrefixPrimitive(swan_obj, owner, owner_property)

    def visit_TypeConstraint(
        self,
        swan_obj: S.TypeConstraint,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Type Constraint visitor

        Parameters
        ----------
        swan_obj : S.TypeConstraint
            Visited Swan object, it's a TypeConstraint instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type_vars": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << "@n" << "where "
        if swan_obj.is_protected:
            _decl << R.DText(S.Markup.to_str(swan_obj.type_vars))
        else:
            _tv = []
            for item in swan_obj.type_vars:
                self._visit(item, swan_obj, "type_vars")
                _tv.append(swan_obj.pprint_array["type_vars"])
            if _tv:
                _decl << R.doc_list(*_tv, sep=", ")
        _decl << " " << R.DText(swan_obj.kind.name.lower())
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_TypeDecl(
        self,
        swan_obj: S.TypeDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a type declaration

        Parameters
        ----------
        swan_obj : S.TypeDecl
            Visited Swan object, it's a TypeDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "definition": None,
        }
        # Visit parent class
        super().visit_TypeDecl(swan_obj, owner, owner_property)
        # Visit properties
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.pprint_array["definition"]:
            _decl << " = " << swan_obj.pprint_array["definition"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_TypeDeclarations(
        self,
        swan_obj: S.TypeDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of type declarations

        Parameters
        ----------
        swan_obj : S.TypeDeclarations
            Visited Swan object, it's a TypeDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"types": []}
        # Visit parent class
        super().visit_TypeDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "types", "type")
        owner.pprint_array[owner_property] = swan_obj.pprint_array[self.__own_property]

    def visit_TypeGroupTypeExpression(
        self,
        swan_obj: S.TypeGroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Type Expression visitor

        Parameters
        ----------
        swan_obj : S.TypeGroupTypeExpression
            Visited Swan object, it's a TypeGroupTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type": None}
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["type"]

    def visit_TypeReferenceExpression(
        self,
        swan_obj: S.TypeReferenceExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Type Reference Expression visitor

        Parameters
        ----------
        swan_obj : S.TypeReferenceExpression
            Visited Swan object, it's a TypeReferenceExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"alias": None}
        # Visit properties
        self._visit(swan_obj.alias, swan_obj, "alias")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["alias"]

    def visit_Uint8Type(
        self,
        swan_obj: S.Uint8Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint8 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint8Type
            Visited Swan object, it's a Uint8Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Uint16Type(
        self,
        swan_obj: S.Uint16Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint16 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint16Type
            Visited Swan object, it's a Uint16Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Uint32Type(
        self,
        swan_obj: S.Uint32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint32 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint32Type
            Visited Swan object, it's a Uint32Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Uint64Type(
        self,
        swan_obj: S.Uint64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint64 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint64Type
            Visited Swan object, it's a Uint64Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_UnaryExpr(
        self,
        swan_obj: S.UnaryExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Unary Expression visitor

        Parameters
        ----------
        swan_obj : S.UnaryExpr
            Visited Swan object, it's a UnaryExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["operator"]
        _decl << " "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_UnaryOp(
        self,
        swan_obj: S.UnaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        Unary Operator visitor

        Parameters
        ----------
        swan_obj : S.UnaryOp
            Visited Swan object, it's a UnaryOp instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.text(S.UnaryOp.to_str(swan_obj))

    def visit_UnderscorePattern(
        self,
        swan_obj: S.UnderscorePattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Underscore Pattern visitor

        Parameters
        ----------
        swan_obj : S.UnderscorePattern
            Visited Swan object, it's a UnderscorePattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[owner_property] = R.DText("_")

    def visit_UseDirective(
        self,
        swan_obj: S.UseDirective,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Use Directive visitor

        Parameters
        ----------
        swan_obj : S.UseDirective
            Visited Swan object, it's a UseDirective instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path": None, "alias": None}
        # Visit properties
        self._visit(swan_obj.path, swan_obj, "path")
        _decl = R.DBlock()
        _decl << "use "
        _decl << swan_obj.pprint_array["path"]
        if swan_obj.alias:
            self._visit(swan_obj.alias, swan_obj, "alias")
            _decl << " as "
            _decl << swan_obj.pprint_array["alias"]
        _decl << ";" << "@n"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_VarDecl(
        self,
        swan_obj: S.VarDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variable Declaration visitor

        Parameters
        ----------
        swan_obj : S.VarDecl
            Visited Swan object, it's a VarDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "type": None,
            "when": None,
            "default": None,
            "last": None,
        }
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _decl = R.DBlock() << "@i"
        if swan_obj.is_clock:
            _decl << "clock "
        if swan_obj.is_probe:
            _decl << "#pragma cg probe #end "
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.type:
            self._visit(swan_obj.type, swan_obj, "type")
            _decl << ": "
            _decl << swan_obj.pprint_array["type"]
        if swan_obj.when:
            self._visit(swan_obj.when, swan_obj, "when")
            _decl << " when "
            _decl << swan_obj.pprint_array["when"]
        if swan_obj.default:
            self._visit(swan_obj.default, swan_obj, "default")
            _decl << " default = "
            _decl << swan_obj.pprint_array["default"]
        if swan_obj.last:
            self._visit(swan_obj.last, swan_obj, "last")
            _decl << " last = "
            _decl << swan_obj.pprint_array["last"]
        # Update property
        _decl << "@u"
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VariableTypeExpression(
        self,
        swan_obj: S.VariableTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variable Type Expression visitor

        Parameters
        ----------
        swan_obj : S.VariableTypeExpression
            Visited Swan object, it's a VariableTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"name": None}
        # Visit properties
        self._visit(swan_obj.name, swan_obj, "name")
        owner.pprint_array[owner_property] = swan_obj.pprint_array["name"]

    def visit_VariantPattern(
        self,
        swan_obj: S.VariantPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant Pattern visitor

        Parameters
        ----------
        swan_obj : S.VariantPattern
            Visited Swan object, it's a VariantPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None, "captured": None}
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["path_id"]
        if swan_obj.has_capture:
            self._visit(swan_obj.captured, swan_obj, "captured")
            _decl << " {"
            _decl << swan_obj.pprint_array["captured"]
            _decl << "}"
        elif swan_obj.underscore:
            _decl << " _"
        else:
            _decl << " {}"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VariantComponent(
        self,
        swan_obj: S.VariantSimple,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        VariantComponent Type Definition visitor.

        This is a helper function for variant type definition
        derived classes.

        Parameters
        ----------
        swan_obj : S.VariantComponent
            Visited Swan object, it's a VariantComponent derived instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self._visit(swan_obj.tag, swan_obj, "tag")

    def visit_VariantSimple(
        self,
        swan_obj: S.VariantSimple,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant type only defined by a tag visitor

        Parameters
        ----------
        swan_obj : S.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        swan_obj.pprint_array = {"tag": None}
        self.visit_VariantComponent(swan_obj, owner, owner_property)
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["tag"] << " {}"

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VariantTypeExpr(
        self,
        swan_obj: S.VariantTypeExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant type with expression visitor

        Parameters
        ----------
        swan_obj : S.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        swan_obj.pprint_array = {"tag": None, "type": None}
        self.visit_VariantComponent(swan_obj, owner, owner_property)
        self._visit(swan_obj.type, swan_obj, "type")

        _decl = R.DBlock()
        (_decl << swan_obj.pprint_array["tag"] << " { " << swan_obj.pprint_array["type"] << " }")

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VariantStruct(
        self,
        swan_obj: S.VariantStruct,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant type as structure visitor

        Parameters
        ----------
        swan_obj : S.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        swan_obj.pprint_array = {"tag": None, "fields": []}
        self.visit_VariantComponent(swan_obj, owner, owner_property)
        for item in swan_obj.fields:
            self._visit(item, swan_obj, "fields")

        _decl = R.DBlock()
        (
            _decl
            << swan_obj.pprint_array["tag"]
            << " {"
            << R.doc_list(*swan_obj.pprint_array["fields"], sep=", ")
            << "}"
        )

        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VariantTypeDefinition(
        self,
        swan_obj: S.VariantTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant Type Definition visitor

        Parameters
        ----------
        swan_obj : S.VariantTypeDefinition
            Visited Swan object, it's a VariantTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"tags": []}
        # Visit properties
        for itm in swan_obj.tags:
            self._visit(itm, swan_obj, "tags")

        _decl = R.DBlock()
        _decl << R.doc_list(*swan_obj.pprint_array["tags"], sep=" | ")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VariantValue(
        self,
        swan_obj: S.VariantValue,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant Value visitor

        Parameters
        ----------
        swan_obj : S.VariantValue
            Visited Swan object, it's a VariantValue instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"tag": None, "group": None}
        # Visit properties
        self._visit(swan_obj.tag, swan_obj, "tag")
        self._visit(swan_obj.group, swan_obj, "group")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["tag"]
        _decl << " {"
        _decl << swan_obj.pprint_array["group"]
        _decl << "}"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_VarSection(
        self,
        swan_obj: S.VarSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variable Section visitor

        Parameters
        ----------
        swan_obj : S.VarSection
            Visited Swan object, it's a VarSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"var_decls": None}
        _vr = []
        # Visit properties
        for item in swan_obj.var_decls:
            self._visit(item, swan_obj, "var_decls")
            _vr.append(swan_obj.pprint_array["var_decls"])
        owner.pprint_array[owner_property] = PPrinter._format_list("var", _vr)

    def visit_WhenClockExpr(
        self,
        swan_obj: S.WhenClockExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        When Clock Expression visitor

        Parameters
        ----------
        swan_obj : S.WhenClockExpr
            Visited Swan object, it's a WhenClockExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "clock": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.clock, swan_obj, "clock")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << " when "
        _decl << swan_obj.pprint_array["clock"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_WhenMatchExpr(
        self,
        swan_obj: S.WhenMatchExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        When Match Expression visitor

        Parameters
        ----------
        swan_obj : S.WhenMatchExpr
            Visited Swan object, it's a WhenMatchExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "when": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.when, swan_obj, "when")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["expr"]
        _decl << " when match "
        _decl << swan_obj.pprint_array["when"]
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Window(
        self,
        swan_obj: S.Window,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Window visitor

        Parameters
        ----------
        swan_obj : S.Window
            Visited Swan object, it's a Window instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"size": None, "init": None, "params": None}
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        self._visit(swan_obj.init, swan_obj, "init")
        self._visit(swan_obj.params, swan_obj, "params")
        _decl = R.DBlock()
        _decl << "window " << "<<"
        _decl << swan_obj.pprint_array["size"]
        _decl << ">> " << "("
        _decl << swan_obj.pprint_array["init"]
        _decl << ") " << "("
        _decl << swan_obj.pprint_array["params"] << ")"
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)

    def visit_Wire(self, swan_obj: S.Wire, owner: Owner, owner_property: OwnerProperty) -> None:
        """
        Wire visitor

        Parameters
        ----------
        swan_obj : S.Wire
            Visited Swan object, it's a Wire instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        swan_obj.pprint_array = {"source": None, "targets": []}
        # Visit properties
        self._visit(swan_obj.source, swan_obj, "source")
        for item in swan_obj.targets:
            self._visit(item, swan_obj, "targets")
        _decl = R.DBlock()
        _decl << "wire "
        _decl << swan_obj.pprint_array["source"]
        _decl << " => "
        _decl << R.doc_list(*swan_obj.pprint_array["targets"], sep=", ")
        # Update property
        PPrinter._update_property(owner, owner_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)


def swan_to_str(swan_obj: Union[S.SwanItem, None], normalize: bool = False) -> str:
    """
    Convert a Swan object to string.

    Parameters
    ----------
    swan_obj : swan_obj: S.SwanItem
        Swan construct to be converted.
    normalize : bool, optional
        Write each Swan declaration or all the same declarations on one line,
        by default False i.e. each Swan declaration per line.

    Returns
    -------
    str
        A Swan properties string according to its syntax description.
    """
    buffer = StringIO()
    printer = PPrinter(normalize=normalize)
    printer.print(buffer, swan_obj)
    res = buffer.getvalue()
    buffer.close()
    return res
