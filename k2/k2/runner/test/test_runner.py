import unittest
from queue import Queue
from unittest.mock import Mock

from zaf.component.decorator import component, requires
from zaf.component.factory import Factory, _InstanceId
from zaf.component.manager import ComponentManager
from zaf.component.scope import Scope

from k2.finder.testfinder import TestCaseDefinition
from k2.scheduler import SCHEDULE_NEXT_TEST

from ..decorator import disabled
from ..messages import AbortTestCaseRequest
from ..runner import TestCaseAborted, TestRunner
from ..testcase import Verdict


class TestTestRunner(unittest.TestCase):

    def setUp(self):
        self.run_queue = []
        messagebus = Mock()

        def send_request(message_id, endpoint_id=None, entities=None, data=None):
            futures = Mock()
            if message_id == SCHEDULE_NEXT_TEST:
                future = Mock()
                if self.run_queue:
                    future.result.return_value = self.run_queue.pop(0)
                else:
                    future.result.return_value = None

                futures.wait.return_value = [future]
            return futures

        messagebus.send_request.side_effect = send_request

        self.tr = TestRunner(
            messagebus=messagebus,
            component_factory=Factory(ComponentManager()),
            suite_name='suite-name')
        self.tr.QUEUE_TIMEOUT_SECONDS = 1
        self.tr.EXECUTION_PAUSED_TIMEOUT_SECONDS = 1

    def test_run_history_is_initially_the_empty_list(self):
        assert self.tr.run_history == []

    def test_is_running_returns_false_initially(self):
        assert self.tr.is_running is False

    def test_running_test_cases_is_initially_the_empty_list(self):
        assert self.tr.running_test_cases == []

    def test_run_single_passing_test_case(self):

        def my_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert self.tr.run_history[0].verdict == Verdict.PASSED

    def test_run_multiple_passing_test_cases(self):

        def my_test_case():
            pass

        def my_other_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert self.tr.run_history[0].verdict == Verdict.PASSED
        assert self.tr.run_history[1].run == my_other_test_case
        assert self.tr.run_history[1].verdict == Verdict.PASSED

    def test_run_test_case_that_results_in_error(self):
        my_exception = Exception()

        def my_test_case():
            raise my_exception

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert self.tr.run_history[0].verdict == Verdict.ERROR
        assert self.tr.run_history[0].exception == my_exception

    def test_run_test_case_that_is_disabled(self):

        @disabled('this test case is disabled')
        def my_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert self.tr.run_history[0].verdict == Verdict.IGNORED
        assert 'this test case is disabled' in str(self.tr.run_history[0].exception)

    def test_run_test_case_that_results_in_failure(self):
        my_exception = AssertionError()

        def my_test_case():
            raise my_exception

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert self.tr.run_history[0].verdict == Verdict.FAILED
        assert self.tr.run_history[0].exception == my_exception

    def test_run_multiple_test_cases(self):
        running_tests = []

        def my_first_test_case():
            running_tests.append('my_first_test_case')

        def my_other_test_case():
            running_tests.append('my_other_test_case')

        self.run_queue.append(TestCaseDefinition(my_first_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert running_tests == ['my_first_test_case', 'my_other_test_case']

    def test_running_test_cases_contains_the_currently_running_test(self):
        running_test_cases = []

        def my_test_case():
            running_test_cases.extend(self.tr.running_test_cases)

        run_queue = [TestCaseDefinition(my_test_case)]
        self.run_queue.extend(run_queue)
        self.tr.run()
        assert running_test_cases[0].run == run_queue[0].run_function

    def test_abort_test_case(self):

        class MyException(Exception):
            pass

        def my_test_case():
            execution_id = self.tr.running_test_cases[0].execution_id
            request = AbortTestCaseRequest(execution_id, MyException)
            self.tr.abort_test_case(request)

        def my_other_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert isinstance(self.tr.run_history[0].exception, MyException)
        assert self.tr.run_history[0].verdict == Verdict.ERROR
        assert self.tr.run_history[1].run == my_other_test_case
        assert self.tr.run_history[1].verdict == Verdict.PASSED
        assert len(self.tr.run_history) == 2

    def test_abort_run_after_current_test_cases_have_completed(self):

        def my_test_case():
            self.tr.abort_run_after_current_test_cases_have_completed()

        def my_other_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert self.tr.run_history[0].verdict == Verdict.PASSED
        assert self.tr.run_history[1].run == my_other_test_case
        assert self.tr.run_history[1].verdict == Verdict.SKIPPED

    def test_abort_run_immediately(self):

        def my_test_case():
            self.tr.abort_run_immediately()

        def my_other_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert isinstance(self.tr.run_history[0].exception, TestCaseAborted)
        assert self.tr.run_history[0].verdict == Verdict.ERROR
        assert self.tr.run_history[1].run == my_other_test_case
        assert self.tr.run_history[1].verdict == Verdict.SKIPPED

    def test_runner_can_be_used_again_after_a_run_has_been_aborted(self):

        def my_test_case():
            self.tr.abort_run_immediately()

        def my_other_test_case():
            pass

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert self.tr.run_history[0].run == my_test_case
        assert isinstance(self.tr.run_history[0].exception, TestCaseAborted)
        assert self.tr.run_history[0].verdict == Verdict.ERROR
        assert self.tr.run_history[1].run == my_other_test_case
        assert self.tr.run_history[1].verdict == Verdict.SKIPPED
        assert len(self.run_queue) == 0
        assert len(self.tr.running_test_cases) == 0

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.run_queue.append(TestCaseDefinition(my_other_test_case))
        self.tr.run()
        assert self.tr.run_history[2].run == my_test_case
        assert isinstance(self.tr.run_history[0].exception, TestCaseAborted)
        assert self.tr.run_history[2].verdict == Verdict.ERROR
        assert self.tr.run_history[3].run == my_other_test_case
        assert self.tr.run_history[3].verdict == Verdict.SKIPPED
        assert len(self.run_queue) == 0
        assert len(self.tr.running_test_cases) == 0

    def test_run_multiple_test_cases_in_parallel_when_workers_is_more_than_1(self):
        block1 = Queue()
        block2 = Queue()

        def test1():
            block2.put('')
            block1.get(timeout=1)

        def test2():
            block1.put('')
            block2.get(timeout=1)

        self.run_queue.append(TestCaseDefinition(test1))
        self.run_queue.append(TestCaseDefinition(test2))
        self.tr.run(worker_count=2)
        assert self.tr.run_history[0].run in [test1, test2]
        assert self.tr.run_history[0].verdict == Verdict.PASSED
        assert self.tr.run_history[1].run in [test1, test2]
        assert self.tr.run_history[1].verdict == Verdict.PASSED


class TestTestRunnerComponents(unittest.TestCase):

    class Verifier(object):

        def __init__(self):
            self.data = []

    def load_components(self):

        @component()
        @requires(verifier='Verifier')
        class MyComponent(object):

            def __init__(self, verifier):
                self.verifier = verifier

            def __enter__(self):
                self.verifier.data.append('enter')
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.verifier.data.append('exit')

            def __call__(self, *args, **kwargs):
                self.verifier.data.append('call')

        @component()
        @requires(verifier='Verifier')
        class MyEnterFailComponent(object):

            def __init__(self, verifier):
                self.verifier = verifier

            def __enter__(self):
                self.verifier.data.append('enter')
                raise (Exception('enter fails'))

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.verifier.data.append('exit')

            def __call__(self, *args, **kwargs):
                self.verifier.data.append('call')

        @component()
        @requires(verifier='Verifier')
        class MyExitFailComponent(object):

            def __init__(self, verifier):
                self.verifier = verifier

            def __enter__(self):
                self.verifier.data.append('enter')
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.verifier.data.append('exit')
                raise (Exception('exit fails'))

            def __call__(self, *args, **kwargs):
                self.verifier.data.append('call')

    def setUp(self):
        self.component_manager = ComponentManager()
        self.component_manager.clear_component_registry()
        component(scope='session')(TestTestRunnerComponents.Verifier)
        self.load_components()
        self.verifier = TestTestRunnerComponents.Verifier()
        self.parent_scope = Scope('session', None)
        self.parent_scope.register_instance(
            _InstanceId(TestTestRunnerComponents.Verifier, ()), self.verifier)
        self.run_queue = []
        self.messagebus = Mock()

        def send_request(message_id, endpoint_id=None, entities=None, data=None):
            futures = Mock()
            if message_id == SCHEDULE_NEXT_TEST:
                future = Mock()
                if self.run_queue:
                    future.result.return_value = self.run_queue.pop(0)
                else:
                    future.result.return_value = None

                futures.wait.return_value = [future]
            return futures

        self.messagebus.send_request.side_effect = send_request
        self.tr = TestRunner(
            self.messagebus,
            Factory(self.component_manager),
            'suite-name',
            parent_scope=self.parent_scope)

    def test_enters_and_exit_called_on_component_with_test_scope(self):

        @requires(comp='MyComponent', scope='test')
        def my_test_case(comp):
            comp()

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert 'enter' in self.verifier.data
        assert 'call' in self.verifier.data
        assert 'exit' in self.verifier.data

    def test_enters_and_exit_called_on_component_with_module_scope(self):

        @requires(comp='MyComponent', scope='module')
        def my_test_case(comp):
            comp()

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert 'enter' in self.verifier.data
        assert 'call' in self.verifier.data
        assert 'exit' in self.verifier.data

    def test_enters_and_exit_called_on_component_with_class_scope(self):

        class TestMyTestCase(object):

            @requires(comp='MyComponent', scope='class')
            def my_test_case(self, comp):
                comp()

        self.run_queue.append(TestCaseDefinition(TestMyTestCase().my_test_case))
        self.tr.run()
        assert 'enter' in self.verifier.data
        assert 'call' in self.verifier.data
        assert 'exit' in self.verifier.data

    def test_enters_and_exit_called_on_component_with_runner_scope(self):

        @requires(comp='MyComponent', scope='module')
        def my_test_case(comp):
            comp()

        self.run_queue.append(TestCaseDefinition(my_test_case))
        self.tr.run()
        assert 'enter' in self.verifier.data
        assert 'call' in self.verifier.data
        assert 'exit' in self.verifier.data

    def test_enter_and_exit_called_once_on_class_scope_component_for_test_cases_in_same_class(self):

        class TestMyTestCase(object):

            @requires(comp='MyComponent', scope='class')
            def my_test_case1(self, comp):
                comp()

            @requires(comp='MyComponent', scope='class')
            def my_test_case2(self, comp):
                comp()

        test_case_class = TestMyTestCase()
        self.run_queue.extend(
            [
                TestCaseDefinition(test_case_class.my_test_case1),
                TestCaseDefinition(test_case_class.my_test_case2)
            ])
        self.tr.run()
        assert self.verifier.data.count('enter') == 1
        assert self.verifier.data.count('call') == 2
        assert self.verifier.data.count('exit') == 1

    def test_enter_and_exit_called_once_on_module_scope_component_for_test_cases_in_same_module(
            self):

        @requires(comp='MyComponent', scope='module')
        def my_test_case1(comp):
            comp()

        @requires(comp='MyComponent', scope='module')
        def my_test_case2(comp):
            comp()

        self.run_queue.extend(
            [TestCaseDefinition(my_test_case1),
             TestCaseDefinition(my_test_case2)])
        self.tr.run()
        assert self.verifier.data.count('enter') == 1
        assert self.verifier.data.count('call') == 2
        assert self.verifier.data.count('exit') == 1

    def test_enter_and_exit_called_once_on_runner_scope_component(self):

        @requires(comp='MyComponent', scope='runner')
        def my_test_case1(comp):
            comp()

        @requires(comp='MyComponent', scope='runner')
        def my_test_case2(comp):
            comp()

        self.run_queue.extend(
            [TestCaseDefinition(my_test_case1),
             TestCaseDefinition(my_test_case2)])
        self.tr.run()
        assert self.verifier.data.count('enter') == 1
        assert self.verifier.data.count('call') == 2
        assert self.verifier.data.count('exit') == 1

    def test_enter_fails_sets_test_case_verdict_to_error_and_exit_is_called(self):

        @requires(comp='MyEnterFailComponent', scope='runner')
        def my_test_case1(comp):
            comp()

        self.run_queue.extend([TestCaseDefinition(my_test_case1)])
        self.tr.run()
        assert self.tr.run_history[0].verdict == Verdict.ERROR
        assert 'enter' in self.verifier.data
        assert 'call' not in self.verifier.data
        assert 'exit' in self.verifier.data

    def test_enter_fails_sets_test_case_verdict_to_error_and_continues_to_next_test_case(self):

        @requires(comp='MyEnterFailComponent', scope='runner')
        def my_test_case1(comp):
            comp()

        @requires(comp='MyComponent', scope='runner')
        def my_test_case2(comp):
            comp()

        self.run_queue.extend(
            [TestCaseDefinition(my_test_case1),
             TestCaseDefinition(my_test_case2)])
        self.tr.run()
        assert self.tr.run_history[0].verdict == Verdict.ERROR
        assert self.tr.run_history[1].verdict == Verdict.PASSED

    def test_exit_fails_on_test_scope_aborts_test_run(self):

        @requires(comp='MyExitFailComponent', scope='test')
        def my_test_case1(comp):
            comp()

        @requires(comp='MyComponent', scope='runner')
        def my_test_case2(comp):
            comp()

        self.run_queue.extend(
            [TestCaseDefinition(my_test_case1),
             TestCaseDefinition(my_test_case2)])
        self.tr.run()
        assert self.tr.run_history[0].verdict == Verdict.PASSED
        assert self.tr.run_history[1].verdict == Verdict.SKIPPED

    def test_exit_fails_on_non_test_scope_aborts_test_run(self):

        class MyTestCase1(object):

            @requires(comp='MyExitFailComponent', scope='class')
            def my_test_case1(self, comp):
                comp()

        class MyTestCase2(object):

            @requires(comp='MyComponent', scope='class')
            def my_test_case2(self, comp):
                comp()

        self.run_queue.extend(
            [
                TestCaseDefinition(MyTestCase1().my_test_case1),
                TestCaseDefinition(MyTestCase2().my_test_case2)
            ])
        self.tr.run()
        assert self.tr.run_history[0].verdict == Verdict.PASSED
        assert self.tr.run_history[1].verdict == Verdict.SKIPPED


class TestFindParentExceptionOfType(unittest.TestCase):

    def test_find_parent_exception_of_type_returns_child_when_matching_type(self):
        tr = TestRunner(Mock(), Mock(), 'suite-name', parent_scope=Mock())

        class ExceptionType(Exception):
            pass

        exception1 = ExceptionType('')
        exception2 = Exception('')

        try:
            try:
                raise exception1
            except Exception as e:
                raise exception2 from e
        except Exception as e:
            self.assertEqual(tr._find_parent_exception_of_type(e, ExceptionType), exception1)

    def test_find_parent_exception_of_type_returns_none_when_not_matching_type(self):
        tr = TestRunner(Mock(), Mock(), 'suite-name', parent_scope=Mock())

        class ExceptionType(Exception):
            pass

        exception1 = Exception('')
        exception2 = Exception('')

        try:
            try:
                raise exception1
            except Exception as e:
                raise exception2 from e
        except Exception as e:
            self.assertIsNone(tr._find_parent_exception_of_type(e, ExceptionType))
