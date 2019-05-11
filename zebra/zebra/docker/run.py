import logging
import os
import pty
import select
import shlex
import signal
import sys
import termios
from io import StringIO
from subprocess import Popen

from zebra.docker.signals import DockerSignalHandler, SignalListener
from zebra.docker.util import create_unique_container_name, in_foreground, is_interactive

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def run_docker_run(
        docker_command, image, flags, docker_workdir, command_with_arguments, execute,
        forward_signals):
    """
    Execute docker run using the execute function.

    :param docker_command: The docker command, default 'docker'
    :param image: the docker image
    :param flags: the flags to the docker command
    :param docker_workdir: the docker workdir
    :param command_with_arguments: the command, with arguents, to run inside docker
    :param execute: the execute function
    :param forward_signals: if signals should be forwarded to the docker container
    :return: the return values from the execute function
    """
    container_name = create_unique_container_name()

    run_command = [docker_command, 'run', '--rm']
    run_command.extend(flags)
    run_command.extend(['--name', container_name])
    run_command.extend(
        [
            '--workdir', docker_workdir, image, '/bin/bash', '-c', '{command} {arguments}'.format(
                command=command_with_arguments[0],
                arguments=' '.join(
                    ['{arg}'.format(arg=shlex.quote(arg)) for arg in command_with_arguments[1:]]))
        ])

    if not forward_signals:
        with DockerSignalHandler(container_name) as h:
            return execute(run_command, forward_signals, h)
    else:
        return execute(run_command, forward_signals)


def execute_interactive(run_command, forward_signals, signal_handler=None):
    return_value = _execute_internal(
        run_command, forward_signals, signal_handler, sys.stdout, sys.stderr)
    return return_value


def execute_capture(run_command, forward_signals, signal_handler):
    stdout = StringIO()
    stderr = StringIO()

    return_value = _execute_internal(run_command, forward_signals, signal_handler, stdout, stderr)
    return return_value, stdout.getvalue(), stderr.getvalue()


def _execute_internal(run_command, forward_signals, signal_handler, stdout, stderr):
    log_suffix = ''
    if not in_foreground():
        log_suffix = ' in background'

    logger.debug(
        'Running docker run{log_suffix}: {command}'.format(
            log_suffix=log_suffix, command=' '.join([shlex.quote(part) for part in run_command])))

    if forward_signals:
        return _execute_internal_forward_signals(run_command, stdout, stderr)
    else:
        return _execute_internal_capture_signals(run_command, signal_handler, stdout, stderr)


def _execute_internal_forward_signals(run_command, stdout, stderr):
    p = Popen(
        run_command,
        preexec_fn=os.setsid,
        stdin=sys.stdin,
        stdout=stdout,
        stderr=stderr,
        universal_newlines=True)

    return p.wait()


def _execute_internal_capture_signals(run_command, signal_handler, stdout, stderr):

    # Listener used to know if SIGCONT has been received
    listener = SignalListener()
    if signal_handler:
        signal_handler.add_listener(signal.SIGCONT, listener)

    # save original tty setting if a tty exists
    old_tty_attr = None
    if is_interactive():
        old_tty_attr = termios.tcgetattr(sys.stdin)

        # get the current settings se we can modify them
        newattr = termios.tcgetattr(sys.stdin)

        # set the terminal to uncanonical mode and turn off
        # input echo.
        newattr[3] &= ~termios.ICANON & ~termios.ECHO

        # set our new attributes
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, newattr)

    master_fd = None
    master_stderr_fd = None
    try:
        # Open pseudo-terminals to interact with subprocess. Need one for stdout and one for stderr
        master_fd, slave_fd = pty.openpty()
        master_stderr_fd, slave_stderr_fd = pty.openpty()

        # Use os.setsid() make it run in a new process group, or bash job control will not be enabled
        # This is needed because docker needs to run in the foreground but if it runs in the foreground
        # of the current process group it will automatically catch all signals.
        p = Popen(
            run_command,
            preexec_fn=os.setsid,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_stderr_fd,
            universal_newlines=True)

        data_in_last_loop = True  # True to start with to always enter loop
        while p.poll() is None or data_in_last_loop:
            if in_foreground() and is_interactive():
                r, w, e = select.select([sys.stdin, master_fd, master_stderr_fd], [], [], 0.2)
            else:
                r, w, e = select.select([master_fd, master_stderr_fd], [], [], 0.2)
            data_in_last_loop = bool(r)

            if listener.occurred:
                # After SIGCONT the select says that there is something  to read from stdin
                # but for some reason there isn't which makes os.read block until next input
                # which might be never
                listener.occurred = False

                if is_interactive() and in_foreground():
                    # drain stdin only if the process is in the foreground otherwise
                    # we don't have access to stdin and this will hang
                    termios.tcdrain(sys.stdin)

                # Similar to stdin the select says that there are things to read
                # but reading hangs. This could lead to data loss if there are things
                # to read from the subprocess stdout/stderr but no idea how to handle that
                termios.tcdrain(master_fd)
                termios.tcdrain(master_stderr_fd)

            else:
                if sys.stdin in r:
                    # Read from stdin and write to subprocess stdin
                    d = os.read(sys.stdin.fileno(), 10240)
                    os.write(master_fd, d)

                if master_fd in r:
                    # Read from subprocess stdout and write to stdout
                    o = os.read(master_fd, 10240)
                    if o:
                        try:
                            # If stderr is a StringIO this will fail
                            os.write(stdout.fileno(), o)
                        except Exception:
                            stdout.write(o.decode('utf-8', 'ignore'))

                if master_stderr_fd in r:
                    # Read from subprocess stderr and write to stderr
                    o = os.read(master_stderr_fd, 10240)
                    if o:
                        try:
                            # If stderr is a StringIO this will fail
                            os.write(stderr.fileno(), o)
                        except Exception:
                            stderr.write(o.decode('utf-8', 'ignore'))

        return_value = p.wait()

        logger.debug(
            'Docker run completed with return value: {return_value}'.format(
                return_value=return_value))

    finally:
        if master_fd:
            os.close(master_fd)

        if master_stderr_fd:
            os.close(master_stderr_fd)

        if old_tty_attr is not None and in_foreground() and is_interactive():
            # Reset stdin if in foreground
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty_attr)

        if signal_handler:
            signal_handler.remove_listener(signal.SIGCONT, listener)

    return return_value
