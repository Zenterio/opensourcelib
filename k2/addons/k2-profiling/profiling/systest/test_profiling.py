import os
from tempfile import TemporaryDirectory

from zaf.component.decorator import requires
from zaf.messages.message import EndpointId

SYSTEST = EndpointId('systest', 'systest endpoint')


@requires(zk2='Zk2')
def test_profiling_dir_default_value_uses_output_dir(zk2):
    with TemporaryDirectory() as tmpdir:
        result = zk2(
            ['profiling', 'configcommand', 'metrics'],
            '--output-dir {d} '
            'config profiling.dir'.format(d=tmpdir))
        path = os.path.join(tmpdir, 'profiling')
        line = 'profiling.dir: {path}  -  prio: 0, source: default'.format(path=path)
        assert line in result.stdout


@requires(zk2='Zk2')
def test_profile_report_json_path_config_default_value_uses_profiling_dir(zk2):
    with TemporaryDirectory() as tmpdir:
        result = zk2(
            ['profiling', 'configcommand', 'metrics'],
            '--profiling-dir {d} '
            'config profiling.report.json.path'.format(d=tmpdir))
        path = os.path.join(tmpdir, 'report.json')
        line = 'profiling.report.json.path: {path}  -  prio: 0, source: default'.format(path=path)
        assert line in result.stdout


@requires(zk2='Zk2')
def test_profile_csv_report_written(zk2):
    with TemporaryDirectory() as tmpdir:
        report_file = os.path.join(tmpdir, 'report.json')
        zk2(
            ['profiling', 'noop', 'metrics'],
            '--profiling-report-csv True '
            '--profiling-report-csv-path {rp} '
            'noop'.format(rp=report_file))

        assert os.path.exists(report_file)
        with open(report_file) as f:
            file_content = f.read()
            assert 'command' in file_content
            assert 'noop' in file_content
            assert 'startup_time' in file_content
            assert 'k2_execution_time' in file_content
            assert 'command_execution_time' in file_content


@requires(zk2='Zk2')
def test_profile_json_report_written(zk2):
    with TemporaryDirectory() as tmpdir:
        report_file = os.path.join(tmpdir, 'report.json')
        zk2(
            ['profiling', 'noop', 'metrics'],
            '--profiling-report-json True '
            '--profiling-report-json-path {rp} '
            'noop'.format(rp=report_file))

        assert os.path.exists(report_file)
        with open(report_file) as f:
            file_content = f.read()
            assert 'command' in file_content
            assert 'noop' in file_content
            assert 'startup_time' in file_content
            assert 'k2_execution_time' in file_content
            assert 'command_execution_time' in file_content


@requires(zk2='Zk2')
def test_profile_text_report_written(zk2):
    with TemporaryDirectory() as tmpdir:
        report_file = os.path.join(tmpdir, 'report.txt')
        zk2(
            ['profiling', 'noop', 'metrics'],
            '--profiling-report-text True '
            '--profiling-report-text-path {rp} '
            'noop'.format(rp=report_file))

        assert os.path.exists(report_file)
        with open(report_file) as f:
            file_content = f.read()
            assert 'command' in file_content
            assert 'noop' in file_content
            assert 'startup_time' in file_content
            assert 'k2_execution_time' in file_content
            assert 'command_execution_time' in file_content
