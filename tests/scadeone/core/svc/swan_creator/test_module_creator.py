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

import pytest

from ansys.scadeone.core import swan
from ansys.scadeone.core.svc.swan_creator.module_creator import (
    DeclarationFactory,
    UseDirectiveFactory,
    ModuleFactory,
)
from ansys.scadeone.core.swan import Identifier, Module, PathIdentifier


@pytest.fixture
def use_factory_singleton():
    return UseDirectiveFactory()


@pytest.fixture
def dec_factory_singleton():
    return DeclarationFactory()


@pytest.fixture
def module_factory_singleton():
    return ModuleFactory()


class TestUseDirectiveFactory:
    def test_singleton(self, use_factory_singleton):
        factory1 = UseDirectiveFactory()
        factory2 = UseDirectiveFactory()
        assert use_factory_singleton is factory1
        assert use_factory_singleton is factory2

    def test_create_invalid_use_directive(self, use_factory_singleton):
        with pytest.raises(swan.ScadeOneException):
            id = Identifier("module0&")
            path_id = PathIdentifier([id])
            module = Module(path_id)
            use_factory_singleton.create_use_directive(module)

    def test_create_invalid_use_directive_by_str(self, use_factory_singleton):
        with pytest.raises(swan.ScadeOneException):
            use_factory_singleton.create_use_directive("module0%")

    def test_create_use_directive(self, use_factory_singleton):
        id = Identifier("module0")
        path_id = PathIdentifier([id])
        module = Module(path_id)
        use_directive = use_factory_singleton.create_use_directive(module)
        assert isinstance(use_directive, swan.UseDirective)
        assert swan.swan_to_str(use_directive) == "use module0;\n"

    def test_create_use_directive_with_str(self, use_factory_singleton):
        use_directive = use_factory_singleton.create_use_directive("module0")
        assert isinstance(use_directive, swan.UseDirective)
        assert swan.swan_to_str(use_directive) == "use module0;\n"

    def test_create_use_directive_with_path(self, use_factory_singleton):
        path_id = PathIdentifier.from_string("lib::sublib::module0")
        module = Module(path_id)
        use_directive = use_factory_singleton.create_use_directive(module)
        assert isinstance(use_directive, swan.UseDirective)
        assert len(use_directive.path.path_id) == 3
        assert swan.swan_to_str(use_directive.path.path_id[0]) == "lib"
        assert swan.swan_to_str(use_directive.path.path_id[1]) == "sublib"
        assert swan.swan_to_str(use_directive.path.path_id[2]) == "module0"
        assert swan.swan_to_str(use_directive) == "use lib::sublib::module0;\n"

    def test_create_use_directive_with_path_str(self, use_factory_singleton):
        use_directive = use_factory_singleton.create_use_directive("lib::sublib::module0")
        assert isinstance(use_directive, swan.UseDirective)
        assert len(use_directive.path.path_id) == 3
        assert swan.swan_to_str(use_directive.path.path_id[0]) == "lib"
        assert swan.swan_to_str(use_directive.path.path_id[1]) == "sublib"
        assert swan.swan_to_str(use_directive.path.path_id[2]) == "module0"
        assert swan.swan_to_str(use_directive) == "use lib::sublib::module0;\n"

    def test_create_use_directive_with_alias(self, use_factory_singleton):
        id = Identifier("module0")
        path_id = PathIdentifier([id])
        module = Module(path_id)
        use_directive = use_factory_singleton.create_use_directive(module, "m0")
        assert isinstance(use_directive, swan.UseDirective)
        assert swan.swan_to_str(use_directive) == "use module0 as m0;\n"

    def test_create_use_directive_with_alias_str(self, use_factory_singleton):
        use_directive = use_factory_singleton.create_use_directive("module0", "m0")
        assert isinstance(use_directive, swan.UseDirective)
        assert swan.swan_to_str(use_directive) == "use module0 as m0;\n"


