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

from typing import TYPE_CHECKING, Optional, Union, cast
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.svc.swan_creator.operator_creator import OperatorCreator
from ansys.scadeone.core.svc.swan_creator.diagram_creator import DiagramFactory


if TYPE_CHECKING:
    from ansys.scadeone.core import swan


class TestHarnessDiagramFactory(DiagramFactory):
    """Factory class for test harness diagram."""

    @staticmethod
    def create_data_source(instance: "swan.Identifier") -> "swan.Block":
        """
        Create a data source for the test harness.

        Parameters
        ----------
        instance: Identifier
            Identifier instance to be used as a data source.

        Returns
        -------
        swan.Block
            Block object.
        """

        from ansys.scadeone.core.swan import DataSource, Block, OperatorExpressionInstance

        source = DataSource(instance)
        op_expr = cast("swan.OperatorExpression", source)
        pref_op = OperatorExpressionInstance(op_expr, [])
        return Block(pref_op)

    @staticmethod
    def create_oracle(instance: "swan.Identifier") -> "swan.Block":
        """
        Create a data oracle for the test harness.

        Parameters
        ----------
        instance: Identifier
            Identifier instance to be used as an oracle.

        Returns
        -------
        swan.Block
            Block object.
        """
        from ansys.scadeone.core.swan import Oracle, Block, OperatorExpressionInstance

        source = Oracle(instance)
        op_expr = cast("swan.OperatorExpression", source)
        pref_op = OperatorExpressionInstance(op_expr, [])
        return Block(pref_op)

    @staticmethod
    def create_set_sensor(
        diagram: "swan.Diagram", instance: "swan.SensorDecl"
    ) -> "swan.SetSensorBlock":
        """
        Create a set sensor block for the test harness.

        Parameters
        ----------
        diagram: Diagram
            Diagram where the block will be added.
        instance: SensorDecl
            Sensor instance. A **use** directive may be required in the *diagram*'s module to
            resolve the operator module.

        Returns
        -------
        swan.SetSensorBlock
            Set sensor block object.
        """

        from ansys.scadeone.core.model import Model
        from ansys.scadeone.core.swan import SetSensorBlock

        if instance.module is None:
            raise ScadeOneException(f"Sensor {instance.get_full_path()} does not have a module.")
        if diagram.module is None:
            raise ScadeOneException("Diagram does not have a module.")
        path_id = Model.get_path_in_module(instance, diagram.module)
        return SetSensorBlock(path_id)


class TestHarnessDiagramCreator(OperatorCreator):
    """Test harness diagram creator class."""

    def add_input(
        self,
        name: Optional[str] = None,
        input_type: Union[str, "swan.Declaration"] = None,
        is_probe: bool = False,
        default: Optional[str] = None,
        last: Optional[str] = None,
        declaration: Optional[str] = None,
    ) -> "swan.VarDecl":
        raise ScadeOneException("Test harness does not support adding inputs directly.")

    def add_output(
        self,
        name: Optional[str] = None,
        output_type: Union[str, "swan.Declaration"] = None,
        is_clock: bool = False,
        is_probe: bool = False,
        when: Optional[str] = None,
        default: Optional[str] = None,
        last: Optional[str] = None,
        declaration: Optional[str] = None,
    ) -> "swan.VarDecl":
        raise ScadeOneException("Test harness does not support adding outputs directly.")
