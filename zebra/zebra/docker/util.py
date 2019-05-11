import os
import sys
import uuid


def create_unique_container_name(prefix='zebra'):
    return '{prefix}-{uuid}'.format(prefix=prefix, uuid=uuid.uuid4())


def in_foreground():
    try:
        return os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno())
    except OSError:
        return False


def is_interactive():
    """
    Check if zebra is running in an interactive tty.

    This is not the case on Jenkins for example.
    If not running in a tty the -it flags are not applicable and gives error messages.
    """
    return sys.__stdin__.isatty()
