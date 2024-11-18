# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

import sys
from pathlib import Path
import pythonnet

pythonnet.load("coreclr")
# pylint: disable=wrong-import-position
import clr  # noqa

DLL_DIR = Path(__file__).parents[1] / "libs/dotnet"
assert DLL_DIR.exists()
sys.path.append(str(DLL_DIR))
# pylint: disable=no-member
clr.AddReference("ANSYS.SONE.Infrastructure.Services.Serialization.BNF.Parsing")  # noqa
clr.AddReference("ANSYS.SONE.Core.Toolkit.Logging")  # noqa
