import logging
from collections import namedtuple

import requests

from . import ZnailError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

DnsOverride = namedtuple('DnsOverride', ['ip_address', 'hostname'])
IpRedirect = namedtuple(
    'IpRedirect', ['ip', 'port', 'destination_ip', 'destination_port', 'protocol'])


class ZnailComponent(object):

    def __init__(self, ip, port=80, timeout=10):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def packet_corruption(self, percent):
        """
        Emulates poor network conditions by corrupting a percentage of all incoming packets.

        Packets are corrupted by introducing single bit errors.

        * DSL Modem with degrading filter: 1%
        * Poorly shielded cable next to an EMI source: 5%
        """
        endpoint = self._api_endpoint('disciplines/packet_corruption')
        self._send_request(endpoint, {'percent': percent})

    def clear_packet_corruption(self):
        endpoint = self._api_endpoint('disciplines/packet_corruption/clear')
        self._send_request(endpoint)

    def packet_delay(self, milliseconds):
        """
        Delay incoming network packets for the specified amount of time.

        All packets are delayed by the same amount.
        The delay is added in addition to any delay already present on the network.
        For example, if a packet normally takes 5ms to arrive and is delayed by 50ms,
        the total time for the packet to arrive will be 55ms.

        * The average delay of a transatlantic connection: 100 ms
        * The average delay of a connection within the EU or the US: 35 ms
        * A satellite modem in the woods (terrible!): 600 ms
        """
        endpoint = self._api_endpoint('disciplines/packet_delay')
        self._send_request(endpoint, {'milliseconds': milliseconds})

    def clear_packet_delay(self):
        endpoint = self._api_endpoint('disciplines/packet_delay/clear')
        self._send_request(endpoint)

    def packet_duplication(self, percent):
        """
        Emulates poor network conditions by duplicating a percentage of all incoming packets.

        A duplicated package will be transmitted twice.
        Packages will not be duplicated multiple times.

        * Two switches misconfigured to broadcast the same traffic to the same address: 100%
        * Duplication due to high packet loss causing dropped ACKs: 5%
        * Duplication due to minor packet loss causing dropped ACKs: 2%
        """
        endpoint = self._api_endpoint('disciplines/packet_duplication')
        self._send_request(endpoint, {'percent': percent})

    def clear_packet_duplication(self):
        endpoint = self._api_endpoint('disciplines/packet_duplication/clear')
        self._send_request(endpoint)

    def packet_loss(self, percent):
        """
        Emulates poor network conditions by dropping a percentage of all incoming packets.

        * A wifi connection on the same channel as all your neighbours in an densely
          populated apartment building: 10%
        * Packet loss high enough for streamed video/voip to have problems: 7.5%
        * A fairly high packet loss rate under which things should still work: 2.5%
        """
        endpoint = self._api_endpoint('disciplines/packet_loss')
        self._send_request(endpoint, {'percent': percent})

    def clear_packet_loss(self):
        endpoint = self._api_endpoint('disciplines/packet_loss/clear')
        self._send_request(endpoint)

    def packet_rate_control(self, kbit, latency_milliseconds=1000, burst_bytes=10000):
        """
        Emulates poor network conditions by limiting the rate at which packages are transfered.

        Package transfer is rate limited by putting incoming packets into a queue and limiting
        the rate at which packets may leave the queue.

        * A dialup modem: 56 kbit, 1000 ms, 10000 bytes
        * A slow ADSL connection: 1536 kbit, 1000 ms, 10000 bytes
        * A standard ADSL connection: 4096 kbit, 1000 ms, 10000 bytes
        * The max throughput of udp over 802.11b wifi: 7270 kbit, 1000 ms, 10000 bytes

        :param kbit: The rate limit in kbit.
        :param latency_milliseconds: The amount of time a packet may spend in
                                     the queue before being discarded.
        :param burst_bytes: The size of the queue in bytes.
        """
        endpoint = self._api_endpoint('disciplines/packet_rate_control')
        self._send_request(
            endpoint, {
                'kbit': kbit,
                'latency_milliseconds': latency_milliseconds,
                'burst_bytes': burst_bytes
            })

    def clear_packet_rate_control(self):
        endpoint = self._api_endpoint('disciplines/packet_rate_control/clear')
        self._send_request(endpoint)

    def packet_reordering(self, milliseconds, percent):
        """
        Emulates poor network conditions by reordering a percentage of all incoming packets.

        Packets are reordered by delaying all packages a fixed amount, while sending a
        percentage of them immediately.

        * Some packets taking a slower path through the network: 100 ms, 5%
        * Many packets taking an almost as good path through the network: 10 ms, 50%
        """
        endpoint = self._api_endpoint('disciplines/packet_reordering')
        self._send_request(endpoint, {'milliseconds': milliseconds, 'percent': percent})

    def clear_packet_reordering(self):
        endpoint = self._api_endpoint('disciplines/packet_reordering/clear')
        self._send_request(endpoint)

    def network_disconnect(self):
        """
        Emulates the scenario where the network cable of the device under test is disconnected.

        This is done by powering down the device-facing network adapter.
        """
        endpoint = self._api_endpoint('disconnect')
        self._send_request(endpoint, {'disconnect': True})

    def clear_network_disconnect(self):
        endpoint = self._api_endpoint('disconnect/clear')
        self._send_request(endpoint)

    def get_network_whitelist(self):
        endpoint = self._api_endpoint('whitelist')
        try:
            response = self._send_request(endpoint, method='get')
            return response.json()
        except Exception as e:
            msg = 'Could not get whitelist data: {reason}'.format(reason=str(e))
            logger.debug(msg, exc_info=True)
            logger.error(msg)
            raise ZnailError(msg)

    def add_to_network_whitelist(self, ip_address):
        """
        Add an ip_address to the whitelist.

        Emulated network conditions are applied to all incoming packets.

        For cases where this is not desired, a whitelist is provided.
        Packets being sent to or originating from addresses on the
        whitelist are not subject to the emulated conditions.
        """
        endpoint = self._api_endpoint('whitelist')
        whitelist = self.get_network_whitelist()
        whitelist.append(ip_address)
        self._send_request(endpoint, [{'ip_address': ip_address} for ip_address in whitelist])

    def clear_network_whitelist(self):
        endpoint = self._api_endpoint('whitelist/clear')
        self._send_request(endpoint)

    def get_dns_overrides(self):
        """
        List of DNS overrides.

        :return: List of DnsOverride objects.
        """
        endpoint = self._api_endpoint('dnsoverride')
        try:
            response = self._send_request(endpoint, method='get')
            return [
                DnsOverride(response['ip_address'], response['hostname'])
                for response in response.json()
            ]
        except Exception as e:
            msg = 'Could not get DNS override data: {reason}'.format(reason=str(e))
            logger.debug(msg, exc_info=True)
            logger.error(msg)
            raise ZnailError(msg)

    def add_dns_override(self, ip_address, hostname):
        """
        Add a DNS override.

        Redirect all outgoing DNS traffic to the DNS server provided by the Network Emulator.

        DNS queries are normally forwarded upstream. However, specific hosts and FQDN may be overridden.

        The DNS server functions in a round-robin fashion. If multiple entries are provided for a
        single host name, the DNS server will cycle through this list when responding to DNS
        queries. An entry with the IP address set to None will remove all knowledge of a hostname
        from the DNS server.
        """
        self._add_dns_overrides([DnsOverride(ip_address, hostname)])

    def add_dns_overrides(self, *args):
        """
        Add multiple DNS overrides.

        Takes a list of 2-tuples containing IP address and hostname pairs.
        """
        self._add_dns_overrides(
            [DnsOverride(ip_address, hostname) for ip_address, hostname in args])

    def _add_dns_overrides(self, dns_overrides):
        endpoint = self._api_endpoint('dnsoverride')
        self._send_request(
            endpoint, [
                {
                    'hostname': dns_override.hostname,
                    'ip_address': dns_override.ip_address if dns_override.ip_address else ''
                } for dns_override in self.get_dns_overrides() + dns_overrides
            ])

    def clear_dns_overrides(self):
        endpoint = self._api_endpoint('dnsoverride/clear')
        self._send_request(endpoint)

    def get_ip_redirects(self):
        endpoint = self._api_endpoint('ipredirect')
        try:
            response = self._send_request(endpoint, method='get')
            return [
                IpRedirect(
                    response['ip'], response['port'], response['destination_ip'],
                    response['destination_port'], response['protocol'])
                for response in response.json()
            ]
        except Exception as e:
            msg = 'Could not get IP redirect data: {reason}'.format(reason=str(e))
            logger.debug(msg, exc_info=True)
            logger.error(msg)
            raise ZnailError(msg)

    def add_ip_redirect(self, ip, port, destination_ip, destination_port, protocol):
        """
        Add an IP redirect.

        Redirect packets with one destination (ip:port) to another destination (ip:port).
        """
        endpoint = self._api_endpoint('ipredirect')
        ip_redirects = self.get_ip_redirects()
        ip_redirects.append(IpRedirect(ip, port, destination_ip, destination_port, protocol))
        self._send_request(
            endpoint, [
                {
                    'ip': ip_redirect.ip,
                    'port': ip_redirect.port,
                    'destination_ip': ip_redirect.destination_ip,
                    'destination_port': ip_redirect.destination_port,
                    'protocol': ip_redirect.protocol
                } for ip_redirect in ip_redirects
            ])

    def clear_ip_redirects(self):
        endpoint = self._api_endpoint('ipredirect/clear')
        self._send_request(endpoint)

    def health_check(self):
        """
        Check if the Znail is healthy.

        Raises ZnailError if the Znail is not healthy or can not be reached.
        """
        endpoint = self._api_endpoint('healthcheck')
        try:
            response = self._send_request(endpoint, method='get')
            health_data = response.json()
        except Exception as e:
            msg = 'Could not get Znail health data: {reason}'.format(reason=str(e))
            logger.debug(msg, exc_info=True)
            logger.error(msg)
            raise ZnailError(msg)

        for name, status in health_data.items():
            if not status:
                raise ZnailError('Health check failed: {name}'.format(name=name))

    def clear(self):
        """Clear all applied network emulation."""
        self.clear_packet_corruption()
        self.clear_packet_delay()
        self.clear_packet_duplication()
        self.clear_packet_loss()
        self.clear_packet_rate_control()
        self.clear_packet_reordering()
        self.clear_network_disconnect()
        self.clear_network_whitelist()
        self.clear_dns_overrides()
        self.clear_ip_redirects()

    def _send_request(self, endpoint, data=None, method='post'):
        try:
            logger.info(
                'Sending request to {endpoint}: {data}'.format(endpoint=endpoint, data=data))
            if method == 'post':
                response = requests.post(endpoint, timeout=self.timeout, json=data)
            elif method == 'get':
                response = requests.get(endpoint, timeout=self.timeout, json=data)
            else:
                raise ZnailError('Unknown method: {method}'.format(method=method))
            logger.info('Sent request to {endpoint}: {data}'.format(endpoint=endpoint, data=data))
            self._assert_response_ok(response)
            return response
        except Exception as e:
            msg = 'Could not send request to {endpoint}: {reason}'.format(
                endpoint=endpoint, reason=str(e))
            logger.debug(msg, exc_info=True)
            logger.error(msg)
            raise

    def _assert_response_ok(self, response):
        if not response.ok:
            try:
                reason = response.json()['message']
            except Exception:
                reason = 'unknown'
            raise ZnailError('Error response from Znail: {reason}'.format(reason=reason))

    def _api_endpoint(self, endpoint):
        return 'http://{ip}:{port}/api/{endpoint}'.format(
            ip=self.ip, port=self.port, endpoint=endpoint)

    def __enter__(self):
        self.clear()
        return self

    def __exit__(self, *args):
        try:
            self.clear()
        except Exception as e:
            logger.info('Ignoring error during exit: {reason}'.format(reason=str(e)))
