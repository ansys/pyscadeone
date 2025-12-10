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
# pyright: reportUnusedExpression=false

from io import IOBase, StringIO
from typing import Any, List, Optional, Union, cast
from enum import Flag, auto
from collections import deque

import ansys.scadeone.core.svc.common.renderer as R
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor, Owner, OwnerProperty
import ansys.scadeone.core.swan as Swan
from ansys.scadeone.core.common.versioning import gen_swan_version

PrintData = dict[str, Optional[Union[R.DElt, List[R.DElt], Flag]]]


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
        - Operator declaration and definition
        - Project

        Constructs all the necessary attributes for the PPrinter object

    Parameters
    ----------
    normalize : bool, optional
        Write all the same Swan declarations or each declaration on one line,
        by default True i.e. each Swan declaration per line
    """

    __own_property = "visitor"

    def __init__(self, normalize=True) -> None:
        super().__init__()
        self._normalize = normalize
        self._doc_data_stack: deque[PrintData] = deque()

    # Push/Pop doc data stack methods
    # the self._doc_data_stack is used to manage the current doc data, that is to say
    # the documents corresponding to the properties of the currently visited Swan object.
    # Invariants:
    #  - the top of the stack is always the doc data of the currently visited Swan object.
    #  - the second element from the top of the stack is always the doc data of the **owner** Swan object.
    # A visit method must:
    # 1. push a new doc data on the stack at the beginning of the method, with keys corresponding to the properties.
    #    Done using _push_and_get_doc_data() method
    # 2. calls the visit methods for each property, which will fill the doc data
    # 3. pop the doc data from the stack at the end of the method, and set the corresponding property for its owner,
    #    which is the result of 2. for properties
    #    Done using _pop_and_set_doc_data() method
    # Other methods are:
    # - _set_doc_data(): to set a property in the current doc data. Can used when it is not necessary to push/pop the stack.
    #   for simple cases.
    #   /!\: for properties that are lists, the document is appended to the list, else the document is set to the key.
    # - _get_current_doc_data(): to get the current doc data from the top of the stack.
    # - _get_owner_doc_data(): to get the owner doc data from the stack. Used when some context is stored in the owner doc data.

    def _push_and_get_doc_data(self, doc_data: PrintData):
        """Set doc data on the top of the stack.

        Parameters
        ----------
        doc_data : PrintData
            The doc data to set on top of the stack.
        Returns
        -------
        PrintData
            The doc data on the top of the stack.
        """
        self._doc_data_stack.append(doc_data)
        return doc_data

    def _pop_and_set_doc_data(self, key: OwnerProperty, doc: R.DElt | Flag) -> None:
        """Pop the top doc  data from the stack and set own doc data.

        Parameters
        ----------
        key: OwnerProperty
            key in the dictionary, actually of type str
        doc : R.DElt
            The document element to set as own doc data.
        """
        self._doc_data_stack.pop()
        self._set_doc_data(key, doc)

    def _set_doc_data(self, key: OwnerProperty, doc: R.DElt | Flag) -> None:
        """Set own doc data on the top of the stack.

        If the key correspondent to a list, append the doc to the list, else set
        the dict[key] to doc.

        Parameters
        ----------
        key: OwnerProperty
            key in the dictionary, actually of type str
        doc : R.DElt
            The document element to set as own print data.
        """
        top = self._get_current_doc_data()
        if isinstance(key, str):
            if isinstance(top[key], list):
                cast(List[R.DElt], top[key]).append(cast(R.DElt, doc))
            else:
                top[key] = doc

    def _get_current_doc_data(self) -> PrintData:
        """Get the current doc data from the top of the stack.

        Returns
        -------
        PrintData
            The doc data on the top of the stack.
        """
        return self._doc_data_stack[-1]

    def _get_owner_doc_data(self) -> PrintData:
        """Get the owner doc data from the stack.

        Returns
        -------
        PrintData
            The doc data of the owner, i.e. the second element from the top of the stack.
        """
        return self._doc_data_stack[-2]

    def print(
        self,
        stream: IOBase,
        swan_obj: Union[Swan.SwanItem, None],
        render: Optional[R.Renderer] = None,
    ):
        """
        Print a Swan object to the output stream

        Parameters
        ----------
        stream : IOBase
            A file or buffer to which the output will be written.
        swan_obj : Swan.SwanItem | None
            A Swan object to print. If None, 'None' is rendered.
        render : Optional[R.Renderer], optional
            A renderer to use for printing, by default None.
            If None, a new renderer will be created from R.Renderer class.
        """

        if not swan_obj:
            stream.write("None")
            return
        # Our own print
        self._doc_data_stack.clear()
        _p_data = self._push_and_get_doc_data({self.__own_property: None})
        # Visit Swan object to build document
        self.visit(swan_obj)
        # Write visited Swan code
        doc = R.Document()
        doc << _p_data[self.__own_property]
        if render is None:
            render = R.Renderer(stream)
        else:
            render.set_stream(stream)
        render.render(doc)

    def _decl_formatting(self, pprint_data: PrintData, key: str, prefix: str):
        """
        Helper to update a declaration formatting according to the 'normalize' attribute.

        Parameters
        ----------
        pprint_data : PrintData
            Documents for Swan declaration properties
        key : str
            Key name in the pprint_data dictionary
        prefix : str
            Prefix of a visited swan declaration syntax
        """

        if pprint_data[key]:
            _doc = R.DBlock()
            _decls = cast(List[R.DElt], pprint_data[key])
            if self._normalize:
                # Normalized format, one declaration per line
                _doc << prefix << " " << _decls[0] << ";" << "@n"
                for decl in _decls[1:]:
                    _doc << "@n" << prefix << " " << decl << ";" << "@n"
            else:
                # One single declaration
                _doc << prefix << " " << "@m" << _decls[0] << ";"
                for decl in _decls[1:]:
                    _doc << "@n" << decl << ";"
                _doc << "@M"
                _doc << "@n"
        else:
            _doc = R.DText(prefix)
        # Update data stream for declaration property
        pprint_data[key] = _doc

    def _decl_pragmas(self, swan_obj: Swan.HasPragma, _doc: R.DElt):
        """Add pragmas to the declaration _doc

        Parameters
        ----------
        swan_obj : Swan.HasPragma
            Object with pragmas. The object has been visited before calling this method,
            ensuring that the "pragmas" property is filled.
        _doc : R.DElt
            Declaration document to which the pragmas will be added
        """
        if swan_obj.pragmas:
            if len(swan_obj.pragmas) > 1:
                _doc << "@n"
            else:
                # multiple pragma possible case.
                _doc << "@m"
            _p_data = self._get_current_doc_data()
            _doc << _p_data["pragmas"]
            if len(swan_obj.pragmas) == 1:
                _doc << "@M"
            _doc << " "

    @classmethod
    def _expr_at_property(cls, expr: Swan.Expression, decl: R.DElt) -> R.DElt:
        """Check if expr as "at" property and return "(expr at ID)",
        or return decl

        Parameters
        ----------
        expr : Swan.Expression
            Expression to check
        decl : R.DElt
            Expression document

        Returns
        -------
        R.DElt
            A document with "(expr at ID)" or decl
        """
        if at := expr.at:
            _at = R.DBlock()
            _at << "(" << decl << " at " << str(at) << ")"
            return _at
        return decl

    @staticmethod
    def _doc_or_list(inp: Union[List[Any], R.DElt]) -> R.DElt:
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
    def _format_list(
        pref: str, lst: List[R.DElt], end: Optional[str] = ";", single_line=False
    ) -> R.DBlock:
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

        _doc = R.DBlock()
        _doc << pref
        if lst:
            if single_line:
                _doc << " "
            else:
                _doc << "@m" << "@n"
            _doc << R.doc_list(*[item << end for item in lst], sep="@n")
            if not single_line:
                _doc << "@M"
        return _doc

    def visit(self, swan_obj: Swan.SwanItem) -> None:
        """
        Visit method - Pretty prints a Swan item to data stream

        Parameters
        ----------
        swan_obj : Swan.SwanItem
            a visited Swan object, it's a Declaration instance
        """

        # Visit Swan declaration.
        self._visit(swan_obj, self, self.__own_property)  # type: ignore

    def visit_ActivateClock(
        self,
        swan_obj: Swan.ActivateClock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateClock visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateClock
            Visited Swan object, it's a ActivateClock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None, "clock": None})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.clock, swan_obj, "clock")
        _doc = R.DBlock()
        _doc << "activate "
        _doc << _p_data["operator"]
        _doc << " every "
        _doc << _p_data["clock"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ActivateIf(
        self,
        swan_obj: Swan.ActivateIf,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateIf visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateIf
            Visited Swan object, it's a ActivateIf instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"if_activation": None, "luid": None, "lunum": None})
        # Visit properties
        _doc = R.DBlock()
        if not isinstance(owner, Swan.DefByCaseBlockBase):
            # indentation from the beginning of the keyword
            _doc << "@m"
        _doc << "activate"
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << " " << _p_data["lunum"]
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << " " << _p_data["luid"]
        self._visit(swan_obj.if_activation, swan_obj, "if_activation")
        _doc << "@i" << "@n"
        _doc << _p_data["if_activation"]
        # Pass data to DefByCase visitor
        _p_data["defbycase_"] = _doc  # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, owner_property)

    def visit_ActivateIfBlock(
        self,
        swan_obj: Swan.ActivateIfBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateIf Block visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateIfBlock
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
        swan_obj: Swan.ActivateEvery,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateEvery visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateEvery
            Visited Swan object, it's a ActivateEvery instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None, "condition": None, "expr": None})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.condition, swan_obj, "condition")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << "activate "
        _doc << _p_data["operator"]
        _doc << " every "
        _doc << _p_data["condition"]
        if swan_obj.is_last:
            _doc << " last "
        else:
            _doc << " default "
        _doc << _p_data["expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ActivateWhen(
        self,
        swan_obj: Swan.ActivateWhen,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateWhen visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateWhen
            Visited Swan object, it's a ActivateWhen instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {"condition": None, "branches": [], "lunum": None, "luid": None}
        )
        # Visit properties
        _doc = R.DBlock()
        if not isinstance(owner, Swan.DefByCaseBlockBase):
            # indentation from the beginning of the keyword
            _doc << "@m"
        _doc << "activate"
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << " " << _p_data["lunum"]
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << " " << _p_data["luid"]
        _doc << " when "
        self._visit(swan_obj.condition, swan_obj, "condition")
        _doc << _p_data["condition"]
        _doc << " match" << "@i"
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")
        if _p_data["branches"]:
            _doc << "@n"
            _doc << R.doc_list(*(cast(List[R.DElt], _p_data["branches"])), sep="@n")
        _doc << "@u"
        if not isinstance(owner, Swan.DefByCaseBlockBase):
            _doc << "@u"
        # Pass data to DefByCase visitor
        _p_data["defbycase_"] = _doc
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, owner_property)

    def visit_ActivateWhenBlock(
        self,
        swan_obj: Swan.ActivateWhenBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateWhen Block visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateWhenBlock
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
        swan_obj: Swan.ActivateWhenBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        ActivateWhen Branch visitor

        Parameters
        ----------
        swan_obj : Swan.ActivateWhenBranch
            Visited Swan object, it's a ActivateWhenBranch instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"pattern": None, "data_def": None})
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        self._visit(swan_obj.data_def, swan_obj, "data_def")
        _doc = R.DBlock()
        _doc << "| "
        _doc << _p_data["pattern"]
        _doc << " :" << "@i" << "@n"
        _doc << _p_data["data_def"] << "@u"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_AnonymousOperatorWithDataDefinition(
        self,
        swan_obj: Swan.AnonymousOperatorWithDataDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Anonymous Operator With Data Definition visitor

        Parameters
        ----------
        swan_obj : Swan.AnonymousOperatorWithDataDefinition
            Visited Swan object, it's a AnonymousOperatorWithDataDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"inputs": None, "outputs": None, "data_def": None})
        _in = []
        _out = []
        # Visit properties
        _doc = R.DBlock()
        if swan_obj.is_node:
            _doc << "node"
        else:
            _doc << "function"

        for item in swan_obj.inputs:
            self._visit(item, swan_obj, "inputs")
            _in.append(_p_data["inputs"])
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
            _out.append(_p_data["outputs"])
        if isinstance(swan_obj.data_def, (Swan.Equation, Swan.Scope)):
            self._visit(swan_obj.data_def, swan_obj, "data_def")
        _doc << " (" << R.doc_list(*_in, sep="; ") << ")"
        _doc << " returns "
        _doc << "(" << R.doc_list(*_out, sep="; ") << ") "
        _doc << _p_data["data_def"]

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_AnonymousOperatorWithExpression(
        self,
        swan_obj: Swan.AnonymousOperatorWithExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Anonymous Operator With Expression visitor

        Parameters
        ----------
        swan_obj : Swan.AnonymousOperatorWithExpression
            Visited Swan object, it's a AnonymousOperatorWithExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"params": None, "sections": None, "expr": None})
        _pm = []
        _st = []
        # Visit properties
        _doc = R.DBlock()
        if swan_obj.is_node:
            _doc << "node"
        else:
            _doc << "function"
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")
            _pm.append(_p_data["params"])
        for item in swan_obj.sections:
            self._visit(item, swan_obj, "sections")
            _st.append(_p_data["sections"])
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc << " " << R.doc_list(*_pm, sep=", ")
        if _st:
            _doc << " " << R.doc_list(*_st, sep=" ")
        _doc << " => " << _p_data["expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ArrayConstructor(
        self,
        swan_obj: Swan.ArrayConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Constructor visitor

        Parameters
        ----------
        swan_obj : Swan.ArrayConstructor
            Visited Swan object, it's a ArrayConstructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"group": None})
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        _doc = R.DBlock()
        _doc << "["
        _doc << _p_data["group"]
        _doc << "]"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ArrayProjection(
        self,
        swan_obj: Swan.ArrayProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Projection visitor

        Parameters
        ----------
        swan_obj : Swan.ArrayProjection
            Visited Swan object, it's a ArrayProjection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "index": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.index, swan_obj, "index")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << _p_data["index"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ArrayRepetition(
        self,
        swan_obj: Swan.ArrayRepetition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Repetition visitor

        Parameters
        ----------
        swan_obj : Swan.ArrayRepetition
            Visited Swan object, it's a ArrayRepetition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "size": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.size, swan_obj, "size")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << "^"
        _doc << _p_data["size"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ArrayTypeExpression(
        self,
        swan_obj: Swan.ArrayTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array Type Expression visitor

        Parameters
        ----------
        swan_obj : Swan.ArrayTypeExpression
            Visited Swan object, it's a ArrayTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"type": None, "size": None})

        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        self._visit(swan_obj.size, swan_obj, "size")
        _doc = R.DBlock()
        _doc << _p_data["type"]
        _doc << "^"
        _doc << _p_data["size"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_AssertSection(
        self,
        swan_obj: Swan.AssertSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Assert Section visitor

        Parameters
        ----------
        swan_obj : Swan.AssertSection
            Visited Swan object, it's a AssertSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"assertions": None})
        _ast = []
        # Visit properties
        for item in swan_obj.assertions:
            self._visit(item, swan_obj, "assertions")
            _ast.append(_p_data["assertions"])
        self._pop_and_set_doc_data(owner_property, PPrinter._format_list("assert", _ast))

    def visit_AssumeSection(
        self,
        swan_obj: Swan.AssumeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Assume Section visitor

        Parameters
        ----------
        swan_obj : Swan.AssumeSection
            Visited Swan object, it's a AssumeSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"assertions": []})
        # Visit properties
        for item in swan_obj.assertions:
            self._visit(item, swan_obj, "assertions")

        self._pop_and_set_doc_data(
            owner_property,
            PPrinter._format_list("assume", cast(List[R.DElt], _p_data["assertions"])),
        )

    def visit_ByPos(
        self, swan_obj: Swan.ByPos, owner: Owner, owner_property: OwnerProperty
    ) -> None:
        """
        ByPos visitor

        Parameters
        ----------
        swan_obj : Swan.ByPos
            Visited Swan object, it's a ByPos instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _doc = R.DBlock()
        _doc << "group bypos"
        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = _doc
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_ByName(
        self, swan_obj: Swan.ByName, owner: Owner, owner_property: OwnerProperty
    ) -> None:
        """
        ByName visitor

        Parameters
        ----------
        swan_obj : Swan.ByName
            Visited Swan object, it's a ByName instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _doc = R.DBlock()
        _doc << "group byname"
        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = _doc
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_GroupNormalize(
        self, swan_obj: Swan.GroupNormalize, owner: Owner, owner_property: OwnerProperty
    ) -> None:
        """
        GroupNormalize visitor

        Parameters
        ----------
        swan_obj : Swan.GroupNormalize
            Visited Swan object, it's a GroupNormalize instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _doc = R.DBlock()
        _doc << "group ()"
        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = _doc
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_GroupBlock(
        self, swan_obj: Swan.GroupBlock, owner: Owner, owner_property: OwnerProperty
    ) -> None:
        """
        GroupBlock visitor

        Parameters
        ----------
        swan_obj : Swan.GroupBlock
            Visited Swan object, it's a GroupBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _doc = R.DBlock()
        _doc << "group"
        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = _doc
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_Bar(self, swan_obj: Swan.Bar, owner: Owner, owner_property: OwnerProperty) -> None:
        """
        Bar visitor

        Parameters
        ----------
        swan_obj : Swan.Bar
            Visited Swan object, it's a Bar instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        _doc = R.DBlock()
        _doc << "group"
        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = _doc
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_Concat(
        self, swan_obj: Swan.Concat, owner: Owner, owner_property: OwnerProperty
    ) -> None:
        """
        Concat visitor

        Parameters
        ----------
        swan_obj : Swan.Concat
            Visited Swan object, it's a Concat instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _doc = R.DBlock()
        _doc << "expr ("
        lunums = []
        for item in getattr(swan_obj.group, "items", []):
            expr = getattr(item, "expr", None)
            if isinstance(expr, Swan.PortExpr) and expr.lunum is not None:
                lunums.append(str(expr.lunum))
        _doc << ", ".join(lunums)
        _doc << ")"

        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = _doc
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_BinaryExpr(
        self,
        swan_obj: Swan.BinaryExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Binary Expression visitor

        Parameters
        ----------
        swan_obj : Swan.BinaryExpr
            Visited Swan object, it's a BinaryExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None, "left": None, "right": None})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.left, swan_obj, "left")
        self._visit(swan_obj.right, swan_obj, "right")
        _doc = R.DBlock()
        _doc << _p_data["left"]
        _doc << " "
        _doc << _p_data["operator"]
        _doc << " "
        _doc << _p_data["right"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_PreWithInitialValueExpr(
        self,
        swan_obj: Swan.PreWithInitialValueExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pre with initial value visitor

        Parameters
        ----------
        swan_obj : Swan.PreWithInitialExpr
            Visited Swan object, it's a PreWithInitialExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self.visit_BinaryExpr(swan_obj, owner, owner_property)

    def visit_InitialValueExpr(
        self,
        swan_obj: Swan.InitialValueExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Initial value expression visitor

        Parameters
        ----------
        swan_obj : Swan.InitialValueExpr
            Visited Swan object, it's a InitialValueExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self.visit_BinaryExpr(swan_obj, owner, owner_property)

    def visit_ArrayConcatExpr(
        self,
        swan_obj: Swan.ArrayConcatExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Array concatenation expression visitor

        Parameters
        ----------
        swan_obj : Swan.ArrayConcatExpr
            Visited Swan object, it's a InitialArrayConcatExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self.visit_BinaryExpr(swan_obj, owner, owner_property)

    def visit_BinaryOp(
        self,
        swan_obj: Swan.BinaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        Binary Operator visitor

        Parameters
        ----------
        swan_obj : Swan.BinaryOp
            Visited Swan object, it's a BinaryOp instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.text(Swan.BinaryOp.to_str(swan_obj)))

    def visit_Block(
        self,
        swan_obj: Swan.Block,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Block visitor

        Parameters
        ----------
        swan_obj : Swan.Block
            Visited Swan object, it's a Block instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"instance": None, "instance_luid": None})
        # Visit properties
        self._visit(swan_obj.instance, swan_obj, "instance")

        _doc = R.DBlock()
        _doc << "block "
        _doc << _p_data["instance"]
        _p_data["description"] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_BoolPattern(
        self,
        swan_obj: Swan.BoolPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Bool Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.BoolPattern
            Visited Swan object, it's a BoolPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.text(str(swan_obj)))

    def visit_BoolType(
        self,
        swan_obj: Swan.BoolType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Bool Type visitor

        Parameters
        ----------
        swan_obj : Swan.BoolType
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
        swan_obj: Swan.CaseBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Case Branch visitor

        Parameters
        ----------
        swan_obj : Swan.CaseBranch
            Visited Swan object, it's a CaseBranch instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"pattern": None, "expr": None})
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << " | "
        _doc << _p_data["pattern"]
        _doc << ": "
        _doc << _p_data["expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_CaseExpr(
        self,
        swan_obj: Swan.CaseExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Case Expression visitor

        Parameters
        ----------
        swan_obj : Swan.CaseExpr
            Visited Swan object, it's a CaseExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "branches": []})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")

        _doc = R.DBlock()
        _doc << "(case "
        _doc << _p_data["expr"]
        _doc << " of"
        _doc << R.doc_list(*(cast(List[R.DElt], _p_data["branches"])), sep="")
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_CharType(
        self,
        swan_obj: Swan.CharType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Char Type visitor

        Parameters
        ----------
        swan_obj : Swan.CharType
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
        swan_obj: Swan.CharPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Character Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.CharPattern
            Visited Swan object, it's a CharPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.text(str(swan_obj)))

    def visit_ClockExpr(
        self,
        swan_obj: Swan.ClockExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Clock Expression visitor

        Parameters
        ----------
        swan_obj : Swan.ClockExpr
            Visited Swan object, it's a ClockExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None, "is_not": None, "pattern": None})

        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        if swan_obj.pattern:
            self._visit(swan_obj.pattern, swan_obj, "pattern")
            _doc << "("
            _doc << _p_data["id"]
            _doc << " match "
            _doc << _p_data["pattern"]
            _doc << ")"
        elif swan_obj.is_not:
            self.visit_builtin(swan_obj.is_not, swan_obj, "is_not")
            _doc << "not "
            _doc << _p_data["id"]
        else:
            _doc << _p_data["id"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Connection(
        self,
        swan_obj: Swan.Connection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Connection visitor

        Parameters
        ----------
        swan_obj : Swan.Connection
            Visited Swan object, it's a Connection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        _p_data = self._push_and_get_doc_data({"port": None, "adaptation": None})
        # Visit properties
        if swan_obj.port:
            self._visit(swan_obj.port, swan_obj, "port")
        if swan_obj.adaptation:
            self._visit(swan_obj.adaptation, swan_obj, "adaptation")
        _doc = R.DBlock()
        if swan_obj.is_connected:
            _doc << _p_data["port"]
            if swan_obj.adaptation:
                _doc << " "
                _doc << _p_data["adaptation"]
        else:
            _doc << "()"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ConstDecl(
        self,
        swan_obj: Swan.ConstDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a constant declaration
        Syntax: const {{ const_decl ; }}
                const_decl ::= id : type_expr [[ = expr ]] | id = expr

        Parameters
        ----------
        swan_obj : Swan.ConstDecl
            Visited Swan object, it's a ConstantDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None, "type": None, "value": None})
        # Visit parent class
        super().visit_ConstDecl(swan_obj, owner, owner_property)
        # Visit properties
        _doc = R.DBlock()
        self._decl_pragmas(swan_obj, _doc)
        _doc << _p_data["id"]
        if _p_data["type"]:
            _doc << ": " << _p_data["type"]
        if _p_data["value"]:
            _doc << " = " << _p_data["value"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ConstDeclarations(
        self,
        swan_obj: Swan.ConstDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of constant declarations

        Parameters
        ----------
        swan_obj : Swan.ConstDeclarations
            Visited Swan object, it's a ConstDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"constants": []})
        # Visit parent class
        super().visit_ConstDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(_p_data, "constants", "const")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["constants"]))

    def visit_DefaultPattern(
        self,
        swan_obj: Swan.DefaultPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Default Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.DefaultPattern
            Visited Swan object, it's a DefaultPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.DText(str(swan_obj)))

    def visit_DefBlock(
        self,
        swan_obj: Swan.DefBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Def Block visitor

        Parameters
        ----------
        swan_obj : Swan.DefBlock
            Visited Swan object, it's a DefBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lhs": None})

        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        _doc = R.DBlock()
        _doc << "def "
        _doc << _p_data["lhs"]

        _p_data["description"] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_DefByCase(
        self,
        swan_obj: Swan.DefByCase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        DefByCase visitor

        Parameters
        ----------
        swan_obj : Swan.DefByCase
            Visited Swan object, it's a DefByCase instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Get data set by derived classes
        _p_data = self._get_current_doc_data()
        _p_data.update({"lhs": None, "name": None})
        _doc = R.DBlock()
        # Visit properties
        if swan_obj.lhs:
            self._visit(swan_obj.lhs, swan_obj, "lhs")
            _doc << _p_data["lhs"] << " : "
        _doc << _p_data["defbycase_"]
        if not isinstance(owner, Swan.DefByCaseBlockBase):
            _doc << ";"
        if isinstance(swan_obj, Swan.ActivateIf):
            _doc << "@u"
            if not isinstance(owner, Swan.DefByCaseBlockBase):
                # indentation from the beginning of the keyword
                _doc << "@u"

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_DefByCaseBlockBase(
        self,
        swan_obj: Swan.DefByCaseBlockBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        DefByCase Block Base visitor

        Parameters
        ----------
        swan_obj : Swan.DefByCaseBlockBase
            Visited Swan object, it's a DefByCaseBlockBase instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({})
        _p_data["description"] = None
        # Visit properties
        self._visit(swan_obj.def_by_case, swan_obj, "description")

        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_Diagram(
        self,
        swan_obj: Swan.Diagram,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Diagram visitor

        Parameters
        ----------
        swan_obj : Swan.Diagram
            Visited Swan object, it's a Diagram instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"objects": None, "luid": None})
        if swan_obj.luid is not None:
            self._visit(swan_obj.luid, swan_obj, "luid")
        _doc = R.DBlock() << "@i"
        _doc << "diagram"
        if _p_data["luid"] is not None:
            _doc << " " << _p_data["luid"]
        _objs = []
        iterator = iter(swan_obj.objects)
        wires_section = None
        while True:
            try:
                item = next(iterator)
                if wires_section is None:
                    # First item defines first section
                    wires_section = isinstance(item, Swan.Wire)
                elif wires_section != isinstance(item, Swan.Wire):
                    # Entering or leaving wires section: must add line break
                    wires_section = not wires_section
                    _doc << "@n"
                    _doc << R.doc_list(*_objs, sep="@n") << "@n"
                    _objs.clear()
                self._visit(item, swan_obj, "objects")
                _objs.append(_p_data["objects"])
            except StopIteration:
                _doc << "@n"
                _doc << R.doc_list(*_objs, sep="@n")
                _doc << "@u"
                break

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_DiagramObject(
        self,
        swan_obj: Swan.DiagramObject,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Diagram Object visitor

        Parameters
        ----------
        swan_obj : Swan.DiagramObject
            Visited Swan object, it's a DiagramObject instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # visit_DiagramObject is called by its derived classes, so we need to retrieve its doc data
        _p_data = self._get_current_doc_data()
        # Init data buffer
        _p_data.update({"lunum": None, "luid": None, "locals": None})
        _doc = R.DBlock()
        _doc << "("
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << _p_data["lunum"]
            _doc << " "
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << _p_data["luid"]
            _doc << " "
        _doc << _p_data["description"]
        if swan_obj.locals:
            _lc = []
            for item in swan_obj.locals:
                _p_data["locals"] = None
                self._visit(item, swan_obj, "locals")
                _lc.append(_p_data["locals"])
            if _lc:
                _doc << "@i" << "@n" << "where" << "@i" << "@n"
                _doc << R.doc_list(*_lc, sep="@n") << "@u" << "@u"
        self.visit_HasPragma(swan_obj, owner, owner_property)
        if _p_data["pragmas"]:
            _doc << "@n"
            _doc << _p_data["pragmas"]
        _doc << ")"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_EmitSection(
        self,
        swan_obj: Swan.EmitSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Emit Section visitor

        Parameters
        ----------
        swan_obj : Swan.EmitSection
            Visited Swan object, it's a EmitSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"emissions": []})
        # Visit properties
        for item in swan_obj.emissions:
            self._visit(item, swan_obj, "emissions")

        self._pop_and_set_doc_data(
            owner_property, PPrinter._format_list("emit", cast(List[R.DElt], _p_data["emissions"]))
        )

    def visit_EmissionBody(
        self,
        swan_obj: Swan.EmissionBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Emission Body visitor

        Parameters
        ----------
        swan_obj : Swan.EmissionBody
            Visited Swan object, it's a EmissionBody instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"flows": None, "condition": None, "luid": None})
        _fls = []
        # Visit properties
        _doc = R.DBlock()
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << _p_data["luid"]
            _doc << " "
        for item in swan_obj.flows:
            self._visit(item, swan_obj, "flows")
            _fls.append(_p_data["flows"])
        _doc << R.doc_list(*_fls, sep=", ")
        if swan_obj.condition:
            self._visit(swan_obj.condition, swan_obj, "condition")
            _doc << " if "
            _doc << _p_data["condition"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_EnumTag(
        self,
        swan_obj: Swan.EnumTag,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """Default EnumTag visitor method."""
        _p_data = self._push_and_get_doc_data({"id": None})
        # Visit base class(es)
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        # Visit properties
        self._visit(
            swan_obj.id,
            swan_obj,
            "id",
        )
        if swan_obj.pragmas:
            _doc = R.DBlock()
            _doc << _p_data["pragmas"] << " " << _p_data["id"]
        else:
            _doc = _p_data["id"]
        # Update property
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _doc))

    def visit_EnumTypeDefinition(
        self,
        swan_obj: Swan.EnumTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Enumeration Type Definition visitor

        Parameters
        ----------
        swan_obj : Swan.EnumTypeDefinition
            Visited Swan object, it's a EnumTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"tags": []})
        # Visit properties
        for itm in swan_obj.tags:
            self._visit(itm, swan_obj, "tags")
        _doc = R.DBlock()
        _doc << "enum "
        _doc << R.doc_list(*(cast(List[R.DElt], _p_data["tags"])), sep=", ", start="{", last="}")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_EquationLHS(
        self,
        swan_obj: Swan.EquationLHS,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Equation LHS visitor

        Parameters
        ----------
        swan_obj : Swan.EquationLHS
            Visited Swan object, it's a EquationLHS instance
        owner : Owner
            Owner of the property, 'None' for the root visited object
        property : Union[str, None]
            Property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lhs_items": None})
        _lms = []
        # Visit properties
        for item in swan_obj.lhs_items:
            self._visit(item, swan_obj, "lhs_items")
            _lms.append(_p_data["lhs_items"])
        _doc = R.DBlock()
        if _lms:
            _doc << R.doc_list(*_lms, sep=", ")
            if swan_obj.is_partial_lhs:
                _doc << ", .."
        else:
            _doc << "()"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ExprBlock(
        self,
        swan_obj: Swan.ExprBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Expression Block visitor

        Parameters
        ----------
        swan_obj : Swan.ExprBlock
            Visited Swan object, it's a ExprBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << "expr "
        _doc << _p_data["expr"]

        _p_data["description"] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_ExprEquation(
        self,
        swan_obj: Swan.ExprEquation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Expression Equation visitor

        Parameters
        ----------
        swan_obj : Swan.ExprEquation
            Visited Swan object, it's a ExprEquation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lhs": None, "expr": None, "luid": None})
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << _p_data["lhs"]
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << " " << _p_data["luid"]
        _doc << " = " << _p_data["expr"] << ";"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ExprTypeDefinition(
        self,
        swan_obj: Swan.ExprTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Expression Type Definition visitor

        Parameters
        ----------
        swan_obj : Swan.ExprTypeDefinition
            Visited Swan object, it's a ExprTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"type": None})
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["type"]))

    def visit_Float32Type(
        self,
        swan_obj: Swan.Float32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Float32 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Float32Type
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
        swan_obj: Swan.Float64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Float64 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Float64Type
            Visited Swan object, it's a Float64Type instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, owner_property)

    def visit_Fork(
        self,
        swan_obj: Swan.Fork,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Fork visitor

        Parameters
        ----------
        swan_obj : Swan.Fork
            Visited Swan object, it's a Fork instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _p_data = self._push_and_get_doc_data(
            {
                "transitions": [],
                "context": PPrinter.__StateTransitionContext.FROM_FORK,
            },
        )

        _doc = R.DBlock()
        _owner_p_data = self._get_owner_doc_data()
        if "context" not in _owner_p_data.keys():
            # case where one wants to call swan_to_str(fork_instance): force the context to be from a state
            _owner_p_data["context"] = PPrinter.__StateTransitionContext.IN_STATE

        if cast(Flag, _owner_p_data["context"]) & PPrinter.__StateTransitionContext.IN_DECL:
            # declaration case, transitions use priority information
            _p_data["context"] = (
                cast(Flag, _p_data["context"]) | PPrinter.__StateTransitionContext.IN_DECL
            )
            _transitions = swan_obj._transitions
        else:
            # state case, transition must be sorted by priority, and "if-elsif-else" style applies
            _p_data["context"] = (
                cast(Flag, _p_data["context"]) | PPrinter.__StateTransitionContext.IN_STATE
            )
            _transitions = swan_obj.transitions  # these are sorted by priority
        if not _transitions:
            raise Swan.ScadeOneException("Fork must have at least one transition")
        self._visit(_transitions[0], swan_obj, "transitions")
        _p_data["context"] |= PPrinter.__StateTransitionContext.ELSIF
        if len(_transitions) > 1:
            for item in _transitions[1:]:
                self._visit(item, swan_obj, "transitions")
        _doc << R.doc_list(*(cast(List[R.DElt], _p_data["transitions"])), sep="@n")
        # Unindent and close fork
        _doc << " end"
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Forward(
        self,
        swan_obj: Swan.Forward,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward visitor

        Parameters
        ----------
        swan_obj : Swan.Forward
            Visited Swan object, it's a Forward instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "dimensions": [],
                "body": None,
                "returns": [],
                "luid": None,
            },
        )
        # Visit properties
        for item in swan_obj.dimensions:
            self._visit(item, swan_obj, "dimensions")
        self._visit(swan_obj.body, swan_obj, "body")
        for item in swan_obj.returns:
            self._visit(item, swan_obj, "returns")
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
        _doc = R.DBlock()
        _doc << "forward"
        if swan_obj.luid:
            _doc << " "
            _doc << _p_data["luid"]
        if swan_obj.restart is True:
            _doc << " restart"
        elif swan_obj.restart is False:
            _doc << " resume"
        _doc << "@i"
        if _p_data["dimensions"]:
            _doc << "@n"
            _doc << R.doc_list(*cast(List[R.DElt], _p_data["dimensions"]), sep="@n")
        _doc << _p_data["body"] << "@n" << "returns ("
        if _p_data["returns"]:
            _doc << R.doc_list(*cast(List[R.DElt], _p_data["returns"]), sep=", ")
        _doc << ")" << "@u"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Assertion(
        self,
        swan_obj: Swan.Assertion,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Property visitor

        Parameters
        ----------
        swan_obj : Swan.Assertion
            Visited Swan object, it's a Assertion instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"luid": None, "expr": None})
        # Visit properties
        self._visit(swan_obj.luid, swan_obj, "luid")
        self._visit(swan_obj.expr, swan_obj, "expr")
        self.visit_HasPragma(swan_obj, owner, owner_property)
        _doc = R.DBlock()
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        _doc << _p_data["luid"]
        _doc << ": "
        _doc << _p_data["expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardArrayClause(
        self,
        swan_obj: Swan.ForwardArrayClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Array Clause visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardArrayClause
            Visited Swan object, it's a ForwardArrayClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"return_clause": None})
        # Visit properties
        _doc = R.DBlock()
        _doc << "["
        if isinstance(swan_obj.return_clause, (Swan.ForwardItemClause, Swan.ForwardArrayClause)):
            self._visit(swan_obj.return_clause, swan_obj, "return_clause")
            _doc << _p_data["return_clause"]
        _doc << "]"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardBody(
        self,
        swan_obj: Swan.ForwardBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Body visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardBody
            Visited Swan object, it's a ForwardBody instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {"body": None, "unless_expr": None, "until_expr": None}
        )
        _bdy = []
        # Visit properties
        for item in swan_obj.body:
            self._visit(item, swan_obj, "body")
            _bdy.append(_p_data["body"])
        _doc = R.DBlock()
        if swan_obj.unless_expr:
            self._visit(swan_obj.unless_expr, swan_obj, "unless_expr")
            _doc << "@n" << "unless "
            _doc << _p_data["unless_expr"]
        if _bdy:
            _doc << "@n" << R.doc_list(*_bdy, sep=R.DLineBreak(True))
        if swan_obj.until_expr:
            self._visit(swan_obj.until_expr, swan_obj, "until_expr")
            _doc << "@n" << "until "
            _doc << _p_data["until_expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardDim(
        self,
        swan_obj: Swan.ForwardDim,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Dimension visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardDim
            Visited Swan object, it's a ForwardDim instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "expr": None,
                "dim_id": None,
                "elems": [],
                "protected": None,
            },
        )
        # Visit properties
        if swan_obj.expr:
            self._visit(swan_obj.expr, swan_obj, "expr")

        if swan_obj.is_protected and swan_obj.protected:
            _doc = R.DText(Swan.Markup.to_str(swan_obj.protected, markup=Swan.Markup.Dim))
        else:
            _doc = R.DBlock()
            _doc << "<<"
            _doc << _p_data["expr"]
            _doc << ">>"
            if swan_obj.dim_id or swan_obj.elems:
                _doc << " with "
            if swan_obj.dim_id:
                self._visit(swan_obj.dim_id, swan_obj, "dim_id")
                _doc << "<<"
                _doc << _p_data["dim_id"]
                _doc << ">> "
            if swan_obj.elems:
                for item in swan_obj.elems:
                    self._visit(item, swan_obj, "elems")
                _doc << R.doc_list(*cast(List[R.DElt], _p_data["elems"]), sep=" ")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardElement(
        self,
        swan_obj: Swan.ForwardElement,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Element visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardElement
            Visited Swan object, it's a ForwardElement instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lhs": None, "expr": None})
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << _p_data["lhs"]
        _doc << " = "
        _doc << _p_data["expr"]
        _doc << ";"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardItemClause(
        self,
        swan_obj: Swan.ForwardItemClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Item Clause visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardItemClause
            Visited Swan object, it's a ForwardItemClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None, "last_default": None})
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        _doc << _p_data["id"]
        if swan_obj.last_default:
            self._visit(swan_obj.last_default, swan_obj, "last_default")
            _doc << ": "
            _doc << _p_data["last_default"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardLastDefault(
        self,
        swan_obj: Swan.ForwardLastDefault,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Last Default visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardLastDefault
            Visited Swan object, it's a ForwardLastDefault instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"last": None, "default": None, "shared": None})
        # Visit properties
        _doc = R.DBlock()
        if swan_obj.shared:
            self._visit(swan_obj.shared, swan_obj, "shared")
            _doc << "last = default = "
            _doc << _p_data["shared"]
        else:
            if swan_obj.last:
                self._visit(swan_obj.last, swan_obj, "last")
                _doc << "last = "
                _doc << _p_data["last"]
            if swan_obj.last and swan_obj.default:
                _doc << " "
            if swan_obj.default:
                self._visit(swan_obj.default, swan_obj, "default")
                _doc << "default = "
                _doc << _p_data["default"]

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardLHS(
        self,
        swan_obj: Swan.ForwardLHS,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward LHS visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardLHS
            Visited Swan object, it's a ForwardLHS instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lhs": None})
        # Visit properties
        if isinstance(swan_obj.lhs, (Swan.Identifier, Swan.ForwardLHS)):
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        _doc = R.DBlock()
        if swan_obj.is_id:
            _doc << _p_data["lhs"]
        else:
            _doc << "["
            _doc << _p_data["lhs"]
            _doc << "]"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardReturnArrayClause(
        self,
        swan_obj: Swan.ForwardReturnArrayClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Return Array Clause visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardReturnArrayClause
            Visited Swan object, it's a ForwardReturnArrayClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"array_clause": None, "return_id": None})
        # Visit properties
        self._visit(swan_obj.array_clause, swan_obj, "array_clause")
        _doc = R.DBlock()
        if swan_obj.return_id:
            self._visit(swan_obj.return_id, swan_obj, "return_id")
            _doc << _p_data["return_id"]
            _doc << " = "
        _doc << _p_data["array_clause"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ForwardReturnItemClause(
        self,
        swan_obj: Swan.ForwardReturnItemClause,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Forward Return Item Clause visitor

        Parameters
        ----------
        swan_obj : Swan.ForwardReturnItemClause
            Visited Swan object, it's a ForwardReturnItemClause instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"item_clause": None})
        # Visit properties
        self._visit(swan_obj.item_clause, swan_obj, "item_clause")
        _doc = R.DBlock()
        _doc << _p_data["item_clause"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_FunctionalUpdate(
        self,
        swan_obj: Swan.FunctionalUpdate,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Functional Update visitor

        Parameters
        ----------
        swan_obj : Swan.FunctionalUpdate
            Visited Swan object, it's a FunctionalUpdate instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "modifiers": []})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.modifiers:
            self._visit(item, swan_obj, "modifiers")

        _doc = R.DBlock()
        _doc << "("
        _doc << _p_data["expr"]
        _doc << (" with * " if swan_obj.is_starred else " with ")
        _doc << R.doc_list(*cast(List[R.DElt], _p_data["modifiers"]), sep="; ")
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Group(
        self,
        swan_obj: Swan.Group,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group visitor

        Parameters
        ----------
        swan_obj : Swan.Group
            Visited Swan object, it's a Group instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"items": None})
        _itm = []
        # Visit properties
        for item in swan_obj.items:
            self._visit(item, swan_obj, "items")
            _itm.append(_p_data["items"])
        _doc = R.DBlock()
        _doc << R.doc_list(*_itm, sep=", ")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupAdaptation(
        self,
        swan_obj: Swan.GroupAdaptation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Adaption visitor

        Parameters
        ----------
        swan_obj : Swan.GroupAdaptation
            Visited Swan object, it's a GroupAdaptation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"renamings": None})
        _rnm = []
        # Visit properties
        for item in swan_obj.renamings:
            self._visit(item, swan_obj, "renamings")
            _rnm.append(_p_data["renamings"])
        _doc = R.DBlock()
        _doc << ".("
        if _rnm:
            _doc << R.doc_list(*_rnm, sep=", ")
        _doc << ")"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupConstructor(
        self,
        swan_obj: Swan.GroupConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Constructor visitor

        Parameters
        ----------
        swan_obj : Swan.GroupConstructor
            Visited Swan object, it's a GroupConstructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"group": None})
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        _doc = R.DBlock()
        _doc << "("
        _doc << _p_data["group"]
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupDecl(
        self,
        swan_obj: Swan.GroupDecl,
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
        swan_obj : Swan.GroupDecl
            Visited Swan object, it's a GroupDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None, "type": None})
        # Visit parent class
        super().visit_GroupDecl(swan_obj, owner, owner_property)
        # Visit properties
        _doc = R.DBlock()
        self._decl_pragmas(swan_obj, _doc)
        _doc << _p_data["id"]
        _type = PPrinter._doc_or_list(cast(R.DElt, _p_data["type"]))
        _doc << " = " << _type

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupDeclarations(
        self,
        swan_obj: Swan.GroupDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of group declarations

        Parameters
        ----------
        swan_obj : Swan.GroupDeclarations
            Visited Swan object, it's a GroupDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"groups": []})
        # Visit parent class
        super().visit_GroupDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(_p_data, "groups", "group")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["groups"]))

    def visit_GroupItem(
        self,
        swan_obj: Swan.GroupItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Item visitor

        Parameters
        ----------
        swan_obj : Swan.GroupItem
            Visited Swan object, it's a GroupItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "label": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        if swan_obj.label:
            self._visit(swan_obj.label, swan_obj, "label")
            _doc << _p_data["label"]
            _doc << ": "
        _doc << _p_data["expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupOperation(
        self,
        swan_obj: Swan.GroupOperation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Operation visitor

        Parameters
        ----------
        swan_obj : Swan.GroupOperation
            Visited Swan object, it's a GroupOperation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._push_and_get_doc_data({})
        if swan_obj == Swan.GroupOperation.Normalize:
            _doc = R.text("()")
        elif swan_obj == Swan.GroupOperation.NoOp:
            _doc = R.text("")
        else:
            _doc = R.text(Swan.GroupOperation.to_str(swan_obj))
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupRenaming(
        self,
        swan_obj: Swan.GroupRenaming,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Renaming visitor

        Parameters
        ----------
        swan_obj : Swan.GroupRenaming
            Visited Swan object, it's a GroupRenaming instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"source": None, "renaming": None})
        # Visit properties
        _doc = R.DBlock()
        self._visit(swan_obj.source, swan_obj, "source")
        _doc << _p_data["source"]
        if swan_obj.renaming:
            self._visit(swan_obj.renaming, swan_obj, "renaming")
            _doc << ": "
            _doc << _p_data["renaming"]
        elif swan_obj.is_shortcut:
            _doc << ":"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupProjection(
        self,
        swan_obj: Swan.GroupProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Projection visitor

        Parameters
        ----------
        swan_obj : Swan.GroupProjection
            Visited Swan object, it's a GroupProjection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "adaptation": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.adaptation, swan_obj, "adaptation")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << " "
        _doc << _p_data["adaptation"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GroupTypeExpressionList(
        self,
        swan_obj: Swan.GroupTypeExpressionList,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group type expression list visitor

        Parameters
        ----------
        swan_obj : Swan.GroupTypeExpressionList
            Visited Swan object, it's a GroupTypeExpressionList instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"positional": None, "named": None})
        _lst_items = []
        # Visit properties
        for item in swan_obj.positional:
            self._visit(item, swan_obj, "positional")
            _lst_items.append(_p_data["positional"])
        for item in swan_obj.named:
            self._visit(item, swan_obj, "named")
            _lst_items.append(_p_data["named"])
        _doc = R.DBlock()
        _doc << "("
        _doc << R.doc_list(*_lst_items, sep=", ")
        _doc << ")"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_GuaranteeSection(
        self,
        swan_obj: Swan.GuaranteeSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Guarantee Section visitor

        Parameters
        ----------
        swan_obj : Swan.GuaranteeSection
            Visited Swan object, it's a GuaranteeSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"assertions": None})
        _grt = []
        # Visit properties
        for item in swan_obj.assertions:
            self._visit(item, swan_obj, "assertions")
            _grt.append(_p_data["assertions"])
        self._pop_and_set_doc_data(owner_property, PPrinter._format_list("guarantee", _grt))

    def visit_Identifier(
        self,
        swan_obj: Swan.Identifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Identifier visitor

        Parameters
        ----------
        swan_obj : Swan.Identifier
            Visited Swan object, it's a Identifier instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _doc = R.DBlock()
        if not swan_obj.is_valid:
            _doc << R.DText(Swan.Markup.to_str(swan_obj.value))
        else:
            _doc << R.DText(swan_obj.value)
        # Update property
        self._set_doc_data(owner_property, _doc)

    def visit_IfActivation(
        self,
        swan_obj: Swan.IfActivation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        IfActivation visitor

        Parameters
        ----------
        swan_obj : Swan.IfActivation
            Visited Swan object, it's a IfActivation instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"branches": None})
        _brc = []
        # Visit properties
        for idx, item in enumerate(swan_obj.branches):
            self._visit(item, swan_obj, "branches")
            if idx == 0:
                _brc.append(R.DBlock() << "if " << _p_data["branches"])
            else:
                if item.condition:
                    _brc.append(R.DBlock() << "elsif " << _p_data["branches"])
                else:
                    _brc.append(_p_data["branches"])
        _doc = R.DBlock()
        if _brc:
            _doc << R.doc_list(*_brc, sep="@n")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_IfActivationBranch(
        self,
        swan_obj: Swan.IfActivationBranch,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        IfActivation Branch visitor

        Parameters
        ----------
        swan_obj : Swan.IfActivationBranch
            Visited Swan object, it's a IfActivationBranch instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"condition": None, "branch": None})
        # Visit properties
        self._visit(swan_obj.branch, swan_obj, "branch")
        _doc = R.DBlock()
        if swan_obj.condition:
            self._visit(swan_obj.condition, swan_obj, "condition")
            _doc << _p_data["condition"] << "@n"
            _doc << "then" << "@i" << "@n"
            _doc << _p_data["branch"] << "@u"
        else:
            _doc << "else" << "@i" << "@n" << _p_data["branch"] << "@u"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_IfteDataDef(
        self,
        swan_obj: Swan.IfteDataDef,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        IfteDataDef visitor

        Parameters
        ----------
        swan_obj : Swan.IfteDataDef
            Visited Swan object, it's a IfteDataDef instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"data_def": None})
        # Visit properties
        self._visit(swan_obj.data_def, swan_obj, "data_def")
        _doc = R.DBlock()
        _doc << _p_data["data_def"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_IfteExpr(
        self,
        swan_obj: Swan.IfteExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        If Then Else Expression visitor

        Parameters
        ----------
        swan_obj : Swan.IfteExpr
            Visited Swan object, it's a IfteExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "cond_expr": None,
                "then_expr": None,
                "else_expr": None,
            },
        )
        # Visit properties
        self._visit(swan_obj.cond_expr, swan_obj, "cond_expr")
        self._visit(swan_obj.then_expr, swan_obj, "then_expr")
        self._visit(swan_obj.else_expr, swan_obj, "else_expr")
        _doc = R.DBlock()
        _doc << "if "
        _doc << _p_data["cond_expr"]
        _doc << " then "
        _doc << _p_data["then_expr"]
        _doc << " else "
        _doc << _p_data["else_expr"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_IfteIfActivation(
        self,
        swan_obj: Swan.IfteIfActivation,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """IfteIfActivation visitor function. Should be overridden."""
        # Visit properties
        _p_data = self._push_and_get_doc_data({"if_activation": None})
        self._visit(swan_obj.if_activation, swan_obj, "if_activation")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["if_activation"]))

    def visit_Int8Type(
        self,
        swan_obj: Swan.Int8Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int8 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Int8Type
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
        swan_obj: Swan.Int16Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int16 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Int16Type
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
        swan_obj: Swan.Int32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int32 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Int32Type
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
        swan_obj: Swan.Int64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Int64 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Int64Type
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
        swan_obj: Swan.IntPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Integer Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.IntPattern
            Visited Swan object, it's a IntPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.text(str(swan_obj)))

    def visit_Iterator(
        self,
        swan_obj: Swan.Iterator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Iterator visitor

        Parameters
        ----------
        swan_obj : Swan.Iterator
            Visited Swan object, it's a Iterator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"kind": None, "operator": None})
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")
        self._visit(swan_obj.operator, swan_obj, "operator")
        _doc = R.DBlock()
        _doc << _p_data["kind"]
        _doc << " "
        _doc << _p_data["operator"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_IteratorKind(
        self,
        swan_obj: Swan.IteratorKind,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        Iterator Kind visitor

        Parameters
        ----------
        swan_obj : Swan.IteratorKind
            Visited Swan object, it's a IteratorKind instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _p_data = self._push_and_get_doc_data({})
        self._pop_and_set_doc_data(owner_property, R.text(Swan.IteratorKind.to_str(swan_obj)))

    def visit_LabelOrIndex(
        self,
        swan_obj: Swan.LabelOrIndex,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Label Or Index visitor

        Parameters
        ----------
        swan_obj : Swan.LabelOrIndex
            Visited Swan object, it's a LabelOrIndex instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"value": None})
        # Visit properties
        if isinstance(swan_obj.value, (Swan.Identifier, Swan.Expression)):
            self._visit(swan_obj.value, swan_obj, "value")
        _doc = R.DBlock()
        if swan_obj.is_label:
            _doc << "."
            _doc << _p_data["value"]
        else:
            _doc << "["
            _doc << _p_data["value"]
            _doc << "]"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_LastExpr(
        self,
        swan_obj: Swan.LastExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Last Expression visitor

        Parameters
        ----------
        swan_obj : Swan.LastExpr
            Visited Swan object, it's a LastExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None})
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        _doc << "last "
        _doc << _p_data["id"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_LetSection(
        self,
        swan_obj: Swan.LetSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Let Section visitor

        Parameters
        ----------
        swan_obj : Swan.LetSection
            Visited Swan object, it's a LetSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"equations": None})
        _eqt = []
        # Visit properties
        for item in swan_obj.equations:
            self._visit(item, swan_obj, "equations")
            _eqt.append(_p_data["equations"])
        _let = PPrinter._format_list("let", _eqt, "", len(_eqt) == 1)
        self._pop_and_set_doc_data(owner_property, _let)

    def visit_LHSItem(
        self,
        swan_obj: Swan.LHSItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        LHS Item visitor

        Parameters
        ----------
        swan_obj : Swan.LHSItem
            Visited Swan object, it's a LHSItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None})
        # Visit properties
        if isinstance(swan_obj.id, Swan.Identifier):
            self._visit(swan_obj.id, swan_obj, "id")
            self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["id"]))
        else:
            self._pop_and_set_doc_data(owner_property, R.text("_"))

    def visit_Literal(
        self,
        swan_obj: Swan.Literal,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Literal visitor

        Parameters
        ----------
        swan_obj : Swan.Literal
            Visited Swan object, it's a literal instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _doc = R.text(swan_obj.value)
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        self._set_doc_data(owner_property, _doc)

    def visit_Luid(self, swan_obj: Swan.Luid, owner: Owner, owner_property: OwnerProperty) -> None:
        """
        Luid visitor

        Parameters
        ----------
        swan_obj : Swan.Luid
            Visited Swan object, it's a Luid instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        luid_str = str(swan_obj)
        text = R.text(
            Swan.Markup.to_str(luid_str, Swan.Luid.is_valid(luid_str) is False, Swan.Markup.Luid)
        )
        self._set_doc_data(owner_property, text)

    def visit_Lunum(
        self,
        swan_obj: Swan.Lunum,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Lunum visitor

        Parameters
        ----------
        swan_obj : Swan.Lunum
            Visited Swan object, it's a Lunum instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.text(str(swan_obj)))

    def visit_Merge(
        self,
        swan_obj: Swan.Merge,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Merge visitor

        Parameters
        ----------
        swan_obj : Swan.Merge
            Visited Swan object, it's a Merge instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"params": None})
        _prm = []
        if not swan_obj.params:
            raise Swan.ScadeOneException("Merge must have at least one parameter")

        _doc = R.DBlock()
        # Visit properties
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")
            _prm.append(_p_data["params"])
        if _prm:
            _doc = R.DBlock()
            _doc << "merge "
            _doc << R.doc_list(*[R.DBlock() << "(" << itm << ")" for itm in _prm], sep=" ")
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Modifier(
        self,
        swan_obj: Swan.Modifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Modifier visitor

        Parameters
        ----------
        swan_obj : Swan.Modifier
            Visited Swan object, it's a Modifier instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"modifier": None, "expr": None})
        _doc = R.DBlock()
        # Visit properties
        if isinstance(swan_obj.modifier, list):
            _mdp = []
            for item in swan_obj.modifier:
                self._visit(item, swan_obj, "modifier")
                _mdp.append(_p_data["modifier"])
            _doc << R.doc_list(*_mdp, sep="")
        else:
            _doc << R.DText(Swan.Markup.to_str(swan_obj.modifier))

        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc << " = " << _p_data["expr"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Module(
        self,
        swan_obj: Swan.Module,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Module visitor

        Parameters
        ----------
        swan_obj : Swan.Module
            Visited Swan object, it's a Module instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _p_data = self._push_and_get_doc_data({"use_directives": [], "declarations": None})

        # Visit properties
        _doc = R.DBlock()
        _doc << R.DText(gen_swan_version(isinstance(swan_obj, Swan.TestModule))) << "@n"
        if swan_obj.use_directives:
            for item in swan_obj.use_directives:
                self._visit(item, swan_obj, "use_directives")

            if _p_data["use_directives"]:
                _doc << R.doc_list(
                    *cast(List[R.DElt], _p_data["use_directives"]), sep=R.DLineBreak(False)
                )
                _doc << R.DLineBreak(False)
        if swan_obj.declarations:
            _dcl = []
            for item in swan_obj.declarations:
                self._visit(item, swan_obj, "declarations")
                _dcl.append(_p_data["declarations"])
            if _dcl:
                _doc << R.doc_list(*_dcl, sep=R.DLineBreak(False))
        self.visit_HasPragma(swan_obj, owner, owner_property)
        if _p_data["pragmas"]:
            _doc << "@n" << _p_data["pragmas"] << "@n"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ModuleBody(
        self,
        swan_obj: Swan.ModuleBody,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Module Body visitor

        Parameters
        ----------
        swan_obj : Swan.ModuleBody
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
        swan_obj: Swan.ModuleInterface,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Module Interface visitor

        Parameters
        ----------
        swan_obj : Swan.ModuleInterface
            Visited Swan object, it's a ModuleInterface instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_Module(swan_obj, owner, owner_property)

    def visit_TestHarness(
        self,
        swan_obj: Swan.TestHarness,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Test Harness visitor

        Parameters
        ----------
        swan_obj : Swan.TestHarness
            Visited Swan object, it's a TestHarness instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "id": None,
                "body": None,
            },
        )
        # Visit parent class
        super().visit_TestHarness(swan_obj, owner, owner_property)
        _doc = R.DBlock()
        _doc << "_harness "
        self._decl_pragmas(swan_obj, _doc)
        _doc << _p_data["id"]
        _doc << "@n"
        if _p_data["body"]:
            _doc << _p_data["body"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_TestModule(
        self,
        swan_obj: Swan.TestModule,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Test Module visitor

        Parameters
        ----------
        swan_obj : Swan.TestModule
            Visited Swan object, it's a TestModule instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_Module(swan_obj, owner, owner_property)

    def visit_NamedGroupTypeExpression(
        self,
        swan_obj: Swan.NamedGroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Named Group Type Expression visitor

        Parameters
        ----------
        swan_obj : Swan.NamedGroupTypeExpression
            Visited Swan object, it's a NamedGroupTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"label": None, "type": None})
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, owner_property)
        # Visit properties
        self._visit(swan_obj.label, swan_obj, "label")
        self._visit(swan_obj.type, swan_obj, "type")
        _doc = R.DBlock()
        _doc << _p_data["label"]
        _doc << ": "
        _doc << PPrinter._doc_or_list(cast(R.DElt, _p_data["type"]))
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_NaryOp(
        self,
        swan_obj: Swan.NaryOp,
        owner: Owner,
        owner_property: OwnerProperty,
    ):
        """
        NaryOp visitor

        Parameters
        ----------
        swan_obj : Swan.NaryOp
            Visited Swan object, it's a NaryOp instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self._set_doc_data(owner_property, R.text(Swan.NaryOp.to_str(swan_obj)))

    def visit_NAryOperator(
        self,
        swan_obj: Swan.NAryOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        N-Ary Operator visitor

        Parameters
        ----------
        swan_obj : Swan.NAryOperator
            Visited Swan object, it's a NAryOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["operator"]))

    def visit_NumericCast(
        self,
        swan_obj: Swan.NumericCast,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Numeric Casting visitor

        Parameters
        ----------
        swan_obj : Swan.NumericCast
            Visited Swan object, it's a NumericCast instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "type": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.type, swan_obj, "type")
        _doc = R.DBlock()
        _doc << "("
        _doc << _p_data["expr"]
        _doc << " :> "
        _doc << _p_data["type"]
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_OperatorDefinition(
        self,
        swan_obj: Swan.OperatorDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        OperatorDefinition visitor

        Parameters
        ----------
        swan_obj : Swan.OperatorDefinition
            Visited Swan object, it's a OperatorDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _p_data = self._push_and_get_doc_data({"interface_": None, "body": None})
        # Visit base class(es)
        self.visit_OperatorDeclarationDefinitionBase(swan_obj, owner, "interface_")
        _doc = R.DBlock()

        if swan_obj.is_text:
            _doc << "{text%"
        _doc << _p_data["interface_"]

        # Visit properties
        if swan_obj.body:
            self._visit(swan_obj.body, swan_obj, "body")
        if isinstance(swan_obj.body, Swan.Equation):
            _doc << " "
        else:
            _doc << "@n"
        _doc << _p_data["body"]
        if swan_obj.is_text:
            _doc << "%text}"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_OperatorInstance(
        self,
        swan_obj: Swan.OperatorInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Operator Base visitor

        Parameters
        ----------
        swan_obj : Swan.OperatorInstance
            Visited Swan object, it's a OperatorInstance instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Get current information set by derived classes
        _p_data = self._get_current_doc_data()
        _p_data.update({"sizes": []})

        # Visit properties
        for item in swan_obj.sizes:
            self._visit(item, swan_obj, "sizes")
        _doc = R.DBlock()
        if swan_obj.is_text:
            _doc << "{text%"
        _doc << _p_data["instance_"]
        _sizes = cast(List[R.DElt], _p_data["sizes"])
        if _sizes:
            _doc << " <<"
            _doc << R.doc_list(*_sizes, sep=", ")
            _doc << ">>"
        if swan_obj.is_text:
            _doc << "%text}"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_OperatorInstanceApplication(
        self,
        swan_obj: Swan.OperatorInstanceApplication,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Operator Instance visitor

        Parameters
        ----------
        swan_obj : Swan.OperatorInstanceApplication
            Visited Swan object, it's a OperatorInstanceApplication instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None, "params": None, "luid": None})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.params, swan_obj, "params")
        _doc = R.DBlock()
        _doc << _p_data["operator"]
        _doc << " "
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << _p_data["luid"]
            _doc << " "
        _doc << "("
        _doc << _p_data["params"]
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_OperatorDeclarationDefinitionBase(
        self,
        swan_obj: Swan.OperatorDeclarationDefinitionBase,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        OperatorDeclaration visitor

        Parameters
        ----------
        swan_obj : Swan.OperatorDeclaration
            Visited Swan object, it's a OperatorDeclaration instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "id": None,
                "pragmas": None,
                "inputs": None,
                "outputs": None,
                "size_parameters": None,
                "type_constraints": None,
                "specialization": None,
            },
        )
        _in = []
        _ou = []
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()

        if swan_obj.is_inlined:
            _doc << "inline "
        if swan_obj.is_node:
            _doc << "node "
        else:
            _doc << "function "
        self.visit_HasPragma(swan_obj, owner, owner_property)
        if _p_data["pragmas"]:
            _doc << "@m" << _p_data["pragmas"] << "@M" << " "

        _doc << _p_data["id"]
        if swan_obj.size_parameters:
            _sz = []
            _siz_pragmas = False
            for item in swan_obj.size_parameters:
                _siz_pragmas = _siz_pragmas or (isinstance(item, Swan.HasPragma) and item.pragmas)
                self._visit(item, swan_obj, "size_parameters")
                _sz.append(_p_data["size_parameters"])
            if _sz:
                _doc << " <<"
                if _siz_pragmas:
                    _doc << "@m"
                _doc << R.doc_list(*_sz, sep="@s:,:t" if _siz_pragmas else ", ")
                if _siz_pragmas:
                    _doc << "@M"
                _doc << ">>"
        for item in swan_obj.inputs:
            self._visit(item, swan_obj, "inputs")
            _in.append(_p_data["inputs"])
        _doc << " ("
        if _in:
            _doc << "@m" << R.doc_list(*_in, sep=R.doc_list(";", "@n")) << ";" << "@M"
        _doc << ")"
        _doc << "@i"
        _doc << R.DLineBreak(True)
        _doc << "returns "
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
            _ou.append(_p_data["outputs"])
        _doc << "("
        if _ou:
            _doc << "@m" << R.doc_list(*_ou, sep=R.doc_list(";", "@n")) << ";" << "@M"
        _doc << ")"
        if swan_obj.type_constraints:
            _ct = []
            for item in swan_obj.type_constraints:
                self._visit(item, swan_obj, "type_constraints")
                _ct.append(_p_data["type_constraints"])
            if _ct:
                _doc << R.doc_list(*_ct, sep=" ")
        if swan_obj.specialization:
            self._visit(swan_obj.specialization, swan_obj, "specialization")
            if _p_data["specialization"]:
                _doc << " specialize "
                _doc << _p_data["specialization"]
        _doc << "@u"

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_OptGroupItem(
        self,
        swan_obj: Swan.OptGroupItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        OptGroupItem visitor

        Parameters
        ----------
        swan_obj : Swan.OptGroupItem
            Visited Swan object, it's a OptGroupItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _p_data = self._push_and_get_doc_data({"item": None})
        _doc = R.DBlock()
        # Visit properties
        if swan_obj.item:
            # Init data buffer
            self._visit(swan_obj.item, swan_obj, "item")
            _doc << _p_data["item"]
        else:
            _doc << "_"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Oracle(
        self,
        swan_obj: Swan.Oracle,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Oracle visitor

        Parameters
        ----------
        swan_obj : Swan.Oracle
            Visited Swan object, it's a Oracle instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None})
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        _doc << "_oracle "
        _doc << _p_data["id"]
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_PartialOperator(
        self,
        swan_obj: Swan.PartialOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Partial visitor

        Parameters
        ----------
        swan_obj : Swan.PartialOperator
            Visited Swan object, it's a PartialOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None, "partial_group": []})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        for item in swan_obj.partial_group:
            self._visit(item, swan_obj, "partial_group")
        _doc = R.DBlock()
        _doc << _p_data["operator"]
        _doc << " \\ "
        _doc << R.doc_list(*cast(List[R.DElt], _p_data["partial_group"]), sep=", ")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_PathIdentifier(
        self,
        swan_obj: Swan.PathIdentifier,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Path Identifier visitor

        Parameters
        ----------
        swan_obj : Swan.PathIdentifier
            Visited Swan object, it's a PathIdentifier instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"path_id": None, "pragmas": None})
        # Visit properties
        _doc = R.DBlock()

        if swan_obj.is_protected:
            _doc << R.DText(Swan.Markup.to_str(cast(str, swan_obj.path_id)))
        else:
            _lst = []
            for item in cast(List[Swan.Identifier], swan_obj.path_id):
                self._visit(item, swan_obj, "path_id")
                _lst.append(_p_data["path_id"])
            if _lst:
                _doc << R.doc_list(*_lst, sep="::")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_PathIdExpr(
        self,
        swan_obj: Swan.PathIdExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Path Identifier Expression visitor

        Parameters
        ----------
        swan_obj : Swan.PathIdExpr
            Visited Swan object, it's a PathIdExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"path_id": None})
        # Visit base class(es)
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        _doc = R.DBlock()
        _doc << _p_data["path_id"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_NamedInstance(
        self,
        swan_obj: Swan.NamedInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        PathId Operator Call visitor

        Parameters
        ----------
        swan_obj : Swan.NamedInstance
            Visited Swan object, it's a NamedInstance instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        self._push_and_get_doc_data({"instance_": None})
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "instance_")
        # Visit base class(es)
        self.visit_OperatorInstance(swan_obj, owner, owner_property)

    def visit_PathIdPattern(
        self,
        swan_obj: Swan.PathIdPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        PathId Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.PathIdPattern
            Visited Swan object, it's a PathIdPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"path_id": None})
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        _doc = R.DBlock()
        _doc << _p_data["path_id"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_PortExpr(
        self,
        swan_obj: Swan.PortExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Port Expression visitor

        Parameters
        ----------
        swan_obj : Swan.PortExpr
            Visited Swan object, it's a PortExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lunum": None, "luid": None})
        _doc = R.DBlock()
        # Visit properties
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << _p_data["lunum"]
        if swan_obj.is_self:
            _doc << "self"
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << _p_data["luid"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Pragma(
        self,
        swan_obj: Swan.Pragma,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pragma visitor

        Parameters
        ----------
        swan_obj : Swan.Pragma
            Visited Swan object, it's a Pragma instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self._set_doc_data(owner_property, R.text(str(swan_obj)))

    def visit_HasPragma(
        self,
        swan_obj: Swan.HasPragma,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        HasPragma visitor

        Parameters
        ----------
        swan_obj : Swan.HasPragma
            Visited Swan object, it's a HasPragma instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object (unused)
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object (unused)
        """
        # visit_HasPragma is only called by other visit_ methods, retrieve its doc data
        _p_data = self._get_current_doc_data()
        _p_data.update({"pragmas": []})
        # Visit properties
        if not swan_obj.pragmas:
            return
        for item in swan_obj.pragmas:
            self.visit_Pragma(item, swan_obj, "pragmas")
        _doc = R.doc_list(*cast(List[R.DElt], _p_data["pragmas"]), sep="@n")
        _p_data.update({"pragmas": _doc})

    def visit_PredefinedType(
        self,
        swan_obj: Swan.PredefinedType,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Predefined Type visitor

        Parameters
        ----------
        swan_obj : Swan.PredefinedType
            Visited Swan object, it's a PredefinedType instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.text(swan_obj.name))

    def visit_OperatorExpressionInstance(
        self,
        swan_obj: Swan.OperatorExpressionInstance,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Operator expression instance visitor: *(op_expr)*

        Parameters
        ----------
        swan_obj : Swan.OperatorExpressionInstance
            Visited Swan object, it's a OperatorExpressionInstance instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"op_expr": None, "instance_": None})
        # Visit properties
        self._visit(swan_obj.op_expr, swan_obj, "op_expr")
        _doc = R.DBlock()
        _doc << "("
        if swan_obj.op_expr.is_op_expr:
            _doc << r"{op_expr%"
        _doc << _p_data["op_expr"]
        if swan_obj.op_expr.is_op_expr:
            _doc << r"%op_expr}"
        _doc << ")"
        # Update property
        _p_data["instance_"] = _doc
        # Visit base class(es)
        self.visit_OperatorInstance(swan_obj, owner, owner_property)

    def visit_ReverseOperator(
        self,
        swan_obj: Swan.ReverseOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Reverse operator visitor

        Parameters
        ----------
        swan_obj : Swan.ReverseOperator
            Visited Swan object, it's a ReverseOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _doc = R.DText("reverse")
        # Update property
        self._push_and_get_doc_data({"instance_": _doc})
        # Visit base class(es)
        self.visit_OperatorInstance(swan_obj, owner, owner_property)

    def visit_PackOperator(
        self,
        swan_obj: Swan.PackOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pack operator visitor

        Parameters
        ----------
        swan_obj : Swan.PackOperator
            Visited Swan object, it's a PackOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _doc = R.DText("pack")
        # Update property
        self._push_and_get_doc_data({"instance_": _doc})
        # Visit base class(es)
        self.visit_OperatorInstance(swan_obj, owner, owner_property)

    def visit_FlattenOperator(
        self,
        swan_obj: Swan.FlattenOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Flatten operator visitor

        Parameters
        ----------
        swan_obj : Swan.FlattenOperator
            Visited Swan object, it's a FlattenOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _doc = R.DText("flatten")
        # Update property
        self._push_and_get_doc_data({"instance_": _doc})
        # Visit base class(es)
        self.visit_OperatorInstance(swan_obj, owner, owner_property)

    def visit_ProjectionWithDefault(
        self,
        swan_obj: Swan.ProjectionWithDefault,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Project With Default visitor

        Parameters
        ----------
        swan_obj : Swan.ProjectionWithDefault
            Visited Swan object, it's a ProjectionWithDefault instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "indices": [], "default": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.indices:
            self._visit(item, swan_obj, "indices")
        self._visit(swan_obj.default, swan_obj, "default")
        _indices = cast(List[R.DElt], _p_data["indices"])
        _doc = R.DBlock()
        _doc << "("
        _doc << _p_data["expr"]
        _doc << " . "
        _doc << R.doc_list(*_indices, sep="")
        _doc << " default "
        _doc << _p_data["default"]
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ProtectedDecl(
        self,
        swan_obj: Swan.ProtectedDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Declaration visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedDecl
            Visited Swan object, it's a ProtectedDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        _doc = R.DBlock()
        _p_data = self._push_and_get_doc_data({"pragmas": None})
        self.visit_HasPragma(swan_obj, owner, owner_property)
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        _doc << "{"
        _doc << R.DText(swan_obj.markup) if swan_obj.markup else ""
        _doc << "%"
        _dta = [R.DText(_itm) for _itm in swan_obj.data.split("\n")]
        _doc << R.doc_list(*_dta, sep=R.DLineBreak(False))
        _doc << "%"
        _doc << R.DText(swan_obj.markup) if swan_obj.markup else ""
        _doc << "}" << "@n"
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_ProtectedExpr(
        self,
        swan_obj: Swan.ProtectedExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Expression visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedExpr
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
        swan_obj: Swan.ProtectedGroupRenaming,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected GroupRenaming visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedGroupRenaming
            Visited Swan object, it's a ProtectedGroupRenaming instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self.visit_ProtectedItem(swan_obj, owner, owner_property)

    def visit_ProtectedItem(
        self,
        swan_obj: Swan.ProtectedItem,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Item visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedItem
            Visited Swan object, it's a ProtectedItem instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        _doc = R.DBlock()
        _doc << "{" << swan_obj.markup << "%"
        _dta = [R.DText(_itm) for _itm in swan_obj.data.split("\n")]
        _doc << R.doc_list(*_dta, sep=R.DLineBreak(False))
        _doc << "%" << swan_obj.markup << "}"
        # Update property
        self._set_doc_data(owner_property, _doc)

    def visit_ProtectedOpExpr(
        self,
        swan_obj: Swan.ProtectedOpExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Operator Expression visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedOpExpr
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
        swan_obj: Swan.ProtectedSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Section visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedSection
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
        swan_obj: Swan.ProtectedVariable,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Protected Variable visitor

        Parameters
        ----------
        swan_obj : Swan.ProtectedVariable
            Visited Swan object, it's a ProtectedVariable instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        _p_data = self._push_and_get_doc_data({"pragmas": None, "item_": None})
        self.visit_HasPragma(swan_obj, owner, owner_property)
        _doc = R.DBlock()
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        self.visit_ProtectedItem(swan_obj, owner, "item_")
        _doc << _p_data["item_"]
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_RestartOperator(
        self,
        swan_obj: Swan.RestartOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Restart visitor

        Parameters
        ----------
        swan_obj : Swan.RestartOperator
            Visited Swan object, it's a RestartOperator instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"operator": None, "condition": None})
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.condition, swan_obj, "condition")
        _doc = R.DBlock()
        _doc << "restart "
        _doc << _p_data["operator"]
        _doc << " every "
        _doc << _p_data["condition"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Scope(
        self,
        swan_obj: Swan.Scope,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Scope visitor

        Parameters
        ----------
        swan_obj : Swan.Scope
            Visited Swan object, it's a Scope instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"sections": None, "pragmas": None})
        # Visit base class(es)
        self.visit_HasPragma(swan_obj, owner, "pragmas")
        _sc = []
        # Visit properties
        for item in swan_obj.sections:
            self._visit(item, swan_obj, "sections")
            _sc.append(_p_data["sections"])
        _doc = R.DBlock()
        _doc << "{"
        if _sc:
            _doc << "@i" << "@n"
            _doc << R.doc_list(*_sc, sep="@n") << "@u"
        if swan_obj.pragmas:
            _doc << "@n"
            _doc << _p_data["pragmas"]
        _doc << "@n" << "}"
        if owner_property != "data_def":
            _doc << "@n"

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_OperatorDeclaration(
        self,
        swan_obj: Swan.OperatorDeclaration,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        OperatorDeclaration visitor

        Parameters
        ----------
        swan_obj : Swan.OperatorDeclaration
            Visited Swan object, it's a OperatorDeclaration instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _p_data = self._push_and_get_doc_data({"interface_": None})
        self.visit_OperatorDeclarationDefinitionBase(swan_obj, owner, "interface_")
        _doc = R.DBlock()
        if swan_obj.is_text:
            _doc << "{signature%" << _p_data["interface_"] << ";%signature}"
        else:
            _doc << _p_data["interface_"] << ";"
        _doc << "@n"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_SizeParameter(
        self,
        swan_obj: Swan.SizeParameter,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        SizeParameter visitor

        Parameters
        ----------
        swan_obj : Swan.SizeParameter
            Visited Swan object, it's a SizeParameter instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Visit properties
        _p_data = self._push_and_get_doc_data({"id": None, "pragmas": None})
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        self.visit_HasPragma(swan_obj, owner, "pragmas")
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        _doc << _p_data["id"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_SizedTypeExpression(
        self,
        swan_obj: Swan.SizedTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Sized Type Expression visitor

        Parameters
        ----------
        swan_obj : Swan.SizedTypeExpression
            Visited Swan object, it's a SizedTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"size": None})
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        _doc = R.DBlock()
        if swan_obj.is_signed:
            _doc << "signed "
        else:
            _doc << "unsigned "
        _doc << "<<"
        _doc << _p_data["size"]
        _doc << ">>"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_SectionObject(
        self,
        swan_obj: Swan.SectionObject,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Section Object visitor

        Parameters
        ----------
        swan_obj : Swan.SectionObject
            Visited Swan object, it's a SectionObject instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"section": None})
        # Visit properties
        self._visit(swan_obj.section, swan_obj, "section")
        if swan_obj.section.is_text:
            _doc = R.DBlock()
            _doc << "{text%"
            _doc << _p_data["section"]
            _doc << "%text}"
        else:
            _doc = _p_data["section"]

        _p_data["description"] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_SensorDecl(
        self,
        swan_obj: Swan.SensorDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a sensor declaration
        Syntax: sensor_decl ::= id : type_expr

        Parameters
        ----------
        swan_obj : Swan.SensorDecl
            Visited Swan object, it's a SensorDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "id": None,
                "type": None,
            },
        )
        # Visit parent class
        super().visit_SensorDecl(swan_obj, owner, owner_property)
        _doc = R.DBlock()
        self._decl_pragmas(swan_obj, _doc)
        _doc << _p_data["id"]
        if _p_data["type"]:
            _doc << ": " << _p_data["type"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_SensorDeclarations(
        self,
        swan_obj: Swan.SensorDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of sensor declarations

        Parameters
        ----------
        swan_obj : Swan.SensorDeclarations
            Visited Swan object, it's a SensorDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"sensors": []})
        # Visit parent class
        super().visit_SensorDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(_p_data, "sensors", "sensor")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["sensors"]))

    def visit_SetSensorBlock(
        self, swan_obj: Swan.SetSensorBlock, owner: Owner, owner_property: OwnerProperty
    ) -> None:
        """
        Pretty prints a set sensor block

        Parameters
        ----------
        swan_obj : Swan.SetSensorBlock
            Visited Swan object, it's a SetSensorBlock instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"sensor": None})
        # Visit properties
        self._visit(swan_obj.sensor, swan_obj, "sensor")
        _doc = R.DBlock()
        _doc << "_sensor "
        if swan_obj.is_protected:
            _doc << R.DText(str(swan_obj.sensor))
        else:
            _doc << _p_data["sensor"]

        _p_data["description"] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)

    def visit_Slice(
        self,
        swan_obj: Swan.Slice,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Slice visitor

        Parameters
        ----------
        swan_obj : Swan.Slice
            Visited Swan object, it's a Slice instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "start": None, "end": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.start, swan_obj, "start")
        self._visit(swan_obj.end, swan_obj, "end")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << "["
        _doc << _p_data["start"]
        _doc << " .. "
        _doc << _p_data["end"]
        _doc << "]"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    class __StateTransitionContext(Flag):
        # Context for state transitions as enum Flag, which can be combined (ORed)
        # A transition may be in a state, or as a separate item
        # The information must be carried to the transition visitor for forks
        # We also need to know if we are at the start of a transition, or in a fork branch
        NONE = auto()  # default value
        IN_DECL = auto()  # transition is given as an automaton item (not in state)
        IN_STATE = auto()  # transition given in the state definition
        FROM_STATE = auto()  # transition comes from a state (in state or as decl)
        FROM_FORK = auto()  # transition comes from a fork (in state or as decl)
        ELSIF = auto()  # transition is in an "elsif" branch of a fork

    def visit_State(
        self,
        swan_obj: Swan.State,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        State visitor

        Parameters
        ----------
        swan_obj : Swan.State
            Visited Swan object, it's a State instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init return data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "id": None,
                "lunum": None,
                "strong": [],  # used to collect visit of strong transitions
                "sections": [],  # use to collect visit of all sections in the body
                "weak": [],  # used to collect visit of weak transitions
                "context": PPrinter.__StateTransitionContext.NONE,  # transition context of use
            },
        )

        def _visit_transitions(transitions: List[Swan.Transition], kind: str) -> None:
            # Help to generate transition code.
            # 'kind' is either 'strong' or 'weak'
            # transitions are the transitions found in the state definition.
            sorted_transitions = sorted(transitions, key=Swan.Transition.sort_key)
            for tr in sorted_transitions:
                _p_data["context"] = (
                    PPrinter.__StateTransitionContext.FROM_STATE
                    | PPrinter.__StateTransitionContext.IN_STATE
                )
                self._visit(tr, swan_obj, kind)

        # Initialize document
        _doc = R.DBlock()
        # Visit base class(es)
        self.visit_HasPragma(swan_obj, owner, owner_property)

        # Use the unsorted transitions to keep the order
        _visit_transitions(swan_obj.in_state_strong_transition_decls, "strong")
        # Visit body's sections. For a state, there is no enclosing "{}",
        # so we don't call the visit_Scope method.
        if swan_obj.body:
            for section in swan_obj.body.sections:
                self._visit(section, swan_obj, "sections")
        # Use the unsorted transitions to keep the order
        _visit_transitions(swan_obj.in_state_weak_transition_decls, "weak")

        # Generate state declaration
        if swan_obj.is_initial:
            _doc << "initial "
        _doc << "state"
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << " " << _p_data["lunum"]
        if swan_obj.id:
            self._visit(swan_obj.id, swan_obj, "id")
            _doc << " " << _p_data["id"]
        if swan_obj.pragmas:
            _doc << "@n"
            _doc << _p_data["pragmas"]
        _doc << " :" << "@i"
        if _p_data["strong"]:
            _doc << "@n" << "unless" << "@n"
            _doc << R.doc_list(*cast(List[R.DElt], _p_data["strong"]), sep="@n")
        if _p_data["sections"]:
            _doc << "@n"
            _doc << R.doc_list(*cast(List[R.DElt], _p_data["sections"]), sep="@n")
        if _p_data["weak"]:
            _doc << "@n" << "until" << "@n"
            _doc << R.doc_list(*cast(List[R.DElt], _p_data["weak"]), sep="@n")
        _doc << "@u"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_DataSource(
        self,
        swan_obj: Swan.DataSource,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        DataSource visitor

        Parameters
        ----------
        swan_obj : Swan.DataSource
            Visited Swan object, it's a DataSource instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"id": None})
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        _doc << "_source "
        _doc << _p_data["id"]
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_StateRef(
        self,
        swan_obj: Swan.StateRef,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        StateRef visitor

        Parameters
        ----------
        swan_obj : Swan.StateRef
            Visited Swan object, it's a StateRef instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        _p_data = self._push_and_get_doc_data({"lunum": None, "id": None})
        _doc = R.DBlock()
        # Visit properties
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << _p_data["lunum"]
        elif swan_obj.id:
            self._visit(swan_obj.id, swan_obj, "id")
            _doc << _p_data["id"]
        else:
            raise Swan.ScadeOneException("StateRef must have either lunum or id defined")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_StateMachine(
        self,
        swan_obj: Swan.StateMachine,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        State Machine visitor

        Parameters
        ----------
        swan_obj : Swan.StateMachine
            Visited Swan object, it's a StateMachine instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "lunum": None,
                "luid": None,
                "items": [],
                # transition context of use. Transitions defined as
                # automaton declararation, and start from a state
                "context": (
                    PPrinter.__StateTransitionContext.IN_DECL
                    | PPrinter.__StateTransitionContext.FROM_STATE
                ),
            },
        )

        _doc = R.DBlock()

        if not isinstance(owner, Swan.DefByCaseBlockBase):
            # automaton in let: indentation from the beginning of the keyword
            _doc << "@m"

        _doc << "automaton" << "@i"
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _doc << " " << _p_data["lunum"]
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _doc << " " << _p_data["luid"]
        if swan_obj.items:
            for item in swan_obj.items:
                self._visit(item, swan_obj, "items")
            (_doc << "@n" << R.doc_list(*cast(List[R.DElt], _p_data["items"]), sep="@n"))
        _doc << "@u"
        if not isinstance(owner, Swan.DefByCaseBlockBase):
            # automaton in let: reset indentation
            _doc << "@u"
        # Pass data to DefByCaseBlockBase visitor
        _p_data["defbycase_"] = _doc
        # Visit base class(es)
        self.visit_DefByCase(swan_obj, owner, owner_property)

    def visit_StateMachineBlock(
        self,
        swan_obj: Swan.StateMachineBlock,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        State Machine Block visitor

        Parameters
        ----------
        swan_obj : Swan.StateMachineBlock
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
        swan_obj: Swan.StructConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Constructor visitor

        Parameters
        ----------
        swan_obj : Swan.StructConstructor
            Visited Swan object, it's a StructConstructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"group": None, "type": None})
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        _doc = R.DBlock()
        _doc << "{"
        _doc << _p_data["group"]
        _doc << "}"
        if swan_obj.type:
            self._visit(swan_obj.type, swan_obj, "type")
            _doc << " : "
            _doc << _p_data["type"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_StructDestructor(
        self,
        swan_obj: Swan.StructDestructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Destructor visitor

        Parameters
        ----------
        swan_obj : Swan.StructDestructor
            Visited Swan object, it's a StructDestructor instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"group": None, "expr": None})
        # Visit properties
        self._visit(swan_obj.group_id, swan_obj, "group")
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << _p_data["group"]
        _doc << " group ("
        _doc << _p_data["expr"]
        _doc << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_StructField(
        self,
        swan_obj: Swan.StructField,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Field visitor

        Parameters
        ----------
        swan_obj : Swan.StructField
            Visited Swan object, it's a StructField instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data
        _p_data = self._push_and_get_doc_data({"id": None, "type": None})
        self.visit_HasPragma(
            swan_obj,
            owner,
            owner_property,
        )
        self._visit(swan_obj.id, swan_obj, "id")
        self._visit(swan_obj.type, swan_obj, "type")
        _doc = R.DBlock()
        if swan_obj.pragmas:
            _doc << _p_data["pragmas"] << " "
        _doc << _p_data["id"] << ": " << _p_data["type"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_StructProjection(
        self,
        swan_obj: Swan.StructProjection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Projection visitor

        Parameters
        ----------
        swan_obj : Swan.StructProjection
            Visited Swan object, it's a StructProjection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "label": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.label, swan_obj, "label")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << _p_data["label"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_StructTypeDefinition(
        self,
        swan_obj: Swan.StructTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Struct Type Definition visitor

        Parameters
        ----------
        swan_obj : Swan.StructTypeDefinition
            Visited Swan object, it's a StructTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"fields": []})
        # Visit properties
        for item in swan_obj.fields:
            self._visit(item, swan_obj, "fields")

        _doc = (
            R.DBlock() << "{" << R.doc_list(*cast(List[R.DElt], _p_data["fields"]), sep=", ") << "}"
        )
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Transition(
        self,
        swan_obj: Swan.Transition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Transition visitor

        Parameters
        ----------
        swan_obj : Swan.Transition
            Visited Swan object, it's a Transition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {"state_ref": None, "guard": None, "action": None, "target": None}
        )
        _owner_context = self._get_owner_doc_data()
        _doc = R.DBlock()

        # - context: are we in a state, or in a declaration
        if "context" not in _owner_context.keys():
            # When calling swan_to_str(transition), for context to be IN_STATE
            _owner_context["context"] = PPrinter.__StateTransitionContext.IN_STATE

        _in_decl = cast(Flag, _owner_context["context"]) & PPrinter.__StateTransitionContext.IN_DECL
        _in_fork = (
            cast(Flag, _owner_context["context"]) & PPrinter.__StateTransitionContext.FROM_FORK
        )

        if _in_decl:
            # in declaration of a transition, start with its priority
            _doc << ":" << (str(swan_obj.priority) if swan_obj.priority else " ") << ":"
            # A declaration starting from a state require the source state and the "strong/weak" keyword
            # This happens only for transitions given as declaration in the automaton, where source is provided
            if source := swan_obj.source:
                self._visit(source, swan_obj, "state_ref")
                (
                    _doc
                    << " "
                    << _p_data["state_ref"]
                    << (" unless " if swan_obj.is_strong else " until ")
                )

        # - Guard depends on context: either transition start, or fork branch
        if swan_obj.guard:
            self._visit(swan_obj.guard, swan_obj, "guard")
            prefix = ""
            if _in_decl:
                # in declaration => "if"
                prefix = " if" if _in_fork else "if"
            else:
                # in state => "elsif" if in fork branch, else "if" (start)
                _is_fork_elsif = (
                    cast(Flag, _owner_context["context"]) & PPrinter.__StateTransitionContext.ELSIF
                )
                prefix = "elsif" if _is_fork_elsif else "if"
            _doc << prefix << " (" << _p_data["guard"] << ")"
        elif _in_fork:
            # no guard and fork context => "else", else no guard to print
            _doc << (" else " if _in_decl else "else ")

        # - Action
        if swan_obj.action:
            self._visit(swan_obj.action, swan_obj, "action")
            _doc << "@n" << _p_data["action"]
        # - Transfer context for target, which may be a fork, for fork priority list
        # We are not more in a START context for the target
        _p_data["context"] = (
            PPrinter.__StateTransitionContext.IN_DECL
            if _in_decl
            else PPrinter.__StateTransitionContext.IN_STATE
        )
        if isinstance(swan_obj.target, Swan.Fork):
            _doc << "@i"
        if not (swan_obj.action):
            _doc << "@n"
        self._visit(swan_obj.target, swan_obj, "target")
        if isinstance(swan_obj.target, Swan.StateRef):
            _doc << ("resume " if swan_obj.is_resume else "restart ")
        _doc << _p_data["target"]
        if isinstance(swan_obj.target, Swan.Fork):
            _doc << "@u"

        # end of transition
        owner_p_data = self._get_owner_doc_data()
        if cast(Flag, owner_p_data["context"]) & PPrinter.__StateTransitionContext.FROM_STATE:
            # start of a transition => add the pragmas and semicolon
            self.visit_HasPragma(swan_obj, owner, "pragmas")
            if _p_data["pragmas"]:
                _doc << "@n" << _p_data["pragmas"]
            _doc << ";"

        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_TransposeOperator(
        self,
        swan_obj: Swan.TransposeOperator,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Transpose visitor

        Parameters
        ----------
        swan_obj : Swan.Transpose
            Visited Swan object, it's a Transpose instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        _doc = R.DBlock()
        _doc << "transpose"
        if swan_obj.params:
            _doc << " {"
            if isinstance(swan_obj.params, list):
                _pm = []
                for item in swan_obj.params:
                    _pm.append(R.text(item))
                if _pm:
                    _doc << R.doc_list(*_pm, sep=", ")
            elif SwanVisitor._is_builtin(swan_obj.params):
                _doc << R.text(swan_obj.params)
            _doc << "}"
        # Update property
        self._push_and_get_doc_data({"instance_": _doc})
        # Visit base class(es)
        self.visit_OperatorInstance(swan_obj, owner, owner_property)

    def visit_TypeConstraint(
        self,
        swan_obj: Swan.TypeConstraint,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Type Constraint visitor

        Parameters
        ----------
        swan_obj : Swan.TypeConstraint
            Visited Swan object, it's a TypeConstraint instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"type_vars": None})
        # Visit properties
        _doc = R.DBlock()
        _doc << "@n" << "where "
        if swan_obj.is_protected:
            _doc << R.DText(Swan.Markup.to_str(cast(str, swan_obj.type_vars)))
        else:
            _tv = []
            for item in cast(List[Swan.VariableTypeExpression], swan_obj.type_vars):
                self._visit(item, swan_obj, "type_vars")
                _tv.append(_p_data["type_vars"])
            if _tv:
                _doc << R.doc_list(*_tv, sep=", ")
        _doc << " " << R.DText(swan_obj.kind.name.lower())
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_TypeDecl(
        self,
        swan_obj: Swan.TypeDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a type declaration

        Parameters
        ----------
        swan_obj : Swan.TypeDecl
            Visited Swan object, it's a TypeDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "id": None,
                "definition": None,
            },
        )
        # Visit parent class
        super().visit_TypeDecl(swan_obj, owner, owner_property)
        # Visit properties
        _doc = R.DBlock()
        self._decl_pragmas(swan_obj, _doc)
        _doc << _p_data["id"]
        if _p_data["definition"]:
            _doc << " = " << _p_data["definition"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_TypeDeclarations(
        self,
        swan_obj: Swan.TypeDeclarations,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Pretty prints a list of type declarations

        Parameters
        ----------
        swan_obj : Swan.TypeDeclarations
            Visited Swan object, it's a TypeDeclarations instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"types": []})
        # Visit parent class
        super().visit_TypeDeclarations(swan_obj, owner, owner_property)
        # Update data buffer
        self._decl_formatting(_p_data, "types", "type")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["types"]))

    def visit_TypeGroupTypeExpression(
        self,
        swan_obj: Swan.TypeGroupTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Group Type Expression visitor

        Parameters
        ----------
        swan_obj : Swan.TypeGroupTypeExpression
            Visited Swan object, it's a TypeGroupTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"type": None})
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["type"]))

    def visit_TypeReferenceExpression(
        self,
        swan_obj: Swan.TypeReferenceExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Type Reference Expression visitor

        Parameters
        ----------
        swan_obj : Swan.TypeReferenceExpression
            Visited Swan object, it's a TypeReferenceExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"alias": None})
        # Visit properties
        self._visit(swan_obj.alias, swan_obj, "alias")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["alias"]))

    def visit_Uint8Type(
        self,
        swan_obj: Swan.Uint8Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint8 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Uint8Type
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
        swan_obj: Swan.Uint16Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint16 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Uint16Type
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
        swan_obj: Swan.Uint32Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint32 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Uint32Type
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
        swan_obj: Swan.Uint64Type,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Uint64 Type visitor

        Parameters
        ----------
        swan_obj : Swan.Uint64Type
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
        swan_obj: Swan.UnaryExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Unary Expression visitor

        Parameters
        ----------
        swan_obj : Swan.UnaryExpr
            Visited Swan object, it's a UnaryExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        _doc = R.DBlock()
        _doc << Swan.UnaryOp.to_str(swan_obj.operator)
        match swan_obj:
            case (
                Swan.UnaryExpr(operator=Swan.UnaryOp.Pre)
                | Swan.UnaryExpr(operator=Swan.UnaryOp.Lnot)
                | Swan.UnaryExpr(operator=Swan.UnaryOp.Not)
            ):
                _doc << " "
            case Swan.UnaryExpr(
                operator=Swan.UnaryOp.Minus, expr=Swan.UnaryExpr(operator=Swan.UnaryOp.Minus)
            ):
                _doc << " "  # add a space after "-" to avoid confusion with "--"
            case _:
                pass

        _doc << _p_data["expr"]
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)  # Update property
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_PreExpr(
        self,
        swan_obj: Swan.PreExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Unary Expression visitor

        Parameters
        ----------
        swan_obj : Swan.PreExpr
            Visited Swan object, it's a PreExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self.visit_UnaryExpr(swan_obj, owner, owner_property)

    def visit_UnderscorePattern(
        self,
        swan_obj: Swan.UnderscorePattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Underscore Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.UnderscorePattern
            Visited Swan object, it's a UnderscorePattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        self._set_doc_data(owner_property, R.DText("_"))

    def visit_UseDirective(
        self,
        swan_obj: Swan.UseDirective,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Use Directive visitor

        Parameters
        ----------
        swan_obj : Swan.UseDirective
            Visited Swan object, it's a UseDirective instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"path": None, "alias": None})
        # Visit properties
        self._visit(swan_obj.path, swan_obj, "path")
        _doc = R.DBlock()
        self.visit_HasPragma(swan_obj, owner, owner_property)
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        _doc << "use "
        _doc << _p_data["path"]
        if swan_obj.alias:
            self._visit(swan_obj.alias, swan_obj, "alias")
            _doc << " as "
            _doc << _p_data["alias"]
        _doc << ";" << "@n"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VarDecl(
        self,
        swan_obj: Swan.VarDecl,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variable Declaration visitor

        Parameters
        ----------
        swan_obj : Swan.VarDecl
            Visited Swan object, it's a VarDecl instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data(
            {
                "id": None,
                "type": None,
                "when": None,
                "default": None,
                "last": None,
                "place": None,
            },
        )
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _doc = R.DBlock()
        if swan_obj.is_clock:
            _doc << "clock "
        self.visit_HasPragma(swan_obj, owner, owner_property)
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        _doc << _p_data["id"]
        if swan_obj.is_starred:
            _doc << " *"
        if swan_obj.at is not None:
            self._visit(
                swan_obj.at,
                swan_obj,
                "place",
            )
            _doc << " at " << _p_data["place"]
        if swan_obj.type:
            self._visit(swan_obj.type, swan_obj, "type")
            if (
                swan_obj.is_starred and not swan_obj.at
            ):  # Note is_starred and at should be mutually exclusive
                _doc << " "  # add a space after "*"
            _doc << ": "
            _doc << _p_data["type"]
        if swan_obj.when:
            self._visit(swan_obj.when, swan_obj, "when")
            _doc << " when "
            _doc << _p_data["when"]
        if swan_obj.default:
            self._visit(swan_obj.default, swan_obj, "default")
            _doc << " default = "
            _doc << _p_data["default"]
        if swan_obj.last:
            self._visit(swan_obj.last, swan_obj, "last")
            _doc << " last = "
            _doc << _p_data["last"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VariableTypeExpression(
        self,
        swan_obj: Swan.VariableTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variable Type Expression visitor

        Parameters
        ----------
        swan_obj : Swan.VariableTypeExpression
            Visited Swan object, it's a VariableTypeExpression instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"name": None})
        # Visit properties
        self._visit(swan_obj.name, swan_obj, "name")
        self._pop_and_set_doc_data(owner_property, cast(R.DElt, _p_data["name"]))

    def visit_VariantPattern(
        self,
        swan_obj: Swan.VariantPattern,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant Pattern visitor

        Parameters
        ----------
        swan_obj : Swan.VariantPattern
            Visited Swan object, it's a VariantPattern instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"path_id": None, "captured": None})
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        _doc = R.DBlock()
        _doc << _p_data["path_id"]
        if swan_obj.has_capture:
            self._visit(cast(Swan.Identifier, swan_obj.captured), swan_obj, "captured")
            _doc << " {"
            _doc << _p_data["captured"]
            _doc << "}"
        elif swan_obj.is_underscore:
            _doc << " _"
        else:
            _doc << " {}"
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VariantConstructor(
        self,
        swan_obj: Swan.VariantConstructor,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        VariantConstructor Type Definition visitor.

        This is a helper function for variant type definition
        derived classes.

        Parameters
        ----------
        swan_obj : Swan.VariantConstructor
            Visited Swan object, it's a VariantConstructor derived instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        self._visit(swan_obj.tag, swan_obj, "tag")
        self.visit_HasPragma(swan_obj, owner, owner_property)

    def visit_VariantSimple(
        self,
        swan_obj: Swan.VariantSimple,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant type only defined by a tag visitor

        Parameters
        ----------
        swan_obj : Swan.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _p_data = self._push_and_get_doc_data({"tag": None})
        self.visit_VariantConstructor(swan_obj, owner, owner_property)
        _doc = R.DBlock()
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        _doc << _p_data["tag"] << " {}"

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VariantTypeExpression(
        self,
        swan_obj: Swan.VariantTypeExpression,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant type with expression visitor

        Parameters
        ----------
        swan_obj : Swan.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _p_data = self._push_and_get_doc_data({"tag": None, "type": None})
        self.visit_VariantConstructor(swan_obj, owner, owner_property)
        self._visit(swan_obj.type, swan_obj, "type")

        _doc = R.DBlock()
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        (_doc << _p_data["tag"] << " { " << _p_data["type"] << " }")

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VariantStruct(
        self,
        swan_obj: Swan.VariantStruct,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant type as structure visitor

        Parameters
        ----------
        swan_obj : Swan.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        _p_data = self._push_and_get_doc_data({"tag": None, "structure_type": None})
        self.visit_VariantConstructor(swan_obj, owner, owner_property)
        self._visit(swan_obj.structure_type, swan_obj, "structure_type")

        _doc = R.DBlock()
        if _p_data["pragmas"]:
            _doc << _p_data["pragmas"] << " "
        (_doc << _p_data["tag"] << " " << _p_data["structure_type"])

        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VariantTypeDefinition(
        self,
        swan_obj: Swan.VariantTypeDefinition,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant Type Definition visitor

        Parameters
        ----------
        swan_obj : Swan.VariantTypeDefinition
            Visited Swan object, it's a VariantTypeDefinition instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"tags": []})
        # Visit properties
        for itm in swan_obj.tags:
            self._visit(itm, swan_obj, "tags")

        _doc = R.DBlock()
        _doc << R.doc_list(*cast(List[R.DElt], _p_data["tags"]), sep=" | ")
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VariantValue(
        self,
        swan_obj: Swan.VariantValue,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variant Value visitor

        Parameters
        ----------
        swan_obj : Swan.VariantValue
            Visited Swan object, it's a VariantValue instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"tag": None, "group": None})
        # Visit properties
        self._visit(swan_obj.tag, swan_obj, "tag")
        self._visit(swan_obj.group, swan_obj, "group")
        _doc = R.DBlock()
        _doc << _p_data["tag"]
        _doc << " {"
        _doc << _p_data["group"]
        _doc << "}"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_VarSection(
        self,
        swan_obj: Swan.VarSection,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Variable Section visitor

        Parameters
        ----------
        swan_obj : Swan.VarSection
            Visited Swan object, it's a VarSection instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"var_decls": None})
        _vr = []
        # Visit properties
        for item in swan_obj.var_decls:
            self._visit(item, swan_obj, "var_decls")
            _vr.append(_p_data["var_decls"])
        # Update property
        var_decl = PPrinter._format_list("var", _vr)
        self._pop_and_set_doc_data(owner_property, var_decl)

    def visit_WhenClockExpr(
        self,
        swan_obj: Swan.WhenClockExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        When Clock Expression visitor

        Parameters
        ----------
        swan_obj : Swan.WhenClockExpr
            Visited Swan object, it's a WhenClockExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "clock": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.clock, swan_obj, "clock")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << " when "
        _doc << _p_data["clock"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_WhenMatchExpr(
        self,
        swan_obj: Swan.WhenMatchExpr,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        When Match Expression visitor

        Parameters
        ----------
        swan_obj : Swan.WhenMatchExpr
            Visited Swan object, it's a WhenMatchExpr instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"expr": None, "when": None})
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.when, swan_obj, "when")
        _doc = R.DBlock()
        _doc << _p_data["expr"]
        _doc << " when match "
        _doc << _p_data["when"]
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Window(
        self,
        swan_obj: Swan.Window,
        owner: Owner,
        owner_property: OwnerProperty,
    ) -> None:
        """
        Window visitor

        Parameters
        ----------
        swan_obj : Swan.Window
            Visited Swan object, it's a Window instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        _p_data = self._push_and_get_doc_data({"size": None, "init": None, "params": None})
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        self._visit(swan_obj.init, swan_obj, "init")
        self._visit(swan_obj.params, swan_obj, "params")
        _doc = R.DBlock()
        _doc << "window " << "<<"
        _doc << _p_data["size"]
        _doc << ">> " << "("
        _doc << _p_data["init"]
        _doc << ") " << "("
        _doc << _p_data["params"] << ")"
        # Check "at" property
        _doc = self._expr_at_property(swan_obj, _doc)
        # Update property
        self._pop_and_set_doc_data(owner_property, _doc)

    def visit_Wire(self, swan_obj: Swan.Wire, owner: Owner, owner_property: OwnerProperty) -> None:
        """
        Wire visitor

        Parameters
        ----------
        swan_obj : Swan.Wire
            Visited Swan object, it's a Wire instance
        owner : Owner
            Owner of the swan_obj, 'None' for the root visited object
        owner_property : OwnerProperty
            Owner property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        _p_data = self._push_and_get_doc_data({"source": None, "targets": []})
        # Visit properties
        self._visit(swan_obj.source, swan_obj, "source")
        for item in swan_obj.targets:
            self._visit(item, swan_obj, "targets")
        _doc = R.DBlock()
        _doc << "wire "
        _doc << _p_data["source"]
        _doc << " => "
        _doc << R.doc_list(*cast(List[R.DElt], _p_data["targets"]), sep=", ")

        _p_data["description"] = _doc
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, owner_property)


def swan_to_str(swan_obj: Union[Swan.SwanItem, None], normalize: bool = False) -> str:
    """
    Convert a Swan object to string.

    Parameters
    ----------
    swan_obj : swan_obj: Swan.SwanItem
        Swan construct to be converted.
    normalize : bool, optional
        Write each Swan declaration or all the same declarations on one line,
        by default False i.e. each Swan declaration per line.

    Returns
    -------
    str
        A Swan properties string according to its syntax description.
    """
    if swan_obj is None:
        return ""
    if isinstance(swan_obj, Swan.Pragma):
        return str(swan_obj)
    # use PPPrinter
    buffer = StringIO()
    printer = PPrinter(normalize=normalize)
    printer.print(buffer, swan_obj)
    res = buffer.getvalue()
    buffer.close()
    return res
