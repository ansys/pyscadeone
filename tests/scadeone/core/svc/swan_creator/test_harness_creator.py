# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.scadeone.core import swan
from ansys.scadeone.core.model.model import Model


class TestHarnessDiagramCreator:
    def test_instance_under_test(self, module_factory):
        module = module_factory.create_test_module("TestHarness")
        assert isinstance(module, swan.TestModule)
        op2 = module.add_test_harness("UnderTest")
        harness_op = module.add_operator_definition("G")
        diag0 = op2.add_diagram()
        under_test = diag0.add_instance_under_test(harness_op)
        assert under_test is not None
        assert isinstance(under_test, swan.Block)
        assert isinstance(under_test.instance, swan.NamedInstance)
        assert swan.swan_to_str(under_test.instance) == "G"

    def test_set_sensor(self, model: Model, module_factory):
        module = module_factory.create_test_module("Module0")
        model.add_body(module)
        sensor = module.add_sensor("sCelcius", "bool")
        module_test = module_factory.create_test_module("TestHarness")
        model.add_test_module(module_test)
        assert isinstance(module_test, swan.TestModule)
        op2 = module_test.add_test_harness("SensorTest")
        diag0 = op2.add_diagram()
        module_test.use(module)
        set_sensor = diag0.add_set_sensor(sensor)
        assert set_sensor is not None
        assert isinstance(set_sensor, swan.SetSensorBlock)
        assert set_sensor.owner == diag0
        assert swan.swan_to_str(set_sensor.sensor) == "Module0::sCelcius"

    def test_add_data_source(self, module_factory):
        module = module_factory.create_test_module("TestHarness")
        assert isinstance(module, swan.TestModule)
        op2 = module.add_test_harness("DataSourceTest")
        diag0 = op2.add_diagram()
        data_source = diag0.add_data_source("Key1")
        assert data_source is not None
        assert isinstance(data_source.instance.op_expr, swan.DataSource)

    def test_add_oracle(self, module_factory):
        module = module_factory.create_test_module("TestHarness")
        assert isinstance(module, swan.TestModule)
        op2 = module.add_test_harness("OracleTest")
        diag0 = op2.add_diagram()
        oracle = diag0.add_oracle("Key1")
        assert oracle is not None
        assert isinstance(oracle.instance.op_expr, swan.Oracle)

    def test_test_module(self, model: Model, module_factory):
        module = module_factory.create_test_module("module0")
        assert module is not None
        assert isinstance(module, swan.TestModule)
        module1 = module_factory.create_module_body("module1")
        assert module1 is not None
        assert isinstance(module1, swan.ModuleBody)
        sensor = module1.add_sensor("sensor0", "int32")
        model.add_body(module1)
        model.add_test_module(module)
        op1 = module1.add_operator_definition("G")
        op2 = module.add_test_harness("harness0")
        use = module.use("module1")
        assert use is not None
        diag0 = op2.add_diagram()
        set_sensor = diag0.add_set_sensor(sensor)
        assert set_sensor is not None
        assert str(set_sensor.sensor) == "module1::sensor0"
        op_def = model.operator_definitions[0]
        assert op1.id == op_def.id
        under_test = diag0.add_instance_under_test(op_def)
        assert under_test is not None
        data_source = diag0.add_data_source("Key1")
        assert data_source is not None
        oracle = diag0.add_oracle("Key2")
        assert oracle is not None
        op3 = module.add_operator_definition("op3")
        op3_in0 = op3.add_input("in0", "int32")
        expr = diag0.add_expr_block(op3_in0)
        assert expr is not None
