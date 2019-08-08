import unittest
from unittest.mock import Mock, patch

from nose.case import FunctionTestCase, Test
from nose.failure import Failure
from nose.selector import TestAddress
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.component.decorator import component
from zaf.component.manager import ComponentManager, create_entity_map, create_registry
from zaf.config.manager import ConfigManager

from k2.finder.testfinder import TestCaseDefinition, TestCaseParam
from k2.runner.decorator import foreach

from .. import FIND_TEST_CASES, FINDER_ENDPOINT, TEST_SOURCES
from ..testfinder import Finder, TestFinder


def create_nose_test_case(testfn):
    return Test(FunctionTestCase(testfn))


class TestTestFinder(unittest.TestCase):

    def test_test_finder_extension_calls_finder_when_receiving_request(self):
        config = ConfigManager()
        config.set(TEST_SOURCES, ['name1', 'name2'])

        with ExtensionTestHarness(TestFinder, config=config) as harness:

            expected_result = Mock()
            # Don't want to run the real finder because it's very hard to get nose to work as intended
            # inside a unittest
            with patch('k2.finder.testfinder.Finder.find_tests',
                       return_value=expected_result) as find_tests_mock:
                actual_tests = harness.send_request(
                    FIND_TEST_CASES, FINDER_ENDPOINT).wait(timeout=1)[0].result(timeout=1)
                self.assertEqual(expected_result, actual_tests)
                find_tests_mock.assert_called_with('name1', 'name2')


class TestOfFinderMappingNoseTestsToK2TestCases(unittest.TestCase):

    def setUp(self):
        self.component_manager = ComponentManager(create_registry(), create_entity_map())

    def test_plain_test(self):

        def t():
            pass

        suite = [create_nose_test_case(t)]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        expected = [TestCaseDefinition(t, 'k2.finder.test.test_testfinder.t')]
        self.assertEqual(actual, expected)

    def test_failure_to_parse(self):

        failed_test = Test(
            Failure(
                Exception,
                'msg',
                address=TestAddress(
                    'k2.finder.test.test_test_finder:TestOfFinderMappingNoseTestsToK2TestCases.test_function'
                ).totuple()))
        suite = [failed_test]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        with self.assertRaises(Exception, msg='msg'):
            actual[0].run_function()

    def test_nested_suites(self):

        def t1():
            pass

        def t2():
            pass

        suite = [create_nose_test_case(t1), [create_nose_test_case(t2)]]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        expected = [
            TestCaseDefinition(t1, 'k2.finder.test.test_testfinder.t1'),
            TestCaseDefinition(t2, 'k2.finder.test.test_testfinder.t2'),
        ]
        self.assertEqual(actual, expected)


