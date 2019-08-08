import logging
import xml.etree.ElementTree as etree
from xml.dom.minidom import parseString

from zaf.extensions.extension import get_logger_name

from k2.results.results import TestCaseResult
from k2.runner.testcase import Verdict
from k2.utils.string import strip_ansi_escapes

VERDICT_TO_TESTNG_STATUS_MAPPING = {
    Verdict.PASSED: 'PASS',
    Verdict.FAILED: 'FAIL',
    Verdict.ERROR: 'FAIL',
    Verdict.PENDING: 'FAIL',
    Verdict.SKIPPED: 'SKIP',
    Verdict.IGNORED: 'SKIP',
}

logger = logging.getLogger(get_logger_name('k2', 'testngreport'))
logger.addHandler(logging.NullHandler())


def write_testng_report(test_result, report_file):
    """
    Generate a TestNG XML Report from the test results.

    :param test_result: k2.results.results.ResultsCollection
    :param report_file: where to write the report
    """
    with open(report_file, 'wb') as f:
        f.write(generate_testng_report(test_result))


def generate_testng_report(test_result):
    """
    Generate a TestNG XML Report from the test results as utf-8 encoded bytes.

    :param test_result: k2.results.results.ResultsCollection
    :return: TestNG XML as utf-8 encoded bytes
    """
    suite_name = test_result.run_result.name
    suite_start = test_result.run_result.start_time
    suite_end = test_result.run_result.end_time
    suite_duration = duration_in_ms(test_result.run_result.duration)

    # Mapping the run result to a test case result to be able to include it in the report
    test_results = list(test_result.test_results)
    if test_result.run_result.verdict != Verdict.PASSED:
        suite_result = TestCaseResult(suite_name, suite_name, suite_start)
        suite_result.set_finished(
            suite_end, test_result.run_result.verdict, test_result.run_result.message, '')
        test_results.append(suite_result)

    test_name = suite_name
    test_start = suite_start
    test_end = suite_end
    test_duration = suite_duration

    testng_results = etree.Element('testng-results')
    testng_results.set('version', '1.0')
    etree.SubElement(testng_results, 'reporter-output')

    suite = etree.SubElement(
        testng_results, 'suite', {
            'name': escape_name(suite_name),
            'duration-ms': suite_duration,
            'started-at': format_time(suite_start),
            'finished-at': format_time(suite_end),
        })
    etree.SubElement(suite, 'groups')
    test = etree.SubElement(
        suite, 'test', {
            'name': escape_name(test_name),
            'duration-ms': test_duration,
            'started-at': format_time(test_start),
            'finished-at': format_time(test_end),
        })

    current_class_name = None

    for test_case in test_results:
        class_name = '.'.join(test_case.qualified_name.split('.')[0:-1])
        test_name = test_case.qualified_name.split('.')[-1]

        if class_name == '':
            class_name = test_case.name

        if class_name != current_class_name:
            current_class_name = class_name
            cls = etree.SubElement(test, 'class', {'name': escape_name(class_name)})

        test_method_attributes = {
            'status': VERDICT_TO_TESTNG_STATUS_MAPPING[test_case.verdict],
            'signature': escape_name(test_case.qualified_name),
            'name': escape_name(test_name),
            'duration-ms': duration_in_ms(test_case.duration),
            'started-at': format_time(test_case.start_time),
            'finished-at': format_time(test_case.end_time),
        }
        owner = test_case.owner if test_case.owner is not None else test_result.run_result.owner
        if owner is not None:
            test_method_attributes['description'] = format_owner(owner)

        test_method = etree.SubElement(cls, 'test-method', test_method_attributes)

        if test_case.params:
            params = etree.SubElement(test_method, 'params')
            for index, param_value in enumerate(test_case.params):
                param = etree.SubElement(params, 'param', {'index': str(index)})
                value = etree.SubElement(param, 'value')
                value.append(CDATA(str(param_value)))

        if test_case.exception:
            exception = etree.SubElement(
                test_method, 'exception', {
                    'class': type(test_case.exception).__name__
                })
            message = etree.SubElement(exception, 'message')

            # Extra . to workaround the Jenkins plugin that destroys the stacktrace
            message_string = '{message}.'.format(message=str(test_case.exception))
            message.append(CDATA(message_string))
            full_stacktrace = etree.SubElement(exception, 'full-stacktrace')
            full_stacktrace.append(
                CDATA(
                    '{cls}: {message}\n{stacktrace}'.format(
                        cls=type(test_case.exception).__name__,
                        message=message_string,
                        stacktrace=test_case.stacktrace)))
            etree.SubElement(test_method, 'reporter-output')

    generated_xml = etree.tostring(testng_results, 'unicode')
    logger.debug('Generated XML before prettifying:\n{xml}'.format(xml=generated_xml))

    return parseString(strip_ansi_escapes(generated_xml)).toprettyxml(
        indent='    ', encoding='utf-8')


def format_time(time):
    try:
        return time.strftime('%G-%m-%dT%H:%M:%SZ')
    except AttributeError:
        return ''


def duration_in_ms(duration):
    try:
        return str(int(duration.seconds * 1000 + duration.microseconds / 1000))
    except AttributeError:
        return '0'


def format_owner(owner):
    return 'Test case owner: {owner} (Please contact the owner if you need assistance with trouble-shooting.)'.format(
        owner=owner)


def escape_name(name):
    # The TestNG Jenkins plugin handles : characters by replacing them with _.
    # This has the side effect that links generated by the plugin are broken.
    # Fix by removing the offending character.
    return name.replace(':', '')


# Below here are ugly hacks to get ElementTree to use CDATA


def CDATA(text=None):
    element = etree.Element('![CDATA[')
    element.text = text
    return element


if not hasattr(etree, '_original_serialize_xml'):
    etree._original_serialize_xml = etree._serialize_xml

    def _serialize_xml(write, elem, qnames, namespaces, **kwargs):
        if elem.tag == '![CDATA[':
            write('<{tag}{text}]]>\n'.format(tag=elem.tag, text=elem.text))
            return
        return etree._original_serialize_xml(write, elem, qnames, namespaces, **kwargs)

    etree._serialize_xml = etree._serialize['xml'] = _serialize_xml
