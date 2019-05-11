from collections import OrderedDict
from unittest import TestCase

from ..data import DataDefinition


class TestDataDefinition(TestCase):

    def test_members_are_defined_using_a_list_of_strings(self):
        d = DataDefinition(['a', 'b'])
        assert d.a is None
        assert d.b is None
        with self.assertRaises(AttributeError):
            d.c

    def test_when_members_are_defined_using_a_list_of_strings_default_value_can_be_given(self):
        value = object()
        d = DataDefinition(['a'], default=value)
        assert d.a is value

    def test_members_can_be_an_ordereddict_where_keys_are_members_and_values_initialized_values(
            self):
        d = DataDefinition(OrderedDict([('a', 1), ('b', 2)]))
        self.assertEqual(d.a, 1)
        self.assertEqual(d.b, 2)

    def test_raises_typeerror_for_invalid_type_on_members_argument(self):
        with self.assertRaises(TypeError):
            DataDefinition('a')

    def test_data_is_a_read_only_property_giving_ordereddict_of_members_and_values(self):
        d = DataDefinition(['a'], 1)
        self.assertEqual(d.get_data()['a'], 1)

    def test_a_member_can_not_be__attributes_due_to_name_collision(self):
        with self.assertRaises(AttributeError):
            DataDefinition(['_attributes'])
        with self.assertRaises(AttributeError):
            DataDefinition(OrderedDict([('_attributes', 1)]))

    def test_internal_data_is_not_in_it_self(self):
        d = DataDefinition(['a'])
        data = d.get_data()
        assert '_attributes' not in data.keys()
        assert d._attributes not in data.values()
