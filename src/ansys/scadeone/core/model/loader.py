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

"""
This module contains the :py:class:`Parser` which is a proxy to the Scade One F# parser.
The _Parser_ class offers methods to parse a complete Swan code (interface or module),
or a declaration, or an expression.

It relies on the `ansys.scadeone.core.model.dotnet` and `ansys.scadeone.model.pyofast` modules
to interface with the dotnet DLLs and to transform F# data structure into the
`ansys.scadeone.swan` python classes.
"""

import logging
from typing import Union

# dotnet configuration
import ansys.scadeone.core.model.dotnet  # noqa

# pylint: disable-next=import-error
from ANSYS.SONE.Core.Toolkit.Logging import ILogger  # type:ignore

# pylint: disable-next=import-error
from ANSYS.SONE.Infrastructure.Services.Serialization.BNF.Parsing import (  # type:ignore
    ParserTools,
    Reader,
)

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.storage import SwanStorage

import ansys.scadeone.core.swan as S

from .parser import Parser
from .pyofast import (
    declarationOfAst,
    equationOfAst,
    expressionOfAst,
    interfaceOfAst,
    moduleOfAst,
    operatorBlockOfAst,
    operatorExprOfAst,
    operatorOfAst,
    scopeSectionOfAst,
)

SwanVersion = ParserTools.SwanVersion
SwanTestVersion = ParserTools.SwanTestVersion


class ParserLogger(ILogger):
    """Logger class for the parser. An instance of the
    class is given to the F# parser to get the logging information
    in Python world.

    The class only implements the methods from ILogger that may be called
    from the parser.

    Parameters
    ----------
    ILogger : ILogger
        C# interface
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    @property
    def logger(self):
        return self._logger

    # https://stackoverflow.com/questions/49736531/implement-a-c-sharp-interface-in-python-for-net
    __namespace__ = "MyPythonLogger"

    def _log(self, category, message, log_fn):
        log_fn(f"{category}: {message}")

    # pylint: disable=invalid-name
    def Info(self, category, message):
        self._log(category, message, self.logger.info)

    def Warning(self, category, message):
        self._log(category, message, self.logger.warning)

    def Error(self, category, message):
        self._log(category, message, self.logger.error)

    def Exception(self, category, message):
        self._log(category, message, self.logger.exception)

    def Debug(self, category, message):
        self._log(category, message, self.logger.debug)


class SwanParser(Parser):
    """The parser class is a proxy to the F# methods implemented
    by the parser.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = ParserLogger(logger)

    def _parse(self, rule_fn, swan: SwanStorage):
        """Call F# parser with a given rule

        Parameters
        ----------
        rule_fn : Callable
            Parser rule function
        swan : SwanStorage
            Swan code to parse

        Returns
        -------
        tuple
            Parser value

        Raises
        ------
        ScadeOneException
            _description_
        ScadeOneException
            _description_
        """
        # save current parser for pyofast methods
        Parser.set_current_parser(self)
        Parser.set_source(swan)

        try:
            result = rule_fn(swan.source, swan.content(), self._logger)
        except Reader.ParseError as e:
            raise ScadeOneException(f"Parser: {e.Message}")
        except Exception as e:
            raise ScadeOneException(f"Internal: {e}")
        return result

    def module_body(self, source: SwanStorage) -> S.ModuleBody:
        """Parse a Swan module from a SwanStorage object.

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanStorage
            Swan module (.swan)

        Returns
        -------
        ModuleBody
            Instance of ModuleBody.
        """
        source.check_swan_version()
        result = self._parse(Reader.parse_body, source)
        return moduleOfAst(source.name, result)

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
            Instance of ModuleInterface.
        """
        source.check_swan_version()
        result = self._parse(Reader.parse_interface, source)
        return interfaceOfAst(source.name, result)

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
            Corresponding declaration object
        """
        ast = self._parse(Reader.parse_declaration, source)
        return declarationOfAst(ast)

    def equation(self, source: SwanStorage) -> S.Equation:
        """Parse a Swan equation.

        Parameters
        ----------
        source : SwanStorage
            Swan equation text

        Returns
        -------
        Equation
            Corresponding Equation object
        """
        ast = self._parse(Reader.parse_equation, source)
        return equationOfAst(ast)

    def expression(self, source: SwanStorage) -> S.expressions:
        """Parse a Swan expression

        Parameters
        ----------
        source : SwanStorage
            Swan expression text

        Returns
        -------
        Expression
            Corresponding expression object
        """
        ast = self._parse(Reader.parse_expr, source)
        return expressionOfAst(ast)

    def scope_section(self, source: SwanStorage) -> S.ScopeSection:
        """Parse a Swan scope section

        Parameters
        ----------
        source : str
            Swan scope section text

        Returns
        -------
        ScopeSection
            Corresponding scope section object
        """
        ast = self._parse(Reader.parse_scope_section, source)
        return scopeSectionOfAst(ast)

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
        ast = self._parse(Reader.parse_op_expr, source)
        return operatorExprOfAst(ast)

    def operator_block(self, source: SwanStorage) -> Union[S.OperatorBase, S.OperatorExpression]:
        """Parse a Swan operator block

        *operator_block* ::= *operator* | *op_expr*

        Parameters
        ----------
        source : SwanStorage
            Swan code for operator block

        Returns
        -------
        Union[S.OperatorBase, S.OperatorExpression]
            Instance of the *operator* or *op_expr*
        """
        ast = self._parse(Reader.parse_operator_block, source)
        return operatorBlockOfAst(ast)

    def operator(self, source: SwanStorage) -> S.Operator:
        """Parse a Swan user operator

         Parameters
        ----------
        source : SwanStorage
            Swan user operator text

        Returns
        -------
        S.Operator
            Instance of the user operator
        """
        ast = self._parse(Reader.parse_user_operator, source)
        return operatorOfAst(ast)
