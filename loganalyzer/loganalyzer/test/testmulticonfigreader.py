"""Tests multiconfigreader module."""

import unittest
from unittest.mock import Mock

from ..config import dict_to_raw_config
from ..multiconfigreader import MultiConfigReader


class TestMultiConfigReader(unittest.TestCase):

    def _get_mock_config_reader(self, dictdata):
        cfg = dict_to_raw_config(dictdata)
        reader = Mock()
        reader.get_config.return_value = cfg
        return reader

    def test_config_from_multiple_sources_are_merged(self):
        reader1 = self._get_mock_config_reader({'a': 1})
        reader2 = self._get_mock_config_reader({'b': 2})
        mreader = MultiConfigReader(reader1, reader2)
        cfg = mreader.get_config()
        self.assertEqual(1, cfg.a)
        self.assertEqual(2, cfg.b)

    def test_config_sub_values_are_overwritten(self):
        reader1 = self._get_mock_config_reader({'d': {'a': 1}})
        reader2 = self._get_mock_config_reader({'d': {'b': 2}})
        mreader = MultiConfigReader(reader1, reader2)
        cfg = mreader.get_config()
        self.assertEqual(1, cfg.d.a)
        # due to reader1 having higher priority
        with self.assertRaises(Exception):
            cfg.d.b

    def test_first_reader_has_highest_priority(self):
        reader1 = self._get_mock_config_reader({'a': 1})
        reader2 = self._get_mock_config_reader({'a': 2})
        mreader = MultiConfigReader(reader1, reader2)
        cfg = mreader.get_config()
        self.assertEqual(1, cfg.a)
