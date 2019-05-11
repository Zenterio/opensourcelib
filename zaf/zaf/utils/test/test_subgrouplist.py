import unittest

from ..subgrouplist import eval_subgroup_list, is_subgroup


class TestIsSubGroupInList(unittest.TestCase):

    def test_a_tuple_is_a_subgroup(self):
        self.assertTrue(is_subgroup(('a', )))


class TestEvalSubgroupList(unittest.TestCase):

    @staticmethod
    def _eval(subgrouped_list):

        def is_t(x):
            if x == 'T':
                return True
            return False

        return eval_subgroup_list(is_t, subgrouped_list)

    def test_empty_list_is_true(self):
        self.assertTrue(self._eval([]))

    def test_items_are_anded(self):
        """List items are and:ed."""
        self.assertTrue(self._eval(['T', 'T']))
        self.assertFalse(self._eval(['T', 'F']))

    def test_subgroup_is_ored(self):
        """Items in a subgroup are or:ed."""
        self.assertTrue(self._eval([('T', 'F')]))
        self.assertFalse(self._eval(['F', 'F']))

    def test_mix(self):
        """Can handle a mix of items and subgroups."""
        self.assertTrue(self._eval(['T', ('F', 'T'), 'T', ('T', )]))
        self.assertFalse(self._eval(['T', ('F', 'F'), 'T']))
        self.assertFalse(self._eval(['T', ('T', 'F'), 'F']))
