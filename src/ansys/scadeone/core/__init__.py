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

# Version must be directly defined for flit. No computation, else flit will fails
__version__ = "0.6.1"

Version = namedtuple("Version", ["major", "minor", "patch", "build"])
(M, m, p) = __version__.split(".")
(p, b) = (p, "") if p.find("+") == -1 else p.split("+")

# version as a named tuple
version_info = Version(M, m, p, b)

PYSCADEONE_DIR = Path(__file__).parent
PLATFORM_DIRS = PlatformDirs("PyScadeOne", "Ansys")

# pylint: disable=wrong-import-position
from .scadeone import ScadeOne  # noqa as we export name
from .common.exception import ScadeOneException  # noqa as we export name
from .common.storage import ProjectFile, SwanFile  # noqa as we export name
