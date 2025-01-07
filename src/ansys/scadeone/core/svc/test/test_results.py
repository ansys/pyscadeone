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

# cSpell:ignore strerror
from enum import Enum, auto
import json
from pathlib import Path
from typing import List, Optional, Union

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError, ValidationError

from ansys.scadeone.core import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.versioning import FormatVersions

_SCHEMA = Path(__file__).parents[2] / "libs/test-results-schema.json"


class BaseTestResults:
    __test__ = False


class TestResultsParser(BaseTestResults):
    """Parse the Test results file."""

    @staticmethod
    def load(file: Union[str, Path]) -> Optional["TestResults"]:
        """Read a test results file (.JSON), create and fill a TestResults object.

        Parameters
        ----------
        file
            Test results file path.

        Returns
        -------
        TestResults
            Test results object.

        Raises
        ------
        ScadeOneException
            - Error when file is not found
            - Parse error
        """
        model = TestResultsParser._load_json_file(file)
        if not TestResultsParser._is_valid(model):
            raise ScadeOneException(f"Invalid test results file: {file}")
        if model == {}:
            return None
        return TestResultsParser._create_test_results(model)

    @staticmethod
    def _load_json_file(file: Union[str, Path]) -> dict:
        """Load the JSON file."""
        try:
            if isinstance(file, str):
                try:
                    return json.loads(file)
                except Exception as e1:
                    LOGGER.warning(f"String is not a JSON string: {e1}")
            with open(file, "r") as f:
                return json.load(f)
        except OSError as e2:
            LOGGER.error(f"Error loading test results file: {e2}")
            raise ScadeOneException(f"Error loading test results file: {e2.strerror}")

    @staticmethod
    def _is_valid(model) -> bool:
        """Validate the JSON model against the test results' schema."""
        try:
            with open(_SCHEMA, "r") as f:
                schema = json.load(f)
            Draft7Validator.check_schema(schema)
            validator = Draft7Validator(schema)
            validator.validate(model)
        except OSError as e:
            LOGGER.error(f"Error loading test results schema: {e}")
            return False
        except SchemaError as e:
            LOGGER.error(f"Error validating test results schema: {e}")
            return False
        except ValidationError as e:
            LOGGER.error(f"Error validating test results file: {e}")
            return False
        return True

    @staticmethod
    def _create_test_results(model) -> "TestResults":
        """Create the TestResults object."""
        test_results = TestResults()
        test_results._version = model.get("version")
        TestResultsParser._set_test_cases(model, test_results)
        return test_results

    @staticmethod
    def _set_test_cases(model, test_results: "TestResults") -> None:
        """Set the test cases of the TestResults object."""
        if model.get("test_cases") is None:
            return
        for test_case in model.get("test_cases"):
            tc = TestCase()
            tc._harness = test_case.get("harness")
            tc._start = test_case.get("start")
            tc._end = test_case.get("end")
            tc._status = TestResultsParser._create_test_status(test_case.get("status"))
            tc._cycles_count = test_case.get("cycles_count")
            tc._test_items = TestResultsParser._create_test_items(test_case)
            test_results._test_cases.append(tc)

    @staticmethod
    def _create_test_status(status: str) -> Optional["TestStatus"]:
        if status == "passed":
            return TestStatus.Passed
        elif status == "failed":
            return TestStatus.Failed
        elif status == "error":
            return TestStatus.Error
        else:
            return None

    @staticmethod
    def _create_test_items(test_case) -> List["TestItem"]:
        """Create the TestItem objects of the test case."""
        test_items = []
        if test_case.get("test_items") is None:
            return test_items
        for test_item in test_case.get("test_items"):
            ti = TestItem()
            ti._kind = TestResultsParser._create_test_item_kind(test_item.get("kind"))
            ti._model_path = test_item.get("model_path")
            ti._passed_count = test_item.get("passed_count")
            ti._failures = TestResultsParser._create_failures(test_item)
            test_items.append(ti)
        return test_items

    @staticmethod
    def _create_test_item_kind(kind: str) -> Optional["TestItemKind"]:
        if kind == "assert":
            return TestItemKind.Assert
        elif kind == "oracle":
            return TestItemKind.Oracle
        else:
            return None

    @staticmethod
    def _create_failures(test_item) -> List["Failure"]:
        """Create the Failure objects of the test item."""
        failures = []
        if test_item.get("failures") is None:
            return failures
        for failure in test_item.get("failures"):
            f = Failure()
            f._cycle = failure.get("cycle")
            f._actual = failure.get("actual")
            f._expected = failure.get("expected")
            f._float32_atol = failure.get("float32_atol")
            f._float32_rtol = failure.get("float32_rtol")
            f._float64_atol = failure.get("float64_atol")
            f._float64_rtol = failure.get("float64_rtol")
            f._parts_error_paths = failure.get("parts_error_paths")
            failures.append(f)
        return failures


