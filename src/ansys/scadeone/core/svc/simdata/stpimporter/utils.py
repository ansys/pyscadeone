#
# Copyright (c) 2024-2024 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

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
