from unittest import TestCase

from debpacker.common.utils import InvalidPackageNameException, create_deb_package_name, \
    validate_deb_package_name


class TestDebPackageName(TestCase):

    def test_validate_deb_package_name(self):
        test_data = [
            '', 'zenterio-name_with_underscore', 'zenterio-name-with-UpperCase',
            'zenterio-name-with space', 'zenterio-invalid_Package name',
            'zenterio-name-with-non-valid-!'
        ]

        for package_name in test_data:
            expected = 'Package name "{name}" is invalid'.format(name=package_name)
            with self.assertRaisesRegex(InvalidPackageNameException, expected):
                validate_deb_package_name(package_name)

    def test_create_deb_package_name(self):
        test_data = {
            'name': 'zenterio-name',
            'name_with_underscore': 'zenterio-name-with-underscore',
            'name-with-UpperCase': 'zenterio-name-with-uppercase',
            'name with spaces': 'zenterio-name-with-spaces',
            'name_With all': 'zenterio-name-with-all'
        }
        for package_name, expected in test_data.items():
            output = create_deb_package_name(package_name)
            self.assertEqual(output, expected)
            self.assertEqual(validate_deb_package_name(output), True)

    def test_create_deb_package_name_empty(self):
        package_name = ''
        with self.assertRaisesRegex(InvalidPackageNameException,
                                    'Package name "{name}" is invalid'.format(name=package_name)):
            create_deb_package_name('')
