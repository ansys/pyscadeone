import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.common.storage import ProjectFile


class TestModel:

    @pytest.mark.skip("JOB NYI")
    def test_jobs(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        jobs = project.jobs()
        assert True

    @pytest.mark.skip("JOB NYI")
    def test_code_gen(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        jobs = project.jobs()
        job = project.job_of_name(jobs[0])
        res = job.run()
        assert res
