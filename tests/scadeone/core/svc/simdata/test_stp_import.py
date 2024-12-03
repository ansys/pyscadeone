# Copyright (c) 2024 - 2024 ANSYS, Inc. and/or its affiliates.
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

from difflib import ndiff
import sys
import gc
import logging
from pathlib import Path
import shutil
import pytest

import ansys.scadeone.core.svc.simdata as sd
import ansys.scadeone.core.svc.simdata.stpimporter as converter

# stpimporter return codes
RET_OK = 0
RET_ERR = 1
RET_WARN = 2


@pytest.fixture(scope="module")
def stpimporter():
    return str(Path(__file__).parents[5] / ".venv" / "Scripts" / "stpimporter")


TestDir = Path(__file__).parents[5] / "tests/models/simdata"
Verbose = False
DisableGC = False
ScadeOne = "C:/Scade One"


class TestStpImport:

    @pytest.mark.parametrize(
        "test_dir,stp,sproj,record,summary,expected_sd_number",
        [
            [
                r"StpImporter",  # Test directory
                r"TestProject/Procedure1.stp",  # STP file
                r"SI/StpImporter/StpImporter.sproj",  # SPROJ file, expected to be in SI
                None,  # specific record name, else all records
                "Summary: errors: 2 warnings: 0",  # expected summary
                4,  # expected number of SD files
            ],
        ],
    )
    def test_import_stp(
        self,
        test_dir,
        stp: str,
        sproj: str,
        record: str,
        summary: str,
        expected_sd_number: int,
        capsys,
        caplog,
    ):
        caplog.set_level(logging.DEBUG if Verbose else logging.INFO)
        stp = TestDir / test_dir / stp
        sproj = TestDir / test_dir / sproj
        sys.argv = ["argv0"]
        sys.argv.extend(["-v"] if Verbose else [])
        out_dir = TestDir / "stpimporter_results" / test_dir
        shutil.rmtree(out_dir, ignore_errors=True)
        sys.argv.extend(["-o", str(out_dir), "-s", ScadeOne])
        sys.argv.extend([str(stp), str(sproj)])
        SI = TestDir / test_dir / "SI"
        if SI.exists():
            renamings = SI / "renamings.log"
            if renamings.exists():
                sys.argv.extend(["-n", str(renamings)])
        with capsys.disabled():
            if DisableGC:
                gc.disable()
            status = converter.cmd_parse()
            if DisableGC:
                gc.enable()
        (out_dir / "stpimporter.log").write_text(caplog.text)
        if caplog.records:
            assert summary == caplog.records[-1].msg
        # Check sd files
        generated_sd = list(out_dir.glob("**/*.sd"))
        assert expected_sd_number == len(generated_sd)

        for sd in generated_sd:
            ref_file = TestDir / test_dir / "sd_refs" / sd.relative_to(out_dir)
            assert ref_file.exists()
            cmp = compare_sd_files(ref_file, sd, out_dir)
            assert cmp

        shutil.rmtree(out_dir, ignore_errors=True)


def compare_sd_files(sd_ref: Path, sd_new: Path, out_dir: Path) -> bool:
    if files_are_equal(sd_ref, sd_new):
        return True
    ref_fd = sd.open_file(str(sd_ref))
    a = str(ref_fd)
    ref_fd.close()
    sd_fd = sd.open_file(str(sd_new))
    b = str(sd_fd)
    sd_fd.close()
    diff_file = out_dir / "stpimporter_diff.txt"
    if diff_file.exists():
        diff_file.unlink()
    diff = ndiff(a.splitlines(), b.splitlines())
    result = "\n".join(diff)
    diff_file.write_text(f"ref: {sd_ref}\n" + f"new: {sd_new}\n" + ("=" * 10) + result)

    logging.error(f"/!\\ .sd files differs *** /!\\ \n{diff_file}\n")
    return False


def files_are_equal(file1_path: Path, file2_path: Path) -> bool:
    with file1_path.open("rb") as file1, file2_path.open("rb") as file2:
        while True:
            chunk1 = file1.read(8192)
            chunk2 = file2.read(8192)
            if chunk1 != chunk2:
                return False
            if not chunk1:
                return True
