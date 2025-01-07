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

from enum import IntEnum
import logging

from ansys.scadeone.core.common.exception import ScadeOneException


class SDType(IntEnum):
    """
    Defines whether the simulation data file to be made
    is a data source (input) or an oracle
    """

    INPUT = 0
    OUTPUT = 1


class ConverterLogger:
    warnings = 0
    errors = 0
    _logger = None
    SD_VERBOSE = False

    @classmethod
    def getLogger(cls, name: str):
        cls._logger = logging.getLogger(name)
        return cls._logger

    @classmethod
    def debug(cls, txt: str):
        cls._logger.debug(txt)

    @classmethod
    def info(cls, txt: str):
        cls._logger.info(txt)

    @classmethod
    def warning(cls, txt: str):
        cls._logger.warning(txt)
        cls.warnings += 1

    @classmethod
    def error(cls, txt: str):
        cls._logger.error(txt)
        cls.errors += 1

    @classmethod
    def exception(cls, txt: str):
        # cls._logger.exception(txt)
        cls.errors += 1
        raise ScadeOneException(txt)

    @classmethod
    def reset_counts(cls):
        cls.warnings = 0
        cls.errors = 0
