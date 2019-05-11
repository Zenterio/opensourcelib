import datetime
import logging
import os
import time
from textwrap import dedent

from zaf.component.decorator import component, requires
from zaf.extensions.extension import get_logger_name

from virt.docker import DOCKER_IMAGE_PULL, DOCKER_IMAGE_REGISTRY, DockerContainerExec, \
    DockerContainerNode

logger = logging.getLogger(get_logger_name('k2', 'ansible', 'docker'))


class AnsiblePlaybookAlreadyFailedException(Exception):
    pass


@component(name='AnsibleDeleteLog', scope='session')
@requires(path='AnsibleLogPath')
def delete_ansible_log(path):
    try:
        if path:
            logger.debug('Removing log at {path}'.format(path=path))
            os.remove(path)
    except OSError:
        pass


@component(name='AnsibleLogPath')
@requires(sut='Sut', can=['ansibletestnode'])
@requires(ansible_config='AnsibleConfig')
def ansible_log_path(sut, ansible_config):
    if ansible_config.log_dir:
        logger.debug('Creating log directory {dir}'.format(dir=ansible_config.log_dir))
        os.makedirs(ansible_config.log_dir, exist_ok=True)
        return os.path.join(
            ansible_config.log_dir, 'ansible-playbook-{entity}.log'.format(entity=sut.entity))
    else:
        return None


@component(name='AnsibleLog')
@requires(sut='Sut', can=['ansibletestnode'])
@requires(path='AnsibleLogPath', uses=['sut'])
@requires(delete='AnsibleDeleteLog', uses=['path'], scope='session')
def ansible_log(sut, path, delete):
    return path


@component(name='AnsibleRunner', can=['ansible:docker'])
@requires(ansible_config='AnsibleConfig', can=['ansiblebackend:docker'])
@requires(config='Config')
@requires(logpath='AnsibleLog')
class DockerAnsibleRunner(object):

    def __init__(self, ansible_config, config, logpath):
        import docker
        self._client = docker.from_env()
        self._ansible_config = ansible_config
        self._logpath = logpath
        self._config = config
        self._pull = config.get(DOCKER_IMAGE_PULL, False)
        self._registry = config.get(DOCKER_IMAGE_REGISTRY, '')
        self._image = '{reg}edgegravity/ansible.run'.format(reg=self._registry)
        self._tag = 'latest'
        self._update()

    def _update(self):
        try:
            if self._pull:
                self._client.images.pull(self._image, self._tag)
        except Exception:
            pass

    def wait_for_running(self, hostgroup, timeout=20):
        import docker
        logger.info('Wait for {hg} to be running'.format(hg=hostgroup))

        cmd = 'ansible {hg} -m ping'.format(hg=hostgroup)

        start_time = datetime.datetime.now()
        while True:
            try:
                self._run_command(cmd, hostgroup)
                break
            except docker.errors.ContainerError:
                if (datetime.datetime.now() - start_time).seconds > timeout:
                    logging.error(
                        'ansible ping for {hg} failed. See the ansible log for more details.'.
                        format(hg=hostgroup))
                    raise
                else:
                    time.sleep(1)

    def playbook(self, hostgroup, args=None):
        import docker
        logger.info('Run playbook for {hg}'.format(hg=hostgroup))

        if args is None:
            args = []
        extra_vars_file = ''
        if self._ansible_config.extra_vars_file:
            extra_vars_file = '--extra-vars "@{vars}"'.format(
                vars=self._ansible_config.extra_vars_file)

        cmd = 'ansible-playbook {pb} -l {hg} {extra_vars_file} {args}'.format(
            pb=self._ansible_config.playbook,
            hg=hostgroup,
            extra_vars_file=extra_vars_file,
            args=' '.join(args))
        try:
            self._run_command(cmd, hostgroup)
        except docker.errors.ContainerError:
            logging.error(
                'ansible-playbook for {hg} failed. See the ansible playbook log for more details.'.
                format(hg=hostgroup))
            raise

    def _run_command(self, cmd, hostgroup):
        import docker
        kwargs = {}
        kwargs['environment'] = self._ansible_config.env
        kwargs['environment']['ANSIBLE_LOG_PATH'] = self._logpath
        kwargs['remove'] = True
        kwargs['network'] = 'ansiblenetwork'
        cwd_mount = docker.types.Mount(
            target='/mnt', source=os.getcwd(), type='bind', read_only=False)
        kwargs['mounts'] = [cwd_mount]

        message = dedent(
            """\
            Docker run
            image: {image}
            command: {cmd}
            kwargs: {kwargs}
            """).format(
                image=self._image, cmd=cmd, kwargs=kwargs)
        logger.debug(message)

        self._client.containers.run(self._image, cmd, **kwargs)


@component(name='AnsibleNode', can=['ansible', 'applied-playbook'], scope='session')
@requires(sut='Sut', can=['ansibletestnode'])
@requires(
    node=DockerContainerNode,
    args=[{
        'privileged': True,
        'security_opt': ['apparmor=unconfined']
    }],
    uses=['sut'],
    scope='session')
@requires(exec=DockerContainerExec, uses=['sut', 'node'], scope='session')
@requires(ansible_runner='AnsibleRunner')
class DockerAnsibleAppliedPlayBookNode(object):

    already_failed = set()

    def __init__(self, ansible_runner, exec, node, sut):
        self._exec = exec
        self._node = node
        self._ansible_runner = ansible_runner
        self._sut = sut
        if sut.entity in self.already_failed:
            msg = 'The ansible playbook for {sut} has already failed'.format(sut=sut.entity)
            raise AnsiblePlaybookAlreadyFailedException(msg)

    def __enter__(self):
        hostname = self._node.hostname
        stdout, stderr, exit_code = self._exec.send_line('uname -a')
        logger.info('Node: ' + stdout + stderr)
        try:
            self._ansible_runner.wait_for_running(hostname)
            self._ansible_runner.playbook(hostname)
            return self
        except Exception:
            self.already_failed.add(self._sut.entity)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def exec(self):
        return self._exec


@component(name='Exec', can=['ansible'], priority=-1)
@requires(node=DockerAnsibleAppliedPlayBookNode, scope='session')
class DockerAnsibleExec(object):

    def __init__(self, node):
        self._node = node

    def send_line(
            self, line, timeout=None, expected_exit_code=None, extended_process_information=True):
        logger.debug(
            'send_line: line={line}, timeout={to}, expected_exit_code={ec}, extended_process_information={epi}'.
            format(line=line, to=timeout, ec=expected_exit_code, epi=extended_process_information))
        return self._node.exec.send_line(
            line, timeout, expected_exit_code, extended_process_information)


class DockerBackend(object):

    def __init__(self, ansible_config):
        self.ansible_config = ansible_config

    def register_components(self, component_manager):
        pass
        # sut = component_manager.get_unique_class_for_entity(self._entity)
        # add_cans(sut, ['docker'])
