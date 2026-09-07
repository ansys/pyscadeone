# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

import os
import importlib
import shutil
from os.path import getsize, isfile
from pathlib import Path
import sys
import pytest

from test_tools.utils import SysContext
from typing import cast

from ansys.scadeone.core import ScadeOne, cli
from ansys.scadeone.core.svc.pywrapper import PythonWrapper


# To remove all generated code
_remove_swan_cg_code = False


@pytest.fixture
def mockup_installation(scadeone_install_path):
    # Return a function to mock the installation if generate is True
    # remove the config file after.
    conf = (
        Path(__file__).parents[4] / "src/ansys/scadeone/core/Configuration/modulesLocation.config"
    )

    def mockup_config(generate: bool):
        if generate:
            ScadeOne()._Tools.generate_config(scadeone_install_path)

    yield mockup_config
    conf.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def app(scadeone_install_path):
    return ScadeOne(scadeone_install_path)


@pytest.fixture(scope="module")
def wrapper_projects(app):
    root_path = Path("tests/models/wrapper")
    default_path = root_path / "project/project.sproj"
    wrapper_types_path = root_path / "wrapper_types/project.sproj"
    elaboration_path = root_path / "elaboration/elaboration.sproj"
    imported_code_textual_func = root_path / "imported_codes/textual_func/project.sproj"
    imported_code_textual_node = root_path / "imported_codes/textual_node/project.sproj"
    imported_code_incl_deps = root_path / "imported_codes/incl_deps/project.sproj"
    return {
        "default": app.load_project(default_path),
        "wrapper_types": app.load_project(wrapper_types_path),
        "elaboration": app.load_project(elaboration_path),
        "imported_code_textual_func": app.load_project(imported_code_textual_func),
        "imported_code_textual_node": app.load_project(imported_code_textual_node),
        "imported_code_incl_deps": app.load_project(imported_code_incl_deps),
    }


def generate_code(project):
    project.load_jobs()
    for job in project.jobs:
        if not job.is_code_generation:
            continue
        out = job.storage.path.parent / "out"
        if _remove_swan_cg_code:
            shutil.rmtree(str(out), ignore_errors=True)
        if out.exists():
            continue
        result = job.run()
        if result.code != 0:
            raise RuntimeError(f"Code generation job '{job.name}' failed with code {result.code}.")


@pytest.fixture(scope="module", autouse=True)
def generate_code_for_test_projects(wrapper_projects):
    for proj_name, proj in wrapper_projects.items():
        if not proj:
            raise RuntimeError(f"Project '{proj_name}' is empty.")
        generate_code(proj)


