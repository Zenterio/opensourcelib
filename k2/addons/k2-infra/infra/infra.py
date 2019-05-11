"""
Provides TestInfra integration for K2.

To learn more about TestInfra, please see:
https://testinfra.readthedocs.io/en/latest/

This extensions provides a TestInfra backend that is built on top of K2s :ref:`exec-label`.
TestInfra functionality is made available via the :ref:`component-Infra` component.

Example usage:

.. code-block:: python

    @requires(infra='Infra')
    def test_passwd_file(infra):
        passwd = infra.file('/etc/passwd')
        assert passwd.contains('root')
        assert passwd.user == 'root'
        assert passwd.group == 'root'
        assert passwd.mode == 0o644


.. code-block:: python

    @requires(infra='Infra')
    def test_nginx_is_installed(infra):
        nginx = infra.package('nginx')
        assert nginx.is_installed
        assert nginx.version.startswith('1.2')


.. code-block:: python

    @requires(infra='Infra')
    def test_nginx_running_and_enabled(infra):
        nginx = infra.service('nginx')
        assert nginx.is_running
        assert nginx.is_enabled

"""

import logging

from testinfra.backend import base
from testinfra.host import Host
from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.cmd.run import RUN_COMMAND

logger = logging.getLogger(get_logger_name('k2', 'infra'))
logger.addHandler(logging.NullHandler())


class K2TestInfraHostShim(Host):
    # TestInfra provides a __getattr__() to dynamically find its modules.
    # This does not play nicely with K2s automatic discovery of context managers.
    # Provide concrete __enter__() and __exit__() methods to make it work.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class K2ExecBackend(base.BaseBackend):
    NAME = 'k2-exec'

    def __init__(self, exec, *args, **kwargs):
        super().__init__(self.NAME, **kwargs)
        self._exec = exec

    def get_pytest_id(self):
        return self.NAME

    @classmethod
    def get_hosts(cls, host, **kwargs):
        return [host]

    def decode(self, data):
        # Stub out TestInfras decode mechanism. It is already done by K2s exec components.
        return data

    def run(self, command, *args, **kwargs):
        stdout, stderr, exit_code = self._exec.send_line(
            self.get_command(command, *args), extended_process_information=True)
        return self.result(exit_code, command, stdout, stderr)


@component(name='Infra')
@requires(exec='Exec')
def infra(exec):
    return K2TestInfraHostShim(K2ExecBackend(exec))


@CommandExtension(name='infra', extends=[RUN_COMMAND], config_options=[], endpoints_and_messages={})
class InfraExtension(AbstractExtension):

    def __init__(self, config, instances):
        pass
