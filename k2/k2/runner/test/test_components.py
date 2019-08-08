import unittest

from k2.finder.testfinder import TestCaseDefinition, TestCaseParam
from k2.runner.components import RunnerComponentException, TestContext


def run_function():
    pass


class TestTestContext(unittest.TestCase):

    def test_wraps_test_case_definition_functionality(self):
        tc = TestCaseDefinition(run_function, 'name', [TestCaseParam('key', 'value', str, False)])
        context = TestContext(tc)

        self.assertEqual(tc.name, context.name)
        self.assertEqual(tc.filename_with_params, context.filename_with_params)
        self.assertEqual(tc.params, context.params)
        self.assertEqual(tc.description, context.description)

    def test_raises_exception_when_instantiated_without_test_case_definition(self):
        with self.assertRaises(RunnerComponentException):
            TestContext()
