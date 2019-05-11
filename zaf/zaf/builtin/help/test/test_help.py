import unittest
from unittest.mock import patch

from ..help import disambiguate_name, get_doc_root, get_html_page_type


class TestHelp(unittest.TestCase):

    def test_disambiguate_guides(self):
        for dg in ['dg', 'dev-guide', 'dev_guide']:
            self.assertEqual(disambiguate_name(dg), 'dev-guide')

        for ug in ['ug', 'user-guide', 'user_guide']:
            self.assertEqual(disambiguate_name(ug), 'user-guide')

    def test_disambiguate_name_returns_name_if_not_guide(self):
        self.assertEqual(disambiguate_name('not guide'), 'not guide')

    def test_html_page_type_mapping(self):
        self.assertEqual(get_html_page_type(True, False, False, False), 'guide')
        self.assertEqual(get_html_page_type(False, True, False, False), 'command')
        self.assertEqual(get_html_page_type(False, False, True, False), 'component')
        self.assertEqual(get_html_page_type(False, False, False, True), 'extension')

    def test_get_doc_root_for_installed_deb_package_for_zapplication(self):
        with patch('inspect.getfile', return_value='/opt/venvs/zenterio-zaf/lib/...'):
            self.assertEqual(get_doc_root('zaf', 'zaf'), '/opt/venvs/zenterio-zaf/doc')

    def test_get_doc_root_for_local_development_for_zapplication(self):
        with patch('inspect.getfile', return_value='/path/to/zaf/zaf/__init__.py'):
            self.assertEqual(get_doc_root('zaf', 'zaf'), '/path/to/zaf/doc/build')

    def test_get_doc_root_for_installed_deb_package(self):
        with patch('inspect.getfile', return_value='/opt/venvs/zenterio-zk2/lib/...'),\
                patch('importlib.import_module'):
            self.assertEqual(get_doc_root('k2', 'k2'), '/opt/venvs/zenterio-zk2/doc')

    def test_get_new_style_doc_root_for_local_development(self):
        with patch('inspect.getfile', return_value='/path/to/k2/k2/__init__.py'), \
                patch('importlib.import_module'), \
                patch('zaf.builtin.help.help.exists', return_value=True):
            self.assertEqual(get_doc_root('k2', 'k2'), '/path/to/k2/build/doc')

    def test_get_old_style_doc_root_for_local_development(self):
        with patch('inspect.getfile', return_value='/path/to/k2/k2/__init__.py'), \
                patch('importlib.import_module'), \
                patch('zaf.builtin.help.help.exists', return_value=False):
            self.assertEqual(get_doc_root('k2', 'k2'), '/path/to/k2/doc/build')
