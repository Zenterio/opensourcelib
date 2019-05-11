"""
Tests for the addon extension.

Note that addons are installed by adding them to the Python environment.

Given that it is probably a bad idea to pollute the users Python environment
by installing generated addons, these tests are currently limited to checking
that the expected directory structure was generated.
"""

import functools
import os
import tempfile

from zaf.component.decorator import component, requires


@component
@requires(zk2='Zk2')
def create_addon_wizard(zk2):
    return zk2(['addon'], 'addon create', wait=False)


@requires(wizard=create_addon_wizard)
def test_create_framework_extension(wizard):
    with tempfile.TemporaryDirectory() as d:
        for line in ('framework\n'
                     'frameworkextension\n'
                     '1.2.3\n'
                     'this is my short description\n'
                     'this is my long description\n'
                     'I Am Maintainer\n'
                     'i.am.maintainer@zenterio.com\n'
                     'some_package==1.2.3\n'
                     'FrameworkExtensionEntryPoint\n' + d + '\n'):
            wizard.write_stdin(line)

        exit_code = wizard.wait(30)
        assert exit_code == 0

        relative_path = functools.partial(os.path.join, d, 'frameworkextension')
        assert os.path.exists(relative_path('setup.py'))
        assert os.path.exists(relative_path('frameworkextension'))
        assert os.path.exists(relative_path('frameworkextension', '__init__.py'))
        assert os.path.exists(relative_path('frameworkextension', 'frameworkextension.py'))
        assert os.path.exists(relative_path('frameworkextension', 'test'))
        assert os.path.exists(relative_path('frameworkextension', 'test', '__init__.py'))
        assert os.path.exists(
            relative_path('frameworkextension', 'test', 'test_frameworkextension.py'))


@requires(wizard=create_addon_wizard)
def test_create_command_extension(wizard):
    with tempfile.TemporaryDirectory() as d:

        for line in ('command\n'
                     'commandextension\n'
                     '1.2.3\n'
                     'this is my short description\n'
                     'this is my long description\n'
                     'I Am Maintainer\n'
                     'i.am.maintainer@zenterio.com\n'
                     'some_package==1.2.3\n'
                     'CommandExtensionEntryPoint\n' + d + '\n'
                     'addon\n'):
            wizard.write_stdin(line)

        exit_code = wizard.wait(30)
        assert exit_code == 0

        relative_path = functools.partial(os.path.join, d, 'commandextension')
        assert os.path.exists(relative_path('setup.py'))
        assert os.path.exists(relative_path('commandextension'))
        assert os.path.exists(relative_path('commandextension', '__init__.py'))
        assert os.path.exists(relative_path('commandextension', 'commandextension.py'))
        assert os.path.exists(relative_path('commandextension', 'test'))
        assert os.path.exists(relative_path('commandextension', 'test', '__init__.py'))
        assert os.path.exists(relative_path('commandextension', 'test', 'test_commandextension.py'))
