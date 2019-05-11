import os
from textwrap import dedent

from zaf.component.decorator import requires


@requires(zebra='Zebra')
def test_help_make(zebra):
    zebra('make --help')


@requires(zebra='Zebra')
def test_make_command_runs_zmake_with_arguments(zebra):
    result = zebra('-v make help')

    assert 'zmake help' in result.stdout


@requires(zebra='Zebra')
def test_make_command_supports_arguments_with_dashes(zebra):
    """Test that click doesn't consume arguments beginning with dashes."""
    result = zebra('-v make -j --output-sync help')

    assert 'zmake -j --output-sync help' in result.stdout
