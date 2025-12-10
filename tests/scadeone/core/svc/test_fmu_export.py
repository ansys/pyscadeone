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
import shutil
import zipfile
import platform

from fmpy import validation as fmpy_validation
import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.svc.fmu import FMU_2_Export


class TestFMUExport:
    def test_init_no_project(self):
        try:
            FMU_2_Export(None, "")
            assert False
        except ScadeOneException as error:
            assert error.args[0] == "FMU_Export: Valid Scade One project is expected."

    @pytest.mark.parametrize("job_name", ["", "foo", "Simu"])
    def test_init_no_job(self, job_name):
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            FMU_2_Export(prj, job_name)
            assert False
        except ScadeOneException as error:
            assert error.args[0] == f'Generated code: no CodeGeneration kind job named "{job_name}"'

    @pytest.mark.parametrize(("job", "oper_name"), [("CodeGenForFMU", "foo"), ("CodeGen2", "foo")])
    def test_init_incorrect_root(self, job, oper_name):
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            FMU_2_Export(prj, job, oper_name)
            assert False
        except ScadeOneException as error:
            assert (
                error.args[0]
                == f"FMU_Export: No root operator named {oper_name} for selected job {job}."
            )

    @pytest.mark.parametrize("job", ["CodeGen2"])
    def test_init_multiroot(self, job):
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            FMU_2_Export(prj, job)
            assert False
        except ScadeOneException as error:
            assert (
                error.args[0] == f"FMU_Export: The job {job} has several root operators."
                " Use parameter 'oper_name' to select one."
            )

    @pytest.mark.parametrize("kind", ["", "foo"])
    def test_generate_wrong_kind(self, kind):
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            fmu = FMU_2_Export(prj, "CodeGenForFMU")
            fmu.generate(kind, "")
            assert False
        except ScadeOneException as error:
            assert error.args[0] == 'FMU_Export: Unknown FMU kind (expected "CS" or "ME")'

    def test_generate_no_codegen(self):
        job_name = "CodeGenNoExecution"
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            fmu = FMU_2_Export(prj, job_name)
            fmu.generate("ME", "")
            assert False
        except ScadeOneException as error:
            assert error.args[0] == f"FMU_Export: Code is not generated for job {job_name}"

    @pytest.mark.parametrize("max", [0, 10])
    def test_generate_max_variables(self, max):
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            fmu = FMU_2_Export(prj, "CodeGenForFMU", max_variables=max)
            fmu.generate("ME", "")
            assert False
        except ScadeOneException as error:
            assert (
                error.args[0] == "FMU export: The maximum number of supported model variables "
                f"({max}) is reached. Use max_variables parameter of "
                f"FMU_2_Export class to increase it."
            )

    def test_generate_imported_type(self):
        job_name = "CodeGenImpType"
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            fmu = FMU_2_Export(prj, job_name)
            fmu.generate("ME", "")
            assert False
        except ScadeOneException as error:
            assert "imported types are not supported" in error.args[0]

    @pytest.mark.parametrize("kind", ["ME", "CS"])
    def test_generate(self, kind):
        basegen = Path(__file__).parent / "test_fmu_data"
        basegen.mkdir(exist_ok=True)
        out_dir = basegen / f"test_FMU_{kind}"
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            fmu = FMU_2_Export(prj, "CodeGenForFMU")
            fmu.generate(kind, out_dir)
            assert (out_dir / "modelDescription.xml").exists()
            assert (out_dir / "sources" / (fmu.model_id + "_FMU.c")).exists()
            shutil.rmtree(str(out_dir))
        except ScadeOneException:
            assert False
        finally:
            shutil.rmtree(basegen, True)

    def test_build_no_generate(self):
        job_name = "CodeGen1"
        app = ScadeOne()
        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            fmu = FMU_2_Export(prj, job_name)
            fmu.build()
            assert False
        except ScadeOneException as error:
            assert error.args[0] == "FMU export: 'generate' method must be called first."

    @pytest.mark.parametrize(
        ("job", "root", "kind", "with_sources", "keep_outdir", "sources", "link_opts"),
        [
            ("CodeGenForFMU", "", "ME", False, 0, [], []),
            ("CodeGenForFMU", "", "CS", False, 0, [], []),
            ("CodeGenForFMU", "", "ME", True, 0, [], []),
            ("CodeGenForFMU", "", "CS", True, 0, [], []),
            ("CodeGen1", "", "ME", False, 0, [], []),
            ("CodeGen2", "module0::oper_misc2", "ME", False, 1, ["foo"], []),
            ("CodeGen2", "module0::oper_misc2", "ME", False, 2, [], []),
            (
                "CodeGenImportedFunc",
                "",
                "ME",
                False,
                0,
                ["tests/models/test_codegen/imported_code/oper_imp_func_module0.c"],
                [
                    "tests/models/test_codegen/imported_code/link_obj_module0.o",
                    "tests/models/test_codegen/imported_code/libstatic.a",
                ],
            ),
            (
                "CodeGenImportedNode",
                "",
                "ME",
                False,
                0,
                ["tests/models/test_codegen/imported_code"],
                [],
            ),
            (
                "CodeGenImportedNode",
                "",
                "ME",
                False,
                0,
                [
                    "tests/models/test_codegen/imported_code/oper_imp_func_module0.c",
                    "tests/models/test_codegen/imported_code/oper_imp_node_module0.c",
                    "tests/models/test_codegen/imported_code/oper_imp_node_module0.h",
                ],
                [],
            ),
            ("CodeGenNoOutput", "", "ME", False, 0, [], []),
        ],
    )
    def test_build(
        self,
        job,
        root,
        kind,
        with_sources,
        keep_outdir,
        sources,
        link_opts,
        scadeone_install_path,
        tmp_path,
    ):
        basegen = tmp_path / "test_fmu_data"
        basegen.mkdir(exist_ok=True)
        out_dir = basegen / f"test_FMU_{kind}"
        args = {}
        app = ScadeOne(scadeone_install_path)

        prj = app.load_project("tests/models/test_codegen/test_codegen.sproj")
        try:
            if keep_outdir == 0 and out_dir.exists():
                shutil.rmtree(out_dir)
            fmu = FMU_2_Export(prj, job, root)
            fmu.generate(kind, out_dir)
            if len(sources):
                args["user_sources"] = sources
            if len(link_opts):
                args["link_opts"] = link_opts
            fmu.build(with_sources, args)
            assert (out_dir / (fmu.model_id + ".fmu")).exists()
            # unzip fmu and check that it corresponds to generated files
            extract_dir = basegen / "test_FMU_temp"
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(out_dir / (fmu.model_id + ".fmu"), "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            assert (extract_dir / "modelDescription.xml").exists()
            assert (extract_dir / "model.png").exists()

            if platform.system() == "Windows":
                for item in (extract_dir / "binaries").iterdir():
                    assert item.is_dir() and (item / (fmu.model_id + ".dll")).exists()
            else:
                for item in (extract_dir / "binaries").iterdir():
                    assert item.is_dir() and (item / (f"{fmu.model_id}.so")).exists()
            if with_sources:

                def list_files_recursively(directory):
                    return {
                        f.relative_to(directory) for f in Path(directory).rglob("*") if f.is_file()
                    }

                files_dir1 = list_files_recursively(out_dir / "sources")
                files_dir2 = list_files_recursively(extract_dir / "sources")
                assert files_dir1 == files_dir2
            assert not len(fmpy_validation.validate_fmu(str(out_dir / (fmu.model_id + ".fmu"))))
            if not keep_outdir < 2:
                shutil.rmtree(str(out_dir))
            shutil.rmtree(str(extract_dir))
        except ScadeOneException as error:
            if (
                error.args[0] == "FMU export: the compiler command gcc cannot be found."
                " Use the 'args' parameter to provide proper path."
            ):
                print(
                    "gcc cannot be found in Path."
                    " Either update path or script to update Scade One installation location"
                )
            assert False
        finally:
            # shutil.rmtree(basegen, True)
            pass