class TestPythonWrapper:
    _list_expected = ["h", "c", "def", "py"]

    def _generate_wrapper(self, project, job_name, wrapper_name, output_path) -> PythonWrapper:
        """Generate the wrapper code and load the module.

        Parameters
        ----------
        project: Project
            Scade One project
        job_name : str
            Job name.
        wrapper_name : str
            Generated wrapper name.
        output_path : Path
            Path to the target directory.

        Returns
        -------
        gen : PythonWrapper
            The PythonWrapper object used to generate the wrapper.
        """
        _gen = PythonWrapper(
            project=project,
            job=job_name,
            output=wrapper_name,
            target_dir=output_path,
        )
        _gen.generate()

        assert self._generation_ok(output_path / wrapper_name)
        return _gen

    def _generation_ok(self, target_path: Path) -> bool:
        # Verify that the generation is good or failed.
        file = target_path / "py_wrapper_files.txt"
        _rtn = False
        if isfile(file) and os.access(file, os.R_OK) and getsize(file) != 0:
            _list_file = []
            with file.open(mode="r") as f:
                for _ln in f:
                    _list_file.append(_ln.rstrip().split(".")[-1])
            if set(_list_file) == set(self._list_expected):
                _rtn = True
        return _rtn

    @staticmethod
    def _load_wrapper_module(wrapper_name: str, gen: PythonWrapper):
        # Load the wrapper module from the generated file
        # File is found from gen target directory.
        spec = importlib.util.spec_from_file_location(
            wrapper_name, gen._target_dir() / f"{wrapper_name}.py"
        )
        wrapper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper_module)
        # add it to sys.modules so that it can be used as a normal module
        sys.modules[wrapper_name] = wrapper_module
        return wrapper_module

    @staticmethod
    def _format_name(opt_name: str) -> str:
        return "_".join(reversed(opt_name.split("::")))

    def test_wrapper_one_output(self, wrapper_projects, tmp_path):
        project = wrapper_projects["default"]
        job_name = "CGJob4OneOutput"
        wrapper_name = "one_output_wrapper"

        gen = self._generate_wrapper(project, job_name, wrapper_name, tmp_path)

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator_path_name = "module0::oneOutput"
        operator_name = self._format_name(operator_path_name)
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = 1
        operator.cycle()
        assert operator.outputs.o0 == 1

    @pytest.mark.parametrize(
        ("job_name", "wrapper_name"),
        [
            ("CGJob4Func", "fn_wrapper"),
            ("CGJob4Node", "n_wrapper"),
        ],
    )
    def test_py_wrapper(self, wrapper_projects, tmp_path, job_name, wrapper_name):
        """
        - app: ScadeOne instance
        - tmp_path: Path to the target directory
        - job_name: Job name, corresponding to "Name" field in .sjob file generated
        - wrapper_name: Name of the generated wrapper
        - inputs: List of the root operator inputs to be tested
        - outputs: List of the expected root operator outputs
        """
        self._generate_wrapper(wrapper_projects["default"], job_name, wrapper_name, tmp_path)

    @pytest.mark.parametrize(
        ("operator_name", "job_name", "wrapper_name", "inputs", "outputs"),
        [
            ("function0_module0", "CGJob4Func", "fn_wrapper", [1, 2], [1, 2]),
            ("node0_module0", "CGJob4Node", "n_wrapper", [1, 2], [3, 1]),
        ],
    )
    def test_py_wrapper_op_ios(
        self, wrapper_projects, tmp_path, job_name, operator_name, wrapper_name, inputs, outputs
    ):
        """
        - app: ScadeOne instance
        - operator_name: Name of the generated root operator to test
        - job_name: Job name, corresponding to "Name" field in .sjob file generated
        - wrapper_name: Name of the generated wrapper
        - inputs: List of the root operator inputs to be tested
        - outputs: List of the expected root operator outputs
        """
        gen = self._generate_wrapper(wrapper_projects["default"], job_name, wrapper_name, tmp_path)

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = inputs[0]
        operator.inputs.i1 = inputs[1]
        operator.cycle()
        assert operator.outputs.o0 == outputs[0]
        assert operator.outputs.o1 == outputs[1]

    def test_specific_types(self, wrapper_projects, tmp_path):
        wrapper_name = "specific_types_wrapper"
        job_name = "CodeGenerationJob0"
        gen = self._generate_wrapper(
            wrapper_projects["wrapper_types"], job_name, wrapper_name, tmp_path
        )
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)

        op = wrapper_module.operator0_module0()
        op.inputs.i0 = 10
        op.inputs.i1 = 1
        op.inputs.i3 = 2.75
        assert op.inputs.i4 == wrapper_module.tColor_module0.GREEN
        op.inputs.i4 = wrapper_module.tColor_module0.ORANGE

        try:
            op.inputs.i5 = wrapper_module.tColor_module0.RED
            assert False
        except TypeError as e:
            assert str(e) == "i5 expected a tSize_TypesModule, but tColor_module0 was given."
        op.inputs.i5 = wrapper_module.tSize_TypesModule.Small
        op.inputs.i6 = True
        op.inputs.i7 = (1, 3.14)
        op.inputs.i8 = (1, 2)
        op.cycle()
        assert type(op.outputs.o0) is int
        assert type(op.outputs.o1) is int
        assert type(op.outputs.o3) is float
        assert type(op.outputs.o4) is wrapper_module.tColor_module0
        assert type(op.outputs.o5) is wrapper_module.tSize_TypesModule
        assert type(op.outputs.o6) is bool
        assert type(op.inputs.i7) is wrapper_module.tStruct_module0
        assert type(op.outputs.o7) is wrapper_module.tStruct_module0
        assert type(op.outputs.o7.x) is int
        assert type(op.outputs.o7.y) is float
        assert type(op.outputs.o8) is tuple
        assert op.outputs.o0 == 10
        assert op.outputs.o1 == -9
        assert op.outputs.o3 == 2.75
        assert op.outputs.o4 == wrapper_module.tColor_module0.ORANGE
        assert op.outputs.o5 == wrapper_module.tSize_TypesModule.Small
        assert op.outputs.o6 is True
        assert op.outputs.o7 == (1, 3.14)
        assert op.outputs.o8 == (1, 2)

        op.inputs.i7.y = 7.55
        op.cycle()
        assert op.outputs.o7 == wrapper_module.tStruct_module0(1, 7.55)
        assert op.outputs.o7 == (1, 7.55)

    @pytest.mark.parametrize(
        ("operator_name", "job_name", "wrapper_name", "sensors_values", "output"),
        [
            ("opSensor0_module0", "CGJob4OpSensor", "sensor_wrapper", [1, 2.0], 3),
        ],
    )
    def test_py_wrapper_op_sensors(
        self,
        wrapper_projects,
        tmp_path,
        job_name,
        operator_name,
        wrapper_name,
        sensors_values,
        output,
    ):
        """
        - app: ScadeOne instance
        - operator_name: Name of the generated root operator to test
        - job_name: Job name, corresponding to "Name" field in .sjob file generated
        - wrapper_name: Name of the generated wrapper
        - inputs: List of the root operator inputs to be tested
        - outputs: List of the expected root operator outputs
        """
        gen = self._generate_wrapper(wrapper_projects["default"], job_name, wrapper_name, tmp_path)
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator = getattr(wrapper_module, operator_name)()
        sensors = getattr(wrapper_module, "sensors")
        sensors.sensor0 = sensors_values[0]
        sensors.sensor1 = sensors_values[1]
        operator.cycle()
        assert operator.outputs.o0 == output

    @pytest.mark.parametrize(
        ("job_name", "wrapper_name", "inputs", "outputs"),
        [
            (
                "CGMultiRoots",
                "wrapper",
                {"node_module": [1, 2], "fn_module": [1, 2]},
                {"node_module": [3, 1], "fn_module": [1, 2]},
            ),
        ],
    )
    def test_multi_roots(self, wrapper_projects, tmp_path, job_name, wrapper_name, inputs, outputs):
        gen = self._generate_wrapper(wrapper_projects["default"], job_name, wrapper_name, tmp_path)
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)

        node_name = "node0_module0"
        node = getattr(wrapper_module, node_name)()
        node.inputs.i0 = inputs["node_module"][0]
        node.inputs.i1 = inputs["node_module"][1]
        node.cycle()
        assert node.outputs.o0 == outputs["node_module"][0]
        assert node.outputs.o1 == outputs["node_module"][1]
        fn_name = "function0_module0"
        fn = getattr(wrapper_module, fn_name)()
        fn.inputs.i0 = inputs["fn_module"][0]
        fn.inputs.i1 = inputs["fn_module"][1]
        fn.cycle()
        assert fn.outputs.o0 == outputs["fn_module"][0]
        assert fn.outputs.o1 == outputs["fn_module"][1]

    @pytest.mark.parametrize(
        ("job_name", "wrapper_name", "input_", "output"),
        [
            (
                "CG4Array",
                "array_wrapper",
                ((1, 2), (3, 4), (5, 6)),
                ((1, 2), (3, 4), (5, 6)),
            ),
        ],
    )
    def test_array_type(self, wrapper_projects, tmp_path, job_name, wrapper_name, input_, output):
        gen = self._generate_wrapper(wrapper_projects["default"], job_name, wrapper_name, tmp_path)

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)

        node_name = "arrayOp_module0"
        node = getattr(wrapper_module, node_name)()
        node.inputs.i0 = input_
        node.cycle()
        assert len(node.outputs.o0) == 3
        assert node.outputs.o0 == output

    def test_wrapper_cli(self, scadeone_install_path, wrapper_projects, tmp_path):
        project_path = wrapper_projects["default"].storage.path
        job_name = "CGJob4Func"
        wrapper_name = "cli_wrapper"

        old_sys_argv = sys.argv
        sys.argv = [
            "<cmd name>",
            "pycodewrap",
            "--install-dir",
            scadeone_install_path,
            "-j",
            job_name,
            "-o",
            wrapper_name,
            "--target-dir",
            str(tmp_path),
            str(project_path),
        ]
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.type is SystemExit
        assert e.value.code == 0
        sys.argv = old_sys_argv

        assert self._generation_ok(tmp_path / wrapper_name)

    @pytest.mark.parametrize(
        ("operator_name", "job_name"),
        [
            ("operator0_module0", "CodeGen"),
            ("operator0_elab_module0_elab", "CodeGen_elab"),
        ],
    )
    def test_elaboration(self, wrapper_projects, tmp_path, operator_name, job_name):
        wrapper_name = "elab_wrapper"
        gen = self._generate_wrapper(
            wrapper_projects["elaboration"], job_name, wrapper_name, tmp_path
        )
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = True
        operator.cycle()
        assert operator.outputs.o0 == 9
        operator.inputs.i0 = False
        operator.cycle()
        assert operator.outputs.o0 == -1

    def test_external_code_func(self, wrapper_projects, tmp_path):
        wrapper_name = "imported_code_func_wrapper"
        gen = self._generate_wrapper(
            wrapper_projects["imported_code_textual_func"],
            "CodeGenerationJob0",
            wrapper_name,
            tmp_path,
        )

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator_path_name = "module0::test_func"
        operator_name = self._format_name(operator_path_name)
        operator = getattr(wrapper_module, operator_name)()
        assert operator_name == "test_func_module0"
        operator.inputs.i0 = (0, 1, 2, 3)
        operator.cycle()
        assert operator.outputs.o0 == (5, 10, 15, 20)

    def test_external_code_node(self, wrapper_projects, tmp_path):
        wrapper_name = "imported_code_node_wrapper"
        gen = self._generate_wrapper(
            wrapper_projects["imported_code_textual_node"],
            "CodeGenerationJob0",
            wrapper_name,
            tmp_path,
        )

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator_path_name = "module0::test_node"
        operator_name = self._format_name(operator_path_name)
        operator = getattr(wrapper_module, operator_name)()
        assert operator_name == "test_node_module0"
        operator.inputs.i0 = (0, 1, 2, 3)
        operator.cycle()
        assert operator.outputs.o0 == (0, 10, 20, 30)

    # @pytest.mark.skip(reason="Need Scade One library")
    def test_external_code_dependencies(self, wrapper_projects, tmp_path, capsys):
        wrapper_name = "imported_code_dependencies_wrapper"
        gen = self._generate_wrapper(
            wrapper_projects["imported_code_incl_deps"],
            "CodeGenerationJob0",
            wrapper_name,
            tmp_path,
        )
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator_path_name = "M::root"
        operator_name = self._format_name(operator_path_name)
        operator = getattr(wrapper_module, operator_name)()
        assert operator_name == "root_M"
        operator.inputs.i0 = 3
        operator.cycle()
        assert operator.outputs.o0 == 9

    @pytest.mark.parametrize(
        ("path_opt", "env_var", "config", "expected"),
        [
            (None, None, None, False),
            # check --install-dir
            ("std", None, None, True),
            ("fake", None, None, False),
            # check env
            (None, "std", None, True),
            (None, "fake", None, False),
            # check config generation
            (None, None, True, True),
            # priority of options: CLI > env var
            ("std", "fake", None, True),
            ("fake", None, True, False),
        ],
    )
    def test_installation(
        self,
        path_opt,
        env_var,
        config,
        expected,
        scadeone_install_path,
        wrapper_projects,
        mockup_installation,
        tmp_path,
        capsys,
    ):
        cmd = ["pyscadeone", "pycodewrap"]
        # handle --install-dir option
        if path_opt:
            cmd += ["--install-dir", scadeone_install_path if path_opt == "std" else "/fake/path"]
        default_proj_path = wrapper_projects["default"].storage.path
        cmd += [
            "--job",
            "CGJob4Func",
            "--target-dir",
            str(tmp_path),
            str(default_proj_path),
        ]
        # handle environment variable
        new_env = None
        if env_var:
            new_env = {
                "SCADE_ONE_INSTALL_DIR": scadeone_install_path if env_var == "std" else "/fake/path"
            }
        # handle optional config generation
        mockup_installation(config)
        # trace
        with capsys.disabled():
            cmd_str = "' '".join(cmd)
            print(f"Running command:\n'{cmd_str}'\nwith env var {new_env}")

        # cli call with args and env var
        exit_code = -1
        with SysContext(args=cmd, env_vars=new_env):
            with pytest.raises(SystemExit) as e:
                cli.main()
            exit_code = cast(SystemExit, e).value.code
        assert expected == (exit_code == 0)
