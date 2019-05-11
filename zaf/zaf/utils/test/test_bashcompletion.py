import os
from unittest import TestCase
from unittest.mock import patch

from ..bashcompletion import is_bash_completion


class TestBashCompletion(TestCase):

    def test_bash_completion_is_not_set_during_normal_runtime(self):
        self.assertFalse(is_bash_completion())

    def test_bash_completion_is_active_if_comp_words_variable_is_set(self):
        with patch.dict('os.environ', {'COMP_WORDS': 'value'}):
            self.assertTrue(is_bash_completion())

    def test_bash_completion_is_inactive_if_comp_words_variable_is_not_set(self):
        with patch.dict('os.environ', {'COMP_WORDS': 'value'}):
            del os.environ['COMP_WORDS']
            self.assertFalse(is_bash_completion())
