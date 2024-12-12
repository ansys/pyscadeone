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

# %%
from pathlib import Path

import pytest

from ansys.scadeone.core import ScadeOne, __version__, version_info
from ansys.scadeone.core.common.storage import SwanFile, SwanString
from ansys.scadeone.core.common.versioning import FormatVersions


swan = FormatVersions.version("swan")
graph = FormatVersions.version("graph")
swant = FormatVersions.version("swant")


class TestApp:
    def test_app(self):
        app = ScadeOne()
        assert app is not None

    def test_app_with(self):
        # check as container
        with ScadeOne() as app:
            assert app.version == __version__

    def test_app_with_exc(self):
        # check as container with exception
        with pytest.raises(KeyError) as exc_info:
            with ScadeOne() as app:
                d = {}
                d["no_key"]
        assert str(exc_info.value) == "'no_key'"

    def test_version(self):
        assert __version__ == ".".join((version_info.major, version_info.minor, version_info.patch))
        assert FormatVersions.version("swan") == "2025.0"

    @pytest.mark.parametrize(
        "source",
        [
            f"""\
-- version swan: {swan} graph: {graph}
/* some code */
""",
            f"""\
-- version swan: {swant} swan: {swan} graph:{graph}
/* some code */
""",  # noqa
        ],
    )
    def test_swan_version(self, source):
        def check(storage):
            storage.check_swan_version()

        check(SwanString(source))
        file = Path("check_version.swan")
        file.write_text(source)
        check(SwanFile(file))
        file.unlink()

    def test_swan_no_version(self):
        with pytest.raises(Exception) as exc_info:
            SwanString("/* some code */").check_swan_version()
        assert str(exc_info.value) == "No version information found."
        assert type(exc_info.value).__name__ == "ScadeOneException"
