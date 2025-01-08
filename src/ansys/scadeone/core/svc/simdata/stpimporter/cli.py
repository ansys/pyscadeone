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


# cSpell: ignore levelname stpimporter

import argparse
import logging
from pathlib import Path

from ansys.scadeone.core.common.exception import LOGGER, ScadeOneException

from .stp_context import STPContext
from .swan_context import SwanContext
from .utils import ConverterLogger  # noqa: F401

logging.basicConfig(
    filename="stpimporter.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)

LOGGER.logger = ConverterLogger.getLogger("stpimporter")


def cmd_parse():
    ConverterLogger.reset_counts()
    parser = argparse.ArgumentParser(
        prog="stpimporter", description="Convert test procedure to simulation data"
    )
    parser.add_argument("stp_path", type=str, help="STP file path")
    parser.add_argument("sproj_path", type=str, help="Associated Swan project path")
    parser.add_argument("-r", "--record_name", type=str, help="Specific record name")
    parser.add_argument("-o", "--output_directory", type=str, help="Use specific directory")
    parser.add_argument("-s", "--s_one_install", type=str, help="Scade One installation path")
    parser.add_argument("-v", "--verbose_sd", action="store_true", help="Print exported sd files")
    parser.add_argument(
        "-R", "--root", type=str, help="Specify root operator (override STP information)"
    )
    parser.add_argument(
        "-n", "--renamings", type=str, help="Renaming log file from Scade Suite importer"
    )
    parser.add_argument("--no_gc", action="store_true", help="Disable garbage collection")

    args = parser.parse_args()
    if not Path(args.stp_path).exists():
        parser.error(f"STP file does not exists: {args.stp_path}")
    if not Path(args.sproj_path).exists():
        parser.error(f"SPROJ file does not exists: {args.sproj_path}")
    if args.renamings is not None and not Path(args.renamings).exists():
        parser.error(f"Renaming file does not exists: {args.renamings}")

    swan_ctx = SwanContext(
        project_path=args.sproj_path, s_one_path=args.s_one_install, renamings=args.renamings
    )

    stp_ctx = STPContext(swan_ctx, args.root)

    stp_ctx.stp_path = args.stp_path
    stp_ctx.proj_path = args.sproj_path
    ConverterLogger.info(
        f"""Importing:
    STP: {args.stp_path}
    SPROJ: {args.sproj_path}
    Record: {args.record_name}
    Renamings: {args.renamings}
    Root: {args.root}
    S-One: {args.s_one_install}
"""
    )

    if args.verbose_sd:
        ConverterLogger.SD_VERBOSE = True

    if args.output_directory is not None:
        stp_ctx.output_dir = args.output_directory
    try:
        if args.record_name is not None:
            stp_ctx.load_record(args.record_name)
        else:
            stp_ctx.load_all_records()

        stp_ctx.start_all_converts(args.no_gc)
    except ScadeOneException as e:
        print(f"A problem has occurred during the conversion: {e}")
        return 1
    except Exception as e:
        LOGGER.exception("Failed with %s", e)
        print(f"Failed with {e}")
        return 1

    logging.info(
        "Summary: "
        f"""errors: {ConverterLogger.errors} """
        f"""warnings: {ConverterLogger.warnings}"""
    )
    if ConverterLogger.errors > 0:
        return 1
    if ConverterLogger.warnings > 0:
        return 2
    return 0
