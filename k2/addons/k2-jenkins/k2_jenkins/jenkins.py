"""Components for interacting with Jenkins."""
import logging
from collections import namedtuple

import requests
from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.builtin.waitfor.common import wait_for
from k2.cmd.run import RUN_COMMAND

logger = logging.getLogger(get_logger_name('k2', 'jenkins'))
logger.addHandler(logging.NullHandler())


class JenkinsException(Exception):
    pass


BuildInfo = namedtuple('BuildInfo', ['number', 'result', 'console_log', 'artifacts'])


@component(name='Jenkins', scope='session')
@requires(sut='Sut', can=['docker', 'jenkins'])
@requires(jenkins_node='Node', uses=['sut'], scope='session')
class JenkinsComponent(object):

    def __init__(self, start_timeout=30, sut=None, jenkins_node=None):
        self._jenkins_node = jenkins_node
        self._server = None
        self._start_timeout = start_timeout

    def __enter__(self):
        jenkins_url = 'http://{ip}:{port}'.format(ip=self._jenkins_node.ip, port='8080')
        logger.info('Starting Jenkins: {url}'.format(url=jenkins_url))

        def jenkins_is_up():
            try:
                r = requests.get(jenkins_url)
                if r.status_code == 200:
                    return r
                else:
                    return False
            except requests.exceptions.ConnectionError:
                return False

        wait_for(jenkins_is_up, timeout=self._start_timeout, poll_interval=2)

        import jenkins
        self._server = jenkins.Jenkins(jenkins_url)
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

    def build_job(self, name, parameters=None, build_timeout=30, name_suffix=''):
        """Build the Jenkins job with the specified name."""
        queue_item_id = self._server.build_job(name, parameters)
        logger.debug(
            'Triggered build with queue item {queue_item}'.format(queue_item=queue_item_id))
        build_executable = wait_for(
            lambda: self._server.get_queue_item(queue_item_id).get('executable'),
            timeout=5,
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

        console_log = wait_for(get_console_log, timeout=10, poll_interval=1.0)

        # Get build info again to make sure everything including artifacts are included
        build_info = self._server.get_build_info(name, build_number)

        for line in console_log.split('\n'):
            logger.debug(
                '{name}{name_suffix}: {line}'.format(name=name, name_suffix=name_suffix, line=line))
        return BuildInfo(
            build_number, build_info['result'], console_log,
            [artifact['relativePath'] for artifact in build_info['artifacts']])


@CommandExtension(
    name='jenkins', extends=[RUN_COMMAND, 'sut'], config_options=[], endpoints_and_messages={})
class JenkinsAddon(AbstractExtension):
    """Provides a Jenkins component to interact with a Jenkins Docker node."""

    def __init__(self, config, instances):
        pass
