import unittest
from unittest.mock import MagicMock, patch

from zebra.cache.common import MCACHE_REPOSITORY
from zebra.config.config import _find_artifact_proxy, _ip_address, _proxy_map_lookup, \
    find_mcache_repository


class TestIpLookup(unittest.TestCase):

    def setUp(self):
        # Since the IP address lookup is cached, make sure to clear the cache
        # before each test!
        _ip_address.cache_clear()

    @patch('socket.socket')
    def test_find_ip_using_getsockname(self, socket):
        s = MagicMock()
        s.getsockname.return_value = ('192.168.1.1', 43927)
        socket.return_value.__enter__.return_value = s

        ip = _ip_address()
        self.assertEqual(ip, '192.168.1.1')

        assert s.getsockname.call_count == 1

    @patch('socket.socket')
    def test_find_ip_caches_result(self, socket):
        s = MagicMock()
        s.getsockname.return_value = ('192.168.1.1', 43927)
        socket.return_value.__enter__.return_value = s

        _ip_address()
        _ip_address()

        assert s.getsockname.call_count == 1


class TestProxyFinder(unittest.TestCase):

    def test_proxy_map_subnet_lookup(self):
        proxy_map = {
            '192.168.1.0/24': 'proxy1',
            '192.168.2.0/24': 'proxy2',
        }

        self.assertEqual(_proxy_map_lookup('192.168.1.7', proxy_map), 'proxy1')
        self.assertEqual(_proxy_map_lookup('192.168.2.1', proxy_map), 'proxy2')

    def test_proxy_map_lookup_returns_none_if_ip_does_not_match_any_subnet(self):
        proxy_map = {
            '192.168.1.0/24': 'proxy1',
        }

        self.assertEqual(_proxy_map_lookup('192.168.2.1', proxy_map), None)

    @patch('zebra.config.config._ip_address')
    def test_find_artifact_proxy_returns_none_if_ip_lookup_raises_exception(self, _ip_address):
        _ip_address.side_effect = Exception('Exception in _ip_address')

        self.assertEqual(_find_artifact_proxy({}), None)
