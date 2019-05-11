import unittest

from ..extension import AbstractExtension, CommandExtension, is_concrete_extension


@CommandExtension(name='test_command_extension')
class MyConcreteExtension():
    pass


class TestIsExtension(unittest.TestCase):

    def test_true_for_concrete_extenion(self):
        self.assertTrue(is_concrete_extension(MyConcreteExtension))

    def test_false_for_abstract_extension(self):
        self.assertFalse(is_concrete_extension(AbstractExtension))

    def test_false_for_non_extension_object(self):
        self.assertFalse(is_concrete_extension(object))
