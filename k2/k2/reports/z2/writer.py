import json
import logging
import os

import requests
from zaf.extensions.extension import get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'z2report'))
logger.addHandler(logging.NullHandler())


def write_report(report, report_file):
    """
    Write a Z2 report to disk.

    :param report: The Z2 report.
    :param report_file: Where to write the report.
    """
    logger.info('Writing Z2 report to file {report_file}'.format(report_file=report_file))
    try:
        _write_report(report, report_file)
        logger.info('Wrote Z2 report to file {report_file}'.format(report_file=report_file))
    except (IOError, OSError) as e:
        msg = 'Could not write Z2 report to file {report_file}: {reason}'.format(
            report_file=report_file, reason=str(e))
        logger.debug(msg, exc_info=True)
        logger.error(msg)
        raise


def _write_report(report, report_file):
    dir = os.path.dirname(report_file)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    with open(report_file, 'w') as f:
        f.write(report)


def upload_report(report, z2_server):
    """
    Upload a Z2 report to a remote Z2 server.

    :param report: The Z2 report.
    :param z2_server: URI for the remote server.
    """
    logger.info('Uploading Z2 report to remote server {z2_server}'.format(z2_server=z2_server))
    try:
        _upload_report(report, z2_server)
        logger.info('Uploaded Z2 report to remote server {z2_server}'.format(z2_server=z2_server))
    except Exception:
        msg = 'Could not upload Z2 report to remote server {z2_server}'.format(z2_server=z2_server)
        logger.debug(msg, exc_info=True)
        logger.error(msg)
        raise


def _upload_report(report, z2_server):
    url = '{z2_server}/api/reports'.format(z2_server=z2_server)
    requests.post(url, json=json.loads(report), verify=False)


def generate_report(test_result, job_name=None, build_number=None):
    """
    Generate a Z2 report.

    :param test_result: list of k2.results.results.TestCaseResult
    :param job_name: Name of the job that initiated this K2 run.
    :param build_number: Build number of the job that initiated this K2 run.
    :return: A Z2 report.
    """
    return json.dumps(
        {
            'jobName':
            job_name,
            'buildNumber':
            build_number,
            'verdict':
            test_result.run_result.verdict.name,
            'name':
            test_result.run_result.name,
            'message':
            test_result.run_result.message,
            'duration':
            None
            if test_result.run_result.duration is None else test_result.run_result.duration.seconds,
            'testCases': [
                {
                    'name':
                    test_case.name,
                    'qualifiedName':
                    test_case.qualified_name,
                    'verdict':
                    test_case.verdict.name,
                    'duration':
                    None if test_case.duration is None else test_case.duration.seconds,
                    'message':
                    test_case.exception
                    if test_case.exception is None else str(test_case.exception),
                    'stacktrace':
                    test_case.stacktrace,
                    'params': [str(param) for param in test_case.params],
                } for test_case in test_result.test_results
            ]
        })
