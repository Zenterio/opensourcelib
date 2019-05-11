"""Finds test cases from specified test sources."""

import copy
import inspect
import itertools
import logging
import re
from collections import namedtuple
from enum import Enum
from textwrap import dedent

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.list import LIST_COMMAND
from k2.cmd.run import RUN_COMMAND

from . import FIND_TEST_CASES, FINDER_ENDPOINT, TEST_SOURCES

logger = logging.getLogger(get_logger_name('k2', 'testfinder'))
logger.addHandler(logging.NullHandler())

Function = namedtuple('Function', ['name', 'callable'])


@CommandExtension(
    'testfinder',
    extends=[RUN_COMMAND, LIST_COMMAND],
    config_options=[ConfigOption(TEST_SOURCES, required=True)],
    endpoints_and_messages={
        FINDER_ENDPOINT: [FIND_TEST_CASES]
    })
class TestFinder(AbstractExtension):
    """Implementation of the test finder."""

    __test__ = False  # Make nosetests not consider this class when finding tests

    def __init__(self, config, instances):
        self._test_sources = config.get(TEST_SOURCES)

    @callback_dispatcher([FIND_TEST_CASES], [FINDER_ENDPOINT])
    @requires(component_manager='ComponentManager')
    def find_test_cases(self, message, component_manager):
        return Finder(component_manager).find_tests(*self._test_sources)


class Finder(object):

    def __init__(self, component_manager):
        self.setup_prefix = 'setup'
        self.test_case_prefix = 'test_'
        self.teardown_prefix = 'teardown'
        self.component_manager = component_manager

    def find_tests(self, *names):
        """
        Use nosetests to find the tests using the default naming rules.

        :param names: one or more names where a name can be a file, directory, module, or any object within a module
        """
        from nose.loader import Config, TestLoader

        suite = TestLoader(
            Config(includeExe=True), selector=K2TestSelector()).loadTestsFromNames(names)
        return self._test_cases_from_suite(suite)

    def _test_cases_from_suite(self, suite):
        """
        Recursively goes through the suite to find all matching tests.

        :param suite:
        :return: list of tests
        """
        from nose.failure import Failure

        tests = []
        for test_or_suite in suite:
            if self._is_test(test_or_suite):
                if isinstance(test_or_suite.test, Failure):
                    if test_or_suite.test.address() is not None:
                        _, module, call = test_or_suite.test.address()
                        if call is not None:
                            if isinstance(call, str):
                                name = '{module}.{call}'.format(module=module, call=call)
                            else:
                                name = self._qualified_name(call)
                        else:
                            # Handling of unknown cases
                            name = str(test_or_suite.test)
                    elif 'No such test' in str(test_or_suite.test):
                        # Better message when the test doesn't exist
                        m = re.search(r'No such test ([^)]+)', str(test_or_suite.test))
                        name = m.group(1)
                    else:
                        # Handling of unknown cases
                        name = str(test_or_suite.test)

                    tests.append(TestCaseFailureDefinition(test_or_suite.test.runTest, name))
                else:
                    tests.extend(self._create_testcase_definitions(test_or_suite.test.test))
            else:
                tests.extend(self._test_cases_from_suite(test_or_suite))

        return tests

    def _qualified_name(self, callable):
        if inspect.ismethod(callable) and callable.__self__ is not None:
            return '{module}.{cls}.{name}'.format(
                module=callable.__module__, cls=callable.__class__, name=callable.__name__)
        else:
            return '{module}.{name}'.format(module=callable.__module__, name=callable.__name__)

    def _is_test(self, test_or_suite):
        """
        Test if a test_or_suite is a test.

        :param test_or_suite: the test or suite
        :return: True if test_or_suite is a test
        """
        try:
            iter(test_or_suite)
            return False
        except Exception:
            return True

    def _create_testcase_definitions(self, test):
        """Create a list of test case definitions from test function/method."""
        qfname = self._qualified_name(test)
        foreach = getattr(test, '_k2_foreach', [])
        definitions = []
        if foreach:
            definitions.extend(
                self._create_parameterized_testcase_definitions(test, qfname, foreach))
        else:
            definitions.append(TestCaseDefinition(test, qfname))
        return definitions

    def _create_parameterized_testcase_definitions(self, test, qfname, foreach):
        param_sources = []
        for source in foreach:
            source_result = []
            if isinstance(source.component, str):
                callables = [
                    c for c in self.component_manager.COMPONENT_REGISTRY[source.component]
                    if source.can.issubset(c._zaf_component_can)
                ]
                for callable in callables:
                    clone = copy.copy(source)
                    clone._component = callable
                    source_result.append(
                        TestCaseParam(
                            key=source.argument, value=clone, format=source.format, is_req=True))
            else:
                try:
                    for item in source.component:
                        source_result.append(
                            TestCaseParam(
                                key=source.argument, value=item, format=source.format,
                                is_req=False))
                except TypeError as e:
                    msg = '{err}. foreach only accepts named component (str) or an iterable of values'.format(
                        err=str(e))
                    logger.debug(msg, exc_info=True)
                    raise Exception(msg) from e
            param_sources.append(source_result)

        definitions = []
        for param_set in itertools.product(*param_sources):
            definitions.append(TestCaseDefinition(test, qfname, False, list(param_set)))

        return definitions


class K2TestSelector(object):

    def __init__(self):
        pass

    def wantClass(self, cls):
        return not issubclass(cls, Enum)

    def wantDirectory(self, dirname):
        return True

    def wantFile(self, file):
        return file.endswith('.py')

    def wantFunction(self, function):
        return function.__name__.startswith('test_')

    def wantMethod(self, method):
        return method.__name__.startswith('test_')

    def wantModule(self, module):
        return True


class TestCaseDefinition(object):

    def __init__(self, run_function, name=None, always_included=False, params=None):
        self.run_function = run_function
        self.name = name
        self.always_included = always_included
        self.params = params if params else []

    def __repr__(self):
        return str(self)

    def __str__(self):
        name = self.name if self.name else str(self.run_function)
        if self.params:
            name += '[{params}]'.format(params=','.join([str(p) for p in self.params]))
        return name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ and isinstance(other, self.__class__)

    @property
    def description(self):
        return dedent(self.run_function.__doc__).strip() if self.run_function.__doc__ else ''


class TestCaseFailureDefinition(TestCaseDefinition):

    def __init__(self, run_function, name=None):
        super().__init__(run_function, name, True)


class TestCaseParam(object):

    def __init__(self, key, value, format, is_req):
        self.key = key
        self.value = value
        self.format = format
        self.is_req = is_req

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ and isinstance(other, self.__class__)

    def __str__(self):
        return '{key}={val}'.format(
            key=self.key, val=self.format(self.value if not self.is_req else self.value.name))
