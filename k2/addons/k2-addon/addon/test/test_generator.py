from unittest import TestCase

from pypsi.namespace import Namespace

from ..generator import generate_command_extension_entrypoint, \
    generate_framework_extension_entrypoint, generate_initial_unittest, generate_setup_py_file

MOCK_COMMAND = object()


class TestGenerate(TestCase):

    def setUp(self):
        self.addon_info = Namespace(
            package_name='mypackagename',
            version='1.2.3',
            description='this is my one-line summary',
            long_description='this is my long description',
            maintainer='I Am Maintainer',
            maintainer_email='i.am.maintainer@zenterio.com',
            install_requires='some_package==1.2.3',
            entrypoint='ThisIsMyEntryPoint',
            command=MOCK_COMMAND,
        )

    def test_setup_py_package_name(self):
        line = "name='{name}'".format(name=self.addon_info.package_name)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_version(self):
        line = "version='{version}' + os.getenv('BUILD_NUMBER', '0')".format(
            version=self.addon_info.version)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_description(self):
        line = "description='{description}'".format(description=self.addon_info.description)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_long_description(self):
        line = "'{long_description}'".format(long_description=self.addon_info.long_description)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_maintainer(self):
        line = "maintainer='{maintainer}'".format(maintainer=self.addon_info.maintainer)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_maintainer_email(self):
        line = "maintainer_email='{maintainer_email}'".format(
            maintainer_email=self.addon_info.maintainer_email)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_license(self):
        line = "license='© 2018 Zenterio AB All rights reserved'"
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_install_requires(self):
        line = "install_requires=['{package}']".format(package=self.addon_info.install_requires)
        assert line in generate_setup_py_file(self.addon_info)

    def test_setup_py_entry_point(self):
        line = '{package_name} = {package_name}.{package_name}:{entrypoint}'.format(
            package_name=self.addon_info.package_name, entrypoint=self.addon_info.entrypoint)
        assert line in generate_setup_py_file(self.addon_info)

    def test_generate_framework_extension_entrypoint(self):
        assert 'FrameworkExtension' in generate_framework_extension_entrypoint(self.addon_info)

    def test_generate_command_extension_entrypoint(self):
        assert 'CommandExtension' in generate_command_extension_entrypoint(self.addon_info)

    def test_generate_unittest(self):
        assert 'raise NotImplementedError' in generate_initial_unittest(self.addon_info)
