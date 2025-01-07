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
