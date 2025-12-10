from pathlib import Path
from typing import cast
from ansys.scadeone.core.common.versioning import FormatVersions

import json

import pytest

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


from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.job import Job, JobType, CodeGenerationJob

import shutil

from ansys.scadeone.core.svc.swan_creator.job_creator import JobFactory

s_one_install = "C:/Scade One"


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
    def test_get_jobs(self, cc_project):
        app = ScadeOne()
        project = app.load_project(cc_project)
        project.load_jobs()
        jobs = project.jobs
        assert len(jobs)
        job_none = project.get_job("CodeGen1")
        assert not job_none
        job = project.get_job("CodeGen")
        assert job

    def test_migrate_job_21_to_current(self, tmp_path: Path):
        app = ScadeOne(s_one_install)

        new_test_project_dir = tmp_path / "test_job_v21"
        shutil.copytree("tests/models/job_migration/test_job_v21", new_test_project_dir)

        project_path = new_test_project_dir / "test_job_v21.sproj"

        project = app.load_project(project_path)
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

    def test_run_jobs(self, cc_project):
        app = ScadeOne(s_one_install)
        project = app.load_project(cc_project)
        project.load_jobs()
        job_to_run = project.get_job("CodeGen")
        res = job_to_run.run()
        assert res.code == 0  # Success

    def test_create_jobs(self, cc_project):
        app = ScadeOne(s_one_install)
        project = app.load_project(cc_project)
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

        clear_temp_job(empty_job)
        clear_temp_job(new_job)

    def test_duplicate_job(self, cc_project):
        app = ScadeOne(s_one_install)
        project = app.load_project(cc_project)
        project.load_jobs()
        job_original = project.get_job("CodeGen")
        job = cast(
            CodeGenerationJob, JobFactory.new_job(JobType.CODE_GENERATION, "CodeGen", project)
        )
        job.input_paths = ["assets/CC.swan"]
        job.root_declarations = ["CC::CruiseControl"]
        job.expansion = None
        job.expansion_exp = ""
        job.properties.expansion_no_exp = ""  # Both setters (with/without properties) must work
        job.keep_assume = False
        job.use_macros = False
        job.static_locals = False
        job.save()
        res = job.run()
        assert res.code == 6  # JobNameDuplicate
        assert job_original == job
        clear_temp_job(job)

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
        self, cc_project, job_type, job_name, input_paths, root_declarations, custom_arguments
    ):
        app = ScadeOne(s_one_install)
        project = app.load_project(cc_project)
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
        assert created_job.name == job_name
        assert created_job._kind == job_type
        assert job_param_eq(created_job.input_paths, input_paths)
        assert job_param_eq(created_job.root_declarations, root_declarations)
        assert job_param_eq(created_job.custom_arguments, custom_arguments)

        clear_temp_job(job)


def clear_temp_job(job: Job):
    path = Path(job.storage.source).parent
    if path.exists():
        shutil.rmtree(path)
