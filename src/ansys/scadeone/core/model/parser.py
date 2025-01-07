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

from abc import ABC, abstractmethod
from typing import Union
from typing_extensions import Self

from ansys.scadeone.core.common.storage import SwanStorage
import ansys.scadeone.core.swan as S


class Parser(ABC):
    """The parser base class as a proxy to the F# methods implemented
    by the F# parser.
    """

    # Current parser in used. Set by derived class
    _CurrentParser = None

    @classmethod
    def get_current_parser(cls) -> Self:
        return cls._CurrentParser

    @classmethod
    def set_current_parser(cls, parser: Self):
        cls._CurrentParser = parser

    # Source of parsing
    _SwanSource = None

    @classmethod
    def get_source(cls) -> SwanStorage:
        return cls._SwanSource

    @classmethod
    def set_source(cls, swan: SwanStorage) -> SwanStorage:
        cls._SwanSource = swan

    @abstractmethod
    def module_body(self, source: SwanStorage) -> S.ModuleBody:
        """Parse a Swan module from a SwanStorage object

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanStorage
            Swan module (.swan)

        Returns
        -------
        ModuleBody:
            Instance of a module body
        """
        pass

    @abstractmethod
    def module_interface(self, source: SwanStorage) -> S.ModuleInterface:
        """Parse a Swan interface from a SwanStorage object.

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanStorage
            Swan interface (.swani)

        Returns
        -------
        ModuleInterface
            Instance of a module interface.
        """
        pass

    @abstractmethod
    def declaration(self, source: SwanStorage) -> S.Declaration:
        """Parse a Swan declaration:
          type, const, sensor, group, use, operator (signature or with body).

        Parameters
        ----------
        source : SwanStorage
            Single Swan declaration

        Returns
        -------
        Declaration
            Instance Declaration object
        """
        pass

    @abstractmethod
    def equation(self, source: SwanStorage) -> S.equations:
        """Parse a Swan equation.

        Parameters
        ----------
        source : SwanStorage
            Swan equation text

        Returns
        -------
        Equation
            Instance of Equation object
        """
        pass

    @abstractmethod
    def expression(self, source: SwanStorage) -> S.Expression:
        """Parse a Swan expression

        Parameters
        ----------
        source : SwanStorage
            Swan expression text

        Returns
        -------
        Expression
            Instance of an expression object
        """

    @abstractmethod
    def scope_section(self, source: SwanStorage) -> S.ScopeSection:
        """Parse a Swan scope section

        Parameters
        ----------
        source : str
            Swan scope section text

        Returns
        -------
        ScopeSection
            Instance of a scope section object
        """
        pass

    @abstractmethod
    def op_expr(self, source: SwanStorage) -> S.OperatorExpression:
        """Parse a Swan operator expression

        Parameters
        ----------
        source : SwanStorage
            Swan code for operator expression

        Returns
        -------
        OperatorExpression
            Instance of the operator expression object
        """
        pass

    @abstractmethod
    def operator_block(self, source: SwanStorage) -> Union[S.OperatorBase, S.OperatorExpression]:
        """Parse a Swan operator block

        *operator_block* ::= *operator* | *op_expr*

        Parameters
        ----------
        source : SwanStorage
            Swan code for operator block

        Returns
        -------
        Union[S.Operator, S.OperatorExpression]
            Instance of the *operator* or *op_expr*
        """
        pass

    @abstractmethod
    def operator(self, source: SwanStorage) -> S.Operator:
        """Parse a Swan operator

         Parameters
        ----------
        source : SwanStorage
            Swan operator text

        Returns
        -------
        S.Operator
            Instance of the operator
        """
        pass
