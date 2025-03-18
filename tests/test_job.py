from pathlib import Path
from typing import cast

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
        empty_job = JobFactory.new_job(JobType.SIMU, "EmptyJob", project)

        res = empty_job.run()
        assert res.code == 4  # JobNotFound
        empty_job.save()
        res = empty_job.run()
        assert res.code == 5  # JobFailure

        new_job = JobFactory.new_job(JobType.CODEGEN, "TempCodeGen", project)
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
        job = cast(CodeGenerationJob, JobFactory.new_job(JobType.CODEGEN, "CodeGen", project))
        job.input_paths = ["assets/CC.swan"]
        job.root_declarations = ["CC::CruiseControl"]
        job.expansion = None
        job.expansion_exp = ""
        job.properties.expansion_no_exp = ""  # Both setters (with/without properties) must work
        job.short_circuit_operators = False
        job.keep_assume = False
        job.use_macros = False
        job.static_locals = False
        job.save()
        res = job.run()
        assert res.code == 6  # JobNameDuplicate
        assert job_original == job
        clear_temp_job(job)


def clear_temp_job(job: Job):
    path = Path(job.storage.source).parent
    if path.exists():
        shutil.rmtree(path)
