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

import os
from pathlib import Path
from typing import cast

import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.project import Project, ProjectFile, ResourceKind
from ansys.scadeone.core.job import JobType
from ansys.scadeone.core.swan import swan_to_str


class TestProject:
    def test_wrong_project(self):
        app = ScadeOne()
        project = app.load_project("foo")
        assert project is None

    @staticmethod
    def resolve(path: str):
        return Path(path).resolve().as_posix()

    def test_assets(self, cc_project):
        app = ScadeOne()
        project = app.load_project(cc_project)
        sources = [swan_file.source for swan_file in project.swan_sources()]
        oracle = [
            TestProject.resolve(p)
            for p in [
                "examples/models/CC/CruiseControl/assets/CarTypes.swani",
                "examples/models/CC/CruiseControl/assets/CC.swan",
            ]
        ]
        # Linux is case-sensitive, while Windows not
        assert sorted(sources) == sorted(oracle)

    def test_all_assets(self, cc_project):
        app = ScadeOne()
        project = app.load_project(cc_project)
        sources = [swan_file.source for swan_file in project.swan_sources(all=True)]
        oracle = [
            TestProject.resolve(p)
            for p in [
                "examples/models/CC/CruiseControl/assets/CarTypes.swani",
                "examples/models/CC/CruiseControl/assets/CC.swan",
                "examples/models/CC/CruiseControl/../utils/assets/Utils.swan",
            ]
        ]
        assert sorted(sources) == sorted(oracle)

    def test_project_assets(self, cc_project):
        app = ScadeOne()
        p1 = app.load_project(cc_project)
        p2 = app.load_project(Path(cc_project))
        p3 = app.load_project(Project(app=app, project=ProjectFile(cc_project)))
        assert p1 and p2 and p3
        assert cast(ProjectFile, p1.storage).source == cast(ProjectFile, p2.storage).source
        assert cast(ProjectFile, p1.storage).source == cast(ProjectFile, p3.storage).source

    def test_multi_projects(self):
        app = ScadeOne()
        project = app.load_project("tests/models/multi_projects/top_level/top_level.sproj")
        swans = [swan_file.source for swan_file in project.swan_sources(True)]
        oracle = []
        for dirname, dirs, files in os.walk("tests/models/multi_projects"):
            if "circular" in dirname.split(os.sep):  # skip circular project used for another test
                continue
            if "other" in dirname.split(os.sep):  # skip other project used for another test
                continue
            for f in files:
                if os.path.splitext(f)[1] == ".swan":
                    p = Path(dirname) / f
                    oracle.append(p.resolve().as_posix())
        swans.sort()
        oracle.sort()
        assert swans == oracle

    def test_multi_projects_loads(self):
        app = ScadeOne()
        # Get top_level_project
        top_level = app.load_project("tests/models/multi_projects/top_level/top_level.sproj")
        assert top_level is not None
        # check that the projects are loaded
        assert len(app.projects) == 4
        # Get other_project
        other_project = app.load_project("tests/models/multi_projects/other/other.sproj")
        assert other_project is not None
        # check that only the new project is loaded.
        assert len(app.projects) == 5
        assert len(top_level.model.constants) == 2
        assert len(other_project.model.constants) == 3
        # check names
        assert ["top_level::const0", "utils::C"] == sorted(
            [c.get_full_path() for c in top_level.model.constants]
        )
        assert ["other::C", "other::C2", "utils::C"] == sorted(
            [c.get_full_path() for c in other_project.model.constants]
        )
        # check that the two utils::C are different objects
        C1 = [c for c in top_level.model.constants if c.get_full_path() == "utils::C"][0]
        C2 = [c for c in other_project.model.constants if c.get_full_path() == "utils::C"][0]
        assert C1 is not C2
        assert swan_to_str(C1) == "C: int32 = 42"
        assert swan_to_str(C2) == "C: float32 = 4.2"

    def test_cyclic_projects(self):
        app = ScadeOne()
        assert app.load_project("tests/models/multi_projects/circular/A/A.sproj") is not None
        assert ["A", "B"] == [p.directory.stem for p in app.projects]

    def test_all_modules(self, cc_project):
        app = ScadeOne()
        project = app.load_project(cc_project)
        assert project is not None
        modules = project.model.all_modules
        assert len(modules) == 3
        names = [str(m.name) for m in modules]
        assert sorted(names) == sorted(["CarTypes", "CC", "Utils"])

    def test_create_project_in_empty_path(self):
        app = ScadeOne()
        with pytest.raises(Exception):
            app.new_project(None)

    def test_create_project_in_existing_project(self):
        app = ScadeOne()
        with pytest.raises(Exception):
            project_path = Path("tests/models/multi_projects/top_level/top_level.sproj").absolute()
            app.new_project(project_path)

    def test_create_project(self, tmp_path):
        app = ScadeOne()
        project_path = tmp_path / "project0/project0.sproj"
        project = app.new_project(project_path)
        assert project is not None
        assert project.directory == project_path.parent
        assert project.model is not None

        assert project.resources == []
        project.add_resource(ResourceKind.HEADER_FILE, "tartanpion\\header.h", exist_check=False)
        project.add_resource(ResourceKind.SOURCE_FILE, "tartanpion/source.c", exist_check=False)
        project.add_resource(ResourceKind.SIMULATION_DATA, "simulation_data.sd", "my_key", False)

        with pytest.raises(ScadeOneException):  # non simulation data with key
            project.add_resource(
                ResourceKind.HEADER_FILE, "simulation_data.sd", "invalid_key", False
            )
        with pytest.raises(ScadeOneException):  # simulation data without key
            project.add_resource(
                ResourceKind.SIMULATION_DATA, "simulation_data_2.sd", exist_check=False
            )
        with pytest.raises(ScadeOneException):  # resource already in project
            project.add_resource(ResourceKind.SOURCE_FILE, "tartanpion/source.c", exist_check=False)
        with pytest.raises(ScadeOneException):  # key already used
            project.add_resource(
                ResourceKind.SIMULATION_DATA, "new_simulation_data.sd", "my_key", False
            )
        with pytest.raises(ScadeOneException):  # wrong extension file
            project.add_resource(ResourceKind.SOURCE_FILE, "source_file.cpp", exist_check=False)
        assert len(project.resources) == 3

        project.save()
        project_loading = app.load_project(project_path)
        assert project.resources == project_loading.resources

    def test_add_delete_job(self, cc_project):
        app = ScadeOne()
        project = app.load_project(cc_project)
        assert project is not None
        assert isinstance(project, Project)
        assert len(project.assets) == 4
        # add a job
        jb = project.add_job(JobType.CODE_GENERATION, "asset_codegen0")
        assert len(project.assets) == 6
        # delete job
        project.delete_job(jb)
        assert len(project.assets) == 4
