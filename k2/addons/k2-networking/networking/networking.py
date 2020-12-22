"""Providing network information to other modules."""

import logging
import socket

from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'networking'))
logger.addHandler(logging.NullHandler())


@component(name='SutFacingHostIpAddress', provided_by_extension='networking')
@requires(sut='Sut')
def sut_facing_host_ip_address(sut):
    """
    Class SutFacingHostIpAddress is used to provide the IP address of the host where K2 is running.

    Example

    .. code-block:: python

        @requries(host_ip='SutFacingHostIpAddress')
        def test_connected_to_zenterio_network_(host_ip):
            assert '10.20.247.' in host_ip
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((sut.ip, 0))
        return s.getsockname()[0]


@component(provided_by_extension='networking')
@requires(host_ip='SutFacingHostIpAddress')
@requires(exec='Exec')
class IpTables(object):
    """Wrapper to the iptables command on a SUT."""

    def __init__(self, host_ip, exec):
        self.host_ip = host_ip
        self.exec = exec
        self.rules = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.clear()

    def clear(self):
        """Clear all previously added rules."""
        for rule in self.rules:
            cmd = 'iptables -D ' + rule
            logger.info('Removing iptables rule: {cmd}'.format(cmd=cmd))
            self.exec.send_line(cmd)
        self.rules.clear()

    def allow_outgoing(self, protocol='tcp', port=None):
        """
        Add iptables rule to the OUTPUT chain.

        Run 'iptables -L OUTPUT -d <k2 IP> [-p <protocol> [--dport <port>]]' on
        the box. Please refer to the iptables documentation for details of '-d'
        and '--dport'. The k2 IP is automatically filled in.
        """
        rule = 'OUTPUT -d {ip} '.format(ip=self.host_ip)
        if protocol:
            rule += '-p {prot} '.format(prot=protocol)
        if port:
            if not protocol:
                raise ValueError('port argument requires protocol to be specified')
            rule += '--dport {port} '.format(port=port)
        rule += '-j ACCEPT'
        cmd = 'iptables -I ' + rule
        logger.info('Inserting iptables rule: {cmd}'.format(cmd=cmd))
        self.exec.send_line(cmd, expected_exit_code=0)
        self.rules.append(rule)


@FrameworkExtension(name='networking', config_options=[], endpoints_and_messages={})
class Networking(AbstractExtension):

    def __init__(self, config, instances):
        pass
