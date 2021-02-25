import json
import re
from unittest.mock import MagicMock, Mock, patch

import httpretty
from nose.tools import assert_raises, assert_raises_regex

from ..component import DnsOverride, IpRedirect, ZnailComponent, ZnailError


class TestZnailComponent(object):

    @httpretty.activate
    def _successful_call_to_endpoint(self, endpoint, fn, args, expected_data=None):
        url = 'http://1.2.3.4:80/api/{endpoint}'.format(endpoint=endpoint)
        body = '{"message": "ok"}'

        httpretty.register_uri(httpretty.POST, url, body=body)

        fn(*args)

        data = httpretty.last_request().body.decode('utf-8')
        if expected_data is not None:
            data = json.loads(data)
            assert data == expected_data
        else:
            assert data == ''

    @httpretty.activate
    def _unsuccessful_call_to_endpoint(self, endpoint, fn, args):
        url = 'http://1.2.3.4:80/api/{endpoint}'.format(endpoint=endpoint)
        body = '{"message": "my very unique error message"}'

        httpretty.register_uri(httpretty.POST, url, body=body, status=500)

        with assert_raises_regex(ZnailError, '.*: my very unique error message.*'):
            fn(*args)

    def test_generator(self):
        component = ZnailComponent('1.2.3.4')
        component.get_network_whitelist = Mock(return_value=[])
        component.get_dns_overrides = Mock(return_value=[])
        component.get_ip_redirects = Mock(return_value=[])

        for endpoint, fn, args, expected_data in (
            ('disciplines/packet_corruption', component.packet_corruption, [1], {'percent': 1}),
            ('disciplines/packet_corruption/clear', component.clear_packet_corruption, [], None),
            ('disciplines/packet_delay', component.packet_delay, [1], {'milliseconds': 1}),
            ('disciplines/packet_delay/clear', component.clear_packet_delay, [], None),
            ('disciplines/packet_duplication', component.packet_duplication, [1], {'percent': 1}),
            ('disciplines/packet_duplication/clear', component.clear_packet_duplication, [], None),
            ('disciplines/packet_loss', component.packet_loss, [1], {'percent': 1}),
            ('disciplines/packet_loss/clear', component.clear_packet_loss, [], None),
            ('disciplines/packet_rate_control', component.packet_rate_control, [1, 2, 3],
             {'kbit': 1, 'latency_milliseconds': 2, 'burst_bytes': 3}),
            ('disciplines/packet_rate_control/clear', component.clear_packet_rate_control, [],
             None),
            ('disciplines/packet_reordering', component.packet_reordering, [1, 2],
             {'milliseconds': 1, 'percent': 2}),
            ('disciplines/packet_reordering/clear', component.clear_packet_reordering, [], None),
            ('disconnect', component.network_disconnect, [], {'disconnect': True}),
            ('disconnect/clear', component.clear_network_disconnect, [], None),
            ('whitelist', component.add_to_network_whitelist, ['1.2.3.4'], [{'ip_address':
                                                                             '1.2.3.4'}]),
            ('whitelist/clear', component.clear_network_whitelist, [], None),
            ('dnsoverride', component.add_dns_override, ['1.2.3.4', 'a.com'],
             [{'hostname': 'a.com', 'ip_address': '1.2.3.4'}]),
            ('dnsoverride', component.add_dns_overrides, [('1.2.3.4', 'a.com'), ('2.3.4.5',
                                                                                 'b.com')],
             [{'hostname': 'a.com', 'ip_address': '1.2.3.4'}, {'hostname': 'b.com', 'ip_address':
                                                               '2.3.4.5'}]),
            ('dnsoverride/clear', component.clear_dns_overrides, [], None),
            ('ipredirect', component.add_ip_redirect, ['1.2.3.4', 1, '2.3.4.5', 2, 'tcp'],
             [{'ip': '1.2.3.4', 'port': 1, 'destination_ip': '2.3.4.5', 'destination_port': 2,
               'protocol': 'tcp'}]),
            ('ipredirect/clear', component.clear_ip_redirects, [], None),
        ):
            yield self._successful_call_to_endpoint, endpoint, fn, args, expected_data
            yield self._unsuccessful_call_to_endpoint, endpoint, fn, args

    @httpretty.activate
    def test_get_whitelist(self):
        url = 'http://1.2.3.4:80/api/whitelist'
        body = '["1.2.3.4", "2.3.4.5"]'

        httpretty.register_uri(httpretty.GET, url, body=body)

        component = ZnailComponent('1.2.3.4')
        assert component.get_network_whitelist() == ['1.2.3.4', '2.3.4.5']

    @httpretty.activate
    def test_get_whitelist_error(self):
        httpretty.register_uri(httpretty.GET, re.compile('.*'), status=500)

        component = ZnailComponent('1.2.3.4')
        with assert_raises(ZnailError):
            component.get_network_whitelist()

    @httpretty.activate
    def test_get_dns_overrides(self):
        url = 'http://1.2.3.4:80/api/dnsoverride'
        body = (
            '[{"ip_address": "2.3.4.5", "hostname": "b.com"},'
            ' {"ip_address": "1.2.3.4", "hostname": "a.com"}]')

        httpretty.register_uri(httpretty.GET, url, body=body)

        component = ZnailComponent('1.2.3.4')
        dns_overrides = component.get_dns_overrides()
        assert DnsOverride('2.3.4.5', 'b.com') in dns_overrides
        assert DnsOverride('1.2.3.4', 'a.com') in dns_overrides

    @httpretty.activate
    def test_get_dns_overrides_error(self):
        httpretty.register_uri(httpretty.GET, re.compile('.*'), status=500)

        component = ZnailComponent('1.2.3.4')
        with assert_raises(ZnailError):
            component.get_dns_overrides()

    @httpretty.activate
    def test_get_ip_redirects(self):
        url = 'http://1.2.3.4:80/api/ipredirect'
        body = (
            '[{"ip": "2.3.4.5", "port": 2, "destination_ip": "3.4.5.6",'
            ' "destination_port": 3, "protocol": "udp"},'
            ' {"ip": "1.2.3.4", "port": 1, "destination_ip": "2.3.4.5",'
            ' "destination_port": 2, "protocol": "tcp"}]')

        httpretty.register_uri(httpretty.GET, url, body=body)

        component = ZnailComponent('1.2.3.4')
        ip_redirects = component.get_ip_redirects()
        assert IpRedirect('1.2.3.4', 1, '2.3.4.5', 2, 'tcp') in ip_redirects
        assert IpRedirect('2.3.4.5', 2, '3.4.5.6', 3, 'udp') in ip_redirects

    @httpretty.activate
    def test_get_ip_redirects_error(self):
        httpretty.register_uri(httpretty.GET, re.compile('.*'), status=500)

        component = ZnailComponent('1.2.3.4')
        with assert_raises(ZnailError):
            component.get_ip_redirects()

    @httpretty.activate
    def test_health_check_fails_due_to_http_error(self):
        httpretty.register_uri(httpretty.GET, re.compile('.*'), status=500)

        component = ZnailComponent('1.2.3.4')
        with assert_raises(ZnailError):
            component.health_check()

    @httpretty.activate
    def test_health_check_fails_due_failed_check(self):
        url = 'http://1.2.3.4:80/api/healthcheck'
        body = '{"a": true, "b": false}'

        httpretty.register_uri(httpretty.GET, url, body=body)

        component = ZnailComponent('1.2.3.4')
        with assert_raises_regex(ZnailError, 'Health check failed: b'):
            component.health_check()

    @httpretty.activate
    def test_health_check_passes(self):
        url = 'http://1.2.3.4:80/api/healthcheck'
        body = '{"a": true, "b": true}'

        httpretty.register_uri(httpretty.GET, url, body=body)

        component = ZnailComponent('1.2.3.4')
        component.health_check()

    def test_clear(self):
        component = ZnailComponent('1.2.3.4')

        component.clear_packet_corruption = Mock()
        component.clear_packet_delay = Mock()
        component.clear_packet_duplication = Mock()
        component.clear_packet_loss = Mock()
        component.clear_packet_rate_control = Mock()
        component.clear_packet_reordering = Mock()
        component.clear_network_disconnect = Mock()
        component.clear_network_whitelist = Mock()
        component.clear_dns_overrides = Mock()
        component.clear_ip_redirects = Mock()

        component.clear()

        component.clear_packet_corruption.assert_called_once_with()
        component.clear_packet_delay.assert_called_once_with()
        component.clear_packet_duplication.assert_called_once_with()
        component.clear_packet_loss.assert_called_once_with()
        component.clear_packet_rate_control.assert_called_once_with()
        component.clear_packet_reordering.assert_called_once_with()
        component.clear_network_disconnect.assert_called_once_with()
        component.clear_network_whitelist.assert_called_once_with()
        component.clear_dns_overrides.assert_called_once_with()
        component.clear_ip_redirects.assert_called_once_with()

    def test_send_request_with_method_post(self):
        component = ZnailComponent('1.2.3.4')
        with patch('requests.post') as mock:
            response = component._send_request('my_endpoint', 'my_data', method='post')
            mock.assert_called_once_with('my_endpoint', json='my_data', timeout=component.timeout)
            assert response == mock()

    def test_send_request_with_method_get(self):
        component = ZnailComponent('1.2.3.4')
        with patch('requests.get') as mock:
            response = component._send_request('my_endpoint', 'my_data', method='get')
            mock.assert_called_once_with('my_endpoint', json='my_data', timeout=component.timeout)
            assert response == mock()

    def test_send_request_with_unknown_mehtod(self):
        component = ZnailComponent('1.2.3.4')
        with assert_raises_regex(ZnailError, 'Unknown method: other'):
            component._send_request('my_endpoint', 'my_data', method='other')

    def test_assert_response_ok_succeeds(self):
        response = Mock()
        response.ok = True
        ZnailComponent('1.2.3.4')._assert_response_ok(response)

    def test_assert_response_ok_fails_with_reason(self):
        response = Mock()
        response.ok = False
        response.json = MagicMock(return_value={'message': 'this is my message'})
        with assert_raises_regex(ZnailError, '.*this is my message.*'):
            ZnailComponent('1.2.3.4')._assert_response_ok(response)

    def test_assert_response_ok_fails_without_reason(self):
        response = Mock()
        response.ok = False
        response.json = MagicMock(side_effect=[Exception()])
        with assert_raises_regex(ZnailError, '.*unknown.*'):
            ZnailComponent('1.2.3.4')._assert_response_ok(response)

    def test_api_endpoint(self):
        assert ZnailComponent('1.2.3.4')._api_endpoint(
            'my_endpoint') == 'http://1.2.3.4:80/api/my_endpoint'
