# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
Scade One Exception
-------------------

The class :py:class:`ScadeOneException` is used to raise an exception.
The message passed when raising the exception is passed to the
Scade One logger :py:class:`ansys.scadeone.core.common.logger.ScadeOneLogger`.
"""
from ansys.scadeone.core.common.logger import LOGGER


class ScadeOneException(Exception):
    """ScadeOne API Exception. When raising a :py:class:`ScadeOneException`
    it is automatically logged.
    See :py:class:`ansys.scadeone.core.common.logger.ScadeOneLogger` for more."""

    def __init__(self, message: str, exc_info: bool = False) -> None:
        super().__init__(message)
        LOGGER.exception(message, exc_info=exc_info)
