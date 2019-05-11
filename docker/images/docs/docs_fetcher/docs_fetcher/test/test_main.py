import unittest

from ..__main__ import DocumentationArchive


class TestDocumentationArchive(unittest.TestCase):

    def test_create_from_dict(self):
        my_dict = {
            'module': 'my_module',
            'name': 'my_name',
            'version': 123,
        }
        archive = DocumentationArchive.from_dict(my_dict)
        assert archive.module == 'my_module'
        assert archive.name == 'my_name'
        assert archive.version == 123
        assert archive.path is None
        assert archive.fetched is False

    def test_key(self):
        archive = DocumentationArchive('my_module', 'my_name', 123)
        assert archive.key == ('my_module', 'my_name')
