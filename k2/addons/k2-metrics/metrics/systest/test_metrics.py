import tempfile
from textwrap import dedent

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_generate_json_report(zk2):
    with tempfile.NamedTemporaryFile() as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-json-ids myreport --metrics-json-myreport@filename {file} '
                '--metrics-json-myreport@namespace system_memory '
                'run metrics.systest.data.suites.test_metrics:test_create_some_metrics'
            ).format(file=report_file.name))

        expected = dedent(
            """\
        {
            "used": [
                {
                    "timestamp": 1,
                    "data": 199905,
                    "tags": null
                },
                {
                    "timestamp": 2,
                    "data": 5,
                    "tags": null
                },
                {
                    "timestamp": 3,
                    "data": 199901,
                    "tags": null
                }
            ],
            "free": [
                {
                    "timestamp": 1,
                    "data": 100,
                    "tags": null
                },
                {
                    "timestamp": 2,
                    "data": 20000,
                    "tags": [
                        "zids.bin crashed!"
                    ]
                },
                {
                    "timestamp": 3,
                    "data": 99,
                    "tags": [
                        "everything is back to normal"
                    ]
                }
            ],
            "total": {
                "timestamp": 1,
                "data": 200005,
                "tags": null
            }
        }""")
        actual = ''.join(map(lambda line: line.decode('UTF-8'), report_file.readlines()))
        assert expected == actual


@requires(zk2='Zk2')
def test_generate_csv_report_from_series(zk2):
    with tempfile.NamedTemporaryFile() as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-csv-ids myreport --metrics-csv-myreport@filename {file} '
                '--metrics-csv-myreport@namespace system_memory '
                '--metrics-csv-myreport@metrics used --metrics-csv-myreport@metrics free '
                'run metrics.systest.data.suites.test_metrics:test_create_some_metrics'
            ).format(file=report_file.name))

        expected = 'system_memory.free,system_memory.used\r\n100,199905\r\n20000,5\r\n99,199901\r\n'
        actual = ''.join(map(lambda line: line.decode('UTF-8'), report_file.readlines()))
        assert expected == actual


@requires(zk2='Zk2')
def test_generate_csv_report_from_single_value(zk2):
    with tempfile.NamedTemporaryFile() as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-csv-ids myreport --metrics-csv-myreport@filename {file} '
                '--metrics-csv-myreport@namespace system_memory '
                '--metrics-csv-myreport@metrics total '
                'run metrics.systest.data.suites.test_metrics:test_create_some_metrics'
            ).format(file=report_file.name))

        expected = 'system_memory.total\r\n200005\r\n'
        actual = ''.join(map(lambda line: line.decode('UTF-8'), report_file.readlines()))
        assert expected == actual


@requires(zk2='Zk2')
def test_generate_graph_report(zk2):
    with tempfile.NamedTemporaryFile(suffix='.svg') as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-graph-ids myreport --metrics-graph-myreport@filename {file} '
                '--metrics-graph-myreport@namespace happy_primes '
                '--metrics-graph-myreport@title "Happy Primes" '
                '--metrics-graph-myreport@ylabel "Prime Values" '
                'run metrics.systest.data.suites.test_metrics:test_create_happy_primes'
            ).format(file=report_file.name),
            timeout=60)

        written_data = ''.join(map(lambda line: line.decode('UTF-8'), report_file.readlines()))
        assert 'Happy Primes' in written_data
        assert 'Prime Values' in written_data


@requires(zk2='Zk2')
def test_generate_graph_report_with_multiple_namespaces(zk2):
    with tempfile.NamedTemporaryFile(suffix='.svg') as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-graph-ids myreport --metrics-graph-myreport@filename {file} '
                '--metrics-graph-myreport@namespace decreasing_series '
                '--metrics-graph-myreport@namespace increasing_series '
                '--metrics-graph-myreport@title "Multiline Graph" '
                '--metrics-graph-myreport@ylabel "Values" '
                'run metrics.systest.data.suites.test_metrics:test_create_linear_sequences'
            ).format(file=report_file.name))

        written_data = ''.join(map(lambda line: line.decode('UTF-8'), report_file.readlines()))
        assert 'increasing_series' in written_data
        assert 'decreasing_series' in written_data


@requires(zk2='Zk2')
def test_generate_graph_report_with_single_measurement_in_series(zk2):
    with tempfile.NamedTemporaryFile(suffix='.svg') as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-graph-ids myreport --metrics-graph-myreport@filename {file} '
                '--metrics-graph-myreport@namespace single_entry '
                '--metrics-graph-myreport@title "Single Entry Graph" '
                '--metrics-graph-myreport@ylabel "Values" '
                'run metrics.systest.data.suites.test_metrics:test_create_metric_series_with_a_single_entry'
            ).format(file=report_file.name))


@requires(zk2='Zk2')
def test_generate_graph_report_with_empty_series(zk2):
    with tempfile.NamedTemporaryFile(suffix='.svg') as report_file:
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'metrics'], (
                '--metrics-graph-ids myreport --metrics-graph-myreport@filename {file} '
                '--metrics-graph-myreport@namespace some_random_series_that_does_not_exist '
                '--metrics-graph-myreport@title "Single Entry Graph" '
                '--metrics-graph-myreport@ylabel "Values" '
                'run metrics.systest.data.suites.test_metrics:test_create_metric_series_with_a_single_entry'
            ).format(file=report_file.name))
