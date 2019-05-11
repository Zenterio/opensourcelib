import socket
from functools import lru_cache
from ipaddress import IPv4Address, IPv4Network

from zebra.cache.common import MCACHE_REPOSITORY

PROXY_MAP = {}


def _proxy_map_lookup(ip, proxy_map):
    ip = IPv4Address(ip)
    for subnet, proxy in proxy_map.items():
        if ip in IPv4Network(subnet):
            return proxy
    return None


@lru_cache()
def _ip_address(timeout=5):
    """
    Determine IP address of the network interface used to connect to <YOUR_REGISTRY>.

    We can't use the current hostname to lookup the IP address, as it is often
    set to some loopback address in the /etc/hosts file. It's also risky to
    enumerate the current IP addresses of the machine, since a computer may
    have several active network interfaces. It's basically impossible to know
    which is actually used to reach the VPN network without going through
    the routing table by opening a socket to some known host.

    We use a 5 second timeout to avoid hanging forever.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        s.connect(('<YOUR_REGISTRY>', 443))
        return s.getsockname()[0]


def _find_artifact_proxy(proxy_map=PROXY_MAP):
    """
    Try to find a suitable cache server.

    For some offices that use a VPN to reach their HQ, there might exist a local
    caching artifact proxy server to make artifact accesses faster. Here, we
    try to figure out which one to use based on the IP address that currently
    routes to a known server.
    """
    try:
        return _proxy_map_lookup(_ip_address(), proxy_map)
    except Exception:
        return None


def find_docker_registry_cache():
    return _find_artifact_proxy()
