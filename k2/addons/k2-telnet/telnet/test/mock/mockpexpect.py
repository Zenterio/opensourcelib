import re


class MockPexpect:

    class ExceptionPexpect(Exception):
        pass

    class EOF(Exception):
        pass

    class TIMEOUT(Exception):
        pass

    class MockProcess:

        def __init__(self):
            self.expect_results = []
            self.seen_lines = []
            self.exitstatus = 0
            self.timeout = None
            self.before = ''
            self.match = None

        def expect(self, pattern_list, timeout=None):
            if not isinstance(pattern_list, list):
                pattern_list = [pattern_list]

            def index_or_raise(exc):
                for index, pattern in enumerate(pattern_list):
                    if pattern == exc:
                        return index
                raise exc()

            self.timeout = timeout
            if self.expect_results:
                result = self.expect_results.pop(0)
                for index, pattern in enumerate(pattern_list):
                    if pattern in [MockPexpect.EOF, MockPexpect.TIMEOUT]:
                        # Not actually patterns. These are used as flags.
                        continue
                    self.match = re.match(pattern, result)
                    if self.match:
                        return index
                return index_or_raise(MockPexpect.TIMEOUT)
            else:
                return index_or_raise(MockPexpect.EOF)

        def sendline(self, line):
            self.seen_lines.append(line)

        def isalive(self):
            return True

        def close(self, force=False):
            pass

    def __init__(self):
        self.process = MockPexpect.MockProcess()

    def spawnu(self, *args, **kwargs):
        return self.process
