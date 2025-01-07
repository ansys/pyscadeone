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
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor
import ansys.scadeone.core.swan as S


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

    def __init__(self, normalize=True):
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

    def print(self, stream: IOBase, swan_obj: S.SwanItem, render: Optional[R.Renderer] = None):
        """
        Print a Swan object to the output stream

        Parameters
        ----------
        stream : IOBase
            A file or buffer to which the output will be written.
        swan_obj : S.Declaration
            A Swan object to print.
        render : Optional[R.Renderer], optional
            A renderer to use for printing, by default None.
            If None, a new renderer will be created from R.Renderer class.
        """

        # Visit Swan object to build document
        self.visit(swan_obj)
        # Write visited Swan code
        doc = R.Document()
        if swan_obj:
            if hasattr(swan_obj, "pprint_array"):
                doc << swan_obj.pprint_array[self.__own_property]
            else:
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

        # Normalized format
        if self._normalize:
            _doc = R.doc_list(*data[key], sep="@n")
        else:
            _doc = R.DBlock()
            _doc << prefix << " " << "@m" << R.doc_list(*data[key], sep="@n") << "@u" << "@n"
        # Update data stream for declaration property
        data[self.__own_property] = _doc

    @classmethod
    def _update_property(cls, owner: Any, swan_property: str, data: str):
        """
        Update owner's data stream via its property with a data given

        Parameters
        ----------
        owner : Any
            Owner of swan property
        swan_property : str
            Swan property name to know the visit context
        data : str
            Data given to update
        """

        if isinstance(owner.pprint_array[swan_property], list):
            owner.pprint_array[swan_property].append(data)
        else:
            owner.pprint_array[swan_property] = data

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
    def _format_list(pref: str, lst: List, end: Optional[str] = ";") -> R.DBlock:
        """
        Format each elem with adding a given separation at the end

        Parameters
        ----------
        pref: str
            A given prefix or keyword
        lst : List
            A given list
        end: Optional[str], optional
            A given separation, by default ";"

        Returns
        -------
        R.DBlock
            A document block
        """

        _decl = R.DBlock()
        _decl << pref
        _decl << "@n"
        _decl << R.doc_list(*[item << end for item in lst], sep="@n")
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

    def visit_AnonymousOperatorWithExpression(
        self,
        swan_obj: S.AnonymousOperatorWithExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Anonymous Operator With Expression visitor

        Parameters
        ----------
        swan_obj : S.AnonymousOperatorWithExpression
            Visited Swan object, it's a AnonymousOperatorWithExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
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
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ArrayProjection(
        self, swan_obj: S.ArrayProjection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Array Projection visitor

        Parameters
        ----------
        swan_obj : S.ArrayProjection
            Visited Swan object, it's a ArrayProjection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "index": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.index, swan_obj, "index")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << swan_obj.pprint_array["index"]
        )

    def visit_ArrayRepetition(
        self, swan_obj: S.ArrayRepetition, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Array Repetition visitor

        Parameters
        ----------
        swan_obj : S.ArrayRepetition
            Visited Swan object, it's a ArrayRepetition instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "size": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.size, swan_obj, "size")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << " ^ "
            << swan_obj.pprint_array["size"]
        )

    def visit_ArrayTypeExpression(
        self,
        swan_obj: S.ArrayTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Array Type Expression visitor

        Parameters
        ----------
        swan_obj : S.ArrayTypeExpression
            Visited Swan object, it's a ArrayTypeExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type": None, "size": None}

        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        self._visit(swan_obj.size, swan_obj, "size")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["type"]
            << " ^ "
            << swan_obj.pprint_array["size"]
        )

    def visit_AssumeSection(
        self, swan_obj: S.AssumeSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Assume Section visitor

        Parameters
        ----------
        swan_obj : S.AssumeSection
            Visited Swan object, it's a AssumeSection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"hypotheses": None}
        _hpt = []
        # Visit properties
        for item in swan_obj.hypotheses:
            self._visit(item, swan_obj, "hypotheses")
            _hpt.append(swan_obj.pprint_array["hypotheses"])
        owner.pprint_array[swan_property] = PPrinter._format_list("assume", _hpt)

    def visit_Bar(
        self, swan_obj: S.Bar, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Bar visitor

        Parameters
        ----------
        swan_obj : S.Bar
            Visited Swan object, it's a Bar instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operation": None}
        # Visit properties
        owner.pprint_array[swan_property] = R.DBlock()
        owner.pprint_array[swan_property] << "group"
        if swan_obj.operation:
            self._visit(swan_obj.operation, swan_obj, "operation")
            if swan_obj.operation != S.GroupOperation.NoOp:
                owner.pprint_array[swan_property] << " "
            owner.pprint_array[swan_property] << swan_obj.pprint_array["operation"]
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)

    def visit_BinaryExpr(
        self, swan_obj: S.BinaryExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Binary Expression visitor

        Parameters
        ----------
        swan_obj : S.BinaryExpr
            Visited Swan object, it's a BinaryExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "left": None, "right": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.left, swan_obj, "left")
        self._visit(swan_obj.right, swan_obj, "right")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["left"]
            << " "
            << swan_obj.pprint_array["operator"]
            << " "
            << swan_obj.pprint_array["right"]
        )

    def visit_BinaryOp(
        self, swan_obj: S.BinaryOp, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """
        Binary Operator visitor

        Parameters
        ----------
        swan_obj : S.BinaryOp
            Visited Swan object, it's a BinaryOp instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(S.BinaryOp.to_str(swan_obj))

    def visit_Block(
        self, swan_obj: S.Block, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Block visitor

        Parameters
        ----------
        swan_obj : S.Block
            Visited Swan object, it's a Block instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"instance": None, "instance_luid": None}
        # Visit properties
        self._visit(swan_obj.instance, swan_obj, "instance")

        _decl = R.DBlock()
        _decl << "block "
        _decl << swan_obj.pprint_array["instance"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)

    def visit_BoolPattern(
        self, swan_obj: S.BoolPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Bool Pattern visitor

        Parameters
        ----------
        swan_obj : S.BoolPattern
            Visited Swan object, it's a BoolPattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(str(swan_obj))

    def visit_BoolType(
        self, swan_obj: S.BoolType, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Bool Type visitor

        Parameters
        ----------
        swan_obj : S.BoolType
            Visited Swan object, it's a BoolType instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_CaseBranch(
        self, swan_obj: S.CaseBranch, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Case Branch visitor

        Parameters
        ----------
        swan_obj : S.CaseBranch
            Visited Swan object, it's a CaseBranch instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"pattern": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.pattern, swan_obj, "pattern")
        self._visit(swan_obj.expr, swan_obj, "expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "| "
            << swan_obj.pprint_array["pattern"]
            << ": "
            << swan_obj.pprint_array["expr"]
        )

    def visit_CaseExpr(
        self, swan_obj: S.CaseExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Case Expression visitor

        Parameters
        ----------
        swan_obj : S.CaseExpr
            Visited Swan object, it's a CaseExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "branches": None}
        _brc = []
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.branches:
            self._visit(item, swan_obj, "branches")
            _brc.append(swan_obj.pprint_array["branches"])
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "(case "
            << swan_obj.pprint_array["expr"]
            << " of "
            << R.doc_list(*_brc, sep="")
            << ")"
        )

    def visit_CharType(
        self, swan_obj: S.CharType, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Char Type visitor

        Parameters
        ----------
        swan_obj : S.CharType
            Visited Swan object, it's a CharType instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_CharPattern(
        self, swan_obj: S.CharPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Character Pattern visitor

        Parameters
        ----------
        swan_obj : S.CharPattern
            Visited Swan object, it's a CharPattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(str(swan_obj))

    def visit_ClockExpr(
        self, swan_obj: S.ClockExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Clock Expression visitor

        Parameters
        ----------
        swan_obj : S.ClockExpr
            Visited Swan object, it's a ClockExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "is_not": None, "pattern": None}

        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        if swan_obj.is_not:
            self.visit_builtin(swan_obj.is_not, swan_obj, "is_not")
        if swan_obj.pattern:
            self._visit(swan_obj.pattern, swan_obj, "pattern")
        _decl = R.DBlock()
        if swan_obj.pattern:
            _decl << "("
            _decl << swan_obj.pprint_array["id"]
            _decl << " match "
            _decl << swan_obj.pprint_array["pattern"]
            _decl << ")"
        elif swan_obj.is_not:
            _decl << "not "
            _decl << swan_obj.pprint_array["id"]
        else:
            _decl << swan_obj.pprint_array["id"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_Connection(
        self, swan_obj: S.Connection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Connection visitor

        Parameters
        ----------
        swan_obj : S.Connection
            Visited Swan object, it's a Connection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
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
                _decl << swan_obj.pprint_array["adaptation"]
        else:
            _decl << "()"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ConstDecl(
        self, swan_obj: S.ConstDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Pretty prints a constant declaration
        Syntax: const {{ const_decl ; }}
                const_decl ::= id : type_expr [[ = expr ]] | id = expr

        Parameters
        ----------
        swan_obj : S.ConstDecl
            Visited Swan object, it's a ConstantDecl instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "type": None, "value": None}
        # Visit parent class
        super().visit_ConstDecl(swan_obj, owner, swan_property)
        # Visit properties
        _decl = R.DBlock()
        if self._normalize or isinstance(owner, PPrinter):
            _decl << "const "
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.pprint_array["type"]:
            _decl << ": " << swan_obj.pprint_array["type"]
        if swan_obj.pprint_array["value"]:
            _decl << " = " << swan_obj.pprint_array["value"]
        _decl << ";"
        if self._normalize:
            _decl << "@n"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_ConstDeclarations(
        self,
        swan_obj: S.ConstDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Pretty prints a list of constant declarations

        Parameters
        ----------
        swan_obj : S.ConstDeclarations
            Visited Swan object, it's a ConstDeclarations instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"constants": []}
        # Visit parent class
        super().visit_ConstDeclarations(swan_obj, owner, swan_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "constants", "const")
        owner.pprint_array[swan_property] = swan_obj.pprint_array[self.__own_property]

    def visit_DefaultPattern(
        self, swan_obj: S.DefaultPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Default Pattern visitor

        Parameters
        ----------
        swan_obj : S.DefaultPattern
            Visited Swan object, it's a DefaultPattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << "default")

    def visit_DefBlock(
        self, swan_obj: S.DefBlock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Def Block visitor

        Parameters
        ----------
        swan_obj : S.DefBlock
            Visited Swan object, it's a DefBlock instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None}

        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        _decl = R.DBlock()
        _decl << "def "
        _decl << swan_obj.pprint_array["lhs"]
        if "locals" in swan_obj.pprint_array and swan_obj.pprint_array["locals"]:
            _decl << " where "
            _decl << "("
            _decl << swan_obj.pprint_array["locals"]
            _decl << ")"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)

    def visit_Diagram(
        self, swan_obj: S.Diagram, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Diagram visitor

        Parameters
        ----------
        swan_obj : S.Diagram
            Visited Swan object, it's a Diagram instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"objects": None}
        _ob = []
        # Visit properties
        for item in swan_obj.objects:
            self._visit(item, swan_obj, "objects")
            _ob.append(swan_obj.pprint_array["objects"])
        _decl = R.DBlock()
        _decl << "diagram"
        if _ob:
            _decl << "@n"
            _decl << R.doc_list(*[R.DBlock(R.text("(")) << itm << ")" for itm in _ob], sep="@n")
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        if isinstance(owner, PPrinter):
            del swan_obj.pprint_array

    def visit_DiagramObject(
        self, swan_obj: S.DiagramObject, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Diagram Object visitor

        Parameters
        ----------
        swan_obj : S.DiagramObject
            Visited Swan object, it's a DiagramObject instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lunum": None, "luid": None, "locals": None}
        _decl = R.DBlock()
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            _decl << swan_obj.pprint_array["lunum"]
            _decl << " "
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            _decl << swan_obj.pprint_array["luid"]
            _decl << " "
        _decl << owner.pprint_array[swan_property]
        if swan_obj.locals:
            _lc = []
            for item in swan_obj.locals:
                self._visit(item, swan_obj, "locals")
                _lc.append(swan_obj.pprint_array["locals"])
            if _lc:
                _decl << " where "
                _decl << R.doc_list(*[R.DBlock(R.text("(")) << itm << ")" for itm in _lc], sep="@n")
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_EmitSection(
        self, swan_obj: S.EmitSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Emit Section visitor

        Parameters
        ----------
        swan_obj : S.EmitSection
            Visited Swan object, it's a EmitSection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"emissions": None}
        _ems = []
        # Visit properties
        for item in swan_obj.emissions:
            self._visit(item, swan_obj, "emissions")
            _ems.append(swan_obj.pprint_array["emissions"])
        owner.pprint_array[swan_property] = PPrinter._format_list("emit", _ems)

    def visit_EmissionBody(
        self, swan_obj: S.EmissionBody, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Emission Body visitor

        Parameters
        ----------
        swan_obj : S.EmissionBody
            Visited Swan object, it's a EmissionBody instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"flows": None, "condition": None}
        _fls = []
        # Visit properties
        for item in swan_obj.flows:
            self._visit(item, swan_obj, "flows")
            _fls.append(swan_obj.pprint_array["flows"])
        if swan_obj.condition:
            self._visit(swan_obj.condition, swan_obj, "condition")
        _decl = R.DBlock()
        _decl << R.doc_list(*_fls, sep=", ")
        if swan_obj.condition:
            _decl << " if "
            _decl << swan_obj.pprint_array["condition"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_EnumTypeDefinition(
        self,
        swan_obj: S.EnumTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Enumeration Type Definition visitor

        Parameters
        ----------
        swan_obj : S.EnumTypeDefinition
            Visited Swan object, it's a EnumTypeDefinition instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        _items = [_it for _it in swan_obj.tags]
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "enum "
            << R.doc_list(*_items, sep=", ", start="{", last="}")
        )

    def visit_EquationLHS(
        self, swan_obj: S.EquationLHS, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Equation LHS visitor

        Parameters
        ----------
        swan_obj : S.EquationLHS
            Visited Swan object, it's a EquationLHS instance
        owner : Union[Any, None]
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
        owner.pprint_array[swan_property] = R.DBlock()
        if _lms:
            (owner.pprint_array[swan_property] << R.doc_list(*_lms, sep=", "))
            if swan_obj.is_partial_lhs:
                (owner.pprint_array[swan_property] << ", ..")
        else:
            (owner.pprint_array[swan_property] << "()")

    def visit_ExprBlock(
        self, swan_obj: S.ExprBlock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Expression Block visitor

        Parameters
        ----------
        swan_obj : S.ExprBlock
            Visited Swan object, it's a ExprBlock instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << "expr " << swan_obj.pprint_array["expr"])
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)

    def visit_ExprTypeDefinition(
        self,
        swan_obj: S.ExprTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Expression Type Definition visitor

        Parameters
        ----------
        swan_obj : S.ExprTypeDefinition
            Visited Swan object, it's a ExprTypeDefinition instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type": None}
        # Visit properties
        self._visit(swan_obj.type, swan_obj, "type")
        owner.pprint_array[swan_property] = swan_obj.pprint_array["type"]

    def visit_Float32Type(
        self, swan_obj: S.Float32Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Float32 Type visitor

        Parameters
        ----------
        swan_obj : S.Float32Type
            Visited Swan object, it's a Float32Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Float64Type(
        self, swan_obj: S.Float64Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Float64 Type visitor

        Parameters
        ----------
        swan_obj : S.Float64Type
            Visited Swan object, it's a Float64Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Forward(
        self, swan_obj: S.Forward, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward visitor

        Parameters
        ----------
        swan_obj : S.Forward
            Visited Swan object, it's a Forward instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "state": None,
            "dimensions": None,
            "body": None,
            "returns": None,
            "luid": None,
        }
        _dms = []
        _rtn = []
        # Visit properties
        self._visit(swan_obj.state, swan_obj, "state")
        for item in swan_obj.dimensions:
            self._visit(item, swan_obj, "dimensions")
            _dms.append(swan_obj.pprint_array["dimensions"])
        self._visit(swan_obj.body, swan_obj, "body")
        for item in swan_obj.returns:
            self._visit(item, swan_obj, "returns")
            _rtn.append(swan_obj.pprint_array["returns"])
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
        if _dms:
            _decl << R.DLineBreak(False)
            _decl << R.doc_list(*_dms, sep="@n")
        _decl << R.DLineBreak(False)
        _decl << swan_obj.pprint_array["body"]
        _decl << R.DLineBreak(False)
        _decl << "returns ("
        if _rtn:
            _decl << R.doc_list(*_rtn, sep=", ")
        _decl << ")"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_FormalProperty(
        self, swan_obj: S.FormalProperty, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward Property visitor

        Parameters
        ----------
        swan_obj : S.FormalProperty
            Visited Swan object, it's a FormalProperty instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"luid": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.luid, swan_obj, "luid")
        self._visit(swan_obj.expr, swan_obj, "expr")

        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["luid"]
            << ": "
            << swan_obj.pprint_array["expr"]
        )

    def visit_ForwardArrayClause(
        self,
        swan_obj: S.ForwardArrayClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Forward Array Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardArrayClause
            Visited Swan object, it's a ForwardArrayClause instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"return_clause": None}
        # Visit properties
        if isinstance(swan_obj.return_clause, S.ForwardItemClause):
            self._visit(swan_obj.return_clause, swan_obj, "return_clause")
        elif isinstance(swan_obj.return_clause, S.ForwardArrayClause):
            self._visit(swan_obj.return_clause, swan_obj, "return_clause")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << "[" << swan_obj.pprint_array["return_clause"] << "]")

    def visit_ForwardBody(
        self, swan_obj: S.ForwardBody, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward Body visitor

        Parameters
        ----------
        swan_obj : S.ForwardBody
            Visited Swan object, it's a ForwardBody instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"body": None, "unless_expr": None, "until_expr": None}
        _bdy = []
        # Visit properties
        for item in swan_obj.body:
            self._visit(item, swan_obj, "body")
            _bdy.append(swan_obj.pprint_array["body"])
        if swan_obj.unless_expr:
            self._visit(swan_obj.unless_expr, swan_obj, "unless_expr")
        if swan_obj.until_expr:
            self._visit(swan_obj.until_expr, swan_obj, "until_expr")
        _decl = R.DBlock()
        if swan_obj.unless_expr:
            _decl << "unless "
            _decl << swan_obj.pprint_array["unless_expr"]
            _decl << R.DLineBreak(False)
        if _bdy:
            _decl << R.doc_list(*_bdy, sep=R.DLineBreak(False))
        if swan_obj.until_expr:
            if _bdy:
                _decl << R.DLineBreak(False)
            _decl << "until "
            _decl << swan_obj.pprint_array["until_expr"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ForwardDim(
        self, swan_obj: S.ForwardDim, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward Dimension visitor

        Parameters
        ----------
        swan_obj : S.ForwardDim
            Visited Swan object, it's a ForwardDim instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "dim_id": None, "elems": None, "protected": None}
        _elm = []
        # Visit properties
        if swan_obj.expr:
            self._visit(swan_obj.expr, swan_obj, "expr")
        if swan_obj.dim_id:
            self._visit(swan_obj.dim_id, swan_obj, "dim_id")
        if swan_obj.elems:
            for item in swan_obj.elems:
                self._visit(item, swan_obj, "elems")
                _elm.append(swan_obj.pprint_array["elems"])
        if swan_obj.protected:
            # TO-DO: markup
            pass
        _decl = R.DBlock()
        _decl << "<<"
        _decl << swan_obj.pprint_array["expr"]
        _decl << ">>"
        if swan_obj.dim_id or swan_obj.elems:
            _decl << " with "
        if swan_obj.dim_id:
            _decl << "<<"
            _decl << swan_obj.pprint_array["dim_id"]
            _decl << ">> "
        if swan_obj.elems:
            _decl << R.doc_list(*_elm, sep=" ")
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ForwardElement(
        self, swan_obj: S.ForwardElement, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward Element visitor

        Parameters
        ----------
        swan_obj : S.ForwardElement
            Visited Swan object, it's a ForwardElement instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.lhs, swan_obj, "lhs")
        self._visit(swan_obj.expr, swan_obj, "expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["lhs"]
            << " = "
            << swan_obj.pprint_array["expr"]
            << ";"
        )

    def visit_ForwardItemClause(
        self,
        swan_obj: S.ForwardItemClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Forward Item Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardItemClause
            Visited Swan object, it's a ForwardItemClause instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "last_default": None}
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        if swan_obj.last_default:
            self._visit(swan_obj.last_default, swan_obj, "last_default")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.last_default:
            _decl << ": "
            _decl << swan_obj.pprint_array["last_default"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ForwardLastDefault(
        self,
        swan_obj: S.ForwardLastDefault,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Forward Last Default visitor

        Parameters
        ----------
        swan_obj : S.ForwardLastDefault
            Visited Swan object, it's a ForwardLastDefault instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"last": None, "default": None, "shared": None}
        # Visit properties
        if swan_obj.last:
            self._visit(swan_obj.last, swan_obj, "last")
        if swan_obj.default:
            self._visit(swan_obj.default, swan_obj, "default")
        if swan_obj.shared:
            self._visit(swan_obj.shared, swan_obj, "shared")
        _decl = R.DBlock()
        if swan_obj.shared:
            _decl << "last = default = "
            _decl << swan_obj.pprint_array["shared"]
        else:
            if swan_obj.last:
                _decl << "last = "
                _decl << swan_obj.pprint_array["last"]
            if swan_obj.last and swan_obj.default:
                _decl << " "
            if swan_obj.default:
                _decl << "default = "
                _decl << swan_obj.pprint_array["default"]

        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ForwardLHS(
        self, swan_obj: S.ForwardLHS, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward LHS visitor

        Parameters
        ----------
        swan_obj : S.ForwardLHS
            Visited Swan object, it's a ForwardLHS instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lhs": None}
        # Visit properties
        if isinstance(swan_obj.lhs, S.Identifier):
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        elif isinstance(swan_obj.lhs, S.ForwardLHS):
            self._visit(swan_obj.lhs, swan_obj, "lhs")
        _decl = R.DBlock()
        if swan_obj.is_id:
            _decl << swan_obj.pprint_array["lhs"]
        else:
            _decl << "["
            _decl << swan_obj.pprint_array["lhs"]
            _decl << "]"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ForwardReturnArrayClause(
        self,
        swan_obj: S.ForwardReturnArrayClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Forward Return Array Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardReturnArrayClause
            Visited Swan object, it's a ForwardReturnArrayClause instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"array_clause": None, "return_id": None}
        # Visit properties
        self._visit(swan_obj.array_clause, swan_obj, "array_clause")
        if swan_obj.return_id:
            self._visit(swan_obj.return_id, swan_obj, "return_id")
        _decl = R.DBlock()
        if swan_obj.return_id:
            _decl << swan_obj.pprint_array["return_id"]
            _decl << " = "
        _decl << swan_obj.pprint_array["array_clause"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_ForwardReturnItemClause(
        self,
        swan_obj: S.ForwardReturnItemClause,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Forward Return Item Clause visitor

        Parameters
        ----------
        swan_obj : S.ForwardReturnItemClause
            Visited Swan object, it's a ForwardReturnItemClause instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"item_clause": None}
        # Visit properties
        self._visit(swan_obj.item_clause, swan_obj, "item_clause")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << swan_obj.pprint_array["item_clause"])

    def visit_ForwardState(
        self, swan_obj: S.ForwardState, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Forward State visitor

        Parameters
        ----------
        swan_obj : S.ForwardState
            Visited Swan object, it's a ForwardState instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(S.ForwardState.to_str(swan_obj))

    def visit_FunctionalUpdate(
        self, swan_obj: S.FunctionalUpdate, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Functional Update visitor

        Parameters
        ----------
        swan_obj : S.FunctionalUpdate
            Visited Swan object, it's a FunctionalUpdate instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "modifiers": None}
        _mdp = []
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.modifiers:
            self._visit(item, swan_obj, "modifiers")
            _mdp.append(swan_obj.pprint_array["modifiers"])
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "("
            << swan_obj.pprint_array["expr"]
            << " with "
            << R.doc_list(*_mdp, sep="; ")
            << ")"
        )

    def visit_Group(
        self, swan_obj: S.Group, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group visitor

        Parameters
        ----------
        swan_obj : S.Group
            Visited Swan object, it's a Group instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"items": None}
        _itm = []
        # Visit properties
        for item in swan_obj.items:
            self._visit(item, swan_obj, "items")
            _itm.append(swan_obj.pprint_array["items"])
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << R.doc_list(*_itm, sep=", "))

    def visit_GroupAdaptation(
        self, swan_obj: S.GroupAdaptation, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group Adaption visitor

        Parameters
        ----------
        swan_obj : S.GroupAdaptation
            Visited Swan object, it's a GroupAdaptation instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"renamings": None}
        _rnm = []
        # Visit properties
        for item in swan_obj.renamings:
            self._visit(item, swan_obj, "renamings")
            _rnm.append(swan_obj.pprint_array["renamings"])
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << " .(" << R.doc_list(*_rnm, sep=", ") << ")")

    def visit_GroupConstructor(
        self, swan_obj: S.GroupConstructor, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group Constructor visitor

        Parameters
        ----------
        swan_obj : S.GroupConstructor
            Visited Swan object, it's a GroupConstructor instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << "(" << swan_obj.pprint_array["group"] << ")")

    def visit_GroupDecl(
        self, swan_obj: S.GroupDecl, owner: Union[Any, None], swan_property: Union[str, None]
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
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "type": None}
        # Visit parent class
        super().visit_GroupDecl(swan_obj, owner, swan_property)
        # Visit properties
        _decl = R.DBlock()
        if self._normalize or isinstance(owner, PPrinter):
            _decl << "group "
        _type = PPrinter._doc_or_list(swan_obj.pprint_array["type"])
        _decl << swan_obj.pprint_array["id"] << " = " << _type << ";"
        if self._normalize:
            _decl << "@n"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_GroupDeclarations(
        self,
        swan_obj: S.GroupDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Pretty prints a list of group declarations

        Parameters
        ----------
        swan_obj : S.GroupDeclarations
            Visited Swan object, it's a GroupDeclarations instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"groups": []}
        # Visit parent class
        super().visit_GroupDeclarations(swan_obj, owner, swan_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "groups", "group")
        owner.pprint_array[swan_property] = swan_obj.pprint_array[self.__own_property]

    def visit_GroupItem(
        self, swan_obj: S.GroupItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group Item visitor

        Parameters
        ----------
        swan_obj : S.GroupItem
            Visited Swan object, it's a GroupItem instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "label": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        if swan_obj.label:
            self._visit(swan_obj.label, swan_obj, "label")
        _decl = R.DBlock()
        if swan_obj.label:
            _decl << swan_obj.pprint_array["label"]
            _decl << ": "
        _decl << swan_obj.pprint_array["expr"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_GroupOperation(
        self, swan_obj: S.GroupOperation, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group Operation visitor

        Parameters
        ----------
        swan_obj : S.GroupOperation
            Visited Swan object, it's a GroupOperation instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        if swan_obj == S.GroupOperation.Normalize:
            owner.pprint_array[swan_property] = R.text("()")
        elif swan_obj == S.GroupOperation.NoOp:
            owner.pprint_array[swan_property] = R.text("")
        else:
            owner.pprint_array[swan_property] = R.text(S.GroupOperation.to_str(swan_obj))

    def visit_GroupRenaming(
        self, swan_obj: S.GroupRenaming, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group Renaming visitor

        Parameters
        ----------
        swan_obj : S.GroupRenaming
            Visited Swan object, it's a GroupRenaming instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"source": None, "renaming": None, "is_shortcut": None}
        # Visit properties
        if isinstance(swan_obj.source, S.Identifier):
            self._visit(swan_obj.source, swan_obj, "source")
        elif isinstance(swan_obj.source, S.Literal):
            self._visit(swan_obj.source, swan_obj, "source")

        if swan_obj.renaming:
            self._visit(swan_obj.renaming, swan_obj, "renaming")

        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["source"]
        if swan_obj.renaming:
            _decl << ": "
            _decl << swan_obj.pprint_array["renaming"]
        elif swan_obj.is_shortcut:
            _decl << ":"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_GroupProjection(
        self, swan_obj: S.GroupProjection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Group Projection visitor

        Parameters
        ----------
        swan_obj : S.GroupProjection
            Visited Swan object, it's a GroupProjection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "adaptation": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.adaptation, swan_obj, "adaptation")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << swan_obj.pprint_array["adaptation"]
        )

    def visit_GroupTypeExpressionList(
        self,
        swan_obj: S.GroupTypeExpressionList,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Group type expression list visitor

        Parameters
        ----------
        swan_obj : S.GroupTypeExpressionList
            Visited Swan object, it's a GroupTypeExpressionList instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"positional": None, "named": None}
        _lst_items = []
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        for item in swan_obj.positional:
            self._visit(item, swan_obj, "positional")
            if swan_obj.pprint_array["positional"]:
                _lst_items.append(swan_obj.pprint_array["positional"])
        for item in swan_obj.named:
            self._visit(item, swan_obj, "named")
            if swan_obj.pprint_array["named"]:
                _lst_items.append(swan_obj.pprint_array["named"])
        owner.pprint_array[swan_property] = _lst_items

    def visit_GuaranteeSection(
        self, swan_obj: S.GuaranteeSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Guarantee Section visitor

        Parameters
        ----------
        swan_obj : S.GuaranteeSection
            Visited Swan object, it's a GuaranteeSection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"guarantees": None}
        _grt = []
        # Visit properties
        for item in swan_obj.guarantees:
            self._visit(item, swan_obj, "guarantees")
            _grt.append(swan_obj.pprint_array["guarantees"])
        owner.pprint_array[swan_property] = PPrinter._format_list("guarantee", _grt)

    def visit_Identifier(
        self, swan_obj: S.Identifier, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Identifier visitor

        Parameters
        ----------
        swan_obj : S.Identifier
            Visited Swan object, it's a Identifier instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        if swan_obj.pragmas:
            # Init data buffer
            swan_obj.pprint_array = {"pragmas": None}
            _pgm = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgm.append(swan_obj.pprint_array["pragmas"])
            _decl = R.DBlock()
            if _pgm:
                _decl << R.doc_list(*_pgm, sep=" ") << " "
            _decl << R.text(swan_obj.value)
            # Update property
            PPrinter._update_property(owner, swan_property, _decl)
        else:
            owner.pprint_array[swan_property] = R.text(swan_obj.value)

    def visit_IfteExpr(
        self, swan_obj: S.IfteExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        If Then Else Expression visitor

        Parameters
        ----------
        swan_obj : S.IfteExpr
            Visited Swan object, it's a IfteExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"cond_expr": None, "then_expr": None, "else_expr": None}
        # Visit properties
        self._visit(swan_obj.cond_expr, swan_obj, "cond_expr")
        self._visit(swan_obj.then_expr, swan_obj, "then_expr")
        self._visit(swan_obj.else_expr, swan_obj, "else_expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "if "
            << swan_obj.pprint_array["cond_expr"]
            << " then "
            << swan_obj.pprint_array["then_expr"]
            << " else "
            << swan_obj.pprint_array["else_expr"]
        )

    def visit_Int8Type(
        self, swan_obj: S.Int8Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Int8 Type visitor

        Parameters
        ----------
        swan_obj : S.Int8Type
            Visited Swan object, it's a Int8Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Int16Type(
        self, swan_obj: S.Int16Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Int16 Type visitor

        Parameters
        ----------
        swan_obj : S.Int16Type
            Visited Swan object, it's a Int16Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Int32Type(
        self, swan_obj: S.Int32Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Int32 Type visitor

        Parameters
        ----------
        swan_obj : S.Int32Type
            Visited Swan object, it's a Int32Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Int64Type(
        self, swan_obj: S.Int64Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Int64 Type visitor

        Parameters
        ----------
        swan_obj : S.Int64Type
            Visited Swan object, it's a Int64Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_IntPattern(
        self, swan_obj: S.IntPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Integer Pattern visitor

        Parameters
        ----------
        swan_obj : S.IntPattern
            Visited Swan object, it's a IntPattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(str(swan_obj))

    def visit_Iterator(
        self, swan_obj: S.Iterator, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Iterator visitor

        Parameters
        ----------
        swan_obj : S.Iterator
            Visited Swan object, it's a Iterator instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"kind": None, "operator": None}
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")
        self._visit(swan_obj.operator, swan_obj, "operator")
        # f"{IteratorKind.to_str(self.kind)} {self.operator}"
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["kind"]
            << " "
            << swan_obj.pprint_array["operator"]
        )

    def visit_IteratorKind(
        self, swan_obj: S.IteratorKind, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """
        Iterator Kind visitor

        Parameters
        ----------
        swan_obj : S.IteratorKind
            Visited Swan object, it's a IteratorKind instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(S.IteratorKind.to_str(swan_obj))

    def visit_LabelOrIndex(
        self, swan_obj: S.LabelOrIndex, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Label Or Index visitor

        Parameters
        ----------
        swan_obj : S.LabelOrIndex
            Visited Swan object, it's a LabelOrIndex instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"value": None}
        # Visit properties
        if isinstance(swan_obj.value, S.Identifier):
            self._visit(swan_obj.value, swan_obj, "value")
        elif isinstance(swan_obj.value, S.Expression):
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
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_LastExpr(
        self, swan_obj: S.LastExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Last Expression visitor

        Parameters
        ----------
        swan_obj : S.LastExpr
            Visited Swan object, it's a LastExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None}
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << "last " << swan_obj.pprint_array["id"])

    def visit_LetSection(
        self, swan_obj: S.LetSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Let Section visitor

        Parameters
        ----------
        swan_obj : S.LetSection
            Visited Swan object, it's a LetSection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"equations": None}
        _eqt = []
        # Visit properties
        for item in swan_obj.equations:
            self._visit(item, swan_obj, "equations")
            _eqt.append(swan_obj.pprint_array["equations"])
        owner.pprint_array[swan_property] = PPrinter._format_list("let", _eqt, "")

    def visit_LHSItem(
        self, swan_obj: S.LHSItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        LHS Item visitor

        Parameters
        ----------
        swan_obj : S.LHSItem
            Visited Swan object, it's a LHSItem instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None}
        # Visit properties
        if isinstance(swan_obj.id, S.Identifier):
            self._visit(swan_obj.id, swan_obj, "id")
        elif SwanVisitor._is_builtin(swan_obj.id):
            self.visit_builtin(swan_obj.id, swan_obj, "id")
        if swan_obj.pprint_array["id"]:
            owner.pprint_array[swan_property] = swan_obj.pprint_array["id"]
        else:
            owner.pprint_array[swan_property] = "_"

    def visit_Literal(
        self, swan_obj: S.Literal, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Literal visitor

        Parameters
        ----------
        swan_obj : S.Literal
            Visited Swan object, it's a Literal instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(swan_obj.value)

    def visit_Luid(
        self, swan_obj: S.Luid, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Luid visitor

        Parameters
        ----------
        swan_obj : S.Luid
            Visited Swan object, it's a Luid instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(str(swan_obj))

    def visit_Lunum(
        self, swan_obj: S.Lunum, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Lunum visitor

        Parameters
        ----------
        swan_obj : S.Lunum
            Visited Swan object, it's a Lunum instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(str(swan_obj))

    def visit_Merge(
        self, swan_obj: S.Merge, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Merge visitor

        Parameters
        ----------
        swan_obj : S.Merge
            Visited Swan object, it's a Merge instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"params": None}
        _prm = []
        # Visit properties
        for item in swan_obj.params:
            self._visit(item, swan_obj, "params")
            _prm.append(swan_obj.pprint_array["params"])
        if swan_obj.params:
            owner.pprint_array[swan_property] = R.DBlock()
            (
                owner.pprint_array[swan_property]
                << "merge "
                << R.doc_list(*[R.DBlock(R.text("(")) << itm << ")" for itm in _prm], sep=" ")
            )
        else:
            # TO-DO: empty list is invalid - markup
            pass

    def visit_Modifier(
        self, swan_obj: S.Modifier, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Modifier visitor

        Parameters
        ----------
        swan_obj : S.Modifier
            Visited Swan object, it's a Modifier instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"modifier": None, "expr": None}
        owner.pprint_array[swan_property] = R.DBlock()
        # Visit properties
        if isinstance(swan_obj.modifier, list):
            _mdp = []
            for item in swan_obj.modifier:
                self._visit(item, swan_obj, "modifier")
                _mdp.append(swan_obj.pprint_array["modifier"])
            (owner.pprint_array[swan_property] << R.doc_list(*_mdp, sep=""))
        elif SwanVisitor._is_builtin(swan_obj.modifier):
            self.visit_builtin(swan_obj.modifier, swan_obj, "modifier")
            if swan_obj.is_protected:
                (owner.pprint_array[swan_property] << swan_obj.pprint_array["modifier"])

        self._visit(swan_obj.expr, swan_obj, "expr")
        (owner.pprint_array[swan_property] << " = " << swan_obj.pprint_array["expr"])

    def visit_Module(
        self, swan_obj: S.Module, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Module visitor

        Parameters
        ----------
        swan_obj : S.Module
            Visited Swan object, it's a Module instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"use_directives": None, "declarations": None}
        # Visit properties
        _decl = R.DBlock()
        if swan_obj.use_directives:
            _ud = []
            for item in swan_obj.use_directives:
                self._visit(item, swan_obj, "use_directives")
                _ud.append(swan_obj.pprint_array["use_directives"])
            if _ud:
                _decl << R.doc_list(*_ud, sep=R.DLineBreak(False))
                _decl << R.DLineBreak(False)
        if swan_obj.declarations:
            _dcl = []
            for item in swan_obj.declarations:
                self._visit(item, swan_obj, "declarations")
                if isinstance(swan_obj.pprint_array["declarations"], list):
                    _dc = []
                    for _dl in swan_obj.pprint_array["declarations"]:
                        _dc.append(_dl)
                    if _dc:
                        _decl << R.doc_list(*_dc, sep=R.DLineBreak(False))
                else:
                    _dcl.append(swan_obj.pprint_array["declarations"])
            if _dcl:
                _decl << R.doc_list(*_dcl, sep=R.DLineBreak(False))
                _decl << R.DLineBreak(False)
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        if isinstance(owner, PPrinter):
            del swan_obj.pprint_array

    def visit_ModuleBody(
        self, swan_obj: S.ModuleBody, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Module Body visitor

        Parameters
        ----------
        swan_obj : S.ModuleBody
            Visited Swan object, it's a ModuleBody instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_Module(swan_obj, owner, swan_property)

    def visit_ModuleInterface(
        self, swan_obj: S.ModuleInterface, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Module Interface visitor

        Parameters
        ----------
        swan_obj : S.ModuleInterface
            Visited Swan object, it's a ModuleInterface instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_Module(swan_obj, owner, swan_property)

    def visit_NamedGroupTypeExpression(
        self,
        swan_obj: S.NamedGroupTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Named Group Type Expression visitor

        Parameters
        ----------
        swan_obj : S.NamedGroupTypeExpression
            Visited Swan object, it's a NamedGroupTypeExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"label": None, "type": None}
        # Visit base class(es)
        self.visit_GroupTypeExpression(swan_obj, owner, swan_property)
        # Visit properties
        self._visit(swan_obj.label, swan_obj, "label")
        self._visit(swan_obj.type, swan_obj, "type")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["label"]
            << ": "
            << PPrinter._doc_or_list(swan_obj.pprint_array["type"])
        )
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_NaryOp(
        self, swan_obj: S.NaryOp, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """
        NaryOp visitor

        Parameters
        ----------
        swan_obj : S.NaryOp
            Visited Swan object, it's a NaryOp instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        owner.pprint_array[swan_property] = R.text(S.NaryOp.to_str(swan_obj))

    def visit_NAryOperator(
        self, swan_obj: S.NAryOperator, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        N-Ary Operator visitor

        Parameters
        ----------
        swan_obj : S.NAryOperator
            Visited Swan object, it's a NAryOperator instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        owner.pprint_array[swan_property] = swan_obj.pprint_array["operator"]

    def visit_NumericCast(
        self, swan_obj: S.NumericCast, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Numeric Casting visitor

        Parameters
        ----------
        swan_obj : S.NumericCast
            Visited Swan object, it's a NumericCast instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "type": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.type, swan_obj, "type")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "("
            << swan_obj.pprint_array["expr"]
            << " :> "
            << swan_obj.pprint_array["type"]
            << ")"
        )

    def visit_Operator(
        self, swan_obj: S.Operator, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Operator visitor

        Parameters
        ----------
        swan_obj : S.Operator
            Visited Swan object, it's a Operator instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        # Visit base class(es)
        self.visit_Signature(swan_obj, owner, swan_property)
        _decl = R.DBlock()
        _decl << owner.pprint_array[swan_property]
        _decl << "@n"
        # Init data buffer
        swan_obj.pprint_array = {"body": None}
        # Visit properties
        if isinstance(swan_obj.body, S.Scope):
            self._visit(swan_obj.body, swan_obj, "body")
            _decl << swan_obj.pprint_array["body"]
        elif isinstance(swan_obj.body, S.Equation):
            self._visit(swan_obj.body, swan_obj, "body")
            _decl << "  " << swan_obj.pprint_array["body"]
        else:
            _decl << ";"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_OperatorBase(
        self, swan_obj: S.OperatorBase, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Operator Base visitor

        Parameters
        ----------
        swan_obj : S.OperatorBase
            Visited Swan object, it's a OperatorBase instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"sizes": None}
        _sz = []
        # Visit properties
        for item in swan_obj.sizes:
            self._visit(item, swan_obj, "sizes")
            _sz.append(swan_obj.pprint_array["sizes"])
        _decl = R.DBlock()
        _decl << owner.pprint_array[swan_property]
        if _sz:
            _decl << " <<"
            _decl << R.doc_list(*_sz, sep=", ")
            _decl << ">>"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_PathIdentifier(
        self, swan_obj: S.PathIdentifier, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Path Identifier visitor

        Parameters
        ----------
        swan_obj : S.PathIdentifier
            Visited Swan object, it's a PathIdentifier instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit properties
        owner.pprint_array[swan_property] = R.DBlock()
        if isinstance(swan_obj.path_id, list):
            _lst = []
            for item in swan_obj.path_id:
                self._visit(item, swan_obj, "path_id")
                if swan_obj.pprint_array["path_id"]:
                    _lst.append(swan_obj.pprint_array["path_id"])
            (owner.pprint_array[swan_property] << R.doc_list(*_lst, sep="::"))
        elif self._is_builtin(swan_obj.path_id):
            self.visit_builtin(swan_obj.path_id1, swan_obj, "path_id")
            if swan_obj.pprint_array["path_id"]:
                (owner.pprint_array[swan_property] << swan_obj.pprint_array["path_id"])

    def visit_PathIdExpr(
        self, swan_obj: S.PathIdExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Path Identifier Expression visitor

        Parameters
        ----------
        swan_obj : S.PathIdExpr
            Visited Swan object, it's a PathIdExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit base class(es)
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << swan_obj.pprint_array["path_id"])

    def visit_PathIdOpCall(
        self, swan_obj: S.PathIdOpCall, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        PathId Operator Call visitor

        Parameters
        ----------
        swan_obj : S.PathIdOpCall
            Visited Swan object, it's a PathIdOpCall instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        owner.pprint_array[swan_property] = swan_obj.pprint_array["path_id"]
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, swan_property)

    def visit_PathIdPattern(
        self, swan_obj: S.PathIdPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        PathId Pattern visitor

        Parameters
        ----------
        swan_obj : S.PathIdPattern
            Visited Swan object, it's a PathIdPattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None}
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << swan_obj.pprint_array["path_id"])

    def visit_PortExpr(
        self, swan_obj: S.PortExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Port Expression visitor

        Parameters
        ----------
        swan_obj : S.PortExpr
            Visited Swan object, it's a PortExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"lunum": None, "luid": None}
        # Visit properties
        if swan_obj.lunum:
            self._visit(swan_obj.lunum, swan_obj, "lunum")
            owner.pprint_array[swan_property] = swan_obj.pprint_array["lunum"]
        if swan_obj.is_self:
            owner.pprint_array[swan_property] = R.text("self")
        if swan_obj.luid:
            self._visit(swan_obj.luid, swan_obj, "luid")
            owner.pprint_array[swan_property] = swan_obj.pprint_array["luid"]

    def visit_Pragma(
        self, swan_obj: S.Pragma, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Pragma visitor

        Parameters
        ----------
        swan_obj : S.Pragma
            Visited Swan object, it's a Pragma instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(swan_obj.pragma)

    def visit_PragmaBase(
        self, swan_obj: S.PragmaBase, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        PragmaBase visitor

        Parameters
        ----------
        swan_obj : S.PragmaBase
            Visited Swan object, it's a PragmaBase instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        # Visit properties
        if swan_obj.pragmas:
            swan_obj.pprint_array = {"pragmas": None}
            _pgs = []
            for item in swan_obj.pragmas:
                self._visit(item, swan_obj, "pragmas")
                _pgs.append(swan_obj.pprint_array["pragmas"])
            if _pgs:
                owner.pprint_array[swan_property] = R.doc_list(*_pgs, sep=" ")

    def visit_PredefinedType(
        self, swan_obj: S.PredefinedType, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Predefined Type visitor

        Parameters
        ----------
        swan_obj : S.PredefinedType
            Visited Swan object, it's a PredefinedType instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(swan_obj.name)

    def visit_PrefixOperatorExpression(
        self,
        swan_obj: S.PrefixOperatorExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Prefix Operator Expression visitor

        Parameters
        ----------
        swan_obj : S.PrefixOperatorExpression
            Visited Swan object, it's a PrefixOperatorExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"op_expr": None}
        # Visit properties
        self._visit(swan_obj.op_expr, swan_obj, "op_expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << "(" << swan_obj.pprint_array["op_expr"] << ")")
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, swan_property)

    def visit_PrefixPrimitive(
        self, swan_obj: S.PrefixPrimitive, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Prefix Primitive visitor

        Parameters
        ----------
        swan_obj : S.PrefixPrimitive
            Visited Swan object, it's a PrefixPrimitive instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"kind": None}
        # Visit properties
        self._visit(swan_obj.kind, swan_obj, "kind")
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["kind"]
        _decl << owner.pprint_array[swan_property]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Visit base class(es)
        self.visit_OperatorBase(swan_obj, owner, swan_property)

    def visit_PrefixPrimitiveKind(
        self,
        swan_obj: S.PrefixPrimitiveKind,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ):
        """
        Prefix Primitive Kind visitor

        Parameters
        ----------
        swan_obj : S.PrefixPrimitiveKind
            Visited Swan object, it's a PrefixPrimitiveKind instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(S.PrefixPrimitiveKind.to_str(swan_obj))

    def visit_ProjectionWithDefault(
        self,
        swan_obj: S.ProjectionWithDefault,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Project With Default visitor

        Parameters
        ----------
        swan_obj : S.ProjectionWithDefault
            Visited Swan object, it's a ProjectionWithDefault instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "indices": None, "default": None}
        _indices = []
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        for item in swan_obj.indices:
            self._visit(item, swan_obj, "indices")
            _indices.append(swan_obj.pprint_array["indices"])
        self._visit(swan_obj.default, swan_obj, "default")

        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "("
            << swan_obj.pprint_array["expr"]
            << " . "
            << R.doc_list(*_indices, sep="")
            << " default "
            << swan_obj.pprint_array["default"]
            << ")"
        )

    def visit_ProtectedDecl(
        self, swan_obj: S.ProtectedDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Protected Declaration visitor

        Parameters
        ----------
        swan_obj : S.ProtectedDecl
            Visited Swan object, it's a ProtectedDecl instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        _decl = R.DBlock()
        if swan_obj.markup:
            _decl << "{"
            _decl << R.DText(swan_obj.markup)
            _decl << "%"
        _decl << R.DText(swan_obj.data)
        if swan_obj.markup:
            _decl << "%"
            _decl << R.DText(swan_obj.markup)
            _decl << "}"
        owner.pprint_array[swan_property] = _decl

    def visit_ProtectedExpr(
        self, swan_obj: S.ProtectedExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Protected Expression visitor

        Parameters
        ----------
        swan_obj : S.ProtectedExpr
            Visited Swan object, it's a ProtectedExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_ProtectedItem(
        self, swan_obj: S.ProtectedItem, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Protected Item visitor

        Parameters
        ----------
        swan_obj : S.ProtectedItem
            Visited Swan object, it's a ProtectedItem instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit properties
        owner.pprint_array[swan_property] = R.text(str(swan_obj))

    def visit_ProtectedOpExpr(
        self, swan_obj: S.ProtectedOpExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Protected Operator Expression visitor

        Parameters
        ----------
        swan_obj : S.ProtectedOpExpr
            Visited Swan object, it's a ProtectedOpExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_ProtectedItem(swan_obj, owner, swan_property)

    def visit_Signature(
        self, swan_obj: S.Signature, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Signature visitor

        Parameters
        ----------
        swan_obj : S.Signature
            Visited Swan object, it's a Signature instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
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
        _ot = []
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        _decl = R.DBlock()
        if swan_obj.has_inline:
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
        _decl << " ("
        if _in:
            _decl << R.doc_list(*_in, sep="; ")
            _decl << ";"
        _decl << ")"
        _decl << R.DLineBreak(False)
        _decl << "returns "
        for item in swan_obj.outputs:
            self._visit(item, swan_obj, "outputs")
            _ot.append(swan_obj.pprint_array["outputs"])
        _decl << "("
        if _ot:
            _decl << R.doc_list(*_ot, sep="; ")
            _decl << ";"
        _decl << ")"
        if swan_obj.constraints:
            _ct = []
            for item in swan_obj.constraints:
                self._visit(item, swan_obj, "constraints")
                _ct.append(swan_obj.pprint_array["constraints"])
            if _ct:
                _decl << " " << R.doc_list(*_ct, sep=" ")
        if swan_obj.specialization:
            self._visit(swan_obj.specialization, swan_obj, "specialization")
            if swan_obj.pprint_array["specialization"]:
                _decl << " specialize "
                _decl << swan_obj.pprint_array["specialization"]
        if isinstance(owner, (S.ModuleInterface, PPrinter)):
            _decl << ";"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_SizedTypeExpression(
        self,
        swan_obj: S.SizedTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Sized Type Expression visitor

        Parameters
        ----------
        swan_obj : S.SizedTypeExpression
            Visited Swan object, it's a SizedTypeExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
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
        _decl << "<< "
        _decl << swan_obj.pprint_array["size"]
        _decl << " >>"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_SectionBlock(
        self, swan_obj: S.SectionBlock, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Section Block visitor

        Parameters
        ----------
        swan_obj : S.SectionBlock
            Visited Swan object, it's a SectionBlock instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"section": None}
        # Visit properties
        self._visit(swan_obj.section, swan_obj, "section")
        owner.pprint_array[swan_property] = swan_obj.pprint_array["section"]
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)

    def visit_SensorDecl(
        self, swan_obj: S.SensorDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Pretty prints a sensor declaration
        Syntax: sensor_decl ::= id : type_expr

        Parameters
        ----------
        swan_obj : S.SensorDecl
            Visited Swan object, it's a SensorDecl instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "type": None,
        }
        # Visit parent class
        super().visit_SensorDecl(swan_obj, owner, swan_property)
        _decl = R.DBlock()
        if self._normalize or isinstance(owner, PPrinter):
            _decl << "sensor "
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.pprint_array["type"]:
            _decl << ": " << swan_obj.pprint_array["type"]
        _decl << ";"
        if self._normalize:
            _decl << "@n"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_SensorDeclarations(
        self,
        swan_obj: S.SensorDeclarations,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Pretty prints a list of sensor declarations

        Parameters
        ----------
        swan_obj : S.SensorDeclarations
            Visited Swan object, it's a SensorDeclarations instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"sensors": []}
        # Visit parent class
        super().visit_SensorDeclarations(swan_obj, owner, swan_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "sensors", "sensor")
        owner.pprint_array[swan_property] = swan_obj.pprint_array[self.__own_property]

    def visit_Slice(
        self, swan_obj: S.Slice, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Slice visitor

        Parameters
        ----------
        swan_obj : S.Slice
            Visited Swan object, it's a Slice instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "start": None, "end": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.start, swan_obj, "start")
        self._visit(swan_obj.end, swan_obj, "end")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << "["
            << swan_obj.pprint_array["start"]
            << " .. "
            << swan_obj.pprint_array["end"]
            << "]"
        )

    def visit_StructConstructor(
        self,
        swan_obj: S.StructConstructor,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Struct Constructor visitor

        Parameters
        ----------
        swan_obj : S.StructConstructor
            Visited Swan object, it's a StructConstructor instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None, "type": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        if swan_obj.type:
            self._visit(swan_obj.type, swan_obj, "type")
        _decl = R.DBlock()
        _decl << "{"
        _decl << swan_obj.pprint_array["group"]
        _decl << "}"
        if swan_obj.type:
            _decl << " : "
            _decl << swan_obj.pprint_array["type"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_StructDestructor(
        self, swan_obj: S.StructDestructor, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Struct Destructor visitor

        Parameters
        ----------
        swan_obj : S.StructDestructor
            Visited Swan object, it's a StructDestructor instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"group": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.group, swan_obj, "group")
        self._visit(swan_obj.expr, swan_obj, "expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["group"]
            << " group ("
            << swan_obj.pprint_array["expr"]
            << ")"
        )

    def visit_StructField(
        self, swan_obj: S.StructField, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Struct Field visitor

        Parameters
        ----------
        swan_obj : S.StructField
            Visited Swan object, it's a StructField instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"id": None, "type": None}
        # Visit properties
        self._visit(swan_obj.id, swan_obj, "id")
        self._visit(swan_obj.type, swan_obj, "type")
        _decl = R.DBlock() << swan_obj.pprint_array["id"] << ": " << swan_obj.pprint_array["type"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_StructProjection(
        self, swan_obj: S.StructProjection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Struct Projection visitor

        Parameters
        ----------
        swan_obj : S.StructProjection
            Visited Swan object, it's a StructProjection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "label": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.label, swan_obj, "label")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << swan_obj.pprint_array["label"]
        )

    def visit_StructTypeDefinition(
        self,
        swan_obj: S.StructTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Struct Type Definition visitor

        Parameters
        ----------
        swan_obj : S.StructTypeDefinition
            Visited Swan object, it's a StructTypeDefinition instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"fields": []}
        # Visit properties
        for item in swan_obj.fields:
            self._visit(item, swan_obj, "fields")

        _decl = R.DBlock() << "{" << R.doc_list(*swan_obj.pprint_array["fields"], sep=", ") << "}"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_Transpose(
        self, swan_obj: S.Transpose, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Transpose visitor

        Parameters
        ----------
        swan_obj : S.Transpose
            Visited Swan object, it's a Transpose instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
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
        PPrinter._update_property(owner, swan_property, _decl)
        # Visit base class(es)
        self.visit_PrefixPrimitive(swan_obj, owner, swan_property)

    def visit_TypeConstraint(
        self, swan_obj: S.TypeConstraint, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Type Constraint visitor

        Parameters
        ----------
        swan_obj : S.TypeConstraint
            Visited Swan object, it's a TypeConstraint instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"type_vars": None, "kind": None}
        # Visit properties
        _decl = R.DBlock()
        _decl << "where "
        if isinstance(swan_obj.type_vars, list):
            _tv = []
            for item in swan_obj.type_vars:
                self._visit(item, swan_obj, "type_vars")
                _tv.append(swan_obj.pprint_array["type_vars"])
            _decl << R.doc_list(*_tv, sep=", ")
        elif SwanVisitor._is_builtin(swan_obj.type_vars):
            self.visit_builtin(swan_obj.type_vars, swan_obj, "type_vars")
            _decl << swan_obj.pprint_array["type_vars"]
        _decl << " " << R.DText(swan_obj.kind.name.lower())
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_TypeDecl(
        self, swan_obj: S.TypeDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Pretty prints a type declaration

        Parameters
        ----------
        swan_obj : S.TypeDecl
            Visited Swan object, it's a TypeDecl instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {
            "id": None,
            "definition": None,
        }
        # Visit parent class
        super().visit_TypeDecl(swan_obj, owner, swan_property)
        # Visit properties
        _decl = R.DBlock()
        if self._normalize or isinstance(owner, PPrinter):
            _decl << "type "
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.pprint_array["definition"]:
            _decl << " = " << swan_obj.pprint_array["definition"]

        _decl << ";"
        if self._normalize:
            _decl << "@n"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_TypeDeclarations(
        self, swan_obj: S.TypeDeclarations, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Pretty prints a list of type declarations

        Parameters
        ----------
        swan_obj : S.TypeDeclarations
            Visited Swan object, it's a TypeDeclarations instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"types": []}
        # Visit parent class
        super().visit_TypeDeclarations(swan_obj, owner, swan_property)
        # Update data buffer
        self._decl_formatting(swan_obj.pprint_array, "types", "type")
        owner.pprint_array[swan_property] = swan_obj.pprint_array[self.__own_property]

    def visit_TypeGroupTypeExpression(
        self,
        swan_obj: S.TypeGroupTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Group Type Expression visitor

        Parameters
        ----------
        swan_obj : S.TypeGroupTypeExpression
            Visited Swan object, it's a TypeGroupTypeExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        self.visit_PredefinedType(swan_obj.type, owner, swan_property)

    def visit_TypeReferenceExpression(
        self,
        swan_obj: S.TypeReferenceExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Type Reference Expression visitor

        Parameters
        ----------
        swan_obj : S.TypeReferenceExpression
            Visited Swan object, it's a TypeReferenceExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(swan_obj.alias.as_string)

    def visit_Uint8Type(
        self, swan_obj: S.Uint8Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Uint8 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint8Type
            Visited Swan object, it's a Uint8Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Uint16Type(
        self, swan_obj: S.Uint16Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Uint16 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint16Type
            Visited Swan object, it's a Uint16Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Uint32Type(
        self, swan_obj: S.Uint32Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Uint32 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint32Type
            Visited Swan object, it's a Uint32Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_Uint64Type(
        self, swan_obj: S.Uint64Type, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Uint64 Type visitor

        Parameters
        ----------
        swan_obj : S.Uint64Type
            Visited Swan object, it's a Uint64Type instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Visit base class(es)
        self.visit_PredefinedType(swan_obj, owner, swan_property)

    def visit_UnaryExpr(
        self, swan_obj: S.UnaryExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Unary Expression visitor

        Parameters
        ----------
        swan_obj : S.UnaryExpr
            Visited Swan object, it's a UnaryExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"operator": None, "expr": None}
        # Visit properties
        self._visit(swan_obj.operator, swan_obj, "operator")
        self._visit(swan_obj.expr, swan_obj, "expr")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["operator"]
            << " "
            << swan_obj.pprint_array["expr"]
        )

    def visit_UnaryOp(
        self, swan_obj: S.UnaryOp, owner: Union[Any, None], swan_property: Union[str, None]
    ):
        """
        Unary Operator visitor

        Parameters
        ----------
        swan_obj : S.UnaryOp
            Visited Swan object, it's a UnaryOp instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.text(S.UnaryOp.to_str(swan_obj))

    def visit_UnderscorePattern(
        self,
        swan_obj: S.UnderscorePattern,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Underscore Pattern visitor

        Parameters
        ----------
        swan_obj : S.UnderscorePattern
            Visited Swan object, it's a UnderscorePattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        owner.pprint_array[swan_property] = R.DText("_")

    def visit_UseDirective(
        self, swan_obj: S.UseDirective, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Use Directive visitor

        Parameters
        ----------
        swan_obj : S.UseDirective
            Visited Swan object, it's a UseDirective instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path": None, "alias": None}
        # Visit properties
        self._visit(swan_obj.path, swan_obj, "path")
        if swan_obj.alias:
            self._visit(swan_obj.alias, swan_obj, "alias")
        _decl = R.DBlock()
        _decl << "use "
        _decl << swan_obj.pprint_array["path"]
        if swan_obj.alias:
            _decl << " as "
            _decl << swan_obj.pprint_array["alias"]
        _decl << ";"
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Delete data buffer
        del swan_obj.pprint_array

    def visit_VarDecl(
        self, swan_obj: S.VarDecl, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Variable Declaration visitor

        Parameters
        ----------
        swan_obj : S.VarDecl
            Visited Swan object, it's a VarDecl instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
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
        if swan_obj.type:
            self._visit(swan_obj.type, swan_obj, "type")
        if swan_obj.when:
            self._visit(swan_obj.when, swan_obj, "when")
        if swan_obj.default:
            self._visit(swan_obj.default, swan_obj, "default")
        if swan_obj.last:
            self._visit(swan_obj.last, swan_obj, "last")
        _decl = R.DBlock()
        if swan_obj.is_clock:
            _decl << "clock "
        if swan_obj.is_probe:
            _decl << "#pragma cg probe #end "
        _decl << swan_obj.pprint_array["id"]
        if swan_obj.type:
            _decl << ": "
            _decl << swan_obj.pprint_array["type"]
        if swan_obj.when:
            _decl << " when "
            _decl << swan_obj.pprint_array["when"]
        if swan_obj.default:
            _decl << " default = "
            _decl << swan_obj.pprint_array["default"]
        if swan_obj.last:
            _decl << " last = "
            _decl << swan_obj.pprint_array["last"]
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_VariableTypeExpression(
        self,
        swan_obj: S.VariableTypeExpression,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Variable Type Expression visitor

        Parameters
        ----------
        swan_obj : S.VariableTypeExpression
            Visited Swan object, it's a VariableTypeExpression instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"name": None}
        # Visit properties
        self._visit(swan_obj.name, swan_obj, "name")
        owner.pprint_array[swan_property] = swan_obj.pprint_array["name"]

    def visit_VariantPattern(
        self, swan_obj: S.VariantPattern, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Variant Pattern visitor

        Parameters
        ----------
        swan_obj : S.VariantPattern
            Visited Swan object, it's a VariantPattern instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"path_id": None, "captured": None}
        # Visit properties
        self._visit(swan_obj.path_id, swan_obj, "path_id")
        if swan_obj.captured:
            self._visit(swan_obj.captured, swan_obj, "captured")

        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["path_id"]
        if swan_obj.captured:
            _decl << swan_obj.pprint_array["captured"]
        elif swan_obj.underscore:
            _decl << " _"
        else:
            _decl << " {}"

        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_VariantComponent(
        self,
        swan_obj: S.VariantSimple,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        VariantComponent Type Definition visitor.

        This is a helper function for variant type definition
        derived classes.

        Parameters
        ----------
        swan_obj : S.VariantComponent
            Visited Swan object, it's a VariantComponent derived instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        self._visit(swan_obj.tag, swan_obj, "tag")

    def visit_VariantSimple(
        self,
        swan_obj: S.VariantSimple,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Variant type only defined by a tag visitor

        Parameters
        ----------
        swan_obj : S.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        swan_obj.pprint_array = {"tag": None}
        self.visit_VariantComponent(swan_obj, owner, swan_property)
        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["tag"] << " {}"

        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_VariantTypeExpr(
        self,
        swan_obj: S.VariantTypeExpr,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Variant type with expression visitor

        Parameters
        ----------
        swan_obj : S.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        swan_obj.pprint_array = {"tag": None, "type": None}
        self.visit_VariantComponent(swan_obj, owner, swan_property)
        self._visit(swan_obj.type, swan_obj, "type")

        _decl = R.DBlock()
        _decl << swan_obj.pprint_array["tag"] << " { " << swan_obj.pprint_array["type"] << " }"

        # Update property
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_VariantStruct(
        self,
        swan_obj: S.VariantStruct,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Variant type as structure visitor

        Parameters
        ----------
        swan_obj : S.VariantSimple
            Visited Swan object, it's a VariantSimple instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        swan_obj.pprint_array = {"tag": None, "fields": []}
        self.visit_VariantComponent(swan_obj, owner, swan_property)
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
        PPrinter._update_property(owner, swan_property, _decl)

    def visit_VariantTypeDefinition(
        self,
        swan_obj: S.VariantTypeDefinition,
        owner: Union[Any, None],
        swan_property: Union[str, None],
    ) -> None:
        """
        Variant Type Definition visitor

        Parameters
        ----------
        swan_obj : S.VariantTypeDefinition
            Visited Swan object, it's a VariantTypeDefinition instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"tags": None}
        _tags = []
        # Visit properties
        for itm in swan_obj.tags:
            self._visit(itm, swan_obj, "tags")
            _tags.append(swan_obj.pprint_array["tags"])
        owner.pprint_array[swan_property] = R.DBlock()
        (owner.pprint_array[swan_property] << R.doc_list(*_tags, sep=" | "))

    def visit_VariantValue(
        self, swan_obj: S.VariantValue, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Variant Value visitor

        Parameters
        ----------
        swan_obj : S.VariantValue
            Visited Swan object, it's a VariantValue instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"tag": None, "group": None}
        # Visit properties
        self._visit(swan_obj.tag, swan_obj, "tag")
        self._visit(swan_obj.group, swan_obj, "group")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["tag"]
            << " {"
            << swan_obj.pprint_array["group"]
            << "}"
        )

    def visit_VarSection(
        self, swan_obj: S.VarSection, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Variable Section visitor

        Parameters
        ----------
        swan_obj : S.VarSection
            Visited Swan object, it's a VarSection instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"var_decls": None}
        _var = []
        # Visit properties
        for _id, item in enumerate(swan_obj.var_decls):
            self._visit(item, swan_obj, "var_decls")
            _var.append(swan_obj.pprint_array["var_decls"])
        owner.pprint_array[swan_property] = PPrinter._format_list("var", _var)

    def visit_WhenClockExpr(
        self, swan_obj: S.WhenClockExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        When Clock Expression visitor

        Parameters
        ----------
        swan_obj : S.WhenClockExpr
            Visited Swan object, it's a WhenClockExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "clock": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.clock, swan_obj, "clock")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << " when "
            << swan_obj.pprint_array["clock"]
        )

    def visit_WhenMatchExpr(
        self, swan_obj: S.WhenMatchExpr, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        When Match Expression visitor

        Parameters
        ----------
        swan_obj : S.WhenMatchExpr
            Visited Swan object, it's a WhenMatchExpr instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"expr": None, "when": None}
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, "expr")
        self._visit(swan_obj.when, swan_obj, "when")
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << swan_obj.pprint_array["expr"]
            << " when match "
            << swan_obj.pprint_array["when"]
        )

    def visit_Window(
        self, swan_obj: S.Window, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Window visitor

        Parameters
        ----------
        swan_obj : S.Window
            Visited Swan object, it's a Window instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """

        # Init data buffer
        swan_obj.pprint_array = {"size": None, "init": None, "params": None}
        # Visit properties
        self._visit(swan_obj.size, swan_obj, "size")
        self._visit(swan_obj.init, swan_obj, "init")
        self._visit(swan_obj.params, swan_obj, "params")
        # f"window <<{self.size}>> ({self.init}) ({self.params})"
        owner.pprint_array[swan_property] = R.DBlock()
        (
            owner.pprint_array[swan_property]
            << "window "
            << "<<"
            << swan_obj.pprint_array["size"]
            << ">> "
            << "("
            << swan_obj.pprint_array["init"]
            << ") "
            << "("
            << swan_obj.pprint_array["params"]
            << ")"
        )

    def visit_Wire(
        self, swan_obj: S.Wire, owner: Union[Any, None], swan_property: Union[str, None]
    ) -> None:
        """
        Wire visitor

        Parameters
        ----------
        swan_obj : S.Wire
            Visited Swan object, it's a Wire instance
        owner : Union[Any, None]
            Owner of swan property, 'None' for the root visited object
        swan_property : Union[str, None]
            Swan property name to know the visit context, 'None' for the root visited object
        """
        # Init data buffer
        swan_obj.pprint_array = {"source": None, "targets": None}
        _tg = []
        # Visit properties
        self._visit(swan_obj.source, swan_obj, "source")
        for item in swan_obj.targets:
            self._visit(item, swan_obj, "targets")
            _tg.append(swan_obj.pprint_array["targets"])
        _decl = R.DBlock()
        _decl << "wire "
        _decl << swan_obj.pprint_array["source"]
        _decl << " => "
        _decl << R.doc_list(*_tg, sep=", ")
        # Update property
        PPrinter._update_property(owner, swan_property, _decl)
        # Visit base class(es)
        self.visit_DiagramObject(swan_obj, owner, swan_property)


def swan_to_str(swan_obj: S.SwanItem, normalize: bool = False) -> str:
    """
    Convert a visited Swan object to string

    Parameters
    ----------
    swan_obj : swan_obj: S.SwanItem
        A visited Swan object, it's a SwanItem instance.
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
