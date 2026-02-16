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

import json
import os
from pathlib import Path

import pytest

from ansys.scadeone.core import ProjectFile, ScadeOne
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.project import Project
from ansys.scadeone.core.svc.swan_creator.project_creator import ProjectFactory
from ansys.scadeone.core import swan
from ansys.scadeone.core.common.versioning import FormatVersions


@pytest.fixture
def project(cc_project):
    app = ScadeOne()
    project = app.load_project(cc_project)
    return project


class TestProjectCreator:
    def test_create_project(self):
        app = ScadeOne()
        project_path = Path(r"C:\project0\project0.sproj")
        storage = ProjectFile(project_path)
        project = ProjectFactory.create_project(app, storage)
        assert project is not None
        assert isinstance(project, Project)

    def test_add_module_body(self, project: Project):
        project.model.load_all_modules()
        assert project.model.is_all_modules_loaded
        module = project.add_module_body("NewModule")
        assert module is not None
        assert len(project.modules) == 4
        assert swan.swan_to_str(project.modules[2].name) == "NewModule"
        assert module.file_name == "NewModule.swan"
        project_path = project.storage.path.parent
        assert module.source == str(project_path / "assets" / module.file_name)

    def test_add_module_interface(self, project: Project):
        project.model.load_all_modules()
        assert project.model.is_all_modules_loaded
        module = project.add_module_interface("NewModuleInterface")
        assert module is not None
        assert len(project.modules) == 4
        assert swan.swan_to_str(project.modules[3].name) == "NewModuleInterface"
        assert module.file_name == "NewModuleInterface.swani"
        project_path = project.storage.path.parent
        assert module.source == str(project_path / "assets" / module.file_name)

    def test_add_module_path(self, project: Project):
        project.model.load_all_modules()
        assert project.model.is_all_modules_loaded
        module = project.add_module_body("lib::sublib::module0")
        assert module is not None
        assert len(project.modules) == 4
        assert swan.swan_to_str(project.modules[2].name) == "lib::sublib::module0"
        assert module.file_name == "lib-sublib-module0.swan"
        project_path = project.storage.path.parent
        assert module.source == str(project_path / "assets" / module.file_name)

    def test_save_project(self, tmp_path: Path):
        app = ScadeOne()
        parent_dir = tmp_path / "ProjectSaveTest0"
        project_path = parent_dir / r"ProjectSaveTest0.sproj"
        assets_dir = parent_dir / "assets"
        storage = ProjectFile(project_path)
        project = ProjectFactory.create_project(app, storage)
        project.add_module_body("OneModule")
        assert not project.check_exists(parent_dir)
        assert not project.storage.exists()
        project.save()
        assert app.model.is_all_modules_loaded
        assert project.check_exists(parent_dir)
        assert project.storage.exists()
        assert os.listdir(str(assets_dir)) == ["OneModule.swan"]
        module1 = project.add_module_body("SameName")
        module2 = project.add_module_interface("SameName")
        module3 = project.add_test_module("SameName")
        module1.add_constant("const_save0", "type0", "7")
        module2.add_declaration("type type0 = int32")
        module3.add_constant("const_save1", "type1", "17")
        assert len(os.listdir(assets_dir)) == 1
        project.save()
        assert len(os.listdir(assets_dir)) == 4
        assert os.listdir(assets_dir) == [
            "OneModule.swan",
            "SameName.swan",
            "SameName.swani",
            "SameName.swant",
        ]
        with open(project.storage.source, "r") as sproj_file:
            sproj_dict = json.load(sproj_file)
            assert sproj_dict["Dependencies"] == []
            assert sproj_dict["Resources"] == []
            assert sproj_dict["Name"] == "ProjectSaveTest0"
            assert sproj_dict["Version"] == FormatVersions.version("sproj")
        file1 = assets_dir / "SameName.swan"
        file2 = assets_dir / "SameName.swani"
        file3 = assets_dir / "SameName.swant"
        with file1.open() as swan_f, file2.open() as swani_f, file3.open() as swant_f:
            lines_swan = swan_f.readlines()
            lines_swani = swani_f.readlines()
            lines_swant = swant_f.readlines()
            assert "version" in lines_swan[0]
            assert lines_swan[0] == lines_swani[0]
            assert f"{lines_swan[0].rstrip()} swant: 1.1\n" == lines_swant[0]
            assert lines_swan[1] == "const const_save0: type0 = 7;\n"
            assert lines_swani[1] == "type type0 = int32;\n"
            assert lines_swant[1] == "const const_save1: type1 = 17;\n"
        app2 = ScadeOne()
        project2 = app2.load_project(project_path)
        assert not app2.model.is_all_modules_loaded
        project2.save()
        assert app2.model.is_all_modules_loaded

    def test_add_dependency(self, tmp_path: Path):
        """Test adding project dependencies."""
        app = ScadeOne()

        # Create two test projects
        project1 = app.new_project(Path(tmp_path / "Project1" / "project1.sproj"))
        project2 = app.new_project(Path(tmp_path / "Project2" / "project2.sproj"))

        # Test successful dependency add
        project1.add_dependency(project2)
        project2_rel_path = os.path.relpath(project2.storage.source, project1.directory)
        assert project2_rel_path in project1._dependencies
        assert len(project1._dependencies) == 1

        # Test adding same dependency twice - should not duplicate
        project1.add_dependency(project2)
        assert len(project1._dependencies) == 1

        # Test cannot add self as dependency
        with pytest.raises(ScadeOneException, match="A project cannot depend on itself"):
            project1.add_dependency(project1)

    def test_remove_dependency(self):
        """Test removing project dependencies."""
        app = ScadeOne()

        # Create test projects
        project1 = app.new_project(Path(r"C:\Project1\project1.sproj"))
        project2 = app.new_project(Path(r"C:\Project2\project2.sproj"))

        # Add dependency first
        project2_rel_path = os.path.relpath(project2.storage.source, project1.directory)
        project1.add_dependency(project2)
        assert project2_rel_path in project1._dependencies

        # Test successful dependency removal
        project1.remove_dependency(project2)
        assert project2_rel_path not in project1._dependencies

        # Test removing non-existent dependency raises error
        with pytest.raises(ScadeOneException, match="The project is not a dependency"):
            project1.remove_dependency(project2)
