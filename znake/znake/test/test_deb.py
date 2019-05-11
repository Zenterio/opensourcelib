import os
import unittest
from textwrap import dedent
from unittest.mock import Mock, patch

from znake.builddir import BuildDir
from znake.deb import _render_build_debian_package_command, _render_changelog_file, \
    _render_compat_file, _render_control_file, _render_copy_documentation_command, \
    _render_copy_scripts_command, _render_install_file, _render_links_file, _render_rules_file, \
    get_namespace


class TestRenderCopy(unittest.TestCase):

    def test_render_copy_documentation_command(self):
        ctx = self._get_mock_context()
        result = _render_copy_documentation_command('my_doc', ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                mkdir -p ./build/debian/doc/my_doc/pdf &&
                cp ./build/doc/my_doc/pdf/my_doc.pdf ./build/debian/doc/my_doc/pdf &&
                cp -r ./build/doc/my_doc/html ./build/debian/doc/my_doc/"""))

    def test_render_copy_scripts_command(self):
        ctx = self._get_mock_context()
        result = _render_copy_scripts_command('my_package', ctx)
        expected_result = ('cp ./znaketools/debian_config/* ' './build/debian || true')
        self.assertEqual(result, expected_result)

    def _get_mock_context(self):
        ctx = Mock()
        ctx.build_dir = BuildDir()
        return ctx


class TestRenderControlFile(unittest.TestCase):

    def test_render_control_file_with_no_dependencies(self):
        ctx = self._get_mock_context()
        ctx.znake.deb.dependencies = None
        result = _render_control_file(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                Source: my_package
                Section: python
                Priority: extra
                Maintainer: intercalguy83 <comefrom@hotmail.com>
                Standards-Version: 3.9.5

                Package: my_package
                Architecture: any
                Pre-Depends: python3.6-minimal | python3.6
                Depends: ${python:Depends}, ${misc:Depends}
                Description: this is my short description
                  this is my long description please"""))

    def test_render_control_with_with_dependencies(self):
        ctx = self._get_mock_context()
        ctx.znake.deb.dependencies = ['seahorse-adventures', 'gnat-5']
        result = _render_control_file(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                Source: my_package
                Section: python
                Priority: extra
                Maintainer: intercalguy83 <comefrom@hotmail.com>
                Standards-Version: 3.9.5

                Package: my_package
                Architecture: any
                Pre-Depends: python3.6-minimal | python3.6
                Depends: seahorse-adventures, gnat-5, ${python:Depends}, ${misc:Depends}
                Description: this is my short description
                  this is my long description please"""))

    def _get_mock_context(self):
        ctx = Mock()
        ctx.build_dir = BuildDir()
        ctx.znake.deb.package = 'my_package'
        ctx.znake.info.maintainer = 'intercalguy83'
        ctx.znake.info.maintainer_email = 'comefrom@hotmail.com'
        ctx.znake.info.short_description = 'this is my short description'
        ctx.znake.info.long_description = 'this is my long description please'
        return ctx


class TestRenderChangelogFile(unittest.TestCase):

    def test_raises_exception_if_changelog_is_empty(self):
        ctx = Mock()
        ctx.znake.info.changelog = None
        with self.assertRaisesRegex(Exception, 'Changelog must not be empty'):
            _render_changelog_file(ctx)

    def test_render_changelog_with_a_single_entry(self):
        ctx = self._get_mock_context()
        ctx.znake.info.changelog = [
            {
                'version': '0.0.1',
                'changes': [
                    'first release',
                ],
                'date': 'Wed, 14 Feb 2018 12:00:00 +0000'
            }
        ]
        result = _render_changelog_file(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
        my_package (0.0.1) unstable; urgency=low

          * first release

         -- nfsguy87 <permissiondenied@noreply.com>  Wed, 14 Feb 2018 12:00:00 +0000"""))

    def test_render_changelog_with_multiple_enties(self):
        ctx = self._get_mock_context()
        ctx.znake.info.changelog = [
            {
                'version': '0.0.2',
                'changes': [
                    'performance improvements',
                    'fix stale mount issue',
                ],
                'date': 'Thu, 15 Feb 2018 12:00:00 +0000'
            }, {
                'version': '0.0.1',
                'changes': [
                    'first release',
                ],
                'date': 'Wed, 14 Feb 2018 12:00:00 +0000'
            }
        ]
        result = _render_changelog_file(ctx)

        self.assertEqual(
            result,
            dedent(
                """\
        my_package (0.0.2) unstable; urgency=low

          * performance improvements
          * fix stale mount issue

         -- nfsguy87 <permissiondenied@noreply.com>  Thu, 15 Feb 2018 12:00:00 +0000

        my_package (0.0.1) unstable; urgency=low

          * first release

         -- nfsguy87 <permissiondenied@noreply.com>  Wed, 14 Feb 2018 12:00:00 +0000"""))

    def _get_mock_context(self):
        ctx = Mock()
        ctx.build_dir = BuildDir()
        ctx.znake.deb.package = 'my_package'
        ctx.znake.info.maintainer = 'nfsguy87'
        ctx.znake.info.maintainer_email = 'permissiondenied@noreply.com'
        return ctx