class TestDeclarationFactory:
    def test_singleton(self, dec_factory_singleton):
        factory1 = DeclarationFactory()
        factory2 = DeclarationFactory()
        assert dec_factory_singleton is factory1
        assert dec_factory_singleton is factory2

    def test_create_invalid_declaration(self, dec_factory_singleton):
        with pytest.raises(swan.ScadeOneException):
            dec_factory_singleton.create_declaration("invalid_declaration")

    def test_create_invalid_dec_by_name(self, dec_factory_singleton):
        with pytest.raises(swan.ScadeOneException):
            dec_factory_singleton.create_declaration("const const&: int32 = 1")

    def test_create_const_by_declaration(self, dec_factory_singleton):
        const = dec_factory_singleton.create_declaration("const const0: int32 = 1")
        assert isinstance(const, swan.ConstDecl)
        assert swan.swan_to_str(const.id) == "const0"
        assert swan.swan_to_str(const.type) == "int32"
        assert swan.swan_to_str(const.value) == "1"

    def test_create_group_by_declaration(self, dec_factory_singleton):
        group = dec_factory_singleton.create_declaration("group group1 = (group0, int32)")
        assert isinstance(group, swan.GroupDecl)
        assert swan.swan_to_str(group.id) == "group1"
        type = group.type
        assert isinstance(type, swan.GroupTypeExpressionList)
        assert len(type.items) == 2
        assert swan.swan_to_str(type.items[0]) == "group0"
        assert swan.swan_to_str(type.items[1]) == "int32"

    def test_create_simple_operator(self, dec_factory_singleton):
        operator = dec_factory_singleton.create_operator("op1")
        assert operator is not None
        assert isinstance(operator, swan.Operator)
        assert swan.swan_to_str(operator.id) == "op1"
        assert operator.is_node
        assert operator.inputs == []
        assert operator.outputs == []

    def test_create_function_operator(self, dec_factory_singleton):
        operator = dec_factory_singleton.create_operator("op2", is_node=False)
        assert operator is not None
        assert isinstance(operator, swan.Operator)
        assert swan.swan_to_str(operator.id) == "op2"
        assert not operator.is_node
        assert operator.inputs == []
        assert operator.outputs == []

    def test_create_textual_operator(self, dec_factory_singleton):
        txt_op = """
            node operator3 (i0: int32; i1: int32)
            returns (o0: int32) {}
        """
        operator = dec_factory_singleton.create_textual_operator(txt_op)
        assert operator is not None
        assert isinstance(operator, swan.Operator)
        assert swan.swan_to_str(operator.id) == "operator3"
        assert operator.is_node
        assert len(operator.inputs) == 2
        assert swan.swan_to_str(operator.inputs[0]) == "i0: int32"
        assert swan.swan_to_str(operator.inputs[1]) == "i1: int32"
        assert len(operator.outputs) == 1
        assert swan.swan_to_str(operator.outputs[0]) == "o0: int32"

    def test_create_textual_signature(self, dec_factory_singleton):
        txt_op = """
            node operator3 (i0: int32; i1: int32)
            returns (o0: int32);
        """
        operator = dec_factory_singleton.create_textual_signature(txt_op)
        assert operator is not None
        assert isinstance(operator, swan.Signature)
        assert swan.swan_to_str(operator.id) == "operator3"
        assert operator.is_node
        assert len(operator.inputs) == 2
        assert swan.swan_to_str(operator.inputs[0]) == "i0: int32"
        assert swan.swan_to_str(operator.inputs[1]) == "i1: int32"
        assert len(operator.outputs) == 1
        assert swan.swan_to_str(operator.outputs[0]) == "o0: int32"


class TestModuleFactory:
    def test_create_invalid_module_by_name(self):
        with pytest.raises(swan.ScadeOneException):
            ModuleFactory.create_module("module$")

    def test_create_invalid_module_by_path(self):
        with pytest.raises(swan.ScadeOneException):
            ModuleFactory.create_module("module::$")

    def test_create_module(self):
        module = ModuleFactory.create_module("module")
        assert module is not None
        assert swan.swan_to_str(module.name) == "module"

    def test_create_module_interface(self):
        module = ModuleFactory.create_module_interface("module")
        assert module is not None
        assert swan.swan_to_str(module.name) == "module"

    def test_create_module_namesapce(self):
        module = ModuleFactory.create_module("lib::submodule::module")
        assert module is not None
        assert swan.swan_to_str(module.name) == "lib::submodule::module"
