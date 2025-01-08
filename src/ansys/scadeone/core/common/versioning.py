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

"""
The versioning module contains the version manager for the Scade One formats.
"""

import re
import json
from pathlib import Path
from ansys.scadeone.core.common.exception import ScadeOneException

VersionFile = Path(__file__).parent / "versions.json"


class VersionManager:
    """Class managing the versions for the Scade One tools formats.

    The version manager is used through the singleton `FormatVersions` instance.
    """

    VersionRE = re.compile(r"(?P<M>\d+)\.(?P<m>\d+)")

    def __init__(self):
        self._format_versions = {}
        self._formats = None

    @property
    def formats(self) -> set:
        """Get the formats as a set of strings."""
        if self._formats is None:
            self._formats = set(self._format_versions.keys())
        return self._formats

    def get_versions(self) -> str:
        """Get the versions as a document string.

        Returns
        -------
        str
            String containing the versions
        """
        buffer = "The versions for the supported format/code are:\n\n"
        for k in sorted(self.formats):
            buffer += f"- {self.description(k)}: {self.version(k)}\n"
        return buffer

    def load_versions(self, version_file: Path):
        """Load the versions from the json file file.

        Parameters
        ----------
        version_file : Path
            JSON file containing the versions

        Raises
        ------
        ScadeOneException
            If the file is not found or if the file is not valid.
        """
        try:
            data = version_file.read_text()
            self._format_versions = json.loads(data)
        except Exception as e:
            raise ScadeOneException(f"Unable to load versions: {e}")
        if not isinstance(self._format_versions, dict):
            raise ScadeOneException(f"{version_file}: invalid versions file versions.json")
        for k, v in self._format_versions.items():
            if not (isinstance(v, dict) and "version" in v and "description" in v):
                raise ScadeOneException(f"{version_file}: Invalid version for {k}")

    def version(self, format: str):
        """Get the version for the format.

        Parameters
        ----------
        format : str
            Format name

        Returns
        -------
        str
            Version
        """
        if format not in self.formats:
            raise ScadeOneException(f"Unknown format: {format}")
        return self._format_versions[format]["version"]

    def description(self, format: str):
        """Get the description for the format.

        Parameters
        ----------
        format : str
            Format name

        Returns
        -------
        str
            Description
        """
        if format not in self.formats:
            raise ScadeOneException(f"Unknown format: {format}")
        return self._format_versions[format]["description"]

    def check(self, format: str, version: str):
        """Check if the version is supported for the format.

        Parameters
        ----------
        format : str
            Format name
        version : str
            Version to be checked

        Raises
        ------
        ScadeOneException
            If the version is not supported for the format.
        """
        if format not in self.formats:
            raise ScadeOneException(f"Unknown format: {format}")
        version_ref = self._format_versions[format]["version"]
        # check expected version is valid
        m = re.match(VersionManager.VersionRE, version_ref)
        if not m:
            raise ScadeOneException(f"Invalid {format} version, check installation: {version_ref}")
        expected = m.groupdict()
        # check provided version is valid
        m = re.match(VersionManager.VersionRE, version)
        if not m:
            raise ScadeOneException(f"Invalid {format} version: {version}, expecting {version_ref}")
        provided = m.groupdict()
        # check version
        if provided["M"] != expected["M"] or int(provided["m"]) > int(expected["m"]):
            raise ScadeOneException(
                f"Unsupported {format} version: {version}, expecting {version_ref}"
            )


FormatVersions = VersionManager()
FormatVersions.load_versions(VersionFile)
