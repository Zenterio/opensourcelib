import json
from datetime import timedelta
from unittest import TestCase

import httpretty

from k2.reports.z2.writer import generate_report, upload_report
from k2.results.results import ResultsCollection, TestCaseResult, TestRunResult, Verdict

_RESULT_COLLECTION = ResultsCollection(
    [
        TestCaseResult('test_name_a', 'qualified_name_a', timedelta(seconds=1)).set_finished(
            timedelta(seconds=2), Verdict.PASSED, None, None),
        TestCaseResult('test_name_b', 'qualified_name_b', timedelta(seconds=2)).set_finished(
            timedelta(seconds=4), Verdict.ERROR, Exception('hoppsan'), 'stacktrace'),
    ],
    TestRunResult('run_name', timedelta(seconds=7)).set_finished(
        timedelta(seconds=13), Verdict.ERROR, message='my message'))


class TestUploadReport(TestCase):

    @httpretty.activate
    def test_upload_report(self):
        url = 'http://1.2.3.4:80'
        data = {'hejhopp': True}

        httpretty.register_uri(httpretty.POST, url + '/api/reports')

        upload_report(json.dumps(data), url)

        result = json.loads(httpretty.last_request().body.decode('utf-8'))
        assert data == result


class TestGenerateReport(TestCase):

    def test_generate_report(self):
        report = generate_report(_RESULT_COLLECTION, 'job name', 14)
        data = json.loads(report)
        assert data['jobName'] == 'job name'
        assert data['buildNumber'] == 14
        assert data['verdict'] == 'ERROR'
        assert data['name'] == 'run_name'
        assert data['message'] == 'my message'
        assert data['duration'] == 6
        assert data['testCases'][0]['name'] == 'test_name_a'
        assert data['testCases'][0]['qualifiedName'] == 'qualified_name_a'
        assert data['testCases'][0]['verdict'] == 'PASSED'
        assert data['testCases'][0]['duration'] == 1
        assert data['testCases'][0]['message'] is None
        assert data['testCases'][0]['stacktrace'] is None
        assert data['testCases'][0]['params'] == []
        assert data['testCases'][1]['name'] == 'test_name_b'
        assert data['testCases'][1]['qualifiedName'] == 'qualified_name_b'
        assert data['testCases'][1]['verdict'] == 'ERROR'
        assert data['testCases'][1]['duration'] == 2
        assert data['testCases'][1]['message'] == 'hoppsan'
        assert data['testCases'][1]['stacktrace'] == 'stacktrace'
        assert data['testCases'][1]['params'] == []
