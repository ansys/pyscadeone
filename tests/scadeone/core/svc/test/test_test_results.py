# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path

import pytest

from ansys.scadeone.core import ScadeOneException
from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.svc.test.test_results import (
    TestItemKind,
    TestResultsParser,
    TestStatus,
)

TEST_RESULTS_FILE = Path(__file__).parents[1] / "test/refs/test-results-example.json"


class TestTestResults:
    def test_valid_str(self):
        test_res_str = """
        {
          "$schema": "test-results-schema.json",
          "version" : "1.0",
          "test_cases" : [
            { "harness" : "test1::harness1",
              "start" : "2024-06-25T13:28:57.592",
              "end" : "2024-06-25T13:28:57.593",
              "status" : "failed",
              "cycles_count" : 3,
                "test_items" : [
                    {
                      "kind" : "oracle",
                      "model_path" : "test1::harness1/#oracle1:oStruct2",
                      "passed_count" : 1,
                      "failures" : [
                        {
                          "cycle" : 1,
                          "actual" : "{{1, 2}, 3.0}",
                          "expected" : "{{1, 2}, 42.0}",
                          "float32_atol": 1e-5,
                          "float32_rtol": 0.01,
                          "parts_error_paths" : [ ".f2" ]
                        }
                      ]
                    }
                ]
            }
          ]
        }
        """
        test_res = TestResultsParser.load(test_res_str)
        test_res.check_version()
        assert test_res.version == FormatVersions.version("test_results")
        assert len(test_res.test_cases) == 1
        test_case = test_res.test_cases[0]
        assert test_case.harness == "test1::harness1"
        assert test_case.start == "2024-06-25T13:28:57.592"
        assert test_case.end == "2024-06-25T13:28:57.593"
        assert test_case.status == TestStatus.Failed
        assert test_case.cycles_count == 3
        assert len(test_case.test_items) == 1
        test_item = test_case.test_items[0]
        assert test_item.kind == TestItemKind.Oracle
        assert test_item.model_path == "test1::harness1/#oracle1:oStruct2"
        assert test_item.passed_count == 1
        failure = test_item.failures[0]
        assert failure.cycle == 1
        assert failure.actual == "{{1, 2}, 3.0}"
        assert failure.expected == "{{1, 2}, 42.0}"
        assert failure.float32_atol == 1e-5
        assert failure.float32_rtol == 0.01
        assert failure.parts_error_paths == [".f2"]

    def test_invalid_json(self):
        with pytest.raises(ScadeOneException) as e:
            TestResultsParser.load("invalid")
        assert len(e.value.args) == 1
        assert "Error loading test results file: No such file or directory" in str(e.value.args[0])

    def test_empty_json(self):
        assert TestResultsParser.load("{}") is None

    def test_invalid_results_json(self):
        test_res_str = """
                {
                  "$schema": "test-results-schema.json",
                  "version" : "0.1",
                  "test_cases" : [
                    {
                        "harness" : "test1::harness1"
                    }
                  ]
                }
        """
        with pytest.raises(ScadeOneException, match="Invalid test results file: \\.*") as e:  # noqa: F841
            TestResultsParser.load(test_res_str)

    def test_valid_file(self):
        test_res = TestResultsParser.load(TEST_RESULTS_FILE)
        assert test_res.version == FormatVersions.version("test_results")
        assert len(test_res.test_cases) == 1
        test_case = test_res.test_cases[0]
        assert test_case.harness == "test1::harness1"
        assert test_case.start == "2024-06-25T13:28:57.592"
        assert test_case.end == "2024-06-25T13:28:57.593"
        assert test_case.status is TestStatus.Failed
        assert test_case.cycles_count == 3
        assert len(test_case.test_items) == 4
        test_item = test_case.test_items[0]
        assert test_item.kind is TestItemKind.Oracle
        assert test_item.model_path == "oracle1/oStruct2"
        assert test_item.passed_count == 1
        assert len(test_item.failures) == 1
        failure = test_item.failures[0]
        assert failure.cycle == 3
        assert failure.actual == "{f1:{1, 2}, f2:3.0}"
        assert failure.expected == "{f1:{1, 2}, f2:43.0}"
        assert failure.float32_atol == 1e-5
        assert failure.float32_rtol == 0.01
        assert failure.float64_atol == 1e-9
        assert failure.float64_rtol == 0.001
        assert failure.parts_error_paths == [".f2"]
        test_item = test_case.test_items[1]
        assert test_item.kind == TestItemKind.Oracle
        assert test_item.model_path == "oracle1/oStruct1Array23"
        assert test_item.passed_count == 2
        assert len(test_item.failures) == 1
        failure = test_item.failures[0]
        assert failure.cycle == 3
        assert (
            failure.actual
            == "[[{f1:1, f2:2}, {f1:3, f2:4}], [{f1:5, f2:6}, {f1:7, f2:8}], [{f1:9, f2:10}, {f1:11, f2:12}]]"
        )
        assert (
            failure.expected
            == "[[{f1:1, f2:2}, {f1:3, f2:4}], [{f1:45, f2:46}, {f1:7, f2:8}], [{f1:49, f2:10}, {f1:11, f2:12}]]"
        )
        assert failure.float32_atol == 1e-5
        assert failure.float32_rtol == 0.01
        assert failure.float64_atol == 1e-9
        assert failure.float64_rtol == 0.001
        assert failure.parts_error_paths == ["[1][0]", "[2][0].f1"]
        test_item = test_case.test_items[2]
        assert test_item.kind == TestItemKind.Assert
        assert test_item.model_path == "test1::harness1/CHECK_O0_ROOT="
        assert test_item.passed_count == 3
        assert len(test_item.failures) == 0
        test_item = test_case.test_items[3]
        assert test_item.kind == TestItemKind.Assert
        assert test_item.model_path == "test1::harness1/#inst1:CHECK_O0_IN_INSTANCE="
        assert test_item.passed_count == 2
        assert len(test_item.failures) == 1
        failure = test_item.failures[0]
        assert failure.cycle == 3
