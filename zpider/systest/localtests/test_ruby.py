import logging
import os
from glob import glob

from zaf.component.decorator import component, requires

logger = logging.getLogger('testcase')


@component()
@requires(process_runner='ProcessRunner')
class RubyUnitTestRunner(object):

    def __init__(self, *ruby_test_patterns, process_runner=None):
        self._ruby_test_patterns = ruby_test_patterns
        self._process_runner = process_runner

    def __call__(self):
        command = (
            'docker run --rm --mount type=bind,source=$(pwd),target=$(pwd) --workdir $(pwd) '
            'docker.zenterio.lan/zenterio/zpider:latest '
            "/usr/bin/ruby -Ilib -e 'ARGV.each {{ |f| load f }}' {ruby_files}"
        ).format(ruby_files=' '.join(self._glob_test_files()))
        logger.info('command: {command}'.format(command=command))
        result = self._process_runner(command, wait=False)

        try:
            result.wait(timeout=10)
            logger.info(result.stdout)
            assert result.exit_code == 0
        except Exception:
            raise AssertionError('Ruby unit tests failed:\n{msg}'.format(msg=result.stdout))

    def _glob_test_files(self):
        for pattern in self._ruby_test_patterns:
            for file in glob(pattern, recursive=True):
                yield os.path.abspath(file)


@requires(runner=RubyUnitTestRunner, args=['zpider/data/plugins/**/test*.rb'])
def test_run_ruby_unit_tests(runner):
    runner()
