import ipaddress
from unittest import TestCase
from unittest.mock import MagicMock

from ..networking import IpTables, sut_facing_host_ip_address


class TestNetworking(TestCase):

    def setUp(self):
        self.sut = MagicMock()

    def test_sut_facing_host_ip_address_returns_valid_address(self):
        """Test that sut_facing_host_ip_address method returns string in IP address format."""
        self.sut.ip = '10.20.247.230'
        ip = sut_facing_host_ip_address(self.sut)
        # ValueError will be raised if 'ip' does not represent a valid IPv4 or IPv6 address
        ipaddress.ip_address(ip)

    def test_iptables_requires_protocol_for_port_argument(self):
        ipt = IpTables(host_ip='127.0.0.1', exec=MagicMock())
        with self.assertRaises(ValueError):
            ipt.allow_outgoing(protocol=None, port=42)

    def test_iptables_with_no_args(self):
        exec_mock = MagicMock()
        with IpTables(host_ip='127.0.0.1', exec=exec_mock) as ipt:
            ipt.allow_outgoing()
        exec_mock.send_line.assert_any_call(
            'iptables -I OUTPUT -d 127.0.0.1 -p tcp -j ACCEPT', expected_exit_code=0)
        exec_mock.send_line.assert_any_call('iptables -D OUTPUT -d 127.0.0.1 -p tcp -j ACCEPT')

    def test_iptables_with_port(self):
        exec_mock = MagicMock()
        with IpTables(host_ip='127.0.0.1', exec=exec_mock) as ipt:
            ipt.allow_outgoing(port=42)
        exec_mock.send_line.assert_any_call(
            'iptables -I OUTPUT -d 127.0.0.1 -p tcp --dport 42 -j ACCEPT', expected_exit_code=0)
        exec_mock.send_line.assert_any_call(
            'iptables -D OUTPUT -d 127.0.0.1 -p tcp --dport 42 -j ACCEPT')
