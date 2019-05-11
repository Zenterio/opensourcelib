import unittest
from unittest.mock import MagicMock

from ..mockserver import TcpMockServer


class TestTcpMockServer(unittest.TestCase):

    def setUp(self):
        self.server = TcpMockServer(MagicMock)

    def test_start_and_stop_manually(self):
        self.server.serve_forever = MagicMock()
        self.server.shutdown = MagicMock()
        self.server.start()
        self.server.serve_forever.assert_called_once_with()
        self.server.stop()
        self.server.shutdown.assert_called_once_with()

    def test_start_and_stop_as_context_manager(self):
        self.server.serve_forever = MagicMock()
        self.server.shutdown = MagicMock()
        with self.server:
            self.server.serve_forever.assert_called_once_with()
        self.server.shutdown.assert_called_once_with()

    def test_servers_can_coexist_and_are_assigned_different_ports(self):
        other_server = TcpMockServer(MagicMock)
        with self.server as s1, other_server as s2:
            assert s1.port != 0
            assert s2.port != 0
            assert s1.port != s2.port
