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

# for reference in Model
# IProject: app return type is 'scadeone.IScadeOne'
# see https://softwareengineering.stackexchange.com/questions/369146/how-to-avoid-bidirectional-class-and-module-dependencies  # noqa: E501
# The point is that ScadeOne and Project uses each other
# Alternative is to create an intermediate interfaces.py.

from pathlib import Path
from typing import Union


class IProject:
    """Interface class"""

    @property
    def app(self) -> "IScadeOne":
        pass


class IScadeOne:
    """Interface class"""

    @property
    def logger(self):
        return None

    @property
    def version(self) -> str:
        return ""

    @property
    def install_dir(self) -> Union[Path, None]:
        """Installation directory as given when creating the ScadeOne instance."""
        assert False

    def subst_in_path(self, _: str) -> str:
        assert False
