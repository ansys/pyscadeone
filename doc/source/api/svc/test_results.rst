.. _ref_test_results:

Test Results
============
The PyScadeOne services allow to load the test results file in Python objects. :py:class:`TestResultsParser` allows
to use the :py:meth:`load` method to load the test results file and return a :py:class:`TestResults` object.

.. code:: python

    from ansys.scadeone.core.svc.test.test_results import TestResultsParser
    test_results = TestResultsParser.load("testResults.json")
