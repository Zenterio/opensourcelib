import re
from unittest import TestCase

from voluptuous import MultipleInvalid

from debpacker.metapackage.configreader import PackageConfigParser


class TestPackageConfigParser(TestCase):

    def setUp(self):
        self.parser = PackageConfigParser()

    def create_document(
            self,
            name='package_name',
            version='1.5.1',
            long_desc='This is the long description',
            short_desc='This is the short description',
            **kwargs):
        document = """
        name: {name}
        version: {version}
        long_description: {long_desc}
        short_description: {short_desc}
        dependencies:
            - dep1
            - dep2
        """.format(
            name=name, version=version, long_desc=long_desc, short_desc=short_desc)
        for key, value in kwargs.items():
            document += """
        {key}: {value}
            """.format(key=key, value=value)
        return document

    def test_parse_config_valid(self):
        document = self.create_document()
        config = self.parser.parse(document)
        self.assertEqual(config.name, 'package_name')
        self.assertEqual(config.version, '1.5.1')
        self.assertEqual(config.long_description, 'This is the long description')
        self.assertEqual(config.short_description, 'This is the short description')
        self.assertEqual(config.dependencies, ['dep1', 'dep2'])
        self.assertEqual(config.architecture, 'all')
        self.assertEqual(config.distributions, [None])

    def test_parse_config_with_valid_architecture(self):
        document = self.create_document(architecture='amd64')
        config = self.parser.parse(document)
        self.assertEqual(config.architecture, 'amd64')

    def test_parse_config_with_invalid_architecture(self):
        document = self.create_document(architecture='x86_64')
        try:
            self.parser.parse(document)
        except MultipleInvalid as e:
            self.assertEqual(
                "not a valid value for dictionary value @ data['architecture']", str(e))

    def test_parse_config_with_valid_distribution(self):
        document = self.create_document(distributions=['xenial'])
        config = self.parser.parse(document)
        self.assertEqual(config.distributions, ['xenial'])

    def test_parse_config_with_invalid_distribution(self):
        document = self.create_document(distributions=['utopic'])
        try:
            self.parser.parse(document)
        except MultipleInvalid as e:
            self.assertEqual("not a valid value @ data['distributions'][0]", str(e))

    def test_parse_config_with_unexpected_key(self):
        document = self.create_document(unexpected_key='unexpected value')
        try:
            self.parser.parse(document)
        except MultipleInvalid as e:
            self.assertIn("extra keys not allowed @ data['unexpected_key']", str(e))

    def test_parse_config_with_missing_key(self):
        document = self.create_document(name='name')
        document = re.sub(r'\s+name: name', '', document)
        try:
            self.parser.parse(document)
        except MultipleInvalid as e:
            self.assertIn("required key not provided @ data['name']", str(e))

    def test_parse_config_with_syntax_error(self):
        document = """
        config_format = simple config
        """
        try:
            self.parser.parse(document)
        except MultipleInvalid as e:
            self.assertIn('expected a dictionary', str(e))
