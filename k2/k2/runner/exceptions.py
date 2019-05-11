class ScopeChangeException(Exception):

    def __init__(self, current_scope, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_scope = current_scope


class TestCaseAborted(BaseException):
    pass


class SkipException(Exception):
    pass


class DisabledException(Exception):
    pass


class ExecutionPausedTooLong(Exception):

    def __init__(self, timeout):
        super().__init__('Execution paused longer than timeout {to}s'.format(to=str(timeout)))
        self.timeout = timeout
