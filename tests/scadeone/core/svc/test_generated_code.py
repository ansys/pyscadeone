# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
import shutil

import pytest

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.job import CodeGenerationJob
from ansys.scadeone.core.svc.generated_code import GeneratedCode


# To remove all generated code
_remove_swan_cg_code = False


@pytest.fixture(scope="module")
def codegen_project(app):
    project = app.load_project("tests/models/test_codegen/test_codegen.sproj")
    if not project:
        raise RuntimeError("Failed to load project.")
    project.load_jobs()
    return project


@pytest.fixture(scope="module", autouse=True)
def generate_code_for_test_project(codegen_project):
    for job in codegen_project.jobs:
        if not isinstance(job, CodeGenerationJob):
            continue
        if job.name in ("CodeGenNoExecution", "CodeGenInvalidMapping"):
            continue
        cg_out = job.storage.path.parent / "out"
        if _remove_swan_cg_code:
            shutil.rmtree(str(cg_out), ignore_errors=True)
        if cg_out.exists():
            continue
        result = job.run()
        if result.code != 0:
            raise RuntimeError(f"Code generation job '{job.name}' failed with code {result.code}.")


class TestGeneratedCode:
    @staticmethod
    def _get_gen_code(job_name, codegen_project) -> GeneratedCode:
        cg_job = codegen_project.get_job(job_name)
        if not isinstance(cg_job, CodeGenerationJob):
            raise RuntimeError(f"Job '{job_name}' is not a code generation job.")
        code_gen_dir = cg_job.storage.path.parent / "out"
        if not code_gen_dir.exists() and job_name != "CodeGenNoExecution":
            raise RuntimeError(f"Generated code of {job_name} does not exist.")
        return GeneratedCode(codegen_project, job_name)

    @staticmethod
    def _check_cfunction(op, cfunc, role):
        if cfunc is not None:
            code = op.get_code_elem(role)
            intf = cfunc.get_interface_file()
            impl = cfunc.get_implementation_file()
            name = cfunc.name
            # check that the function name corresponds to the name found in content section of code elem
            assert name == code["content"]["name"]
            params = cfunc.parameters
            # FIXME check on ret_type tbd
            _ = cfunc.return_type
            # find the function section in the mapping file dictionary
            for elem in op._gen_code.code:
                if elem.get("interface_file", "") == intf:
                    # check that the intf and impl files referenced in CFunction object are the one in the dict
                    assert elem.get("implementation_file") == impl
                    found = False
                    for decl in elem.get("declarations"):
                        if decl[0] == "function" and decl[1].get("name", "") == name:
                            # check that the CParameter objects correspond to the ones in the dict
                            dict_params = decl[1].get("parameters", None)
                            assert dict_params == code["content"]["parameters"]
                            assert dict_params is not None
                            assert len(dict_params) == len(params)
                            for p, dp in zip(params, dict_params):
                                assert p.name == dp.get("name", "")
                                assert p.is_pointer == dp.get("pointer", False)
                                assert p.is_const == dp.get("const", False)
                                assert p.type_name == op._gen_code.get_code_elem(
                                    dp.get("type", 0)
                                ).get("content", {}).get("name", "")
                                assert p.type_name in p.signature
                                assert not p.is_pointer or "*" in p.signature
                                assert not p.is_const or "const" in p.signature

                            found = True
                            break
                    assert found

    def test_init_no_project(self):
        try:
            GeneratedCode(None, "")
            assert False
        except Exception:
            assert True

    @pytest.mark.parametrize("job_name", ["", "foo", "Simu"])
    def test_init_no_job(self, codegen_project, job_name):
        try:
            GeneratedCode(codegen_project, job_name)
            assert False
        except ScadeOneException as error:
            assert error.args[0] == f'Generated code: no CodeGeneration kind job named "{job_name}"'

    @pytest.mark.parametrize(
        ("generated", "job_name"), [(True, "CodeGenForFMU"), (False, "CodeGenNoExecution")]
    )
    def test_is_generated_code(self, generated, job_name, codegen_project):
        gc = self._get_gen_code(job_name, codegen_project)
        assert generated == gc.is_code_generated
        if generated:
            assert gc.generated_code_dir is not None

    def test_error_no_generated_code(self, codegen_project):
        job_name = "CodeGenNoExecution"
        gc = self._get_gen_code(job_name, codegen_project)
        try:
            assert gc.mapping is None
        except ScadeOneException as error:
            assert error.args[0] == f"Generated code: code is not generated for job {job_name}"

    def test_wrong_mapping(self, codegen_project):
        gc = self._get_gen_code("CodeGenInvalidMapping", codegen_project)
        try:
            assert gc.mapping is None
        except ScadeOneException as error:
            assert "Generated code: cannot open mapping file" in error.args[0]

    def test_root_operators(self, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        for op_name in gc.root_operators:
            root_op = gc.get_model_operator(op_name)
            assert root_op.is_root

    @pytest.mark.parametrize(
        "oper_name", ["", "foo", "oper_misc1", "module0::oper_poly[][T=int32]"]
    )
    def test_operator_error(self, oper_name, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        try:
            gc.get_model_operator(oper_name)
        except ScadeOneException as error:
            assert error.args[0] == f"Generated code: no operator named {oper_name}"

    def test_operators(self, codegen_project):
        expected = ["module0::oper_misc1", "module0::oper_misc2", "module0::oper_poly"]
        gc = self._get_gen_code("CodeGen1", codegen_project)
        obtained = []
        for op in gc.get_model_operators():
            obtained.append(op.path)
        assert obtained == expected
        try:
            for name in obtained:
                op = gc.get_model_operator(name)
                assert op.path == name
        except ScadeOneException:
            assert False

    @pytest.mark.parametrize(
        ("oper", "watches", "instances", "is_root", "is_external", "is_expanded", "is_specialized"),
        [
            ("module0::oper_misc1", 0, 1, True, False, False, False),
            ("module0::oper_poly", 0, 0, False, False, False, False),
        ],
    )
    def test_operator_attributes(
        self,
        oper,
        watches,
        instances,
        is_root,
        is_external,
        is_expanded,
        is_specialized,
        codegen_project,
    ):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        op = gc.get_model_operator(oper)
        assert len(op.watches) == watches
        assert len(op.instances) == instances
        assert op.is_root == is_root
        assert op.is_external == is_external
        assert op.is_expanded == is_expanded
        assert op.is_specialized == is_specialized

    @pytest.mark.parametrize(
        ("job", "oper", "cycle", "init", "reset"),
        [
            ("CodeGen1", "module0::oper_misc1", True, True, True),
            ("CodeGen1", "module0::oper_poly", False, False, False),
            ("CodeGenForFMU", "module0::oper_for_fmu", True, False, False),
        ],
    )
    def test_operator_methods(self, job, oper, cycle, init, reset, codegen_project):
        gc = self._get_gen_code(job, codegen_project)
        op = gc.get_model_operator(oper)
        assert (op.cycle_method is not None) == cycle
        assert (op.init_method is not None) == init
        assert (op.reset_method is not None) == reset
        self._check_cfunction(op, op.cycle_method, "CycleMethod")
        self._check_cfunction(op, op.init_method, "InitMethod")
        self._check_cfunction(op, op.reset_method, "ResetMethod")

    @pytest.mark.parametrize("mono_name", ["", "foo", "module0::oper_poly", "module0::oper_poly[]"])
    def test_mono_instance_error(self, mono_name, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        try:
            gc.get_model_monomorphic_instance(mono_name)
        except ScadeOneException as error:
            assert error.args[0] == f"Generated code: no monomorphic instance named {mono_name}"

    def test_mono_instances(self, codegen_project):
        expected = [("module0::oper_poly[][T=int32]", "module0::oper_poly")]
        gc = self._get_gen_code("CodeGen1", codegen_project)
        obtained = []
        for op in gc.get_model_monomorphic_instances():
            obtained.append((op.path, op.source.path))
        assert obtained == expected
        try:
            for name, source in obtained:
                op = gc.get_model_monomorphic_instance(name)
                assert op.path == name
                assert op.source.path == source
        except ScadeOneException:
            assert False

    @pytest.mark.parametrize(
        ("oper", "watches", "instances", "source"),
        [("module0::oper_poly[][T=int32]", 0, 0, "module0::oper_poly")],
    )
    def test_mono_instance_attributes(self, oper, watches, instances, source, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        op = gc.get_model_monomorphic_instance(oper)
        assert len(op.watches) == watches
        assert len(op.instances) == instances
        assert op.source.path == source

    @pytest.mark.parametrize(
        ("oper", "cycle", "init", "reset"),
        [("module0::oper_poly[][T=int32]", True, False, False)],
    )
    def test_mono_instance_methods(self, oper, cycle, init, reset, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        op = gc.get_model_monomorphic_instance(oper)
        assert (op.cycle_method is not None) == cycle
        assert (op.init_method is not None) == init
        assert (op.reset_method is not None) == reset
        self._check_cfunction(op, op.cycle_method, "CycleMethod")
        self._check_cfunction(op, op.init_method, "InitMethod")
        self._check_cfunction(op, op.reset_method, "ResetMethod")

    @pytest.mark.parametrize(
        "sensor_name",
        ["", "foo", "sensor_int", "module0::oper_misc1", "module0::oper_poly[][T=int32]"],
    )
    def test_sensor_error(self, sensor_name, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        try:
            gc.get_model_sensor(sensor_name)
        except ScadeOneException as error:
            assert error.args[0] == f"Generated code: no sensor named {sensor_name}"

    def test_sensors(self, codegen_project):
        expected = [
            "module0::sensor_int",
            "module0::sensor_enum",
            "module0::sensor_variant",
            "module0::sensor_array",
            "module0::sensor_struct",
            "module0::sensor_syn",
            "module0::sensor_float",
            "module0::sensor_bool",
        ]
        gc = self._get_gen_code("CodeGenForFMU", codegen_project)
        obtained = []
        for sen in gc.get_model_sensors():
            obtained.append(sen.path)
        print(obtained)
        assert obtained == expected
        try:
            for name in obtained:
                sen = gc.get_model_sensor(name)
                assert sen.path == name
                code_type = sen.code_type
                assert code_type.get("name", "") == sen.code_type_name
                elem = sen.get_code_elem()
                assert elem["content"]["name"] == sen.code_name
        except ScadeOneException:
            assert False

    @pytest.mark.parametrize(
        (
            "sensor",
            "watches",
            "instances",
            "is_root",
            "is_external",
            "is_expanded",
            "is_specialized",
        ),
        [
            ("module0::oper_misc1", 0, 1, True, False, False, False),
            ("module0::oper_poly", 0, 0, False, False, False, False),
        ],
    )
    def test_sensor_attributes(
        self,
        sensor,
        watches,
        instances,
        is_root,
        is_external,
        is_expanded,
        is_specialized,
        codegen_project,
    ):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        op = gc.get_model_operator(sensor)
        assert len(op.watches) == watches
        assert len(op.instances) == instances
        assert op.is_root == is_root
        assert op.is_external == is_external
        assert op.is_expanded == is_expanded
        assert op.is_specialized == is_specialized

    @pytest.mark.parametrize(
        ("job", "oper"),
        [
            ("CodeGen1", "module0::oper_misc1"),
            ("CodeGen1", "module0::oper_misc2"),
            ("CodeGen1", "module0::oper_poly"),
            ("CodeGenForFMU", "module0::oper_for_fmu"),
        ],
    )
    def test_oper_parameters(self, job, oper, codegen_project):
        def _check_var(var, input_direction, separator=""):
            name = var.name
            full_name = var.full_name(separator)
            assert name in full_name
            code_name = var.code_name
            code_type = var.code_type
            if code_name == "__no_name__":
                # check that it is the return of the function or a polymorphic param
                assert code_type == {} or var.parent.cycle_method.return_type == code_type

        gc = self._get_gen_code(job, codegen_project)
        oper = gc.get_model_operator(oper)
        for i in oper.inputs:
            _check_var(i, True, ".")
        for o in oper.outputs:
            _check_var(o, False)

    @pytest.mark.parametrize(
        ("job", "oper"),
        [
            ("CodeGen1", "module0::oper_poly[][T=int32]"),
        ],
    )
    def test_mono_instance_parameters(self, job, oper, codegen_project):
        def _check_var(var, input_direction):
            source = var.source
            name = source.name
            full_name = source.full_name()
            assert name in full_name
            code_name = var.code_name
            code_type = var.code_type
            if code_name == "__no_name__":
                # input cannot be __no_name__
                assert not input_direction
                # check that it is the return of the function
                assert var.parent.cycle_method.return_type == code_type

        gc = self._get_gen_code(job, codegen_project)
        oper = gc.get_model_monomorphic_instance(oper)
        for i in oper.inputs:
            _check_var(i, True)
        for o in oper.outputs:
            _check_var(o, False)

    @pytest.mark.parametrize("role", ["", "foo"])
    def test_wrong_code_id(self, role, codegen_project):
        gc = self._get_gen_code("CodeGen1", codegen_project)
        try:
            gc.get_code_id(0, role)
            assert False
        except ScadeOneException as error:
            role_str = f"for role {role}" if role != "" else "without role"
            assert (
                error.args[0] == f"Generated code: no code id associated to model id #0 {role_str}"
            )
