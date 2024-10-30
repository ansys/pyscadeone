.. _sec_test_results:

Test Results
============
The PyScadeOne services allow to load the test results file in Python objects. :py:class:`TestResultsParser` allows
to use the :py:meth:`load` method to load the test results file and return a :py:class:`TestResults` object.

.. code:: python

    from ansys.scadeone.core.svc.test.test_results import TestResultsParser
    test_results = TestResultsParser.load("test_results.json")

.. currentmodule:: ansys.scadeone.core.svc.test.test_results

TestResultsParser Class
-----------------------
This section describes the main class for parsing the test results files.

.. autoclass:: TestResultsParser

TestResults Class
-----------------
:py:class:`TestResults` represents the test results.

.. autoclass:: TestResults

TestCase Class
--------------
:py:class:`TestCase` represents the test cases of the test results.

.. autoclass:: TestCase

TestItem Class
--------------
:py:class:`TestItem` represents the test items of the test results.

.. autoclass:: TestItem

Failure Class
-------------
:py:class:`Failure` represents the failures of the test items.

.. autoclass:: Failure

TestStatus Enum
---------------
:py:class:`TestStatus` represents the status of the test items.

.. autoclass:: TestStatus

TestItemKind Enum
-----------------
:py:class:`TestItemKind` represents the kind of the test items.

.. autoclass:: TestItemKind


