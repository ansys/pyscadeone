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

import pytest
from pathlib import Path

from ansys.scadeone.core.svc.build_system import (
    BuildSystem,
    Target,
    TargetKind,
    BuildRequest,
    BuildConfig,
)
from ansys.scadeone.core import ScadeOne
from test_tools import dotexe, platform_name  # type: ignore


class TestBuildSystem:
    @pytest.fixture
    def models_path(self):
        return Path(__file__).parents[3] / "models/build_system"

    @pytest.fixture
    def wrapper_path(self, models_path):
        return models_path / "wrapper"

    @pytest.fixture
    def wrapper_c_files(self, wrapper_path):
        job_dir = wrapper_path / "jobs/codegen"
        c_files = []
        for sub_dir in ["out/code", "python_" + platform_name]:
            c_dir = job_dir / sub_dir
            c_dir = c_dir.resolve()
            c_files.extend(str(file) for file in c_dir.glob("*.c"))
        return c_files

    @pytest.fixture
    def wrapper_def_files(self, wrapper_path):
        job_dir = wrapper_path / "jobs/codegen"
        c_dir = job_dir / ("python_" + platform_name)
        c_dir = c_dir.resolve()
        return [str(file) for file in c_dir.glob("*.def")]

    @pytest.fixture
    def app(self, scadeone_install_path):
        app = ScadeOne(install_dir=scadeone_install_path)
        return app

    def test_exe_build(self, app, tmp_path, models_path):
        request = BuildRequest()
        request.working_dir = str(tmp_path / "simple_exe")
        request.c_files = [str(models_path / "simple" / "simple.c")]
        request.targets = [Target("simple", TargetKind.EXECUTABLE)]
        builder = BuildSystem(app)
        result = builder.build(request)
        assert result.is_succeeded
        exe = dotexe(Path(request.working_dir) / "simple.exe")
        assert exe.exists()

    def test_fail_build(self, app, tmp_path, models_path):
        request = BuildRequest()
        request.working_dir = str(tmp_path / "simple_wrong_c_location")
        request.c_files = [str(models_path / "simple" / "simple_not_found.c")]
        request.targets = [Target("simple", TargetKind.EXECUTABLE)]
        builder = BuildSystem(app)
        result = builder.build(request)
        assert not result.is_succeeded
        assert "failed to build" in result.messages[-1]

    def test_shared_lib_build(self, app, tmp_path, models_path):
        request = BuildRequest()
        request.working_dir = str(tmp_path / "simple_lib")
        request.c_files = [str(models_path / "simple" / "simple_lib.c")]
        request.targets = [Target("simple_lib", TargetKind.SHARED_LIBRARY)]
        builder = BuildSystem(app)
        result = builder.build(request)
        assert result.is_succeeded
        lib = Path(request.working_dir) / (
            "simple_lib.dll" if platform_name == "win" else "libsimple_lib.so"
        )
        assert lib.exists()

    def test_wrapper_build(
        self, app, tmp_path, wrapper_path, wrapper_c_files, wrapper_def_files, capsys
    ):
        request = BuildRequest()
        build_config = BuildConfig()
        build_config.include_dirs = [str(wrapper_path)]
        request.build_config = build_config
        request.working_dir = str(tmp_path / "wrapper")
        request.c_files = wrapper_c_files
        request.o_files = wrapper_def_files
        request.targets = [Target("module0", TargetKind.SHARED_LIBRARY)]
        builder = BuildSystem(app)
        result = builder.build(request)
        with capsys.disabled():
            print(result.messages)
        assert result.is_succeeded
        wrapper = Path(request.working_dir) / (
            "module0.dll" if platform_name == "win" else "libmodule0.so"
        )
        assert wrapper.exists()

    def test_build_config_env_path_dirs(self):
        config = BuildConfig()
        assert config.env_path_dirs == []

        dirs = [str(Path("tools") / "bin"), str(Path("sdk") / "bin")]
        config.env_path_dirs = dirs
        assert config.env_path_dirs == dirs
