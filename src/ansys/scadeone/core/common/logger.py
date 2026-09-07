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

from enum import auto, Enum
from pathlib import Path
from typing import Optional, Union
import logging
import sys
from types import TracebackType

# Default configuration
GLOBAL_LOGGER_NAME = "PyScadeOne"
DEFAULT_FILE_NAME = "pyscadeone.log"

# Formatting
STDOUT_MSG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

FILE_MSG_FORMAT = STDOUT_MSG_FORMAT


class LoggerLevel(Enum):
    """Logging levels."""

    #: Debug log level
    DEBUG = auto()
    #: Information log level
    INFO = auto()
    #: Warning log level
    WARNING = auto()
    #: Error log level
    ERROR = auto()
    #: Critical log level
    CRITICAL = auto()


class ScadeOneLogger:
    """Logger used for PyScadeOne.

    Parameters
    ----------
    level : LoggerLevel, optional
        Logging level to filter the message severity allowed in the logger.
        The default is ``LoggerLevel.ERROR``.
    catch_all_exceptions : bool, optional
        Whether to catch all uncaught exceptions and log them. By default, ``False``.
    logger_name : str, optional
        Name of the logger. By default, ``None``, which will use the global logger
        name defined in ``GLOBAL_LOGGER_NAME``.
    """

    def __init__(
        self,
        level: LoggerLevel = LoggerLevel.ERROR,
        catch_all_exceptions: bool = False,
        logger_name: str = None,
    ):
        self._logger = logging.getLogger(logger_name if logger_name else GLOBAL_LOGGER_NAME)
        self._logger.setLevel(self._to_logging_level(level))

        if catch_all_exceptions:
            self._add_handling_uncaught_expections()

    @property
    def level(self) -> LoggerLevel:
        """Logging level to filter the message severity allowed in the logger."""
        return self._to_logger_level(self._logger.level)

    @level.setter
    def level(self, value: LoggerLevel = LoggerLevel.DEBUG) -> None:
        """Set logging level to filter the message severity allowed in the logger.

        Parameters
        ----------
        value : LoggerLevel
            Level of Logging to set. By default, ``'DEBUG'``.
        """
        self._logger.setLevel(self._to_logging_level(value))

    def _add_handling_uncaught_expections(self) -> None:
        """Redirect the output of an exception to the logger."""

        def handle_exception(
            exc_type: type[BaseException],
            exc_value: BaseException,
            exc_traceback: TracebackType | None,
        ) -> None:
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self._logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback),
            )

        sys.excepthook = handle_exception

    @staticmethod
    def _to_logging_level(level: LoggerLevel) -> int:
        """Converts LoggerLevel enum to standard logging level.

        Parameters
        ----------
        value : LoggerLevel
            Level of logging to convert.
        """

        match level:
            case LoggerLevel.DEBUG:
                return logging.DEBUG
            case LoggerLevel.INFO:
                return logging.INFO
            case LoggerLevel.WARNING:
                return logging.WARN
            case LoggerLevel.ERROR:
                return logging.ERROR
            case LoggerLevel.CRITICAL:
                return logging.CRITICAL
            case _:
                raise ValueError(f"Invalid logging level: {level}")

    @staticmethod
    def _to_logger_level(level: int) -> LoggerLevel:
        """Converts standard logging level to LoggerLevel enum."""
        match level:
            case logging.DEBUG:
                return LoggerLevel.DEBUG
            case logging.INFO:
                return LoggerLevel.INFO
            case logging.WARNING:
                return LoggerLevel.WARNING
            case logging.ERROR:
                return LoggerLevel.ERROR
            case logging.CRITICAL:
                return LoggerLevel.CRITICAL
            case _:
                raise ValueError(f"Invalid logging level: {level}")

    def log_to_file(
        self,
        folder_path: Optional[Union[Path, str]] = None,
        filename: str = DEFAULT_FILE_NAME,
        level: LoggerLevel = LoggerLevel.DEBUG,
    ) -> None:
        """Add file handler to logger.

        Parameters
        ----------
        folder_path : Path or str, optional
            Path to the folder where the log file will be created. If ``None`` (default),
            a user-specific default folder (``~/.pyscadeone``) will be used.
        filename : str, optional
            Name of the file where the logs are recorded. By default, ``'pyscadeone.log'``.
        level : LoggerLevel, optional
            Level of logging. By default, ``'DEBUG'``.
        """

        self.level = level
        if folder_path is None:
            folder_path = Path.home()
        else:
            folder_path = Path(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(folder_path.joinpath(filename))
        file_handler.setLevel(self._to_logging_level(level))
        file_handler.setFormatter(logging.Formatter(FILE_MSG_FORMAT))
        self._logger.addHandler(file_handler)

    def log_to_console(self, level: LoggerLevel = LoggerLevel.DEBUG) -> None:
        """Add standard output handler to the logger.

        Parameters
        ----------
        level : LoggerLevel, optional
            Level of logging record. By default  ``'DEBUG'``.
        """

        self.level = level
        std_out_handler = logging.StreamHandler()
        std_out_handler.setLevel(self._to_logging_level(level))
        std_out_handler.setFormatter(logging.Formatter(STDOUT_MSG_FORMAT))
        self._logger.addHandler(std_out_handler)

    def flush(self) -> None:
        """Flush any pending log from all handlers."""
        for handler in self._logger.handlers:
            handler.flush()

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity DEBUG on the logger."""
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity INFO on the logger."""
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity WARNING on the logger."""
        self._logger.warning(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception message with severity ERROR on the logger."""
        self._logger.exception(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message with severity ERROR on the logger."""
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity CRITICAL on the logger."""
        self._logger.critical(msg, *args, **kwargs)


LOGGER = ScadeOneLogger()
