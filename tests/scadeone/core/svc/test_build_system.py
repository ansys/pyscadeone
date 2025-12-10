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

from pathlib import Path

import pytest

from ansys.scadeone.core.svc.build_system import BuildConfig, BuildSystem, Target, TargetKind


class TestBuildSystem:
    @pytest.fixture
    def models_path(self):
        return Path(__file__).parents[3] / "models/build_system"

    @pytest.fixture
    def wrapper_c_files(self, models_path):
        c_dir = models_path / "wrapper"
        c_dir = c_dir.resolve()
        return [str(file) for file in c_dir.glob("*.c")]

    @pytest.fixture
    def wrapper_def_files(self, models_path):
        c_dir = models_path / "wrapper"
        c_dir = c_dir.resolve()
        return [str(file) for file in c_dir.glob("*.def")]

    @pytest.fixture
    def out_dir(self):
        return Path(__file__).parents[3] / "out/build_system"

    def test_exe_build(self, scadeone_install_path, out_dir, models_path):
        cfg = BuildConfig()
        cfg.working_dir = str(out_dir / "simple_exe")
        cfg.c_files = [str(models_path / "simple" / "simple.c")]
        cfg.targets = [Target("simple", TargetKind.EXECUTABLE)]
        builder = BuildSystem(scadeone_install_path)
        result = builder.build(cfg)
        assert result.is_succeeded
        exe = Path(cfg.working_dir) / "simple.exe"
        assert exe.exists()

    def test_fail_build(self, scadeone_install_path, out_dir, models_path):
        cfg = BuildConfig()
        cfg.working_dir = str(out_dir / "simple_wrong_c_location")
        cfg.c_files = [str(models_path / "simple" / "simple_not_found.c")]
        cfg.targets = [Target("simple", TargetKind.EXECUTABLE)]
        builder = BuildSystem(scadeone_install_path)
        result = builder.build(cfg)
        assert not result.is_succeeded
        assert len(result.messages) == 1
        assert "failed to build" in result.messages[0]

    def test_shared_lib_build(self, scadeone_install_path, out_dir, models_path):
        cfg = BuildConfig()
        cfg.working_dir = str(out_dir / "simple_lib")
        cfg.c_files = [str(models_path / "simple" / "simple_lib.c")]
        cfg.targets = [Target("simple_lib", TargetKind.SHARED_LIBRARY)]
        builder = BuildSystem(scadeone_install_path)
        result = builder.build(cfg)
        assert result.is_succeeded
        lib = Path(cfg.working_dir) / "simple_lib.dll"
        assert lib.exists()

    def test_wrapper_build(
        self, scadeone_install_path, out_dir, wrapper_c_files, wrapper_def_files
    ):
        cfg = BuildConfig()
        cfg.working_dir = str(out_dir / "wrapper")
        cfg.c_files = wrapper_c_files
        cfg.o_files = wrapper_def_files
        cfg.targets = [Target("module0", TargetKind.SHARED_LIBRARY)]
        builder = BuildSystem(scadeone_install_path)
        result = builder.build(cfg)
        assert result.is_succeeded
        wrapper = Path(cfg.working_dir) / "module0.dll"
        assert wrapper.exists()
