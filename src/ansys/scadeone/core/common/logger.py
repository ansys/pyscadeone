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
The :py:class:`ScadeOneLogger` class is a subclass of the `logging.Logger` class.
As a singleton, the `ScadeOneLogger` class is initialized once and used
throughout the application using the `logger.LOGGER` object or the `logger`
application attribute.

The default logger is set to log to a file named `pyscadeone.log` and to
the console. The log level is set to `DEBUG`.

One can set the logger to a different logger by setting the `logger` attribute
as in the following example:

.. code:: python

    LOGGER.logger = logging.getLogger("MyLogger")
"""  # numpydoc ignore

# cSpell:ignore levelname

from pathlib import Path
import logging

# From: https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook


class ScadeOneLogger:
    """Class handling the singleton logger."""

    _Logger = None

    def __init__(self) -> None: ...

    @property
    def logger(self) -> logging.Logger:
        """Return the logger instance. The internal logger can be set
        by setting the `logger` attribute."""
        if ScadeOneLogger._Logger is None:
            self._init_logger()
        return self._Logger

    @logger.setter
    def logger(self, logger: logging.Logger) -> None:
        """Set the logger instance."""
        # Unset PyScadeOne default logger if it exists
        pyscadeone_logger = logging.getLogger("PyScadeOne")
        for handler in pyscadeone_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                Path(handler.baseFilename).unlink(missing_ok=True)
            pyscadeone_logger.removeHandler(handler)
        ScadeOneLogger._Logger = logger

    def _init_logger(self):
        """Set the logger instance.

        If the logger instance is not set, create a file logger.
        """
        if ScadeOneLogger._Logger is not None:
            return
        logger = logging.getLogger("PyScadeOne")
        logger.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format)
        # create file handler which logs even debug messages
        fh = logging.FileHandler("pyscadeone.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(ch)
        ScadeOneLogger._Logger = logger

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity DEBUG on the logger."""
        self._init_logger()
        self._Logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity INFO on the logger."""
        self._init_logger()
        self._Logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity WARNING on the logger."""
        self._init_logger()
        self._Logger.warning(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception message with severity ERROR on the logger."""
        self._init_logger()
        self._Logger.exception(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message with severity ERROR on the logger."""
        self._init_logger()
        self._Logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity CRITICAL on the logger."""
        self._init_logger()
        self._Logger.critical(msg, *args, **kwargs)


LOGGER = ScadeOneLogger()
