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

import os
import importlib
from os.path import getsize, isfile
from pathlib import Path
import shutil
import sys

import pytest

from ansys.scadeone.core import ScadeOne, cli
from ansys.scadeone.core.job import Job
from ansys.scadeone.core.svc.generated_code import GeneratedCode
from ansys.scadeone.core.svc.wrapper.python_wrapper import PythonWrapper

project_path = str(Path(__file__).parents[4] / "tests/models/wrapper/project.sproj")


@pytest.fixture(scope="module")
def app():
    return ScadeOne("C:/Scade One")


class TestPythonWrapper:
    _list_expected = ["h", "c", "def", "py"]

    def _generation_ok(self, cg_job: Job) -> bool:
        # Verify that the generation is good or failed.
        file = cg_job.storage.path.parent / "out/code/py_wrapper_files.txt"
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
    def _remove_generated_files(cg_job: Job) -> None:
        job_path = cg_job.storage.path.parent
        shutil.rmtree(job_path / "out", ignore_errors=True)
        for file in job_path.glob("*.json"):
            file.unlink()

    def test_wrapper_one_output(self, app):
        project = app.load_project(project_path)
        project.load_jobs()
        cg_job = project.get_job("CGJob4OneOutput")
        result = cg_job.run()
        assert result.code == 0

        wrapper_name = "op_wrapper"
        operator_path_name = "module0::oneOutput"
        _code_gen = GeneratedCode(project, "CGJob4OneOutput")
        _gen = PythonWrapper(
            project=project, code_gen=_code_gen, opt_name=operator_path_name, out_name=wrapper_name
        )
        _gen.generate()

        _rtn = self._generation_ok(cg_job)
        assert _rtn is True

        wrapper_name = "op_wrapper"
        spec = importlib.util.spec_from_file_location(
            f"{wrapper_name}", f"{_gen._target_dir()}/{wrapper_name}.py"
        )
        wrapper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper_module)
        operator_name = operator_path_name.split("::")[-1]
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = 1
        operator.cycle()
        assert operator.outputs.o0 == 1

        self._remove_generated_files(cg_job)

    @pytest.mark.parametrize(
        ("operator_path_name", "job_name", "wrapper_name", "inputs", "outputs"),
        [
            ("module0::function0", "CGJob4Func", "fn_wrapper", [1, 2], [1, 2]),
            ("module0::node0", "CGJob4Node", "n_wrapper", [1, 2], [3, 1]),
        ],
    )
    def test_py_wrapper(self, app, job_name, operator_path_name, wrapper_name, inputs, outputs):
        """
        - project: Path of Swan project
        - job: Job name, corresponding to "Name" field in .sjob file generated
        - operator: Root operator name defined in "RootDeclarations" field of .sjob file
        Attention to that, now, the initial version is working with GeneratedCode class,
        so its inputs include job name, this must be changed in the next version.
        """

        project = app.load_project(project_path)
        project.load_jobs()
        cg_job = project.get_job(job_name)
        result = cg_job.run()
        assert result.code == 0

        _code_gen = GeneratedCode(project, job_name)
        _gen = PythonWrapper(
            project=project, code_gen=_code_gen, opt_name=operator_path_name, out_name=wrapper_name
        )
        _gen.generate()

        _rtn = self._generation_ok(cg_job)
        assert _rtn is True

        spec = importlib.util.spec_from_file_location(
            f"{wrapper_name}", f"{_gen._target_dir()}/{wrapper_name}.py"
        )
        wrapper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper_module)
        operator_name = operator_path_name.split("::")[-1]
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = inputs[0]
        operator.inputs.i1 = inputs[1]
        operator.cycle()
        assert operator.outputs.o0 == outputs[0]
        assert operator.outputs.o1 == outputs[1]

        self._remove_generated_files(cg_job)

    @pytest.mark.parametrize(
        "args",
        [
            (
                [
                    "wrapper",
                    project_path,
                    "CGJob4Func",
                    "module0::function0",
                ]
            ),
            (
                [
                    "wrapper",
                    project_path,
                    "CGJob4Func",
                    "module0::function0",
                    "-n",
                    "op_wrapper",
                ]
            ),
        ],
    )
    def test_wrapper_cli(self, args, app):
        prj = app.load_project(args[1])
        prj.load_jobs()
        cg_job = prj.get_job(args[2])
        result = cg_job.run()
        assert result.code == 0
        old_sys_argv = sys.argv
        sys.argv = [old_sys_argv[0]] + args
        cli.main()
        sys.argv = old_sys_argv
        _rtn = self._generation_ok(cg_job)
        assert _rtn is True
        self._remove_generated_files(cg_job)

    @staticmethod
    def _get_wrapper_name(args):
        if len(args) > 4 and args.index("-n"):
            return args[args.index("-n") + 1]
        return args[3].split("::")[1]
