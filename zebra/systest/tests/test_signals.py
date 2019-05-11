import os
import signal

from k2.runner.decorator import disabled
from zaf.component.decorator import requires

DOCKER_MOCK = '{cwd}/systest/data/docker_mock.sh'.format(cwd=os.getcwd())


@requires(zebra='Zebra')
def test_sigint_kills_docker(zebra):

    process = zebra(
        "-v exec 'echo COMMAND_START && sleep 5 && echo COMMAND_END'",
        override_run=DOCKER_MOCK,
        wait=False)
    try:
        process.wait_for_match_in_stdout('COMMAND_START', timeout=2)
        process.signal(signal.SIGINT)
    finally:
        process.wait(timeout=1)

    assert 'Received signal 2' in process.stderr, process.stderr
    assert 'docker rm -f' in process.stderr, process.stderr


@requires(zebra='Zebra')
@disabled("Disabled because can't get the signal to work on Jenkins")
def test_sigquit_kills_docker(zebra):

    process = zebra(
        "-v exec 'echo COMMAND_START && sleep 5 && echo COMMAND_END'",
        override_run=DOCKER_MOCK,
        wait=False)
    try:
        process.wait_for_match_in_stdout('COMMAND_START', timeout=2)
        process.signal(signal.SIGQUIT)
    finally:
        process.wait(timeout=1)

    assert 'Received signal 3' in process.stderr, process.stderr
    assert 'docker rm -f' in process.stderr, process.stderr


@requires(zebra='Zebra')
@disabled('Disabled because this create a coredump')
def test_sigabrt_kills_docker(zebra):

    process = zebra(
        "-v exec 'echo COMMAND_START && sleep 5 && echo COMMAND_END'",
        override_run=DOCKER_MOCK,
        wait=False)
    try:
        process.wait_for_match_in_stdout('COMMAND_START', timeout=2)
        process.signal(signal.SIGABRT)
    finally:
        process.wait(timeout=1)

    assert 'Received signal 6' in process.stderr, process.stderr
    assert 'docker rm -f' in process.stderr, process.stderr


@requires(zebra='Zebra')
def test_sigterm_kills_docker(zebra):

    process = zebra(
        "-v exec 'echo COMMAND_START && sleep 5 && echo COMMAND_END'",
        override_run=DOCKER_MOCK,
        wait=False)
    try:
        process.wait_for_match_in_stdout('COMMAND_START', timeout=2)
        process.signal(signal.SIGTERM)
    finally:
        process.wait(timeout=1)

    assert 'Received signal 15' in process.stderr, process.stderr
    assert 'docker rm -f' in process.stderr, process.stderr


@requires(zebra='Zebra')
def test_sigtstp_and_sigcont_pauses_and_unpauses_container(zebra):

    process = zebra(
        "-v exec 'echo COMMAND_START && sleep 5 && echo COMMAND_END'",
        override_run=DOCKER_MOCK,
        wait=False)
    try:
        process.wait_for_match_in_stdout('COMMAND_START', timeout=2)
        process.signal(signal.SIGTSTP)
        process.wait_for_match_in_stderr('docker pause', timeout=2)
        process.signal(signal.SIGCONT)
        process.wait_for_match_in_stderr('docker unpause', timeout=2)
        process.signal(signal.SIGKILL)
    finally:
        process.wait(timeout=1)

    assert 'Received signal SIGTSTP' in process.stderr, process.stderr
    assert 'Received signal SIGCONT' in process.stderr, process.stderr
