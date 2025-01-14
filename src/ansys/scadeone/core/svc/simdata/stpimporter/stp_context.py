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

# cSpell: ignore sdtype, sdio

import gc
import os
from pathlib import Path
from typing import Union, Optional
import xml.etree.ElementTree as ET

from ansys.scadeone.core.common.exception import ScadeOneException
import ansys.scadeone.core.svc.simdata as sd

from .cmd_context import SDContext
from .swan_context import SwanContext
from .utils import ConverterLogger, SDType


class STPRecord:
    """STP Procedure record"""

    sss_file_extension = ".sss"

    def __init__(self, name, inits=None, preambles=None, scenarios=None) -> None:
        self._name = name
        self._inits: list[Path] = inits if inits else []
        self._preambles: list[Path] = preambles if preambles else []
        self._scenarios: list[Path] = scenarios if scenarios else []

    @property
    def name(self) -> str:
        """Gets record name"""
        return self._name

    @property
    def inits(self) -> list[Path]:
        """Gets record inits"""
        return self._inits

    @property
    def preambles(self) -> list[Path]:
        """Gets record preambles"""
        return self._preambles

    @property
    def scenarios(self) -> list[Path]:
        """Gets record scenarios"""
        return self._scenarios

    @inits.setter
    def inits(self, inits: list[Path]) -> None:
        """Sets init files"""
        self._inits = inits

    @preambles.setter
    def preambles(self, preambles: list[Path]) -> None:
        """Sets preamble files"""
        self._preambles = preambles

    @scenarios.setter
    def scenarios(self, scenarios: list[Path]) -> None:
        """Sets scenario files"""
        self._scenarios = scenarios

    def start_convert(
        self, swan_ctx: SwanContext, out_dir: Path, gc_disable: bool = False
    ) -> list[str]:
        """Converts all the sss files for the record"""
        ConverterLogger.getLogger(self._name)
        ConverterLogger.info("Starting Conversion of record: " + self._name)

        if not out_dir.exists():
            os.makedirs(out_dir)

        ctx = SDContext(swan_ctx)
        for init in self._inits:
            if init.suffix == STPRecord.sss_file_extension:
                ctx.parse_file(init)
            else:
                ConverterLogger.warning(f"Unsupported init file was not converted: {init.name}")

        for preamble in self._preambles:
            if preamble.suffix == STPRecord.sss_file_extension:
                ctx.parse_file(preamble)
            else:
                ConverterLogger.warning(
                    f"Unsupported preamble file was not converted: {preamble.name}"
                )

        for scenario in self._scenarios:
            if scenario.suffix == STPRecord.sss_file_extension:
                ctx.parse_file(scenario)
            else:
                ConverterLogger.warning(
                    f"Unsupported scenario file was not converted: {scenario.name}"
                )

        sd_name = out_dir / (self._name + ".sd")
        sd_name_checks = out_dir / (self._name + "_checks.sd")

        if gc_disable:
            gc.disable()

        ConverterLogger.getLogger(self._name + " (inputs)")

        sd_file = sd.create_file(str(sd_name))
        ctx.sdf = sd_file
        ctx.sdio_type = SDType.INPUT
        self._write_file(sd_name, ctx)

        ConverterLogger.getLogger(self._name + " (checks)")

        sd_file = sd.create_file(str(sd_name_checks))
        ctx.sdf = sd_file
        ctx.sdio_type = SDType.OUTPUT
        self._write_file(sd_name_checks, ctx)

        if gc_disable:
            gc.enable()

        return [sd_name, sd_name_checks]

    def _write_file(self, sd_name: Path, ctx: "SDContext"):
        """Writes the sd file

        Parameters
        ----------
        sd_name : str
            name of created file
        ctx : SDContext
            simdata context of writing file
        """
        ctx.eval_cmds()
        ctx.sdf.close()
        sd_fd = sd.open_file(str(sd_name))
        sd_content = str(sd_fd)
        sd_fd.close()
        if ConverterLogger.SD_VERBOSE:
            print(f"Created {sd_name}")
            print(sd_content)
        ConverterLogger.debug(f"Created {sd_name}: {sd_content}")

    def associate_sd_files(self):
        """Associates the new sd files to project"""
        raise NotImplementedError

    def get_sss_files_names(self) -> str:
        """Gets all file names of all sss file paths"""
        return (
            f"inits {[path.name for path in self._inits]}"
            f"\npreambles {[path.name for path in self._preambles]}"
            f"\nscenarios {[path.name for path in self._scenarios]}"
        )

    def __str__(self):
        return f"inits {self._inits}\npreambles {self._preambles}\nscenarios {self._scenarios}"


