"""
Renders commmand-line strings used for invoking the different tools used in znake.

Functions with suffix _apply will have side-effects such as modifying files.

Functions with suffix _check will not have side-effects, just check and report.

.. autofunction:: render_flake8_check
.. autofunction:: render_isort_apply
.. autofunction:: render_isort_check
.. autofunction:: render_pydocstyle_check
.. autofunction:: render_yapf_apply
.. autofunction:: render_yapf_check
"""

import os

from znake.util import znake_tool_path


def render_flake8_check(ctx):
    """Return command-line for running flake8."""
    packages = ' '.join(ctx.znake.static.packages)
    flags = ' '.join(ctx.znake.static.flake8.flags)

    if '--config' not in flags:
        flags += ' --config {path}'.format(path=os.path.join(_data_dir(), 'flake8_config'))

    return '{flake8} {flags} {packages}'.format(
        flake8=znake_tool_path('flake8'), packages=packages, flags=flags)


def render_pydocstyle_check(ctx):
    """Return command-line for running pydocstyle."""
    packages = ' '.join(ctx.znake.static.packages)
    flags = ' '.join(ctx.znake.static.pydocstyle.flags)

    return '{pydocstyle} {flags} {packages}'.format(
        pydocstyle=znake_tool_path('pydocstyle'), packages=packages, flags=flags)


def _render_yapf(ctx, extra_flags, include_format_message=False):
    flags = ' '.join(ctx.znake.static.yapf.flags)
    packages = ' '.join(ctx.znake.static.packages)

    if '--style' not in flags:
        flags += ' --style {path}'.format(path=os.path.join(_data_dir(), 'yapf_style'))

    format_message = ''
    if include_format_message:
        format_message = ' || (echo "\nRun \'znake format\' to automatically solve formatting problems" && exit 1)'

    return '{yapf} -p --recursive {extra_flags} {flags} {packages}{format_message}'.format(
        yapf=znake_tool_path('yapf'),
        extra_flags=extra_flags,
        flags=flags,
        packages=packages,
        format_message=format_message)


def render_yapf_apply(ctx):
    """
    Return command-line for running yapf and do automatic updates of code.

    The command updates the formatting of the code if possible.
    """
    return _render_yapf(ctx, '--in-place')


def render_yapf_check(ctx):
    """Return command-line for running yapf to verify formatting."""
    return _render_yapf(ctx, '--diff', include_format_message=True)


def _render_isort(ctx, extra_flags, include_format_message=False):
    format_message = ''
    if include_format_message:
        format_message = ' || (echo "Run \'znake format\' to automatically sort includes" && exit 1)'

    return (
        '{isort} --recursive {extra_flags} {flags} {projects} '
        '--section-default THIRDPARTY {packages}{format_message}').format(
            isort=znake_tool_path('isort'),
            extra_flags=extra_flags,
            flags=' '.join(ctx.znake.static.isort.flags),
            projects=' '.join(
                [
                    '--project {project}'.format(project=package)
                    for package in ctx.znake.static.packages
                ]),
            packages=' '.join(ctx.znake.static.packages),
            format_message=format_message,
        )


def render_isort_apply(ctx):
    """Return command-line for running isort to do automatic sorting of imports."""
    return _render_isort(ctx, '--apply')


def render_isort_check(ctx):
    """Return command-line for running isort to verify that imports are sorted."""
    return _render_isort(ctx, '--check-only', include_format_message=True)


def _data_dir():
    return os.path.join(os.path.dirname(__file__), 'data')