class TestRender(unittest.TestCase):

    def test_render_compat_file(self):
        self.assertEqual('9', _render_compat_file(Mock()))

    def test_render_rules_file(self):
        ctx = self._get_mock_config()
        result = _render_rules_file('my_package', ctx)

        dh_virtualenv_command = (
            'dh_virtualenv --python /usr/bin/python3.6 '
            '--upgrade-pip '
            '--preinstall fastentrypoints==0.10 '
            '--builtin-venv '
            '--index-url http://pip.zenterio.lan/simple '
            '--extra-index-url https://pypi.org/simple '
            '--extra-pip-arg --trusted-host '
            '--extra-pip-arg pip.zenterio.lan '
            '--requirements ./build/requirements/requirements.txt')

        expected_result = dedent(
            """\
            #!/usr/bin/make -f

            %:
            \tdh $@ --with python-virtualenv --python /usr/bin/python3.6 --sourcedirectory=my_package

            override_dh_shlibdeps:
            \tdh_shlibdeps --exclude=numpy --exclude=matplotlib --exclude=pandas --exclude=selenium

            override_dh_strip:
            \tdh_strip --no-automatic-dbgsym || dh_strip

            override_dh_virtualenv:
            \t{dh_virtualenv_command}""").format(dh_virtualenv_command=dh_virtualenv_command)
        self.assertEqual(result, expected_result)

    def test_render_links_file(self):
        ctx = self._get_mock_config()
        ctx.znake.deb.links = [
            {
                'target': '/etc/passwd',
                'link': '/var/www/html/passwd'
            }, {
                'target': '/usr/sbin/nologin',
                'link': '/bin/bash'
            }
        ]
        result = _render_links_file(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                /etc/passwd /var/www/html/passwd
                /usr/sbin/nologin /bin/bash
                """))

    def test_render_install_file(self):
        ctx = self._get_mock_config()
        ctx.znake.deb.package = 'zenterio-zpackage'
        ctx.znake.deb.doc = ['document']
        ctx.znake.deb.install = [
            {
                'source': 'motd',
                'target': '/etc'
            },
            {
                'source': 'lynx/lynx.cfg',
                'target': '/etc/lynx'
            },
        ]
        ctx.znake.deb.include = [{'source': 'some/other/dir/motd', 'target': '/etc'}]
        result = _render_install_file(ctx)
        self.assertEqual(
            result,
            dedent(
                """\
                debian/motd /etc
                debian/lynx/lynx.cfg /etc/lynx
                debian/doc /opt/venvs/zenterio-zpackage/
                debian/some/other/dir/motd /etc
                """))

    def test_render_build_debian_package_command(self):
        ctx = self._get_mock_config()
        ctx.znake.deb.package = 'my_package'
        ctx.znake.info.changelog = [
            {
                'version': '0.0.1',
                'changes': [
                    'first release',
                ],
                'date': 'Wed, 14 Feb 2018 12:00:00 +0000'
            }
        ]
        target = {
            'architecture': 'transputer',
            'codename': 'helios',
        }
        with patch.dict(os.environ, {'BUILD_NUMBER': '123'}):
            result = _render_build_debian_package_command(ctx, target)
        expected_result = dedent(
            """\
            cp -R ./build/debian/* ./debian/ &&
            sed -i s/\\(0.0.1\\)/\\(0.0.1+123+helios\\)/g ./debian/changelog &&
            dpkg-buildpackage -us -uc -atransputer &&
            mkdir -p ./build/dist/helios &&
            mv -f ../*.deb ./build/dist/helios/my_package_0.0.1+123+helios_transputer.deb &&
            touch ./build/dist/helios """)
        self.assertEqual(result, expected_result)

    def _get_mock_config(self):
        config = Mock()
        config.build_dir = BuildDir()
        return config


class TestGetNamespace(unittest.TestCase):

    def test_get_namespace_with_no_targets(self):
        config = self._get_mock_config()
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 0)
        self.assertEqual(len(namespace.collections), 1)

    def test_get_namespace_with_single_deb_target(self):
        config = self._get_mock_config()
        config.znake.deb.targets.append(
            {
                'name': 'u14',
                'architecture': 'amd64',
                'image': 'debbuilder.u14',
                'codename': 'trusty'
            })
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 3)
        self.assertEqual(len(namespace.collections), 1)

    def test_get_namespace_with_multiple_deb_targets(self):
        config = self._get_mock_config()
        config.znake.deb.targets.append(
            {
                'name': 'u14',
                'architecture': 'amd64',
                'image': 'debbuilder.u14',
                'codename': 'trusty'
            })
        config.znake.deb.targets.append(
            {
                'name': 'u16',
                'architecture': 'amd64',
                'image': 'debbuilder.u16',
                'codename': 'xenial',
            })
        namespace = get_namespace(config)
        self.assertEqual(len(namespace.tasks), 4)
        self.assertEqual(len(namespace.collections), 1)

    def _get_mock_config(self):
        config = Mock()
        config.znake.deb.package = 'my_package'
        config.znake.deb.targets = []
        return config
