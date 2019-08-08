import logging
from collections import OrderedDict

from zaf.extensions.extension import get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'ansible', 'config'))


class AnsibleConfig(object):

    def __init__(
            self,
            ansible_file,
            playbook,
            log_dir=None,
            environmental_config=None,
            remote_user=None,
            extra_vars=[]):
        self._ansible_file = ansible_file
        self._playbook = playbook
        self._env = OrderedDict()
        self._log_dir = log_dir
        self._remote_user = remote_user
        self._extra_vars = extra_vars

        self._env['ANSIBLE_CONFIG'] = self._ansible_file
        if remote_user:
            self._env['ANSIBLE_REMOTE_USER'] = self._remote_user
        if environmental_config:
            self._env.update(self._environment_config_to_dict(environmental_config))

        logger.debug('ansible_file: {f}'.format(f=self.ansible_file))
        logger.debug('playbook: {pb}'.format(pb=self.playbook))
        logger.debug('remoteuser: {ru}'.format(ru=self.remote_user))
        logger.debug('environmental_config: {envcfg}'.format(envcfg=environmental_config))
        logger.debug('env_str: {env_str}'.format(env_str=self.env_str))
        logger.debug('extra_vars: {ev}'.format(ev=self.extra_vars))

    @property
    def env(self):
        return self._env.copy()

    @property
    def env_str(self):
        return ' '.join(['{k}={v}'.format(k=k, v=v) for k, v in self._env.items()])

    @property
    def ansible_file(self):
        return self._ansible_file

    @property
    def playbook(self):
        return self._playbook

    @property
    def remote_user(self):
        return self._remote_user

    @property
    def extra_vars(self):
        return self._extra_vars

    @property
    def log_dir(self):
        return self._log_dir

    @property
    def log_path(self):
        return self._env.get('ANSIBLE_LOG_PATH', None)

    @staticmethod
    def _environment_config_to_dict(configs):
        result = OrderedDict()
        for item in configs:
            try:
                key, value = item.split('=')
                result[key] = value
            except ValueError:
                raise Exception(
                    "The ansible configuration '{item}' is mall-formated".format(item=item))
        return result
