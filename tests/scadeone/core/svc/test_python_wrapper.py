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
import platform
import importlib
from os.path import getsize, isfile
from pathlib import Path
import shutil
import sys
import ctypes
import pytest
from typing import Union

from ansys.scadeone.core import ScadeOne, cli
from ansys.scadeone.core.job import Job
from ansys.scadeone.core.svc.wrapper import PythonWrapper

wrapper_model_path = Path(__file__).parents[4] / "tests/models/wrapper"

default_project_path = "project/project.sproj"


@pytest.fixture(scope="module")
def app():
    return ScadeOne("C:/Scade One")


@pytest.fixture(scope="module")
def output_path():
    return Path(__file__).parents[3] / "wrapper_out"


class ModuleUnloader:
    """Class to unload the generated module from memory. This is needed to
    to delete the generated .DLLs.

    The DLL can be unloaded only when there is no more objects using it.
    This is case when all operators have been deleted. This class registers
    the DLL handle to unload it whehn the ModuleUnloader object is deleted.

    Usage, in that order:
        unloader = ModuleUnloader(operator)
        del operator
        del unloader

    FIXME: work on Windows only.
    """

    _kernel32 = None

    def __init__(self, operator):
        module = sys.modules[operator.__module__]
        self._handle = module._lib._handle
        ModuleUnloader.set_kernel32()

    @classmethod
    def set_kernel32(cls):
        if platform.system() != "Windows":
            return
        if cls._kernel32 is None:
            # Load the kernel32 DLL and set the argument types for FreeLibrary
            # to avoid the need to use ctypes.windll which expects int = int32, too short for a pointer.
            # https://stackoverflow.com/questions/359498/how-can-i-unload-a-dll-using-ctypes-in-python
            # look end of file.
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.FreeLibrary.argtypes = [ctypes.wintypes.HMODULE]
            cls._kernel32 = kernel32

    def __del__(self):
        if platform.system() != "Windows":
            return
        ModuleUnloader._kernel32.FreeLibrary(self._handle)


