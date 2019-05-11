import csv
import os

from zaf.component.decorator import component, requires


@component
@requires(zk2='Zk2')
class BenchmarkProfileCommand(object):

    def __init__(self, zk2):
        self.zk2 = zk2

    def __call__(
            self,
            command_extension,
            command_name,
            command_args='',
            extra_extensions=[],
            report_suffix=None):
        report_suffix = report_suffix if report_suffix is not None else command_name
        extensions = ['metrics', 'profiling', command_extension]
        extensions.extend(extra_extensions)
        result = self.zk2(
            extensions,
            '--config-file-pattern systest/benchmark/profilingcommands.yaml '
            '--profiling-report-csv-path \\${{profiling.dir}}/profile_{report_suffix}.csv '
            '{command} {args}'.format(
                command=command_name, args=command_args, report_suffix=report_suffix),
            file_logging=False,
            plugin_path=os.path.join('systest', 'data', 'plugins'))

        return result


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_noop(benchmark):
    benchmark('noop', 'noop')
    with open('output/profiling/profile_noop.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        data = next(reader)
        assert float(data[1]) < 1, 'K2 startup time must be less that 1 seconds'


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_config(benchmark):
    benchmark('configcommand', 'config')


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_list(benchmark):
    benchmark('listcommand', 'list', 'systest/benchmark/__init__.py', ['testfinder'])


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_endpoints_noop(benchmark):
    benchmark('endpointscommand', 'endpoints', '--target-command noop', ['noop'], 'endpoints_noop')


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_extensions_noop_with_framework(benchmark):
    benchmark(
        'extensionscommand', 'extensions', '--include-framework true --target-command noop',
        ['noop'], 'extensions_noop_with_framework')


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_extensions_noop_no_framework(benchmark):
    benchmark(
        'extensionscommand', 'extensions', '--include-framework false --target-command noop',
        ['noop'], 'extensions_noop_no_framework')


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_endpoints_run(benchmark):
    benchmark(
        'endpointscommand', 'endpoints', '--target-command run', ['runcommand'], 'endpoints_run')


@requires(benchmark='BenchmarkProfileCommand')
def test_profile_extensions_run_no_framework(benchmark):
    benchmark(
        'extensionscommand', 'extensions', '--include-framework false --target-command run',
        ['runcommand'], 'extensions_run_no_framework')
