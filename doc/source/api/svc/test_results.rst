.. _ref_test_results:

Test results
============
The PyScadeOne services allow to load the test results file in Python objects. :py:class:`TestResultsParser` allows
to use the :py:meth:`load` method to load the test results file and return a :py:class:`TestResults` object.

.. code:: python

    from ansys.scadeone.core.svc.test.test_results import TestResultsParser
    test_results = TestResultsParser.load("testResults.json")

.. currentmodule:: ansys.scadeone.core.svc.test.test_results

Test results parsing
--------------------
This section describes the main class for parsing the test results files.

.. autoclass:: TestResultsParser

Handling test results
----------------------
:py:class:`TestResults` represents the test results.

.. autoclass:: TestResults

Handling test cases
--------------------
:py:class:`TestCase` represents the test cases of the test results.

.. autoclass:: TestCase

Handling test items
-------------------
:py:class:`TestItem` represents the test items of the test results.

.. autoclass:: TestItem

Failure class
-------------
:py:class:`Failure` represents the failures of the test items.

.. autoclass:: Failure

Test status enum
-----------------
:py:class:`TestStatus` represents the status of the test items.

.. autoclass:: TestStatus

Test item kind enum
-------------------
:py:class:`TestItemKind` represents the kind of the test items.

.. autoclass:: TestItemKind


