from zaf.component.decorator import component


class RunnerComponentException(Exception):
    pass


@component(name='TestContext', scope='test')
class TestContext:
    """Information about the running test case."""

    def __init__(self, test_case_definition=None):
        if test_case_definition is None:
            raise RunnerComponentException(
                'The TestContext component can only be pre-instantiated by the test runner and can only be used '
                'on the test scope.')

        self._test_case_definition = test_case_definition

    @property
    def name(self):
        return self._test_case_definition.name

    @property
    def filename_with_params(self):
        return self._test_case_definition.filename_with_params

    @property
    def params(self):
        return self._test_case_definition.params

    @property
    def description(self):
        return self._test_case_definition.description
