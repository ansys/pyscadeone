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

import logging
import sys
from pathlib import Path
from typing import Iterator

import pytest

from ansys.scadeone.core.common.logger import (
    FILE_MSG_FORMAT,
    GLOBAL_LOGGER_NAME,
    DEFAULT_FILE_NAME,
    LOGGER,
    LoggerLevel,
)


@pytest.fixture(autouse=True)
def reset_global_logger_handlers() -> Iterator[None]:
    """Keep tests independent because Logger uses a shared global logger name."""
    logger = logging.getLogger(GLOBAL_LOGGER_NAME)
    original_handlers = list(logger.handlers)
    original_level = logger.level

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    yield

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    logger.setLevel(original_level)
    for handler in original_handlers:
        logger.addHandler(handler)


class TestLogger:
    def test_to_logging_level_maps_all_levels(self) -> None:
        assert LOGGER._to_logging_level(LoggerLevel.DEBUG) == logging.DEBUG
        assert LOGGER._to_logging_level(LoggerLevel.INFO) == logging.INFO
        assert LOGGER._to_logging_level(LoggerLevel.WARNING) == logging.WARN
        assert LOGGER._to_logging_level(LoggerLevel.ERROR) == logging.ERROR
        assert LOGGER._to_logging_level(LoggerLevel.CRITICAL) == logging.CRITICAL

    def test_to_logger_level_maps_enum_levels(self) -> None:
        assert LOGGER._to_logger_level(logging.DEBUG) == LoggerLevel.DEBUG
        assert LOGGER._to_logger_level(logging.INFO) == LoggerLevel.INFO
        assert LOGGER._to_logger_level(logging.WARNING) == LoggerLevel.WARNING
        assert LOGGER._to_logger_level(logging.ERROR) == LoggerLevel.ERROR
        assert LOGGER._to_logger_level(logging.CRITICAL) == LoggerLevel.CRITICAL

    def test_to_logger_level_raises_for_invalid_value(self) -> None:
        with pytest.raises(ValueError, match="Invalid logging level"):
            LOGGER._to_logger_level(logging.NOTSET)

    def test_logger_level_setter_updates_underlying_logger_level(self) -> None:
        LOGGER.level = LoggerLevel.INFO
        assert LOGGER._logger.level == logging.INFO

        LOGGER.level = LoggerLevel.ERROR
        assert LOGGER._logger.level == logging.ERROR

    def test_log_to_file_writes_message_to_file(self, tmp_path: Path) -> None:
        other_log_file = "my_pyscadeone.log"

        # customized log file => up to INFO, no DEBUG logs
        LOGGER.log_to_file(folder_path=tmp_path, filename=other_log_file, level=LoggerLevel.INFO)

        # default pyscadeone logger (LoggerLevel.DEBUG)
        LOGGER.log_to_file(folder_path=tmp_path)

        _generate_logs()

        default_log_content = tmp_path.joinpath(DEFAULT_FILE_NAME).read_text(encoding="utf-8")
        custom_file_content = tmp_path.joinpath(other_log_file).read_text(encoding="utf-8")

        expected_messages = [
            "Critical message for users",
            "Error message for users",
            "Warning message for users",
            "Info message for users",
        ]

        for msg in expected_messages:
            assert msg in default_log_content, (
                f"Expected message: {msg} missing in Default log file"
            )
            assert msg in custom_file_content, f"Expected message: {msg} missing in Custom log file"

        assert "Debug message only for developers" in default_log_content
        assert "Debug message only for developers" not in custom_file_content

    def test_log_to_stdout_adds_stream_handler_with_configured_level(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        LOGGER.log_to_console(level=LoggerLevel.WARNING)

        stream_handlers = [h for h in LOGGER._logger.handlers if type(h) is logging.StreamHandler]
        assert len(stream_handlers) == 1
        assert stream_handlers[0].level == logging.WARNING
        assert stream_handlers[0].formatter is not None
        assert stream_handlers[0].formatter._fmt == FILE_MSG_FORMAT

        # Force the handler stream to stdout so we can assert on captured output.
        stream_handlers[0].setStream(sys.stdout)

        _generate_logs()

        captured = capsys.readouterr()

        expected_messages = [
            "Critical message for users",
            "Error message for users",
            "Warning message for users",
        ]
        for msg in expected_messages:
            assert msg in captured.out, f"Expected message: {msg} not logged in console"

        unexpected_messages = ["Info message for users", "Debug message only for developers"]
        for msg in unexpected_messages:
            assert msg not in captured.out, f"Unexpected message: {msg} logged in console"


def _generate_logs() -> None:
    LOGGER.critical("Critical message for users")
    LOGGER.error("Error message for users")
    LOGGER.warning("Warning message for users")
    LOGGER.info("Info message for users")
    LOGGER.debug("Debug message only for developers")
