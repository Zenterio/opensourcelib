import logging
import socketserver
import tempfile
from textwrap import dedent, indent

from zaf.component.decorator import requires

from mockserver.mockserver import TcpMockServer

logger = logging.getLogger('k2.systest')


class ExitCodeRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        status = '0'
        try:
            while True:
                self.request.send('/ # '.encode('ascii'))
                command = self.request.recv(1024)
                cmd, args = command.decode('ascii').split(maxsplit=1)
                if cmd == 'echo':
                    self.request.send(args.replace('$?', status).encode('ascii'))
                    status = '0'
                elif cmd == 'cat':
                    for line in _gtest_xml_report_output:
                        self.request.send(line.encode('ascii'))
                    status = '0'
                elif cmd == 'rm':
                    status = '0'
                elif cmd.startswith('binary'):
                    if '--gtest_filter=filter' not in args:
                        status = '1'
                    elif '--gtest_output=xml:' in args:
                        status = '0'
                    else:
                        for line in _gtest_text_report_output:
                            self.request.send(line.encode('ascii'))
                        status = '0'
                else:
                    self.request.send('Unknown command'.encode('ascii'))
                    status = '1'
        except Exception:
            pass


@requires(zk2='Zk2')
def test_gtest_runner(zk2):

    with TcpMockServer(ExitCodeRequestHandler) as server:
        result = zk2(
            [
                'sut', 'runcommand', 'multirunner', 'gtestbinaryrunner', 'testresults', 'telnet',
                'textreport'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--multi-runner-enabled true '
            '--suts-box@telnet-port {telnet_port} '
            '--gtest-ids binary '
            '--gtest-binary@binary binary '
            '--gtest-binary@filter filter '.format(telnet_port=server.port))
        assert 'Passed:  2' in result.stdout
        assert 'Failed:  1' in result.stdout
        assert 'Total:   3' in result.stdout


@requires(zk2='Zk2')
def test_gtest_runner_with_two_binaries(zk2):

    with TcpMockServer(ExitCodeRequestHandler) as server:
        result = zk2(
            [
                'sut', 'runcommand', 'multirunner', 'gtestbinaryrunner', 'testresults', 'telnet',
                'textreport'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--multi-runner-enabled true '
            '--suts-box@telnet-port {telnet_port} '
            '--gtest-ids binary1 --gtest-ids binary2 '
            '--gtest-binary1@binary binary1 '
            '--gtest-binary2@binary binary2 '
            '--gtest-binary1@filter filter '
            '--gtest-binary2@filter filter '.format(telnet_port=server.port))
        assert 'Passed:  4' in result.stdout
        assert 'Failed:  2' in result.stdout
        assert 'Total:   6' in result.stdout

        assert indent(
            dedent(
                """\
            this
            is
            an
            error
            message
            """), '  ') in result.stdout, result.stdout


@requires(zk2='Zk2')
def test_gtest_running_with_xml_reporter(zk2):

    with TcpMockServer(ExitCodeRequestHandler) as server, tempfile.NamedTemporaryFile(
            mode='w') as report_xml_file:
        zk2(
            [
                'sut', 'runcommand', 'multirunner', 'gtestbinaryrunner', 'testresults', 'telnet',
                'textreport'
            ], '--log-debug k2.extension.telnet '
            'run --suts-ids box --suts-box@ip localhost '
            '--multi-runner-enabled true '
            '--suts-box@telnet-port {telnet_port} '
            '--gtest-ids binary '
            '--gtest-binary@binary binary '
            '--gtest-binary@filter filter '
            '--gtest-binary@report-xml-path {report_xml_path}'.format(
                telnet_port=server.port,
                report_xml_path=report_xml_file.name,
            ))

        with open(report_xml_file.name, 'r') as f:
            assert _gtest_xml_report_output.strip() == f.read()


_gtest_text_report_output = """\
[ RUN      ] test1
[       OK ] test1
[ RUN      ] test2
this
is
an
error
message
[  FAILED  ] test2
[ RUN      ] test3
[       OK ] test3
"""

_gtest_xml_report_output = """\
<?xml version="1.0" encoding="UTF-8"?>
<testsuites tests="37" failures="0" disabled="0" errors="0" time="0.076" name="AllTests">
  <testsuite name="WebCoreHTMLParserIdioms" tests="2" failures="0" disabled="0" errors="0" time="0.003">
    <testcase name="parseHTMLInteger" status="run" time="0.003" classname="WebCoreHTMLParserIdioms" />
    <testcase name="parseHTMLNonNegativeInteger" status="run" time="0" classname="WebCoreHTMLParserIdioms" />
  </testsuite>
  <testsuite name="WebCoreLayoutUnit" tests="8" failures="0" disabled="0" errors="0" time="0.019">
    <testcase name="LayoutUnitInt" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitFloat" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitRounding" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitMultiplication" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitDivision" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitCeil" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitFloor" status="run" time="0" classname="WebCoreLayoutUnit" />
    <testcase name="LayoutUnitPixelSnapping" status="run" time="0.019" classname="WebCoreLayoutUnit" />
  </testsuite>
</testsuite>
"""
