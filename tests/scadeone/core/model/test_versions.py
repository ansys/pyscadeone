# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.scadeone.core import ScadeOneException, __version__, version_info
from ansys.scadeone.core.model.loader import VersionMap
from ansys.scadeone.core.common.versioning import FormatVersions


@pytest.fixture
def swan_formats():
    return ("swan", "swant", "graph")


def test_version():
    assert __version__ == ".".join((version_info.major, version_info.minor, version_info.patch))


def test_swan_versions(swan_formats):
    for fmt in swan_formats:
        try:
            FormatVersions.check(fmt, VersionMap[fmt])
        except ScadeOneException:
            pytest.fail(f"Version check failed for {fmt}: {FormatVersions.version(fmt)}")


def test_other_versions(swan_formats, capsys):
    # Check that the other formats are not in the version map
    for fmt in FormatVersions.formats:
        if fmt in swan_formats:
            continue
        with capsys.disabled():
            # TODO: find a programmatic way to check the version.
            print(f"Please check that format {fmt} = {FormatVersions.version(fmt)} is valid")
