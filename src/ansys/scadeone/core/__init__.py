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
from collections import namedtuple
from platformdirs import PlatformDirs
import re

# Version must be directly defined for flit. No computation, else flit will fails
__version__ = "0.7.1"

m = re.match(
    r"""(?P<M>\d+)\.(?P<m>\d+)\.(?P<p>\d+)   # Major, minor, patch
        (?:\+(?P<b>\d+))?                    # Build (optional)
        (?:(?P<pr>\D.*))?                    # Pre-release (optional)
    """,
    __version__,
    re.X,
)

# version as a named tuple
Version = namedtuple("Version", ["major", "minor", "patch", "build", "pre_release"])

version_info = (
    Version(
        m.group("M"),
        m.group("m"),
        m.group("p"),
        m.group("b") if m.group("b") else "",
        m.group("pr") is not None,
    )
    if m
    else Version(0, 0, 0, 0, False)
)

# full version as a string
full_version = ".".join([version_info.major, version_info.minor, version_info.patch])
if version_info.build:
    full_version += f"+{version_info.build}"
if version_info.pre_release:
    full_version += " - Prerelease"

PYSCADEONE_DIR = Path(__file__).parent
PLATFORM_DIRS = PlatformDirs("PyScadeOne", "Ansys")

# pylint: disable=wrong-import-position
from .scadeone import ScadeOne  # noqa as we export name
from .common.exception import ScadeOneException  # noqa as we export name
from .common.storage import ProjectFile, SwanFile  # noqa as we export name
