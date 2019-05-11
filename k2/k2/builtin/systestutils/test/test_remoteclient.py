import unittest
from unittest.mock import MagicMock, Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness

from ..remoteclient import SystestRemoteClient
from ..systestutils import SystestUtils


class TestSystestRemoteClient(unittest.TestCase):

    def test_creates_a_socket_to_get_an_available_port(self):
        socket_mock = MagicMock()
        socket_mock.__enter__ = Mock(return_value=socket_mock)
        socket_mock.getsockname.return_value = ('', 12345)
        with patch('socket.socket', return_value=socket_mock):
            self.assertEqual(SystestRemoteClient().port, 12345)

    def test_client_method_makes_a_context_manager_of_zaf_remote_client(self):
        remote_client_mock = MagicMock()
        remote_client_mock.__enter__ = Mock(return_value=remote_client_mock)

        with patch('k2.builtin.systestutils.remoteclient.RemoteClient',
                   return_value=remote_client_mock):
            with SystestRemoteClient().client() as client:
                self.assertEqual(remote_client_mock, client)

            remote_client_mock.__exit__.assert_called_with(None, None, None)


def create_harness():
    return ExtensionTestHarness(SystestUtils, config={}, components=[SystestRemoteClient])
