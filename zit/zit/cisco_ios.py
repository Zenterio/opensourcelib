import functools
import re
import zit.ssh


@functools.lru_cache(maxsize=1)
def get_ports():
    portlist = zit.ssh.run_ssh('show int status | e UPLINK|^Po1').strip().splitlines()[1:]
    portlist = map(lambda item: re.sub(r'\s+', ' ', item), portlist)
    return [{
        'port': item.split(' ')[0],
        'description': item.split(' ')[1],
        'vlan': item.split(' ')[3],
    } for item in portlist]


@functools.lru_cache(maxsize=1024)
def is_known_port(port):
    return port in [item['port'] for item in get_ports()]

def get_port(port):
    if not is_known_port(port):
        raise Exception('Not a valid port!')
    portinfo = zit.ssh.run_ssh(f'show run int {port}').strip().splitlines()
    return {
        'port':
        port,
        'vlan':
            [item.strip().split(' ')[-1] for item in portinfo
             if 'switchport access vlan' in item][0],
        'description':
        [item.strip().split(' ')[-1] for item in portinfo if 'description' in item][0]
    }


def set_vlan_for_port(port, vlan):
    if not is_known_port(port):
        raise Exception('Not a valid port!')
    zit.ssh.run_ssh('config t', f'int {port}', f'switchport access vlan {vlan}', 'end')
    get_ports.cache_clear()
    
