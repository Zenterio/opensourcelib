import unittest
from unittest.mock import Mock

from zaf.config.options import ConfigOptionId
from zaf.utils.subgrouplist import is_subgroup

from ..manager import _is_extension_active


class TestIsExtensionActive(unittest.TestCase):

    def get_mock_extension(self):
        extension = Mock()
        extension.activate_on = []
        extension.deactivate_on = []
        return extension

    def test_config_id_is_not_mistaken_for_subgroup(self):
        my_id = ConfigOptionId('id', 'description')
        self.assertFalse(is_subgroup(my_id))

    def test_empty_lists_gives_active_extension(self):
        extension = self.get_mock_extension()
        self.assertTrue(_is_extension_active({}, extension))

    def test_activate_on_is_grouped_list_of_config_ids(self):
        extension = self.get_mock_extension()
        extension.activate_on = [('a', 'b'), 'c']
        config = {'a': True, 'b': False, 'c': True}
        self.assertTrue(_is_extension_active(config, extension))

    def test_deactivate_is_grouped_list_of_config_ids(self):
        extension = self.get_mock_extension()
        extension.deactivate_on = [('d', 'e'), 'f']
        config = {'d': True, 'e': False, 'f': False}
        self.assertTrue(_is_extension_active(config, extension))

    def test_deactivate_on_has_precedence_over_activate_on(self):
        extension = self.get_mock_extension()
        extension.actiave_on = ['a']
        extension.deactivate_on = ['d']
        config = {'a': True, 'd': True}
        self.assertFalse(_is_extension_active(config, extension))
