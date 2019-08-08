"""
Components for interacting with Jenkins.

When building a job a BuildInfo object will be returned.
This can be used to assert that the build was according to expectations.

.. autoclass:: k2_jenkins.jenkins.BuildInfo
    :members:
"""
import logging

import requests
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.builtin.waitfor.common import wait_for
from k2.cmd.run import RUN_COMMAND
from k2_jenkins import JENKINS_START_TIMEOUT

logger = logging.getLogger(get_logger_name('k2', 'jenkins'))
logger.addHandler(logging.NullHandler())


class JenkinsException(Exception):
    pass


class BuildInfo:
    """
    Handles information about a finished Jenkins build.

    Provides asserts to be able to verify that the build was according to expectations.
    """

    def __init__(self, jenkins_url, job, number, result, console_log, artifacts):
        self._jenkins_url = jenkins_url
        self._job = job
        self._number = number
        self._result = result
        self._console_log = console_log
        self._artifacts = artifacts

    @property
    def jenkins_url(self):
        """Return the URL to the Jenkins that executed the build."""
        return self._jenkins_url

    @property
    def job(self):
        """Return the name of the Jenkins job that was built."""
        return self._job

    @property
    def number(self):
        """Return the build number of the build."""
        return self._number

    @property
    def result(self):
        """Return the build result."""
        return self._result

    @property
    def console_log(self):
        """Return the console log from the build."""
        return self._console_log

    @property
    def artifacts(self):
        """Return the artifacts that were published by the build."""
        return self._artifacts

    def assert_result(self, expected_result):
        """Assert that the build result was equal to the expected result."""
        if expected_result != self.result:
            msg = f'Build {self._build_url()} has unexpected result: Got {self.result} but expected {expected_result}'
            raise AssertionError(msg)

    def assert_not_result(self, unexpected_result):
        """Assert that the build result was not equal to the unexpected result."""
        if unexpected_result == self.result:
            msg = f'Build {self._build_url()} has unexpected result: Got unexpected result {self.result}'
            raise AssertionError(msg)

    def assert_in_console_log(self, expected_content):
        """Assert that the build console_log contains the expected content."""
        if expected_content not in self.console_log:
            msg = f'Build {self._build_url()} does not have expected content in console log: ' \
                f'{expected_content} not found in:\n{self.console_log}'
            raise AssertionError(msg)

    def assert_not_in_console_log(self, unexpected_content):
        """Assert that the build console_log does not contain the unexpected content."""
        if unexpected_content in self.console_log:
            msg = f'Build {self._build_url()} has unexpected content in console log: ' \
                f'{unexpected_content} found in:\n{self.console_log}'
            raise AssertionError(msg)

    def assert_in_artifacts(self, expected_artifact):
        """Assert that the build artifacts contains the expected artifact."""
        if expected_artifact not in self.artifacts:
            msg = f'Build {self._build_url()} does not have expected artifact: ' \
                f'{expected_artifact} not found in: {self.artifacts}'
            raise AssertionError(msg)

    def assert_not_in_artifacts(self, unexpected_artifact):
        """Assert that the build artifacts does not contain the expected artifact."""
        if unexpected_artifact in self.artifacts:
            msg = f'Build {self._build_url()} has unexpected artifact: ' \
                f'{unexpected_artifact} found in: {self.artifacts}'
            raise AssertionError(msg)

    def _build_url(self):
        return f'{self.jenkins_url}/job/{self.job}/{self.number}/'


@component(name='Jenkins', scope='session', provided_by_extension='jenkins')
@requires(config='Config')
@requires(sut='Sut', can=['docker', 'jenkins'])
@requires(jenkins_node='Node', uses=['sut'], scope='session')
class JenkinsComponent(object):
    """Component that starts a Jenkins docker container that can be used to build jobs."""

    def __init__(self, config=None, sut=None, jenkins_node=None):
        self._jenkins_node = jenkins_node
        self._server = None
        self._start_timeout = config.get(JENKINS_START_TIMEOUT)
        self._jenkins_url = None

    def __enter__(self):
        self._jenkins_url = 'http://{ip}:{port}'.format(ip=self._jenkins_node.ip, port='8080')
        logger.info('Starting Jenkins: {url}'.format(url=self._jenkins_url))

        def jenkins_is_up():
            try:
                r = requests.get(self._jenkins_url)
                if r.status_code == 200:
                    return r
                else:
                    return False
            except requests.exceptions.ConnectionError:
                return False

        wait_for(jenkins_is_up, timeout=self._start_timeout, poll_interval=2)

        import jenkins
        self._server = jenkins.Jenkins(self._jenkins_url)
        if self._server.wait_for_normal_op(self._start_timeout):
            return self
        else:
            raise JenkinsException('Starting Jenkins timed out')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def ip(self):
        return self._jenkins_node.ip

    @property
    def port(self):
        return 8080

    def build_job(self, name, parameters=None, build_timeout=90, name_suffix=''):
        """Build the Jenkins job with the specified name and return a BuildInfo object."""
        queue_item_id = self._server.build_job(name, parameters)
        logger.debug(
            'Triggered build with queue item {queue_item}'.format(queue_item=queue_item_id))
        build_executable = wait_for(
            lambda: self._server.get_queue_item(queue_item_id).get('executable'),
            timeout=15,
            poll_interval=0.1)
        build_number = build_executable['number']
        logger.debug(
            "Build of '{job}/{build_number}' started".format(job=name, build_number=build_number))

        def get_build_info():
            build_info = self._server.get_build_info(name, build_number)
            if build_info.get('result'):
                return build_info
            else:
                return False

        build_info = wait_for(get_build_info, timeout=build_timeout)
        logger.debug(
            "Build of '{job}/{build_number}' completed'".format(
                job=name, build_number=build_number))

        def get_console_log():
            console_log = self._server.get_build_console_output(name, build_number)
            if 'Finished: {result}'.format(result=build_info['result']) in console_log:
                return console_log
            else:
                return False

        console_log = wait_for(get_console_log, timeout=30, poll_interval=1.0)

        # Get build info again to make sure everything including artifacts are included
        build_info = self._server.get_build_info(name, build_number)

        for line in console_log.split('\n'):
            logger.debug(
                '{name}{name_suffix}: {line}'.format(name=name, name_suffix=name_suffix, line=line))
        return BuildInfo(
            self._jenkins_url, name, build_number, build_info['result'], console_log,
            [artifact['relativePath'] for artifact in build_info['artifacts']])


@CommandExtension(
    name='jenkins',
    extends=[RUN_COMMAND, 'sut'],
    config_options=[ConfigOption(JENKINS_START_TIMEOUT, required=True)],
    endpoints_and_messages={})
class JenkinsAddon(AbstractExtension):
    """Provides a Jenkins component to interact with a Jenkins Docker node."""

    def __init__(self, config, instances):
        pass
