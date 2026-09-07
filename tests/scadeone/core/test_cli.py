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

import logging
import platform
import pytest

from ansys.scadeone.core import cli
from ansys.scadeone.core.common.logger import DEFAULT_FILE_NAME, LOGGER, STDOUT_MSG_FORMAT

from test_tools.utils import SysContext


class TestCli:
    formatter = logging.Formatter(STDOUT_MSG_FORMAT)

    @staticmethod
    def _run_cli() -> None:
        ret = cli.main()
        assert ret

    @pytest.fixture()
    def pyscadeone_args(self):
        return ["pyscadeone", "--no-exit", "--formats"]

    @pytest.mark.parametrize(
        "v_opt,oracle",
        [
            ["-v", ""],
            [
                "-vv",
                "Running pyscadeone command line with: Namespace(formats=True, log=None, "
                "verbosity=2, set_install_dir=None, no_exit=True, subparser_command=None)",
            ],
        ],
    )
    def test_cli_verbose(self, v_opt, oracle, pyscadeone_args, caplog):
        # Clear handlers to avoid duplicate logs in caplog
        LOGGER._logger.handlers.clear()
        caplog.set_level(logging.DEBUG)
        caplog.handler.setFormatter(self.formatter)
        caplog.clear()
        # The options are added to the SysContext args to simulate running the CLI with those options
        with SysContext(args=pyscadeone_args + [v_opt], env_vars={}):
            self._run_cli()
            assert oracle in caplog.text

    def test_cli_with_log_file_in_tmp_folder(self, pyscadeone_args, tmp_path):
        oracle_log_msg = (
            "Running pyscadeone command line with: Namespace(formats=True, log="
            f"WindowsPath('{tmp_path.as_posix()}'), "
            if platform.system() == "Windows"
            else f"PosixPath('{tmp_path.as_posix()}'), "
            "verbosity=0, set_install_dir=None, no_exit=True, subparser_command=None)"
        )
        with SysContext(args=pyscadeone_args + ["--log", str(tmp_path)], env_vars={}):
            self._run_cli()
            log_file = tmp_path / DEFAULT_FILE_NAME
            assert log_file.exists()
            assert oracle_log_msg in log_file.read_text(encoding="utf-8")