class TestResults(BaseTestResults):
    """Test results object."""

    def __init__(self):
        self._version = None
        self._test_cases = []

    @property
    def version(self) -> str:
        """Returns the test results version."""
        return self._version

    def check_version(self):
        """Check the version of the test results.

        Raises
        ------

        ScadeOneException
            If the version is not supported
        """
        FormatVersions.check("test_results", self.version)

    @property
    def test_cases(self) -> List["TestCase"]:
        """Returns the list of test cases."""
        return self._test_cases


class TestCase(BaseTestResults):
    """Test case object."""

    def __init__(self):
        self._harness = None
        self._start = None
        self._end = None
        self._status = None
        self._cycles_count = None
        self._test_items = []

    @property
    def harness(self) -> str:
        """Returns the test harness namespace."""
        return self._harness

    @property
    def start(self) -> str:
        """Returns the test case start time."""
        return self._start

    @property
    def end(self) -> str:
        """Returns the test case end time."""
        return self._end

    @property
    def status(self) -> "TestStatus":
        """Returns the test case status."""
        return self._status

    @property
    def cycles_count(self) -> int:
        """Returns the test case cycles count."""
        return self._cycles_count

    @property
    def test_items(self) -> List["TestItem"]:
        """Returns the list of test items."""
        return self._test_items


class TestStatus(BaseTestResults, Enum):
    """Test status."""

    Passed = auto()
    """Test passed."""
    Failed = auto()
    """Test failed."""
    Error = auto()
    """Test error."""


class TestItem(BaseTestResults):
    """Test item object."""

    def __init__(self):
        self._kind = None
        self._model_path = None
        self._passed_count = None
        self._failures = []

    @property
    def kind(self) -> "TestItemKind":
        """Returns the test item kind."""
        return self._kind

    @property
    def model_path(self) -> str:
        """Returns the test item model path."""
        return self._model_path

    @property
    def passed_count(self) -> int:
        """Returns the test item passed count."""
        return self._passed_count

    @property
    def failures(self) -> List["Failure"]:
        """Returns the list of failures."""
        return self._failures


class TestItemKind(BaseTestResults, Enum):
    """Test item kind."""

    Assert = auto()
    """Assert test item."""
    Oracle = auto()
    """Oracle test item."""


class Failure:
    """Failure object."""

    def __init__(self):
        self._cycle = None
        self._actual = None
        self._expected = None
        self._float32_atol = None
        self._float32_rtol = None
        self._float64_atol = None
        self._float64_rtol = None
        self._parts_error_paths = []

    @property
    def cycle(self) -> int:
        """Returns the failure cycle."""
        return self._cycle

    @property
    def actual(self) -> str:
        """Returns the failure actual value."""
        return self._actual

    @property
    def expected(self) -> str:
        """Returns the failure expected value."""
        return self._expected

    @property
    def float32_atol(self) -> Union[int, float]:
        """Returns the absolute tolerance applied in float32 comparisons."""
        return self._float32_atol

    @property
    def float32_rtol(self) -> Union[int, float]:
        """Returns the relative tolerance applied in float32 comparisons."""
        return self._float32_rtol

    @property
    def float64_atol(self) -> Union[int, float]:
        """Returns the absolute tolerance applied in float64 comparisons."""
        return self._float64_atol

    @property
    def float64_rtol(self) -> Union[int, float]:
        """Returns the relative tolerance applied in float64 comparisons."""
        return self._float64_rtol

    @property
    def parts_error_paths(self) -> List[str]:
        """Returns the list of parts error paths."""
        return self._parts_error_paths
