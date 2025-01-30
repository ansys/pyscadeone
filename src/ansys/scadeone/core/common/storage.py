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
The **storage** module contains classes that abstract a storage container.
Currently, containers can be a file or a string, or other data

The *content()* method returns the storage content.

The *source* property gives the origin of the storage,
Source is used for error messages.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
from pathlib import Path
import json
import re

from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.common.exception import ScadeOneException


class Storage(ABC):
    """Top-level class for storage: Project, Swan code, etc.

    Storage abstracts the data persistence. It has a _source_ property
    which gives the origin of the data (file name, string, etc.)

    The *content()* method is responsible for returning the data contained
    by the source. For now, content is a string, its interpretation is
    made by its consumer.
    """

    def __init__(self, source: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._source = source

    @property
    def source(self) -> str:
        """Source origin: file name, string, etc."""
        return self._source

    @abstractmethod
    def exists(self) -> bool:
        """True when source exists."""
        pass

    @abstractmethod
    def content(self) -> str:
        """Content of the source."""
        pass

    @abstractmethod
    def set_content(self, data: str) -> str:
        """Sets content of the source."""
        pass


class FileStorage(Storage):
    """Base class for storage as a file.
    file is stored as absolute, posix-style.
    """

    def __init__(self, file: Union[str, Path], **kwargs) -> None:
        path = Path(file) if isinstance(file, str) else file
        path = path.resolve().as_posix()
        super().__init__(source=path)

    @property
    def path(self) -> Path:
        """Saved path."""
        return Path(self.source)

    def exists(self) -> bool:
        """True when file exists."""
        return self.path.exists()

    def content(self) -> str:
        """Content of file."""
        if self.exists():
            content = self.path.read_text(encoding="utf-8")
            return content
        raise ScadeOneException(f"FileStorage.content(): no such file: {self.path}.")

    def set_content(self, data: str) -> str:
        """Sets content and write it to underlying file."""
        self.path.write_text(data)


class StringStorage(Storage):
    """Base class for storage provided as a string."""

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(source="<string>")
        self._text = text

    def exists(self) -> bool:
        """Always return True."""
        return True

    def content(self) -> str:
        """Content of string."""
        return self._text

    def set_content(self, data: str) -> str:
        """Set content of the file."""
        self._text = data


class JSONStorage(object):
    """Toplevel class for JSON-related storage."""

    def __init__(self, asset: Storage, **kwargs) -> None:
        super().__init__(**kwargs)
        self._asset = asset
        self._json = None

    @property
    def json(self):
        """JSON content.
        Any modification is propagated to the underlying JSON object."""
        return self._json

    @json.setter
    def json(self, json_data):
        """Update JSON content"""
        self._json = json_data

    def load(self, **kw):
        """Loads content of JSON data into json property and returns `self`.

        See `json.loads() <https://docs.python.org/3/library/json.html>`_
        for detailed interface.
        """
        self.json = json.loads(self._asset.content(), **kw)
        return self

    def dump(self, **kw):
        """Uses `self.json` to update storage content and returns self.

        See `json.dumps() <https://docs.python.org/3/library/json.html>`_
        for detailed interface.
        """
        data = json.dumps(self.json, **kw)
        self._asset.set_content(data)
        return self


# Swan related storage
# ====================


class SwanStorage(ABC):
    """Toplevel class for Swan input code."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        """Name for module or interface."""
        pass

    @property
    def version(self) -> Union[dict, None]:
        """Swan version."""
        return None

    @staticmethod
    def extract_version(source: str) -> Union[dict, None]:
        """Extracts version information from a Swan source.

        Parameters
        ----------
        source : str
            Version information as a string.

        Returns
        -------
        Union[dict, None]
            Either the version information as a dictionary, or None if no version found.
        """
        m = re.match(r"^--\s*version\s+(?P<ver>.*)$", source, re.MULTILINE)
        if m:
            infos = {
                k: v
                for k, v in re.findall(r"(\w+):\s*(\d+\.\d+)", m["ver"])
                if k in FormatVersions.formats
            }
            infos["version"] = m[0]
            return infos
        return None

    def check_swan_version(self):
        """Check Swan version information.

        Raises
        ------
        ScadeOneException
            When version information is missing or invalid.
        """
        version = self.version
        if version is None:
            raise ScadeOneException("No version information found.")
        for k in ("swan", "graph"):
            if k not in version:
                raise ScadeOneException(f"Missing version information for {k}.")
            FormatVersions.check(k, version[k])
        return version

    def check_swant_version(self):
        """Check Swan test harness version information.

        Raises
        ------
        ScadeOneException
            When version information is missing or invalid.
        """
        version = self.check_swan_version()
        if "swant" not in version:
            raise ScadeOneException("Missing version information for swant.")
        FormatVersions.check("swant", version["swant"])
        return version

    @staticmethod
    def gen_version(is_harness=False):
        """Generate the version for a Swan file.

        Parameters
        ----------
        is_harness : bool
            True if the harness version is needed

        Returns
        -------
        str
            Version
        """
        version = "-- version"
        version += f" swan:{FormatVersions.version('swan')}"
        version += f" graph:{FormatVersions.version('graph')}"
        if is_harness:
            version += f" swant:{FormatVersions.version('swant')}"
        return version


class SwanFile(FileStorage, SwanStorage):
    """Swan code within a file.

    Parameters
    ----------

    file : Path
        File containing the Swan source."""

    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)

    @property
    def name(self) -> str:
        """Returns basename of source file (no suffix)."""
        return self.path.stem

    @property
    def is_module(self):
        """True when file is a module code."""
        return self.path.suffix == ".swan"

    @property
    def is_interface(self):
        """True when file is an interface code."""
        return self.path.suffix == ".swani"

    @property
    def is_test(self):
        """True when file is an test code."""
        return self.path.suffix == ".swant"

    @property
    def version(self) -> Union[dict, None]:
        """Swan version information."""
        try:
            with self.path.open() as fd:
                return self.extract_version(fd.readline())
        except:  # noqa: E722
            return None


class SwanString(StringStorage, SwanStorage):
    """Swan code within a string

    Parameters
    ----------

    swan_code : str
        String containing the Swan source.

    name: str [optional]
        Name that can be used for a module or interface identifier.
    """

    def __init__(self, swan_code: str, name: Optional[str] = None) -> None:
        super().__init__(text=swan_code)
        self._name = name if name else "from_string"

    @property
    def name(self) -> str:
        """Name attribute."""
        return self._name

    @property
    def source(self) -> str:
        """Source string."""
        return f"string:<{self.content()}>"

    @property
    def version(self) -> Union[dict, None]:
        """Swan version."""
        return self.extract_version(self.content())


# Project Storage
# -------------


class ProjectStorage(JSONStorage):
    """Base class for project storage."""

    def __init__(self, **kwargs) -> None:
        super().__init__(asset=self, **kwargs)


class ProjectFile(FileStorage, ProjectStorage):
    """Project as a file."""

    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)


# Job Storage
# --------


class JobStorage(JSONStorage):
    """Base class for job asset."""

    def __init__(self, **kwargs) -> None:
        super().__init__(asset=self, **kwargs)


class JobFile(FileStorage, ProjectStorage):
    """Job asset as a file."""

    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)
