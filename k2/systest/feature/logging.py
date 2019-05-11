import os
from tempfile import TemporaryDirectory

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_rotating_logfile_create_log_for_each_testcase(zk2):
    with TemporaryDirectory() as tmpdir:
        zk2(
            [
                'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'logger', 'filelogger',
                'output'
            ], '--log-level info '
            '--log-file-ids myfile '
            '--log-file-myfile@log-level debug '
            '--log-file-myfile@path TMP_DIR/{scope}.log '
            '--log-file-myfile@loggers testrunner '
            '--log-file-myfile@rotate-scope testcase '
            'run systest.data.suites.test_verdicts'.replace('TMP_DIR', tmpdir))

        files = os.listdir(tmpdir)
        assert len(files) == 4  # Might need to change when test case skip and ignored are handled


@requires(zk2='Zk2')
def test_rotating_logfile_with_delete_on_success_leaves_only_logs_for_failed_tests(zk2):
    with TemporaryDirectory() as tmpdir:
        zk2(
            [
                'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'logger', 'filelogger',
                'output'
            ],
            '--log-level info '
            '--log-file-ids myfile '
            '--log-file-myfile@log-level debug '
            '--log-file-myfile@path TMP_DIR/{scope}.log '
            '--log-file-myfile@loggers testrunner '
            '--log-file-myfile@rotate-scope testcase '
            '--log-file-myfile@rotate-deleteforresults PASSED '
            'run systest.data.suites.test_verdicts'.replace('TMP_DIR', tmpdir),
            timeout=10)

        files = os.listdir(tmpdir)
        assert len(files) == 3  # Might need to change when test case skip and ignored are handled