class TestPythonWrapper:
    _list_expected = ["h", "c", "def", "py"]

    _kernel32 = None

    def _generate_wrapper(
        self, app: ScadeOne, job_name, wrapper_name, output_path, project_path: str = None
    ):
        """Generate the wrapper code and load the module.

        Parameters
        ----------
        app : Scade One instance
            The app.
        job_name : str
            Job name
        wrapper_name : str
            Generated wrapper name
        output_path : Path
            Path to the target directory.
        project_path : str, optional
            Specific project, in `wrapper_model_path` folder, by default None

        Returns
        -------
        Job, PythonWrapper
            Job object and PythonWrapper object.
        """
        if project_path is None:
            project_path = default_project_path
        full_project_path = wrapper_model_path / project_path
        project = app.load_project(str(full_project_path))
        assert project
        project.load_jobs()
        cg_job = project.get_job(job_name)
        result = cg_job.run()
        assert result.code == 0
        _gen = PythonWrapper(
            project=project,
            job=job_name,
            output=wrapper_name,
            target_dir=output_path,
        )
        _gen.generate()

        assert self._generation_ok(output_path / wrapper_name)
        return cg_job, _gen

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

    def _load_wrapper_module(self, wrapper_name: str, gen: PythonWrapper):
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

    @staticmethod
    def _remove_generated_files(cg_job: Job, gen: Union[PythonWrapper, Path]) -> None:
        """Remove the generated files after the test.

        Parameters
        ----------
        cg_job : Job
            Job where to find code generation files.
        gen : Union[PythonWrapper, Path]
            Where to find the generated files by the Python wrapper. Either a Path
            or a PythonWrapper object, which has a _target_dir() method.
        """
        job_path = cg_job.storage.path.parent
        shutil.rmtree(job_path / "out", ignore_errors=True)
        for file in job_path.glob("*.json"):
            file.unlink()
        target_path = gen._target_dir() if isinstance(gen, PythonWrapper) else gen
        shutil.rmtree(target_path, ignore_errors=True)

    def test_wrapper_one_output(self, app, output_path):
        wrapper_name = "one_output_wrapper"
        cg_job, gen = self._generate_wrapper(app, "CGJob4OneOutput", wrapper_name, output_path)

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator_path_name = "module0::oneOutput"
        operator_name = self._format_name(operator_path_name)
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = 1
        operator.cycle()
        assert operator.outputs.o0 == 1

        # Clean up the generated files
        unloader = ModuleUnloader(operator)
        del operator
        del unloader
        self._remove_generated_files(cg_job, gen)

    @pytest.mark.parametrize(
        ("job_name", "wrapper_name"),
        [
            ("CGJob4Func", "fn_wrapper"),
            ("CGJob4Node", "n_wrapper"),
        ],
    )
    def test_py_wrapper(self, app, output_path, job_name, wrapper_name):
        """
        - app: ScadeOne instance
        - output_path: Path to the target directory
        - job_name: Job name, corresponding to "Name" field in .sjob file generated
        - wrapper_name: Name of the generated wrapper
        - inputs: List of the root operator inputs to be tested
        - outputs: List of the expected root operator outputs
        """

        cg_job, gen = self._generate_wrapper(app, job_name, wrapper_name, output_path)
        self._remove_generated_files(cg_job, gen)

    @pytest.mark.parametrize(
        ("operator_name", "job_name", "wrapper_name", "inputs", "outputs"),
        [
            ("function0_module0", "CGJob4Func", "fn_wrapper", [1, 2], [1, 2]),
            ("node0_module0", "CGJob4Node", "n_wrapper", [1, 2], [3, 1]),
        ],
    )
    def test_py_wrapper_op_ios(
        self, app, output_path, job_name, operator_name, wrapper_name, inputs, outputs
    ):
        """
        - app: ScadeOne instance
        - operator_name: Name of the generated root operator to test
        - job_name: Job name, corresponding to "Name" field in .sjob file generated
        - wrapper_name: Name of the generated wrapper
        - inputs: List of the root operator inputs to be tested
        - outputs: List of the expected root operator outputs
        """
        cg_job, gen = self._generate_wrapper(app, job_name, wrapper_name, output_path)

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = inputs[0]
        operator.inputs.i1 = inputs[1]
        operator.cycle()
        assert operator.outputs.o0 == outputs[0]
        assert operator.outputs.o1 == outputs[1]

        # Clean up the generated files
        unloader = ModuleUnloader(operator)
        del operator
        del unloader
        self._remove_generated_files(cg_job, gen)

    def test_specific_types(self, app, output_path):
        wrapper_name = "specific_types_wrapper"
        job_name = "CodeGenerationJob0"
        cg_job, gen = self._generate_wrapper(
            app, job_name, wrapper_name, output_path, "wrapper_types/project.sproj"
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
        assert op.outputs.o0 == 10
        assert op.outputs.o1 == -9
        assert op.outputs.o3 == 2.75
        assert op.outputs.o4 == wrapper_module.tColor_module0.ORANGE
        assert op.outputs.o5 == wrapper_module.tSize_TypesModule.Small
        assert op.outputs.o6 is True
        assert op.outputs.o7 == (1, 3.14)
        op.inputs.i7.y = 7.55
        op.cycle()
        assert op.outputs.o7 == wrapper_module.tStruct_module0(1, 7.55)
        assert op.outputs.o7 == (1, 7.55)

        # Clean up the generated files
        unloader = ModuleUnloader(op)
        del op
        del unloader
        self._remove_generated_files(cg_job, gen)

    @pytest.mark.parametrize(
        ("operator_name", "job_name", "wrapper_name", "sensors_values", "output"),
        [
            ("opSensor0_module0", "CGJob4OpSensor", "sensor_wrapper", [1, 2.0], 3),
        ],
    )
    def test_py_wrapper_op_sensors(
        self, app, output_path, job_name, operator_name, wrapper_name, sensors_values, output
    ):
        """
        - app: ScadeOne instance
        - operator_name: Name of the generated root operator to test
        - job_name: Job name, corresponding to "Name" field in .sjob file generated
        - wrapper_name: Name of the generated wrapper
        - inputs: List of the root operator inputs to be tested
        - outputs: List of the expected root operator outputs
        """
        cg_job, gen = self._generate_wrapper(app, job_name, wrapper_name, output_path)
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator = getattr(wrapper_module, operator_name)()
        sensors = getattr(wrapper_module, "sensors")
        sensors.sensor0 = sensors_values[0]
        sensors.sensor1 = sensors_values[1]
        operator.cycle()
        assert operator.outputs.o0 == output

        # Clean up the generated files
        unloader = ModuleUnloader(operator)
        del operator
        del unloader
        self._remove_generated_files(cg_job, gen)

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
    def test_multi_roots(self, app, output_path, job_name, wrapper_name, inputs, outputs):
        cg_job, gen = self._generate_wrapper(app, job_name, wrapper_name, output_path)
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

        # Clean up the generated files
        unloader = ModuleUnloader(node)
        del node
        del unloader

        self._remove_generated_files(cg_job, gen)

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
    def test_array_type(self, app, output_path, job_name, wrapper_name, input_, output):
        cg_job, gen = self._generate_wrapper(app, job_name, wrapper_name, output_path)

        wrapper_module = self._load_wrapper_module(wrapper_name, gen)

        node_name = "arrayOp_module0"
        node = getattr(wrapper_module, node_name)()
        node.inputs.i0 = input_
        node.cycle()
        assert len(node.outputs.o0) == 3
        assert node.outputs.o0 == output

        # Clean up the generated files
        unloader = ModuleUnloader(node)
        del node
        del unloader

        self._remove_generated_files(cg_job, gen)

    def test_wrapper_cli(self, app, output_path):
        # Generate code before running the CLI
        project_path = wrapper_model_path / default_project_path
        job_name = "CGJob4Func"
        project = app.load_project(project_path)
        project.load_jobs()
        cg_job = project.get_job(job_name)
        result = cg_job.run()
        assert result.code == 0, "Error in job execution"

        wrapper_name = "cli_wrapper"
        project.load_jobs()

        old_sys_argv = sys.argv
        sys.argv = [
            "<cmd name>",
            "pycodewrap",
            "--install-dir",
            "C:/Scade One",
            "-j",
            job_name,
            "-o",
            wrapper_name,
            "--target-dir",
            str(output_path),
            str(project_path),
        ]
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.type is SystemExit
        assert e.value.code == 0
        sys.argv = old_sys_argv

        assert self._generation_ok(output_path / wrapper_name)

        self._remove_generated_files(cg_job, output_path)

    def test_elaboration(self, app, output_path):
        wrapper_name = "elab_wrapper"
        cg_job, gen = self._generate_wrapper(
            app, "CodeGen", wrapper_name, output_path, "elaboration/elaboration.sproj"
        )
        wrapper_module = self._load_wrapper_module(wrapper_name, gen)
        operator_name = "operator0_module0"
        operator = getattr(wrapper_module, operator_name)()
        operator.inputs.i0 = True
        operator.cycle()
        assert operator.outputs.o0 == 9
        operator.inputs.i0 = False
        operator.cycle()
        assert operator.outputs.o0 == -1
        # Clean up the generated files
        unloader = ModuleUnloader(operator)
        del operator
        del unloader
        self._remove_generated_files(cg_job, gen)
