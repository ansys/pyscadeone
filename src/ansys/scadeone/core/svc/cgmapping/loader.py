# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Unified loader for Swan Code Generator mapping data.

This module provides the main entry point for loading code generator mapping
data from JSON files. It orchestrates the loading of model items, code items,
and their mappings into the appropriate registries.
"""

from __future__ import annotations
from ansys.scadeone.core.common.versioning import FormatVersions
import json
from ansys.scadeone.core import ScadeOneException
from pathlib import Path
from typing import Any
from dataclasses import dataclass

from .model import _ModelRegistry, load_model_from_json
from .code import _CodeRegistry, load_code_from_json
from .mapping import _MappingRegistry, load_mapping_from_json

from ansys.scadeone.core.common.logger import LOGGER


@dataclass
class CGMappingData:
    """Container for all code generator mapping data.

    This class holds the three main components of the code generator mapping:
    model registry, code registry, and mapping registry.

    Parameters
    ----------
    version : str
        File format version from the JSON data.
    model_registry : _ModelRegistry
        Registry containing all model items.
    code_registry : _CodeRegistry
        Registry containing all code items and containers.
    mapping_registry : _MappingRegistry
        Registry containing all mappings between model and code items.
    """

    version: str
    model_registry: _ModelRegistry
    code_registry: _CodeRegistry
    mapping_registry: _MappingRegistry


def validate_json_structure(data: dict[str, Any]) -> None:
    """Validate that the JSON data has the required top-level structure.

    Parameters
    ----------
    data : dict[str, Any]
        The JSON data to validate.

    Raises
    ------
    ScadeOneException
        If the JSON structure is invalid or missing required fields.
    """
    if not isinstance(data, dict):
        raise ScadeOneException(f"Expected JSON object at root level, got {type(data).__name__}")

    required_fields = ["model", "code", "mapping"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ScadeOneException(
            f"Missing required fields in JSON data: {', '.join(missing_fields)}"
        )

    # Validate that required fields are arrays
    for field in required_fields:
        if not isinstance(data[field], list):
            raise ScadeOneException(
                f"Field '{field}' must be an array, got {type(data[field]).__name__}"
            )


def load_cg_mapping(file_path: str | Path) -> CGMappingData:
    """Load code generator mapping data from a JSON file.

    This function reads a JSON file containing model items, code items, and
    their mappings, validates the structure, and loads all data into the
    appropriate registries.

    Parameters
    ----------
    file_path : str | Path
        Path to the JSON file to load.

    Returns
    -------
    CGMappingData
        Container with all loaded data including model registry, code registry,
        and mapping registry.

    Raises
    ------
    ScadeOneException
        If the file cannot be read, is not valid JSON, or does not conform
        to the expected schema structure.
    FileNotFoundError
        If the specified file does not exist.
    """
    # Convert to Path object for easier handling
    path = Path(file_path)

    # Check if file exists
    LOGGER.info(f"Loading data from file: {file_path}")
    if not path.exists():
        LOGGER.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read and parse JSON file
    try:
        with open(path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        LOGGER.error(f"Invalid JSON file: {e}")
        raise ScadeOneException(f"Invalid JSON file: {e}") from e
    except IOError as e:
        LOGGER.error(f"Failed to read file: {e}")
        raise ScadeOneException(f"Failed to read file: {e}") from e

    # Validate JSON structure
    validate_json_structure(json_data)

    # Check version
    version = FormatVersions.version("cgmap")
    file_version = json_data.get("version", "no version")
    if version != file_version:
        LOGGER.error(
            f"Version mismatch: expected {version} (API), found {file_version} in file {file_path}"
        )
        raise ScadeOneException(
            f"Version mismatch: expected {version} (API), found {file_version} in file {file_path}"
        )

    # Load model items
    try:
        model_registry = load_model_from_json(json_data["model"])
    except Exception as e:
        LOGGER.error(f"Failed to load model items: {e}")
        raise ScadeOneException(f"Failed to load model items: {e}") from e

    # Load code items
    try:
        code_registry = load_code_from_json(json_data["code"])
    except Exception as e:
        LOGGER.error(f"Failed to load code items: {e}")
        raise ScadeOneException(f"Failed to load code items: {e}") from e

    # Load mappings
    try:
        mapping_registry = load_mapping_from_json(json_data["mapping"])
    except Exception as e:
        LOGGER.error(f"Failed to load mappings: {e}")
        raise ScadeOneException(f"Failed to load mappings: {e}") from e

    # Create and return the unified data container
    LOGGER.info(f"Successfully loaded data from {file_path} - version: {version}")
    return CGMappingData(
        version=version,
        model_registry=model_registry,
        code_registry=code_registry,
        mapping_registry=mapping_registry,
    )
