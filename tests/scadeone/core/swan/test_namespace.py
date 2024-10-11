# Copyright (c) 2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from typing import List

import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.model import Model
from ansys.scadeone.core.model.loader import SwanParser
import ansys.scadeone.core.swan as swan


@pytest.fixture
def parser(unit_test_logger):
    return SwanParser(unit_test_logger)


@pytest.fixture
def cc_module(cc_project):
    app = ScadeOne()
    app.load_project(cc_project)
    project = app.projects[0]
    model = project.model
    model.load_all_modules()
    modules = list(model.modules)
    return modules[1]


def gen_code(swan: str, module: str) -> SwanString:
    return SwanString(SwanString.gen_version() + "\n" + swan, module)


class TestModuleNamespace:

    def test_module_get_group_decl(self, parser: SwanParser):
        code = gen_code("group group0 = (int32, int32);", "test_group")
        body = parser.module_body(code)
        decl = body.get_declaration("group0")
        assert isinstance(decl, swan.GroupDecl)
        assert decl.id.value == "group0"

    def test_get_const_from_interface(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;
             """,
            "module0",
        )
        interface = parser.module_interface(code)
        const0 = interface.get_declaration("const0")
        assert isinstance(const0, swan.ConstDecl)
        assert const0.id.value == "const0"

    def test_get_signature_from_interface(self, parser: SwanParser):
        code = gen_code(
            """
                function operator0 (i0: int32)
                  returns (o0: int32);
             """,
            "module0",
        )
        interface = parser.module_interface(code)
        op0 = interface.get_declaration("operator0")
        assert isinstance(op0, swan.Signature)
        assert op0.id.value == "operator0"

    def test_module_get_type_decl(self, cc_module):
        decl = cc_module.get_declaration("tCruiseState")
        assert isinstance(decl, swan.TypeDecl)
        assert decl.id.value == "tCruiseState"

    def test_module_get_const_decl(self, cc_module):
        decl = cc_module.get_declaration("SpeedInc")
        assert isinstance(decl, swan.ConstDecl)
        assert decl.id.value == "SpeedInc"

    def test_module_get_sensor_decl(self, cc_module):
        decl = cc_module.get_declaration("Ki")
        assert isinstance(decl, swan.SensorDecl)
        assert decl.id.value == "Ki"

    def test_module_get_op_decl(self, cc_module):
        decl = cc_module.get_declaration("Regulation")
        assert isinstance(decl, swan.Operator)
        assert decl.id.value == "Regulation"


class TestScopeNamespace:

    @staticmethod
    def _create_model(modules: List[swan.Module]):
        model = Model()
        for module in modules:
            model._modules[module.name] = module
            module.owner = model
        return model

    def test_get_group(self, parser: SwanParser):
        code = gen_code(
            """
                group group0 = (i0: int32, i1:int32);
                node operator0 (i0: int32;
                                 i1 : int32;)
                  returns (o0: group0;)
                {
                  diagram
                    (#0 def o0)
                    (#1 expr i0)
                    (#2 expr i1)
                    (#3 group)

                    (#4 wire #1 => #3 .(i0))
                    (#5 wire #2 => #3 .(i1))
                    (#6 wire #3 => #0)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        group0 = scope.get_declaration("group0")
        assert isinstance(group0, swan.GroupDecl)
        assert group0.id.value == "group0"

    def test_get_imported_group(self, parser: SwanParser):
        module0 = gen_code(
            """
            group group0 = (i0: int32, i1:int32);
            """,
            "groups",
        )
        module1 = gen_code(
            """
            use groups;

            node operator0 (i0: int32;
                            i1 : int32;)
              returns (o0: group0;)
            {
              diagram
                (#0 def o0)
                (#1 expr i0)
                (#2 expr i1)
                (#3 group)
                (#4 wire #1 => #3 .(i0))
                (#5 wire #2 => #3 .(i1))
                (#6 wire #3 => #0)
            }
            """,
            "module0",
        )
        module0_interface = parser.module_interface(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_interface, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        group0 = scope.get_declaration("groups::group0")
        assert isinstance(group0, swan.GroupDecl)
        assert group0.id.value == "group0"
        assert group0.module.name.as_string == "groups"

    def test_get_type_expr(self, parser: SwanParser):
        code = gen_code(
            """
                type type0 = int32;
                node operator0 (i0: type0;)
                  returns (o0: type0;)
                {
                  diagram
                    (#0 expr i0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        type0 = scope.get_declaration("type0")
        assert isinstance(type0, swan.TypeDecl)
        assert type0.id.value == "type0"

    def test_get_type_struct(self, parser: SwanParser):
        code = gen_code(
            """
                type typeStruct = {a: int32, b: int32};
                node operator0 (i0: typeStruct;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 expr i0.a)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        type_str = scope.get_declaration("typeStruct")
        assert isinstance(type_str, swan.TypeDecl)
        assert type_str.id.value == "typeStruct"

    def test_get_type_enum(self, parser: SwanParser):
        code = gen_code(
            """
                type typeEnum = enum {HI, LO};
                node operator0 (i0: typeEnum;)
                  returns (o0: typeEnum;)
                {
                  diagram
                    (#0 expr i0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        type_str = scope.get_declaration("typeEnum")
        assert isinstance(type_str, swan.TypeDecl)
        assert type_str.id.value == "typeEnum"

    def test_get_type_variant(self, parser: SwanParser):
        code = gen_code(
            """
                type typeVariant = Int {x: int32} | Float {x: float32};
                node operator0 (i0: typeVariant;)
                  returns (o0: typeVariant;)
                {
                  diagram
                    (#0 expr i0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        type_str = scope.get_declaration("typeVariant")
        assert isinstance(type_str, swan.TypeDecl)
        assert type_str.id.value == "typeVariant"

    def test_get_const(self, parser: SwanParser):
        code = gen_code(
            """
                const const0: int32 = 0;

                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 expr const0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        const0 = scope.get_declaration("const0")
        assert isinstance(const0, swan.ConstDecl)
        assert const0.id.value == "const0"

    def test_get_sensor(self, parser: SwanParser):
        code = gen_code(
            """
                sensor sensor0: int32;

                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 expr sensor0)
                    (#1 def o0)
                    (#2 wire #0 => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        sensor0 = scope.get_declaration("sensor0")
        assert isinstance(sensor0, swan.SensorDecl)
        assert sensor0.id.value == "sensor0"

    def test_get_op(self, parser: SwanParser):
        code = gen_code(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }

                node operator1 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 block operator0)
                    (#1 def o0)
                    (#2 expr i0)
                    (#3 wire #2 => #0 .(i0))
                    (#4 wire #0 .(o0) => #1)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op1 = body.declaration_list[1]
        assert isinstance(op1, swan.Operator)
        scope = op1.body
        op0 = scope.get_declaration("operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.id.value == "operator0"

    def test_get_input(self, parser: SwanParser):
        code = gen_code(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        i0 = scope.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.id.value == "i0"

    def test_get_output(self, parser: SwanParser):
        code = gen_code(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        o0 = scope.get_declaration("o0")
        assert isinstance(o0, swan.VarDecl)
        assert o0.id.value == "o0"

    def test_get_local(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#1 expr x0)
                    (#2 wire #1 => #0)
                    (var x0:int32;)
                    (let x0 = 1;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        x0 = scope.get_declaration("x0")
        assert isinstance(x0, swan.VarDecl)
        assert x0.id.value == "x0"

    def test_get_global(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  var x0: int32;
                  let x0 = 1;
                  diagram
                    (#0 def o0)
                    (#1 expr x0)
                    (#2 wire #1 => #0)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        x0 = scope.get_declaration("x0")
        assert isinstance(x0, swan.VarDecl)
        assert x0.id.value == "x0"

    def test_get_imported_op(self, parser: SwanParser):
        module0 = gen_code(
            """
            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 expr i0)
                (#1 def o0)
                (#2 wire #0 => #1)
            }
            """,
            "module0",
        )
        module1 = gen_code(
            """
            use module0;

            node operator1 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 block module0::operator0)
                (#1 expr i0)
                (#2 def o0)
                (#3 wire #1 => #0)
                (#4 wire #0 => #2)
            }
            """,
            "module1",
        )
        module0_body = parser.module_body(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op1 = module1_body.declaration_list[0]
        assert isinstance(op1, swan.Operator)
        scope = op1.body
        op0 = scope.get_declaration("module0::operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.id.value == "operator0"
        assert op0.module.name.as_string == "module0"

    def test_get_imported_type(self, parser: SwanParser):
        module0 = gen_code(
            """
            type type0 = int32;
            """,
            "types",
        )
        module1 = gen_code(
            """
            use types;

            node operator0 (i0: types::type0;)
              returns (o0: types::type0;)
            {
              diagram
                (#0 expr i0)
                (#1 def o0)
                (#2 wire #0 => #1)
            }
            """,
            "module0",
        )
        module0_interface = parser.module_interface(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_interface, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope = op0.body
        type0 = scope.get_declaration("types::type0")
        assert isinstance(type0, swan.TypeDecl)
        assert type0.id.value == "type0"
        assert type0.module.name.as_string == "types"

    def test_get_input_from_automaton(self, parser: SwanParser):
        code = gen_code(
            """
                node operator8 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    ( automaton $automaton0
                           initial state #4 state0 :
                             diagram
                               (#1 expr i0)
                               (#2 def o0)
                               (#3 wire #1 => #2)
                           state #5 state1 :
                           :1: #4 until
                           restart #5;
                    )
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].state_machine.items[0].sections[0]
        i0 = scope_section.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.id.value == "i0"

    def test_get_const_from_automaton(self, parser: SwanParser):
        code = gen_code(
            """
                const const0 : int32 = 0;
                node operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (automaton $automaton0
                           initial state #4 state0 :
                             diagram
                               (#1 expr i0)
                               (#2 def o0)
                               (#3 wire #1 => #2)
                           state #5 state1 :
                           :1: #4 until
                           restart #5;
                    )
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[1]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].state_machine.items[0].sections[0]
        const0 = scope_section.get_declaration("const0")
        assert isinstance(const0, swan.ConstDecl)
        assert const0.id.value == "const0"

    def test_get_global_from_diag(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  var x0: int32;
                  diagram
                    (let x0 = 1;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[1]
        x0 = scope_section.get_declaration("x0")
        assert isinstance(x0, swan.VarDecl)
        assert x0.id.value == "x0"

    def test_get_input_from_emit(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  diagram
                    (var b:bool;)
                    (emit $a 'b;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[1].section
        b = scope_section.get_declaration("b")
        assert isinstance(b, swan.VarDecl)
        assert b.id.value == "b"

    def test_get_input_output_from_assume(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  diagram
                    (assume $i0_positive: i0 > 0;)
                    (assume $o0_positive: 0 < o0;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].section
        i0 = scope_section.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.id.value == "i0"
        scope_section = op0.body.sections[0].objects[1].section
        o0 = scope_section.get_declaration("o0")
        assert isinstance(o0, swan.VarDecl)
        assert o0.id.value == "o0"

    def test_get_input_from_guarantee(self, parser: SwanParser):
        code = gen_code(
            """
                node operator0 (i0: int32)
                returns (o0: int32)
                {
                  diagram
                    (guarantee $i0_positive: i0 > 0;)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op0 = body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0].objects[0].section
        i0 = scope_section.get_declaration("i0")
        assert isinstance(i0, swan.VarDecl)
        assert i0.id.value == "i0"

    def test_get_input_from_forward(self, parser: SwanParser):
        code = gen_code(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }

                function operator1 (A: int32^10)
                    returns (B: int32^10)
                    {
                        let B =
                            forward <<10>> with [ai]=A;
                                let bi = operator0(ai);
                            returns ([bi]);
                    }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op1 = body.declaration_list[1]
        assert isinstance(op1, swan.Operator)
        scope_section = op1.body.sections[0].equations[0].expr.body.body[0]
        op0 = scope_section.get_declaration("operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.id.value == "operator0"

    def test_get_used_const(self, parser: SwanParser):
        module0 = gen_code(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module1 = gen_code(
            """
            use module0;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr module0::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        module0_body = parser.module_body(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0"

    def test_get_used_const_with_ns(self, parser: SwanParser):
        module0 = gen_code(
            """
            const const0: int32 = 0;
            """,
            "module0::module00",
        )
        module1 = gen_code(
            """
            use module0::module00;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr module00::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        module0_body = parser.module_body(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::module00::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0::module00"

    def test_get_used_const_with_alias(self, parser: SwanParser):
        module0 = gen_code(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module1 = gen_code(
            """
            use module0 as m;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr m::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        module0_body = parser.module_body(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("m::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0"

    def test_get_used_const_with_ns_and_alias(self, parser: SwanParser):
        module0 = gen_code(
            """
            const const0: int32 = 0;
            """,
            "module0::module00",
        )
        module1 = gen_code(
            """
            use module0::module00 as m;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr m::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        module0_body = parser.module_body(module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::module00::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0::module00"

    def test_get__const_from_interface(self, parser: SwanParser):
        module0_int = gen_code(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module0 = gen_code(
            """
            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr const0)
                (#2 wire #1 => #0)
            }
            """,
            "module0",
        )
        module0_interface = parser.module_interface(module0_int)
        module0_body = parser.module_body(module0)
        TestScopeNamespace._create_model([module0_interface, module0_body])
        op0 = module0_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0"

    def test_get_input_from_anonymous_op(self, parser: SwanParser):
        code = gen_code(
            """
                function operator0 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 def o0)
                    (#5 expr i0)
                    (#6 wire #5 => #0)
                }

                node operator1 (i0: int32;)
                  returns (o0: int32;)
                {
                  diagram
                    (#0 block ({op_expr%function i => operator0(i)%op_expr}))
                    (#1 expr i0)
                    (#2 def o0)

                    (#3 wire #1 => #0 .(i))
                    (#4 wire #0 => #2)
                }
                """,
            "module0",
        )
        body = parser.module_body(code)
        op1 = body.declaration_list[1]
        assert isinstance(op1, swan.Operator)
        scope_section = op1.body.sections[0]
        op0 = scope_section.get_declaration("operator0")
        assert isinstance(op0, swan.Operator)
        assert op0.id.value == "operator0"

    def test_get_used_const_decl_interface(self, parser: SwanParser):
        i_module0 = gen_code(
            """
            const const0: int32 = 0;
            """,
            "module0",
        )
        module0 = gen_code(
            """
            """,
            "module0",
        )
        module1 = gen_code(
            """
            use module0;

            node operator0 (i0: int32;)
              returns (o0: int32;)
            {
              diagram
                (#0 def o0)
                (#1 expr module0::const0)
                (#2 wire #1 => #0)
            }
            """,
            "module1",
        )
        module0_body = parser.module_body(module0)
        module0_interface = parser.module_interface(i_module0)
        module1_body = parser.module_body(module1)
        TestScopeNamespace._create_model([module0_interface, module0_body, module1_body])
        op0 = module1_body.declaration_list[0]
        assert isinstance(op0, swan.Operator)
        scope_section = op0.body.sections[0]
        c0 = scope_section.get_declaration("module0::const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0"

    def test_get_const_decl_interface(self, parser: SwanParser):
        i_module0 = gen_code(
            """
            const const0: int32 = 0;
            function operator0 (i0: int32)
              returns (o0: int32);
            """,
            "module0",
        )

        module0_interface = parser.module_interface(i_module0)
        op0 = module0_interface.declaration_list[1]
        assert isinstance(op0, swan.Signature)
        module = op0.module
        assert isinstance(module, swan.ModuleInterface)
        c0 = module.get_declaration("const0")
        assert isinstance(c0, swan.ConstDecl)
        assert c0.id.value == "const0"
        assert c0.module.name.as_string == "module0"

    def test_get_regulation_from_state(self, cc_module):
        automaton0 = cc_module.declaration_list[2].body.sections[0].objects[0].state_machine
        automaton1 = automaton0.items[1].sections[0].objects[13].state_machine
        automaton2 = automaton1.items[0].sections[0].objects[10].state_machine
        scope_section = automaton2.items[0].sections[0]
        op = scope_section.get_declaration("Regulation")
        assert isinstance(op, swan.Operator)
        assert op.id.value == "Regulation"

    def test_get_limiter_from_cruise_speed_mng_op(self, cc_module):
        cruise_speed_mng_op = cc_module.declaration_list[3]
        scope_section = cruise_speed_mng_op.body.sections[0]
        op = scope_section.get_declaration("Utils::Limiter")
        assert isinstance(op, swan.Operator)
        assert op.id.value == "Limiter"
        assert op.module.name.as_string == "Utils"
