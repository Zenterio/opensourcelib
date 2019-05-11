"""Provides string utilities."""

import re


def strip_ansi_escapes(s):
    """Strip ANSI escape codes from a string."""
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)


def make_valid_filename(s):
    """Remove characters we do not want to allow in filenames."""
    return ''.join(x for x in s if (x.isalnum() or x in '._- '))
