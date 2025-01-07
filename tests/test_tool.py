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

from difflib import Differ

# %% Standard import
import json
from pathlib import Path
import re
from typing import Union

# %% Scade One imports
log = Path.cwd() / "pyscadeone.log"
try:
    log.unlink(True)
except Exception:
    pass

from ansys.scadeone.core import ScadeOne, ScadeOneException  # noqa: E402
from ansys.scadeone.core.common.logger import LOGGER  # noqa: E402
from ansys.scadeone.core.common.storage import SwanFile  # noqa: E402
from ansys.scadeone.core.common.versioning import FormatVersions  # noqa: E402
from ansys.scadeone.core.model.loader import SwanParser  # noqa: E402
import ansys.scadeone.core.swan as Swan  # noqa: E402

# %% Helpers
reWS = re.compile(r"[ \r\n\t\f]")
reText = re.compile(r"^\s*(?:\{text%|%text\})", re.M)


def check_string(reference: str, new: str) -> Union[str, None]:
    """Check if two strings from Swan source and API result are 'equal'

    Add version to new (to be enhanced)

    Parameters
    ----------
    reference : str
        Reference Swan code
    new : str
        Result from API

    Returns
    -------
    Union[str, None]
        None if success, difference of text else
    """
    smashed_ref = reWS.sub(" ", reference)
    smashed_new = reWS.sub(" ", new)
    if smashed_new == smashed_ref:
        return None
    d = Differ()
    diff = d.compare(smashed_ref.split(), smashed_new.split())
    result = "\n".join(list(diff))
    Path("test_tool.log").write_text(result)
    return "Diff"


def check_module(module: Swan.Module):
    # Check if read module and corresponding str are the same
    source = Path(module.source)
    print(f"### {source}")
    source_str = source.read_text()
    # remove textual operator markups
    source_str = reText.sub("", source_str)

    module_str = f"--version: {FormatVersions['swan']}\n"
    module_str += str(module)
    if info := module.information:
        if info.has_information:
            module_str += "__END__\n"
            module_str += json.dumps(info.info)

    return check_string(source_str, module_str)


def check_swan(swan: str) -> Union[None, str]:
    """Check a Swan file

    Parameters
    ----------
    swan : file name

    rule : function
        Parser rule to apply

    Returns
    -------
    Union[None, str]
        None if success, else comparison result
    """
    swan_path = Path(swan)

    parser = SwanParser(LOGGER)

    if swan_path.suffix == ".swan":
        rule = parser.module_body
    elif swan_path.suffix == ".swani":
        rule = parser.module_interface
    else:
        print(f"Unknown suffix: {swan_path.suffix}")
    swan_file = SwanFile(swan_path)
    (module, info) = rule(swan_file)
    module.information = info
    module.source = swan
    return check_module(module)


def check(project=None, swan=None):
    "Check either a project or a Swan module file (body or interface)"
    try:
        if project:
            project_path = Path(project)
            if project_path.is_dir():
                project_path = project_path / (project_path.name + ".sproj")
            app = ScadeOne()
            project = app.load_project(project_path)
            if project:
                project.model.load_all_modules()
                for module in project.model.modules:
                    if error := check_module(module):
                        return error

        elif swan:
            if error := check_swan(swan):
                return error

        else:
            print("Set either project or swan")

    except ScadeOneException as e:
        return f"Scade One Exception:\n{e}"

    except Exception as e:
        return f"Exception:\n{e}"

    return None


# %% Your test goes here

pass
