import json
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from compiz.coverity_renderer import CoverityFileRule, CoverityRenderer


class TestFileRuleToRegexConversion(unittest.TestCase):

    def _file_rule_to_regex(self, file_rule):
        return CoverityFileRule('root', None, file_rule, 0).as_regex()

    def test_convert_file_rule_to_regex(self):
        self.assertEqual(self._file_rule_to_regex('*'), r'.*/root/.*')
        self.assertEqual(self._file_rule_to_regex('*.*'), r'.*/root/[^/]*\.[^/]*')
        self.assertEqual(self._file_rule_to_regex('dir/*'), r'.*/root/dir/.*')
        self.assertEqual(self._file_rule_to_regex('dir/*.c'), r'.*/root/dir/[^/]*\.c')
        self.assertEqual(self._file_rule_to_regex('*.filetype'), r'.*/[^/]*\.filetype')

    def test_convert_file_rule_to_regex_expand_dirs_but_not_files(self):
        self.assertEqual(self._file_rule_to_regex('dir/'), r'.*/root/dir/.*')
        self.assertEqual(self._file_rule_to_regex('dir/dir2/'), r'.*/root/dir/dir2/.*')

        with patch('os.path.isdir', return_value=True):
            self.assertEqual(self._file_rule_to_regex('dir'), r'.*/root/dir/.*')
            self.assertEqual(self._file_rule_to_regex('dir/dir2'), r'.*/root/dir/dir2/.*')

        with patch('os.path.isdir', return_value=False):
            self.assertEqual(self._file_rule_to_regex('file'), r'.*/root/file')
            self.assertEqual(self._file_rule_to_regex('dir/file'), r'.*/root/dir/file')


class CoverityComponentFileGeneration(unittest.TestCase):

    def _generate_coverity_components(self, components=()):
        out = StringIO()
        renderer = CoverityRenderer(out, 'path/to/root', 'Name of component list')

        for component in components:
            renderer.renderComponent(component, None, None, None)

        renderer.finalize()
        return json.loads(out.getvalue())

    def _create_component(self, name, files=()):
        component = Mock()
        component.name = name
        component.files = files
        return component

    def test_component_list_name(self):
        file_content = self._generate_coverity_components()
        self.assertEqual(file_content['name'], 'Name of component list')

    def test_default_values(self):
        file_content = self._generate_coverity_components()
        self.assertEqual(len(file_content['components']), 4)
        self.assertEqual(len(file_content['fileRules']), 26)

    def test_components_added_to_components_list(self):
        components = [
            self._create_component('comp1'),
            self._create_component('comp2'),
        ]
        file_content = self._generate_coverity_components(components)
        self.assertEqual([c['name'] for c in file_content['components'][4:]], ['comp1', 'comp2'])

    def test_components_get_default_owner_set_to_none(self):
        components = [
            self._create_component('comp1'),
        ]
        file_content = self._generate_coverity_components(components)
        self.assertIsNone(file_content['components'][4]['defaultOwner'])

    def test_components_get_default_rbac_settings_set_to_empty_list(self):
        components = [
            self._create_component('comp1'),
        ]
        file_content = self._generate_coverity_components(components)
        self.assertEqual(file_content['components'][4]['rbacSettings'], [])

    def test_components_file_rules_extended_after_default_rules(self):
        components = [
            self._create_component('comp1', files=[('dir/', 0), ('dir2/*', 0)]),
        ]
        file_content = self._generate_coverity_components(components)
        self.assertEqual(
            [f['componentName'] for f in file_content['fileRules'][26:]], ['comp1', 'comp1'])

    def test_components_file_rules_sorted_by_prio(self):
        components = [
            self._create_component('comp1', files=[('dir/', 1), ('dir2/*', 0)]),
        ]
        file_content = self._generate_coverity_components(components)
        self.assertEqual(
            [f['pathPattern'] for f in file_content['fileRules'][26:]],
            ['.*/root/dir/.*', '.*/root/dir2/.*'])

    def test_components_file_rules_sorted_by_rule_length_if_same_prio(self):
        components = [
            self._create_component('comp1', files=[('dir/', 0), ('dir2/*', 0)]),
        ]
        file_content = self._generate_coverity_components(components)
        self.assertEqual(
            [f['pathPattern'] for f in file_content['fileRules'][26:]],
            ['.*/root/dir2/.*', '.*/root/dir/.*'])
