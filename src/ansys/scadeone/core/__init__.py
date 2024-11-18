# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from pathlib import Path
from collections import namedtuple
from platformdirs import PlatformDirs

# Version must be directly defined for flit. No computation, else flit will fails
__version__ = "0.6.dev1"

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