class TestOfFinderForEach(unittest.TestCase):

    def setUp(self):
        self.component_manager = ComponentManager(create_registry(), create_entity_map())

    def test_data_parameterization(self):

        @foreach(d=range(2))
        def t(d):
            pass

        suite = [create_nose_test_case(t)]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        expected = [
            TestCaseDefinition(
                t, 'k2.finder.test.test_testfinder.t', False, [TestCaseParam('d', 0, str, False)]),
            TestCaseDefinition(
                t, 'k2.finder.test.test_testfinder.t', False, [TestCaseParam('d', 1, str, False)]),
        ]
        self.assertEqual(actual, expected)

    def test_component_parameterization(self):

        @component(name='Comp', component_manager=self.component_manager)
        def comp1():
            pass

        @component(name='Comp', component_manager=self.component_manager)
        def comp2():
            pass

        @foreach(c='Comp')
        def t(c):
            pass

        suite = [create_nose_test_case(t)]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        self.assertEqual(actual[0].params[0].key, 'c')
        self.assertEqual(actual[0].params[0].value.component, comp1)
        self.assertEqual(actual[1].params[0].key, 'c')
        self.assertEqual(actual[1].params[0].value.component, comp2)

    def test_mixed_parameterization(self):

        @component(name='Comp', component_manager=self.component_manager)
        def comp1():
            pass

        @component(name='Comp', component_manager=self.component_manager)
        def comp2():
            pass

        @foreach(c='Comp')
        @foreach(d=[1, 2])
        def t(c, d):
            pass

        suite = [create_nose_test_case(t)]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)

        self.assertEqual(actual[0].params[0].key, 'c')
        self.assertEqual(actual[0].params[0].value.component, comp1)
        self.assertEqual(actual[0].params[1].key, 'd')
        self.assertEqual(actual[0].params[1].value, 1)

        self.assertEqual(actual[1].params[0].key, 'c')
        self.assertEqual(actual[1].params[0].value.component, comp1)
        self.assertEqual(actual[1].params[1].key, 'd')
        self.assertEqual(actual[1].params[1].value, 2)

        self.assertEqual(actual[2].params[0].key, 'c')
        self.assertEqual(actual[2].params[0].value.component, comp2)
        self.assertEqual(actual[2].params[1].key, 'd')
        self.assertEqual(actual[2].params[1].value, 1)

        self.assertEqual(actual[3].params[0].key, 'c')
        self.assertEqual(actual[3].params[0].value.component, comp2)
        self.assertEqual(actual[3].params[1].key, 'd')
        self.assertEqual(actual[3].params[1].value, 2)

    def test_component_parameterization_filtered_on_can(self):

        @component(name='Comp', can=['one', 'common'], component_manager=self.component_manager)
        def comp1():
            pass

        @component(name='Comp', can=['two', 'common'], component_manager=self.component_manager)
        def comp2():
            pass

        @foreach(c='Comp', can=['one'])
        def t1(c):
            pass

        @foreach(c='Comp', can=['common'])
        def t(c):
            pass

        suite = [create_nose_test_case(t1)]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        self.assertEqual(actual[0].params[0].key, 'c')
        self.assertEqual(actual[0].params[0].value.component, comp1)

        suite = [create_nose_test_case(t)]
        actual = Finder(self.component_manager)._test_cases_from_suite(suite)
        self.assertEqual(actual[0].params[0].key, 'c')
        self.assertEqual(actual[0].params[0].value.component, comp1)
        self.assertEqual(actual[1].params[0].key, 'c')
        self.assertEqual(actual[1].params[0].value.component, comp2)

    def test_non_iterable_raise_exception(self):

        @foreach(i=1)
        def t(i):
            pass

        suite = [create_nose_test_case(t)]

        with self.assertRaises(Exception) as ctx:
            Finder(self.component_manager)._test_cases_from_suite(suite)
        self.assertIn("'int' object is not iterable", str(ctx.exception))


def run_function():
    pass


class TestTestCaseDefinition(unittest.TestCase):

    def test_str_returns_name_when_name_is_specified_and_there_are_no_params(self):
        self.assertEqual(str(TestCaseDefinition(run_function, name='name')), 'name')

    def test_str_returns_run_function_name_when_name_is_not_specified_and_there_are_no_params(self):
        self.assertEqual(str(TestCaseDefinition(run_function)), 'run_function')

    def test_str_returns_appends_list_of_params_to_name(self):
        self.assertEqual(
            str(
                TestCaseDefinition(
                    run_function,
                    params=[
                        TestCaseParam('param1', 'value1', str, False),
                        TestCaseParam('param2', 'value2', str, False)
                    ])), 'run_function[param1=value1,param2=value2]')

    def test_filename_with_params_joins_name_and_params_with_dash_and_replaces_equal_with_underscore(
            self):
        self.assertEqual(
            TestCaseDefinition(
                run_function,
                params=[
                    TestCaseParam('param1', 'value1', str, False),
                    TestCaseParam('param2', 'value2', str, False)
                ]).filename_with_params, 'run_function-param1_value1-param2_value2')

    def test_filename_with_params_without_params_returns_name(self):
        self.assertEqual(TestCaseDefinition(run_function).filename_with_params, 'run_function')

    def test_filename_with_params_removes_non_recommended_filename_characters(self):
        self.assertEqual(
            TestCaseDefinition(run_function, name='a!"#!)¤?#¤#.-').filename_with_params, 'a.-')
