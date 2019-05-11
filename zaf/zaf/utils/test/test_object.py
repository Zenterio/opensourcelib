from unittest import TestCase

from ..object import TypeComparator


class TestTypeComparator(TestCase):

    def test_type_equality(self):

        class A(object):
            pass

        self.assertEqual(TypeComparator(A), A())

    def test_type_inequality(self):

        class A(object):
            pass

        class B(object):
            pass

        self.assertNotEqual(TypeComparator(A), B())
