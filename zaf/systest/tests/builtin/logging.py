import os
from tempfile import TemporaryDirectory

from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_log_level_debug(zafapp):
    result = zafapp(
        ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
        '--log-level debug '
        'noop')

    assert 'logsatallloglevels - DEBUG' in result.stderr
    assert 'logsatallloglevels - INFO' in result.stderr
    assert 'logsatallloglevels - WARNING' in result.stderr
    assert 'logsatallloglevels - ERROR' in result.stderr
    assert 'logsatallloglevels - CRITICAL' in result.stderr


@requires(zafapp='ZafApp')
def test_log_level_info(zafapp):
    result = zafapp(
        ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
        '--log-level info '
        'noop')

    assert 'logsatallloglevels - DEBUG' not in result.stderr
    assert 'logsatallloglevels - INFO' in result.stderr
    assert 'logsatallloglevels - WARNING' in result.stderr
    assert 'logsatallloglevels - ERROR' in result.stderr
    assert 'logsatallloglevels - CRITICAL' in result.stderr


@requires(zafapp='ZafApp')
def test_log_level_warning(zafapp):
    result = zafapp(
        ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
        '--log-level warning '
        'noop')

    assert 'logsatallloglevels - DEBUG' not in result.stderr
    assert 'logsatallloglevels - INFO' not in result.stderr
    assert 'logsatallloglevels - WARNING' in result.stderr
    assert 'logsatallloglevels - ERROR' in result.stderr
    assert 'logsatallloglevels - CRITICAL' in result.stderr


@requires(zafapp='ZafApp')
def test_log_level_error(zafapp):
    result = zafapp(
        ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
        '--log-level error '
        'noop')

    assert 'logsatallloglevels - DEBUG' not in result.stderr
    assert 'logsatallloglevels - INFO' not in result.stderr
    assert 'logsatallloglevels - WARNING' not in result.stderr
    assert 'logsatallloglevels - ERROR' in result.stderr
    assert 'logsatallloglevels - CRITICAL' in result.stderr


@requires(zafapp='ZafApp')
def test_log_level_off(zafapp):
    result = zafapp(
        ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
        '--log-level off '
        'noop')

    assert 'logsatallloglevels - DEBUG' not in result.stderr
    assert 'logsatallloglevels - INFO' not in result.stderr
    assert 'logsatallloglevels - WARNING' not in result.stderr
    assert 'logsatallloglevels - ERROR' not in result.stderr
    assert 'logsatallloglevels - CRITICAL' not in result.stderr


@requires(zafapp='ZafApp')
def test_log_file_with_different_log_level(zafapp):
    with TemporaryDirectory() as tmpdir:
        logfile = os.path.join(tmpdir, 'logfile.log')
        result = zafapp(
            ['logsatallloglevels', 'noop'],
            '--config-file-pattern systest/data/simple_config.yaml '
            '--log-level info '
            '--log-file-ids myfile '
            '--log-file-myfile@log-level debug '
            '--log-file-myfile@path {logfile} '
            '--log-file-myfile@loggers logsatallloglevels '
            'noop'.format(logfile=logfile))

        assert 'logsatallloglevels - DEBUG' not in result.stderr
        assert 'logsatallloglevels - INFO' in result.stderr
        assert os.path.isfile(logfile)
        with open(logfile) as f:
            log_contents = f.read()
            assert 'logsatallloglevels - INFO' in log_contents
            assert 'logsatallloglevels - DEBUG' in log_contents


@requires(zafapp='ZafApp')
def test_extension_log_level_does_not_override_file_log_level(zafapp):
    with TemporaryDirectory() as tmpdir:
        logfile = os.path.join(tmpdir, 'logfile.log')
        result = zafapp(
            ['logsatallloglevels', 'noop'],
            '--config-file-pattern systest/data/simple_config.yaml '
            '--log-level info '
            '--log-file-ids myfile '
            '--log-file-myfile@log-level debug '
            '--log-file-myfile@path {logfile} '
            '--log-file-myfile@loggers logsatallloglevels '
            '--ext-logsatallloglevels@log-level info '
            'noop'.format(logfile=logfile))

        assert 'logsatallloglevels - DEBUG' not in result.stderr
        assert 'logsatallloglevels - INFO' in result.stderr
        assert os.path.isfile(logfile)
        with open(logfile) as f:
            log_contents = f.read()
            assert 'logsatallloglevels - INFO' in log_contents
            assert 'logsatallloglevels - DEBUG' in log_contents


@requires(zafapp='ZafApp')
def test_rotating_logfile_create_log_for_each_iteration(zafapp):
    with TemporaryDirectory() as tmpdir:
        zafapp(
            ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
            '--log-level info '
            '--log-file-ids myfile '
            '--log-file-myfile@log-level debug '
            '--log-file-myfile@path TMP_DIR/{scope}.log '
            '--log-file-myfile@loggers logsatallloglevels '
            '--log-file-myfile@rotate-scope iteration '
            'noop --iterations 10'.replace('TMP_DIR', tmpdir))

        files = os.listdir(tmpdir)
        assert len(files) == 10


@requires(zafapp='ZafApp')
def test_rotating_logfile_with_delete_on_success_leaves_only_logs_for_failed_iteration(zafapp):
    with TemporaryDirectory() as tmpdir:
        zafapp(
            ['logsatallloglevels', 'noop'], '--config-file-pattern systest/data/simple_config.yaml '
            '--log-level info '
            '--log-file-ids myfile '
            '--log-file-myfile@log-level debug '
            '--log-file-myfile@path TMP_DIR/{scope}.log '
            '--log-file-myfile@loggers logsatallloglevels '
            '--log-file-myfile@rotate-scope iteration '
            '--log-file-myfile@rotate-deleteforresults OK '
            'noop --iterations 10 --errors 5'.replace('TMP_DIR', tmpdir))

        files = os.listdir(tmpdir)
        assert len(files) == 5
