import datetime
import socket
import sys
import time
from tempfile import TemporaryDirectory

import requests
from pretenders.client.http import HTTPMock
from zaf.component.decorator import component, requires


@component(name='HttpMock')
@requires(process_runner='ProcessRunner')
@requires(jenkins='Jenkins')
def HttpMock(process_runner, jenkins):
    process = None
    with TemporaryDirectory() as dir:
        try:
            server_ip, server_port = target_facing_host_ip_and_free_port(jenkins.ip)
            process = process_runner(
                '{python} -m pretenders.server.server --host {ip} -p {port}'.format(
                    python=sys.executable, ip=server_ip, port=str(server_port)),
                wait=False,
                cwd=dir)

            def mock_server_is_up():
                try:
                    r = requests.get('http://{ip}:{port}'.format(ip=server_ip, port=server_port))
                    if r.status_code == 200:
                        return r
                    else:
                        return False
                except requests.exceptions.ConnectionError:
                    return False

            wait_for(mock_server_is_up, 10)

            yield HTTPMock(server_ip, server_port)
        finally:
            if process:
                process.kill()


def wait_for(predicate, timeout, poll_interval=1.0):
    """Wait for predicate function to return a truthy value."""
    start_time = datetime.datetime.now().timestamp()
    end_time = start_time + timeout * 1000

    while datetime.datetime.now().timestamp() < end_time:
        value = predicate()
        if value:
            return value
        time.sleep(poll_interval)

    raise TimeoutError(
        'wait_for timed out when waiting for {predicate} with timeout {timeout}'.format(
            predicate=str(predicate), timeout=str(timeout)))


def target_facing_host_ip_and_free_port(target_ip):
    """Return the host IP facing the target_ip as well as a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((target_ip, 0))
        return s.getsockname()
