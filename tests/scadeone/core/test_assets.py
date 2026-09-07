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
from pathlib import Path

import pytest

import ansys.scadeone.core.assets as assets
from ansys.scadeone.core.svc.cgmapping.cgmapping import CGMapping
import ansys.scadeone.core.swan as swan
from ansys.scadeone.core.project import Project
from ansys.scadeone.core.job import Job
from ansys.scadeone.core.svc.test import TestResults
from ansys.scadeone.core.svc.simdata import FileBase
from test_tools.utils import str_path


# To remove all job output
_remove_job_output = False


def generate_code(app, project_path):
    project = app.load_project(project_path)
    if not project:
        raise RuntimeError("Failed to load project.")
    project.load_jobs()
    for job in project.jobs:
        out = job.storage.path.parent / "out"
        if _remove_job_output:
            shutil.rmtree(str(out), ignore_errors=True)
        if out.exists():
            continue
        result = job.run()
        if result.code != 0:
            raise RuntimeError(f"Code generation job '{job.name}' failed with code {result.code}.")


@pytest.fixture(scope="module")
def assets_project():
    return Path("tests/models/assets_project/test_assets.sproj")


@pytest.fixture(scope="module", autouse=True)
def generate_code_for_test_projects(app, assets_project, cc_project):
    generate_code(app, assets_project)
    generate_code(app, cc_project)


