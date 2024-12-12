# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

import pytest
import os
from typing import cast
from pathlib import Path
from ansys.scadeone.core import ScadeOne, ProjectFile


class TestProject:
    def test_wrong_project(self):
        app = ScadeOne()
        asset = ProjectFile("foo")
        project = app.load_project(asset)
        assert project is None

    @staticmethod
    def resolve(path: str):
        return Path(path).resolve().as_posix()

    def test_assets(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        sources = [swan.source for swan in project.swan_sources()]
        oracle = [
            TestProject.resolve(p)
            for p in [
                "examples/models/CC/CruiseControl/assets/CarTypes.swani",
                "examples/models/CC/CruiseControl/assets/CC.swan",
            ]
        ]
        assert sources == oracle

    def tests_all_assets(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
        sources = [swan.source for swan in project.swan_sources(all=True)]
        oracle = [
            TestProject.resolve(p)
            for p in [
                "examples/models/CC/CruiseControl/assets/CarTypes.swani",
                "examples/models/CC/CruiseControl/assets/CC.swan",
                "examples/models/CC/CruiseControl/../utils/assets/Utils.swan",
            ]
        ]
        assert sources == oracle

    def test_project_assets(self, cc_project):
        app = ScadeOne()
        asset = cc_project
        p1 = app.load_project(asset)
        asset = Path(cc_project)
        p2 = app.load_project(asset)
        asset = ProjectFile(cc_project)
        p3 = app.load_project(asset)
        assert cast(ProjectFile, p1.storage).source == cast(ProjectFile, p2.storage).source
        assert cast(ProjectFile, p1.storage).source == cast(ProjectFile, p3.storage).source

    def test_multi_projects(self):
        app = ScadeOne()
        project = app.load_project("tests/models/multi_projects/top_level/top_level.sproj")
        swans = [s.source for s in project.swan_sources(True)]
        oracle = []
        for dirname, dirs, files in os.walk("tests/models/multi_projects"):
            for f in files:
                if os.path.splitext(f)[1] == ".swan":
                    p = Path(dirname) / f
                    oracle.append(p.resolve().as_posix())
        swans.sort()
        oracle.sort()
        assert swans == oracle

    @pytest.mark.skip("Not yet implemented")
    def test_jobs(self, cc_project):
        app = ScadeOne()
        asset = ProjectFile(cc_project)
        project = app.load_project(asset)
