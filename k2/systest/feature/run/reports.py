import difflib
import os
from tempfile import TemporaryDirectory

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_xml_report(zk2):
    with TemporaryDirectory() as tmpdir:
        xml_report_file = os.path.join(tmpdir, 'testng-results.xml')
        zk2(
            [
                'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'testngreport'
            ],
            'run systest.data.suites.test_verdicts '
            '--reports-testng true '
            '--reports-testng-file {xml_report_file}'.format(xml_report_file=xml_report_file))

        assert os.path.exists(xml_report_file)
        with open(xml_report_file) as f:
            contents = f.read()

            assert contents.count('status="FAIL"') == 3
            assert contents.count('status="SKIP"') == 2
            assert contents.count('status="PASS"') == 1


@requires(zk2='Zk2')
def test_text_report(zk2):
    with TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, 'test-file')
        result = zk2(
            [
                'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport'
            ],
            'run systest.data.suites.test_verdicts '
            '--reports-text true '
            '--reports-text-output {output} '
            '--reports-text-output -'.format(output=output))

        assert os.path.exists(output)
        with open(output) as f:
            contents = f.read()

            assert 'Failed:  1' in contents
            assert 'Error:   1' in contents
            assert 'Skipped: 1' in contents
            assert 'Ignored: 1' in contents
            assert 'Passed:  1' in contents
            assert 'Total:   5' in contents

            assert contents.strip() in result.stdout, '\n'.join(
                difflib.unified_diff(
                    contents.strip().splitlines(),
                    result.stdout.strip().splitlines()))


@requires(zk2='Zk2')
def test_z2_report(zk2):
    with TemporaryDirectory() as tmpdir:
        z2_report_file = os.path.join(tmpdir, 'z2-results.json')
        zk2(
            ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'z2report'],
            'run systest.data.suites.test_verdicts '
            '--reports-z2 true '
            '--reports-z2-file {z2_report_file}'.format(z2_report_file=z2_report_file))

        assert os.path.exists(z2_report_file)
        with open(z2_report_file) as f:
            contents = f.read()

            assert contents.count('"verdict": "FAILED"') == 1
            assert contents.count('"verdict": "ERROR"') == 2  # One test case + run verdict
            assert contents.count('"verdict": "SKIPPED"') == 1
            assert contents.count('"verdict": "IGNORED"') == 1
            assert contents.count('"verdict": "PASSED"') == 1