class TestAssetProject:
    def test_asset_interface(self, app, cc_project):
        project = app.load_project(cc_project)
        asset = None
        for a in project.assets:
            if isinstance(a, assets.ModuleInterfaceAsset):
                asset = a
                break
        assert asset is not None
        assert str(asset.path) == str_path("assets", "CarTypes.swani")
        _open = asset.open()
        assert isinstance(_open, swan.ModuleInterface)
        assert str(_open.name) == "CarTypes"

    def test_asset_module(self, app, cc_project):
        project = app.load_project(cc_project)
        asset = None
        for a in project.assets:
            if isinstance(a, assets.ModuleBodyAsset) and str(a.path) == str_path(
                "assets", "CC.swan"
            ):
                asset = a
                break
        assert asset is not None
        _open = asset.open()
        assert isinstance(_open, swan.ModuleBody)
        assert len(asset.consumer_jobs) == 1

    def test_asset_test_module(self, app, tmp_path: Path):
        project_path = tmp_path / "project0" / "project0.sproj"
        project = app.new_project(project_path)
        assert project is not None
        assert isinstance(project, Project)
        project.add_module_body("module0")
        project.add_test_module("test0")
        project.save()
        asset = None
        for a in project.assets:
            if isinstance(a, assets.TestModuleAsset) and str(a.path) == str_path(
                "assets", "test0.swant"
            ):
                asset = a
                break
        assert asset is not None
        _open = asset.open()
        assert isinstance(_open, swan.TestModule)

    def test_asset_code_generation_open(self, app, assets_project):
        project = app.load_project(assets_project)
        assert project is not None
        asset = None
        for a in project.assets:
            if isinstance(a, assets.GeneratedCodeAsset) and str(a.job_name) == "CodeGenerationJob1":
                asset = a
                break
        assert asset is not None
        code_dir = asset.open()
        assert isinstance(code_dir, Path)

    def test_asset_code_gen_delete(self, app, assets_project, tmp_path: Path):
        src_dir = Path(assets_project).parents[1]
        tmp_project_dir = tmp_path / src_dir.name
        shutil.copytree(src_dir, tmp_project_dir)
        tmp_sproj = tmp_project_dir / "assets_project/test_assets.sproj"
        project = app.load_project(tmp_sproj)

        gen_asset = next(
            (
                a
                for a in project.assets
                if isinstance(a, assets.GeneratedCodeAsset)
                and str(a.job_name) == "CodeGenerationJob1"
            ),
            None,
        )
        assert gen_asset is not None
        gen_job = project.get_job(gen_asset.job_name)
        trace_dir = Path(gen_job.storage.source).parent / "out/code"
        assert gen_asset._delete() is None
        assert not trace_dir.exists()

    def test_asset_test_result_open(self, app, assets_project):
        project = app.load_project(assets_project)
        asset = None
        for a in project.assets:
            if isinstance(a, assets.TestResultsAsset) and str(a.job_name) == "TestExecutionJob0":
                asset = a
                break
        assert asset is not None
        result = asset.open()
        assert isinstance(result, TestResults)

    def test_asset_test_result_delete(self, app, assets_project, tmp_path: Path):
        src_dir = Path(assets_project).parents[1]
        tmp_project_dir = tmp_path / src_dir.name
        shutil.copytree(src_dir, tmp_project_dir)
        tmp_sproj = tmp_project_dir / "assets_project/test_assets.sproj"
        project = app.load_project(tmp_sproj)

        exe_asset = next(
            (
                a
                for a in project.assets
                if isinstance(a, assets.TestResultsAsset) and str(a.job_name) == "TestExecutionJob0"
            ),
            None,
        )
        assert exe_asset is not None
        exe_job = project.get_job(exe_asset.job_name)
        trace_dir = Path(exe_job.storage.source).parent / "out"
        assert exe_asset._delete() is None
        assert not (trace_dir / "testResults.json").exists()

    def test_asset_simulation_open(self, app, assets_project):
        project = app.load_project(assets_project)
        asset = None
        for a in project.assets:
            if isinstance(a, assets.SimulationDataAsset) and str(a.job_name) == "SimulationJob0":
                asset = a
                break
        assert asset is not None
        result = asset.open()
        try:
            assert isinstance(result, FileBase)
        finally:
            result.close()

    def test_asset_simulation_delete(self, app, assets_project, tmp_path: Path):
        src_dir = Path(assets_project).parents[1]
        tmp_project_dir = tmp_path / src_dir.name
        shutil.copytree(src_dir, tmp_project_dir)
        tmp_sproj = tmp_project_dir / "assets_project/test_assets.sproj"
        project = app.load_project(tmp_sproj)

        sim_asset = next(
            (
                a
                for a in project.assets
                if isinstance(a, assets.SimulationDataAsset) and str(a.job_name) == "SimulationJob0"
            ),
            None,
        )
        assert sim_asset is not None
        sim_job = project.get_job(sim_asset.job_name)
        trace_dir = Path(sim_job.storage.source).parent / "out"
        assert sim_asset._delete() is None
        assert not (trace_dir / "trace.sd").exists()

    def test_add_assets(self, app, tmp_path: Path):
        project_path = tmp_path / "project0" / "project0.sproj"
        project = app.new_project(project_path)
        assert project is not None
        assert isinstance(project, Project)
        assets = len(project.assets)
        assert assets == 0
        project.add_module_body("module0")
        project.save()
        assert len(project.assets) == assets + 1
        project.add_module_interface("interface0")
        project.save()
        assert len(project.assets) == assets + 2
        project.add_test_module("test0")
        project.save()
        assert len(project.assets) == assets + 3

    def test_producer_job_asset(self, app, assets_project):
        project = app.load_project(assets_project)
        asset = None
        for a in project.assets:
            if isinstance(a, assets.GeneratedCodeAsset) and str(a.job_name) == "CodeGenerationJob1":
                asset = a
                break
        assert asset is not None
        # Producer job
        producer = asset.producer_job
        if isinstance(producer, Job):
            code_dir = asset.open()
            assert isinstance(code_dir, Path)

    def test_asset_cgmap_open(self, app, assets_project):
        project = app.load_project(assets_project)
        asset = None
        for a in project.assets:
            if isinstance(a, assets.CGMappingAsset) and str(a.job_name) == "CodeGenerationJob1":
                asset = a
                break
        assert asset is not None
        cgmap = asset.open()
        assert isinstance(cgmap, CGMapping)
        assert cgmap.get_statistics()["code_items"] > 1
