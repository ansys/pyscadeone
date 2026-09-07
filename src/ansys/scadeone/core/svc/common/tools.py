# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

import os
from pathlib import Path
import platform

from ansys.scadeone.core.project import Project


class CodeHelper:
    """Helper class for code generation."""

    @staticmethod
    def get_external_code(project: Project) -> list[Path]:
        """
        Collect external code files from the project resources and dependencies.

        Parameters
        ----------
        project : Project
            Scade One project.

        Returns
        -------
        list[Path]
            A list of external code file paths.
        """
        _resources = set()
        for resource in project.get_all_resources():
            if resource.path.suffix not in [".h", ".c"]:
                continue
            str_path = str(resource.path)
            if platform.system() != "Windows":
                str_path = str_path.replace("\\", "/")
            res_path = (resource.project.directory / str_path).resolve()
            _resources.add(res_path)
        return list(_resources)

    @staticmethod
    def get_C_files(files: list[Path], base_path: Path | None = None) -> list[str]:
        """
        Extract C source files from a list of file paths.

        Parameters
        ----------
        files : list[Path]
            A list of Path objects representing files to filter.
        base_path : Path, optional
            The base path to which the file paths should be made relative.
        Returns
        -------
        list[str]
            A list of strings containing only files with the ".c" suffix.
        """
        c_files = [str(file) for file in files if file.suffix == ".c"]
        return CodeHelper.get_relative_to(c_files, base_path)

    @staticmethod
    def get_H_files(files: list[Path], base_path: Path | None = None) -> list[str]:
        """
        Extract H header files from a list of file paths.

        Parameters
        ----------
        files : list[Path]
            A list of Path objects representing files to filter.
        base_path : Path, optional
            The base path to which the file paths should be made relative.
        Returns
        -------
        list[str]
            A list of strings containing only files with the ".h" suffix.
        """
        headers = [str(file) for file in files if file.suffix == ".h"]
        return CodeHelper.get_relative_to(headers, base_path)

    @staticmethod
    def get_I_paths(files: list[Path], base_path: Path | None = None) -> list[str]:
        """
        Extract unique include directories from a list of file paths.

        Parameters
        ----------
        files : list[Path]
            A list of Path objects representing files to filter.
        base_path : Path, optional
            The base path to which the include directories should be made relative.
        Returns
        -------
        list[str]
            A list of unique strings representing directories containing the files.
        """
        include_dirs = set()
        for file in files:
            include_dirs.add(str(file.parent.resolve()))
        return CodeHelper.get_relative_to(list(include_dirs), base_path)

    @staticmethod
    def get_relative_to(files: list[str], base_path: Path | None) -> list[str]:
        """
        Get relative paths of files with respect to a base path. If *base_path* is None
        the files are unchanged.

        Note: `Path.relative_to()` cannot be used directly as `walk_up` argument is now obsolete since 3.13.
        The point is that '..' with a symlink can cause issues and send not '..' but the real path.
        We take that risk here.

        Parameters
        ----------
        files : list[str]
            A list of file paths as strings.
        base_path : optional Path
            The base path to which the file paths should be made relative. If None, the files are unchanged.
        Returns
        -------
        list[str]
            A list of file paths as strings, relative to the base path.
        """
        if base_path is None:
            return files.copy()

        def relative_to(file: str) -> str:
            try:
                return str(os.path.relpath(file, base_path))
            except ValueError:
                # If the file is not relative to the base path, return the original file path
                return file

        return [relative_to(file) for file in files]