class STPContext:
    """STP data that includes all paths to SSS files"""

    def __init__(self, swan_ctx: SwanContext, root_operator: Optional[str] = None) -> None:
        self._output_dir: Path = Path(".")
        self._stp_path: Path = None
        self._records: list[STPRecord] = []
        self._generated_files = []
        self._stp_root = None
        self._swan_ctx = swan_ctx
        self._operator = None
        self._root_operator = root_operator

    @property
    def swan_context(self) -> SwanContext:
        return self._swan_ctx

    @property
    def stp_path(self) -> Path:
        """Returns STP file path"""
        return self._stp_path

    @stp_path.setter
    def stp_path(self, path: Union[str, Path]):
        """Sets STP file path"""
        if isinstance(path, str):
            path = Path(path)
        self._stp_path = path

    @property
    def proj_path(self) -> str:
        """Returns swan project path"""
        return self._proj_path

    @proj_path.setter
    def proj_path(self, proj_path: str) -> None:
        """Sets swan project path, required to get variable types"""
        self._proj_path = proj_path

    def _load_stp(self):
        if self._stp_path is None:
            ConverterLogger.exception("No STP path was defined for this context")
        try:
            tree = ET.parse(self._stp_path)
            root = tree.getroot()
            self._output_dir = self._output_dir / root.attrib["name"]
            # use user provided operator if it exists, or get from STP file
            if self._root_operator is not None:
                self._operator = self._root_operator
            else:
                if "operator" not in root.attrib:
                    raise Exception("Missing operator attribute")
                self._operator = root.attrib["operator"]
            self._stp_root = root

        except Exception as e:
            ConverterLogger.exception(f"Error while loading STP file : {e}")

    def load_record(self, record_name: str):
        """Reads STP file and loads all sss file paths for the specified record name"""

        self._load_stp()
        try:
            for record in self._stp_root.findall(".//Record"):
                if record.attrib["name"] == record_name:
                    self._parse_xml_record(record)
                    return
        except Exception as e:
            ConverterLogger.exception(f"Error while loading STP file : {e}")
        ConverterLogger.exception(f"No record was found for {record_name} in STP file")

    def load_all_records(self) -> None:
        """Reads STP file and appends sss paths from EACH of the STP records"""

        self._load_stp()
        try:
            for record in self._stp_root.findall(".//Record"):
                self._parse_xml_record(record)
        except Exception as e:
            ConverterLogger.exception(f"Error while loading STP file : {e}")

    def _parse_xml_record(self, record: ET.Element) -> None:
        """Parses a record element in XML"""

        stp_record = STPRecord(record.attrib["name"])
        record_inits = record.find("inits")
        record_preambles = record.find("preambles")
        record_scenarios = record.find("scenarios")
        if record_inits is not None:
            inits = []
            for init in record_inits:
                sss_path = self._stp_path.parent / init.attrib["persistAs"]
                inits.append(sss_path.resolve())
            stp_record.inits = inits
        if record_preambles is not None:
            preambles = []
            for preamble in record_preambles:
                sss_path = self._stp_path.parent / preamble.attrib["persistAs"]
                preambles.append(sss_path.resolve())
            stp_record.preambles = preambles
        if record_scenarios is not None:
            scenarios = []
            for scenario in record_scenarios:
                sss_path = self._stp_path.parent / scenario.attrib["persistAs"]
                scenarios.append(sss_path.resolve())
            stp_record.scenarios = scenarios
        self._records.append(stp_record)

    @property
    def generated_files(self) -> list[str]:
        """Gets the list of created files"""
        return self._generated_files

    def get_record_names(self) -> list[str]:
        """Gets all record names in a list"""
        return [record.name for record in self._records]

    @property
    def output_dir(self) -> Path:
        """Gets output directory for simdata files"""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, path: Union[Path, str]) -> None:
        """Sets output directory for simdata files"""
        self._output_dir = Path(path)

    def start_all_converts(self, gc_disable: bool = False) -> bool:
        """Converts all the loaded sss files"""
        self._swan_ctx.get_operator(self._operator)
        try:
            for record in self._records:
                self._generated_files += record.start_convert(
                    self.swan_context, self._output_dir, gc_disable
                )
            return True
        except ScadeOneException as e:
            ConverterLogger.error(f"Error has occurred while converting files: {e}")
            return False
        except Exception as e:
            ConverterLogger.error(f"Internal error has occurred while converting files: {e}")
            print(f"Internal error {e}")
            return False

    def associate_sd_files():
        """Associates the new sd files to project"""
        raise NotImplementedError

    def __str__(self):
        return (
            f"STP path: {str(self._stp_path)}"
            f"\nSwan path: {str(self._proj_path)}"
            f"\nRecords: {[str(record.name) for record in self._records]}"
        )
