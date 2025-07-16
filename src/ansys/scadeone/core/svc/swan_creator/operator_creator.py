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

from abc import ABC
from typing import TYPE_CHECKING, List, Optional, Union, cast

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.storage import SwanString

if TYPE_CHECKING:
    import ansys.scadeone.core.swan as swan


class OperatorFactory:
    _instance = None

    def __init__(self) -> None:
        from ansys.scadeone.core.model.loader import SwanParser

        self._parser = SwanParser(LOGGER)

    def __new__(cls, *args, **kwargs) -> "OperatorFactory":
        if not cls._instance:
            cls._instance = super(OperatorFactory, cls).__new__(cls)
        return cls._instance

    def create_variable(
        self,
        name: Optional[str] = None,
        var_type: Union[str, "swan.Declaration"] = None,
        is_clock: Optional[bool] = False,
        is_probe: Optional[bool] = False,
        when: Optional[str] = None,
        default: Optional[str] = None,
        last: Optional[str] = None,
        declaration: Optional[str] = None,
        is_input: Optional[bool] = None,
        module: Optional["swan.Module"] = None,
    ) -> "swan.VarDecl":
        """Create a variable.
        A variable can be defined by name, type, ... or by a text declaration."""
        from ansys.scadeone.core.swan import (
            Declaration,
            Identifier,
            Signature,
            VarDecl,
            PathIdentifier,
        )
        from ansys.scadeone.core.model import Model

        if (not name or not var_type) and not declaration:
            raise ScadeOneException(
                "Invalid variable parameters: declaration or name and type are required"
            )
        if isinstance(var_type, Declaration):
            if module is None:
                raise ScadeOneException("Module is required for OperatorFactor.create_variable()")
            type_path: PathIdentifier = Model.get_path_in_module(var_type, module)
            var_type = type_path.as_string
        if name and var_type:
            id = Identifier(name)
            if not id.is_valid:
                raise ScadeOneException(f"Invalid variable name: {name}")
            declaration = f"{name}: {var_type}"
            if when:
                declaration += f" when {when}"
            if default:
                declaration += f" default = {default}"
            if last:
                declaration += f" last = {last}"
        if not declaration:
            raise ScadeOneException("Invalid variable declaration")
        if is_input is False:
            swan_code = f"function temp_op(i0: int32) returns ({declaration});"
        else:
            swan_code = f"function temp_op({declaration}) returns (o0: int32);"
        op_str = SwanString(swan_code, "new_op")
        op = cast(Signature, self._parser.operator_decl(op_str))
        if not op:
            raise ScadeOneException("Invalid operator declaration")
        if is_input is False:
            var = cast(VarDecl, op.outputs[0])
        else:
            var = cast(VarDecl, op.inputs[0])
        var._is_clock = is_clock
        var._is_probe = is_probe
        return var

    @staticmethod
    def create_signature(
        name: Union[List["swan.Identifier"], str],
        is_node: bool = True,
        is_inline: bool = False,
    ) -> "swan.Signature":
        """Create a signature."""
        from ansys.scadeone.core.swan import Identifier, Signature

        id = Identifier(name)
        if not id.is_valid:
            raise ScadeOneException(f"Invalid module name: {name}")
        return Signature(id, is_inline, is_node, [], [])

    @staticmethod
    def create_operator(
        name: Union[List["swan.Identifier"], str],
        is_node: bool = True,
        is_inline: bool = False,
    ) -> "swan.Operator":
        """Create an operator."""
        from ansys.scadeone.core.swan import Identifier, Operator

        id = Identifier(name)  # noqa
        if not id.is_valid:
            raise ScadeOneException(f"Invalid module name: {name}")
        return Operator(id, is_inline, is_node, [], [])


class OperatorAdder:
    @staticmethod
    def add_input(operator: "swan.Signature", variable: "swan.Variable") -> None:
        """Add an input to the operator."""
        variable._is_input = True
        operator.inputs.append(variable)
        variable._owner = operator

    @staticmethod
    def add_output(operator: "swan.Signature", variable: "swan.Variable") -> None:
        """Add an output to the operator."""
        variable._is_output = True
        operator.outputs.append(variable)
        variable._owner = operator


