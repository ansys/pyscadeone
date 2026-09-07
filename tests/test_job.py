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

import json
import pytest
import shutil
from pathlib import Path
from typing import cast

from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.job import JobType, CodeGenerationJob
from ansys.scadeone.core.svc.swan_creator.job_creator import JobFactory


@pytest.fixture(scope="session")
def config_mockup(scadeone_install_path):
    module_location_config_path = ScadeOne()._Tools.generate_config(scadeone_install_path)
    yield module_location_config_path
    if module_location_config_path.exists():
        module_location_config_path.unlink()


def job_param_eq(job_param, value) -> bool:
    if not value:
        return not job_param or job_param == [""]
    if type(job_param) is type(value):
        return job_param == value
    if isinstance(job_param, list):
        return len(job_param) == 1 and job_param[0] == value
    elif isinstance(value, list):
        return len(value) == 1 and value[0] == job_param
    return False


class TestModel:
    def test_get_jobs(self, tmp_cc_project):
        app = ScadeOne()
        project = app.load_project(tmp_cc_project)
        assert project
        project.load_jobs()
        jobs = project.jobs
        assert len(jobs)
        job_none = project.get_job("CodeGen1")
        assert not job_none
        job = project.get_job("CodeGen")
        assert job

    def test_migrate_job_21_to_current(self, tmp_path: Path):
        app = ScadeOne()

        new_test_project_dir = tmp_path / "test_job_v21"
        shutil.copytree("tests/models/job_migration/test_job_v21", new_test_project_dir)

        project_path = new_test_project_dir / "test_job_v21.sproj"

        project = app.load_project(project_path)
        assert project
        jobs_v21 = project.load_jobs()

        expected_jobs_files = 4

        jobs_files = list(Path(new_test_project_dir).glob("**/*.sjob"))
        assert len(jobs_files) == expected_jobs_files

        for sjob_file in jobs_files:
            with sjob_file.open("r", encoding="utf-8") as f:
                sjob_content = json.load(f)
            assert sjob_content.get("Version") == "2.1"

        for job in jobs_v21:
            # Force saving job to migrate to the current version
            job.save()

        # Test nb job files after saving.
        jobs_files = list(Path(new_test_project_dir).glob("**/*.sjob"))
        assert len(jobs_files) == expected_jobs_files

        for sjob_file in jobs_files:
            with sjob_file.open("r", encoding="utf-8") as f:
                sjob_content = json.load(f)
            version_job_current = FormatVersions.version("sjob")
            assert sjob_content.get("Version") == version_job_current
            assert "ShortCircuitOperators" not in sjob_content.get("Properties", {})

    def test_run_jobs(self, tmp_cc_project, scadeone_install_path):
        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        assert project
        project.load_jobs()
        job_to_run = project.get_job("CodeGen")
        assert job_to_run
        res = job_to_run.run()
        assert res.code == 0  # Success

    def test_run_jobs_configuration(self, tmp_cc_project, config_mockup):
        # The configuration file is generated with the correct paths,
        # so the job should run successfully.
        app = ScadeOne(None)  # Don't pass install path to use the generated config_mockup
        project = app.load_project(tmp_cc_project)
        assert project
        project.load_jobs()
        job_to_run = project.get_job("CodeGen")
        assert job_to_run
        res = job_to_run.run()
        assert res.code == 0  # Success

    def test_create_jobs(self, tmp_cc_project, scadeone_install_path):
        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        assert project
        empty_job = JobFactory.new_job(JobType.SIMULATION, "EmptyJob", project)

        res = empty_job.run()
        assert res.code == 4  # JobNotFound
        empty_job.save()
        res = empty_job.run()
        assert res.code == 5  # JobFailure

        new_job = JobFactory.new_job(JobType.CODE_GENERATION, "TempCodeGen", project)
        new_job.input_paths = "assets/CC.swan"
        new_job.properties.root_declarations = "CC::CruiseControl"
        new_job.save()
        res = new_job.run()
        assert res.code == 0  # Success

        empty_job.delete()
        new_job.delete()

    def test_duplicate_job(self, tmp_cc_project, scadeone_install_path):
        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        assert project
        project.load_jobs()
        job_original = cast(CodeGenerationJob, project.get_job("CodeGen"))
        job = cast(
            CodeGenerationJob, JobFactory.new_job(JobType.CODE_GENERATION, "CodeGen", project)
        )
        job.input_paths = job_original.input_paths.copy()
        job.root_declarations = job_original.root_declarations.copy()
        job.expansion = job_original.expansion
        job.expansion_exp = job_original.expansion_exp
        job.expansion_no_exp = job_original.expansion_no_exp
        job.name_length = job_original.name_length
        if job_original.max_function_parameters is not None:
            job.max_function_parameters = job_original.max_function_parameters
        job.keep_assume = job_original.keep_assume
        job.globals_prefix = job_original.globals_prefix
        job.use_macros = job_original.use_macros
        job.static_locals = job_original.static_locals
        job.with_probes = job_original.with_probes
        job.save()

        assert job.name == job_original.name

        res = job.run()
        assert res.code == 6  # JobNameDuplicate

        job.delete()

    @pytest.mark.parametrize(
        "job_type,job_name,input_paths,root_declarations,custom_arguments",
        [
            [JobType.SIMULATION, "name1", ["assets/CC.swan"], None, None],
            [JobType.CODE_GENERATION, "name2", None, ["CC::CruiseControl"], "Something"],
            [JobType.TEST_EXECUTION, "name3", "assets/CC.swan", "CC::CruiseControl", ""],
            [JobType.MODEL_CHECK, "name4", "assets/CC.swan", "CC::CruiseControl", None],
        ],
    )
    def test_all_kinds_jobs(
        self,
        tmp_cc_project,
        scadeone_install_path,
        job_type,
        job_name,
        input_paths,
        root_declarations,
        custom_arguments,
    ):
        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        assert project
        job = JobFactory.new_job(job_type, job_name, project)
        if input_paths:
            job.input_paths = input_paths
        if root_declarations:
            job.root_declarations = root_declarations
        if custom_arguments:
            job.custom_arguments = custom_arguments
        job.save()

        project.load_jobs()
        created_job = project.get_job(job_name)
        assert created_job
        assert created_job.name == job_name
        assert created_job._kind == job_type
        assert job_param_eq(created_job.input_paths, input_paths)
        assert job_param_eq(created_job.root_declarations, root_declarations)
        assert job_param_eq(created_job.custom_arguments, custom_arguments)

        job.delete()

    def test_project_add_delete_job(self, tmp_cc_project, scadeone_install_path):
        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        project.load_jobs()
        assert len(project.jobs) == 1

        added_job = project.add_job(JobType.SIMULATION, "MySimulation")
        assert added_job.name == "MySimulation"
        project.load_jobs()
        assert len(project.jobs) == 2

        loaded_job = project.get_job("MySimulation")
        assert loaded_job is not None
        assert loaded_job.storage is not None

        project.delete_job(loaded_job)
        project.load_jobs()
        assert len(project.jobs) == 1
        assert project.get_job("MySimulation") is None

    def test_add_remove_asset(self, tmp_cc_project, scadeone_install_path):
        import ansys.scadeone.core.assets as assets

        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        assert project
        project.load_jobs()
        project.directory
        jobs = project.jobs
        assert len(jobs)
        job_gen = project.get_job("CodeGen")
        assert job_gen is not None
        project.add_module_body("module0")
        project.save()
        asset = None
        for a in project.assets:
            if (
                isinstance(a, assets.ModuleBodyAsset)
                and a.path.as_posix() == Path("assets/module0.swan").as_posix()
            ):
                asset = a
                break
        assert asset is not None
        assert len(job_gen.input_assets) == 1
        job_gen.add_asset(asset)
        assert len(job_gen.input_assets) == 2
        job_gen.remove_asset(asset)
        assert len(job_gen.input_assets) == 1

    def test_job_output_assets(self, tmp_cc_project, scadeone_install_path):
        import ansys.scadeone.core.assets as assets

        app = ScadeOne(scadeone_install_path)
        project = app.load_project(tmp_cc_project)
        assert project
        project.load_jobs()

        job = project.get_job("CodeGen")
        assert job is not None

        output_assets = job.output_assets
        assert isinstance(output_assets, list)
        assert len(output_assets) > 0
        asset = output_assets[0]
        assert asset is not None
        assert isinstance(asset, assets.GeneratedCodeAsset)
