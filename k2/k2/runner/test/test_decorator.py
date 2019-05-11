import unittest

from ..decorator import disabled


class TestDisabledDecorator(unittest.TestCase):

    def test_disabled_raises_exception_when_no_message(self):
        with self.assertRaises(TypeError):

            @disabled
            def test_case():
                pass