class SignatureCreator(ABC):
    def _add_variable(
        self,
        name: Optional[str] = None,
        var_type: Union[str, "swan.Declaration"] = None,
        is_clock: Optional[bool] = False,
        is_probe: Optional[bool] = False,
        when: Optional[str] = None,
        default: Optional[str] = None,
        last: Optional[str] = None,
        declaration: Optional[str] = None,
        is_input: Optional[bool] = None,
    ) -> "swan.VarDecl":
        """Add an input to the operator.
        Input can be defined by name, type, ... or by a text declaration.

        Parameters
        ----------
        name: str
            Variable name.
        var_type: str or Declaration
            Variable type.
            It could be a text declaration or a Declaration object.
        is_clock: bool
            Clock variable.
        is_probe: bool
            Probe variable.
        when: str
            When condition.
        default: str
            Default value.
        last: str
            Last value.
        declaration: str
            Text declaration.

        Returns
        -------
        VarDecl
            Variable object.
        """
        from ansys.scadeone.core.swan.operators import OperatorSignatureBase

        if not isinstance(self, OperatorSignatureBase):
            raise ScadeOneException("SignatureCreator: expecting Operator or Signature object")
        var = OperatorFactory().create_variable(
            name=name,
            var_type=var_type,
            is_clock=is_clock,
            is_probe=is_probe,
            when=when,
            default=default,
            last=last,
            declaration=declaration,
            is_input=is_input,
            module=None if isinstance(var_type, str) else self.module,
        )
        return var

    def add_input(
        self,
        name: Optional[str] = None,
        input_type: Union[str, "swan.Declaration"] = None,
        is_clock: Optional[bool] = False,
        is_probe: Optional[bool] = False,
        when: Optional[str] = None,
        default: Optional[str] = None,
        last: Optional[str] = None,
        declaration: Optional[str] = None,
    ) -> "swan.VarDecl":
        """Add an input to the operator.
        Input can be defined by name, type, ... or by a text declaration.

        Parameters
        ----------
        name: str
            Input name.
        input type: str or Declaration
            Input type.
            It could be a text declaration or a Declaration object.
        is_clock: bool
            Clock variable.
        is_probe: bool
            Probe variable.
        when: str
            When condition.
        default: str
            Default value.
        last: str
            Last value.
        declaration: str
            Text declaration.

        Returns
        -------
        VarDecl
            Variable object.
        """
        var = self._add_variable(
            name=name,
            var_type=input_type,
            is_clock=is_clock,
            is_probe=is_probe,
            when=when,
            default=default,
            last=last,
            declaration=declaration,
            is_input=True,
        )
        OperatorAdder.add_input(self, var)
        return var

    def add_output(
        self,
        name: Optional[str] = None,
        output_type: Union[str, "swan.Declaration"] = None,
        is_clock: Optional[bool] = False,
        is_probe: Optional[bool] = False,
        when: Optional[str] = None,
        default: Optional[str] = None,
        last: Optional[str] = None,
        declaration: Optional[str] = None,
    ) -> "swan.VarDecl":
        """Add an output to the operator signature.
        Output can be defined by name, type, ... or by a text declaration.

        Parameters
        ----------
        name: str
            Variable name.
        output_type: str or Declaration
            Output type.
            It could be a text declaration or a Declaration object.
        is_clock: bool
            Clock variable.
        is_probe: bool
            Probe variable.
        when: str
            When condition.
        default: str
            Default value.
        last: str
            Last value.
        declaration: str
            Textual declaration.

        Returns
        -------
        VarDecl
            Variable object.
        """
        var = self._add_variable(
            name=name,
            var_type=output_type,
            is_clock=is_clock,
            is_probe=is_probe,
            when=when,
            default=default,
            last=last,
            declaration=declaration,
            is_input=False,
        )
        OperatorAdder.add_output(self, var)
        return var


class OperatorCreator(SignatureCreator):
    def add_diagram(self) -> "swan.Diagram":
        """Add a diagram to the operator.

        Returns
        -------
        Diagram
            Diagram object.
        """
        from ansys.scadeone.core.swan import Diagram, Operator, Scope

        if not isinstance(self, Operator):
            raise ScadeOneException("OperatorCreator must be used with an Operator object")
        diag = Diagram()
        if not self.body or not self.body.sections:
            scope = Scope([diag])
            scope.owner = self
            self._body = scope
            return diag
        self._body._sections.append(diag)
        return diag
