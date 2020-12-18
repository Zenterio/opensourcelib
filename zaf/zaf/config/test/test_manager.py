import unittest

from ..manager import ConfigManager, InvalidReference
from ..options import ConfigOptionId


class TestGetSetConfig(unittest.TestCase):

    def setUp(self):
        self.config = ConfigManager()

    def test_get_returns_value_when_config_has_value(self):
        self.config.set(option1, 'value')
        self.assertEqual(self.config.get(option1), 'value')

    def test_get_returns_option_id_default_when_config_does_not_have_value(self):
        self.assertEqual(self.config.get(option1), 'default1')

    def test_get_returns_default_when_config_does_not_have_value_and_default_is_specified(self):
        self.assertEqual(self.config.get(option1, 'default'), 'default')

    def test_raw_get_returns_default_when_config_does_not_have_value_and_default_is_specified(self):
        self.assertEqual(self.config._raw_get('1', 'default'), 'default')

    def test_get_returns_value_from_additional_config_with_higher_priority_than_config(self):
        self.config.set(option1, 'value')
        self.assertEqual(self.config.get(option1, additional_options={'1': 'value2'}), 'value2')

    def test_get_returns_none_if_no_default_value_is_found(self):
        self.assertIsNone(self.config.get(option2))

    def test_set_and_get_with_entity(self):
        self.config.set_default_values([entity, dependent])
        self.config.set(dependent, 'changed', entity='entity2')
        self.assertEqual(self.config.get(dependent, entity='entity1'), 'dependent')
        self.assertEqual(self.config.get(dependent, entity='entity2'), 'changed')

    def test_get_on_dependent_option_id_without_entity_raises_exception(self):
        self.config.set_default_values([entity, dependent])
        self.assertRaises(ValueError, self.config.get, dependent)

    def test_get_transforms_results_before_returning(self):
        self.config.set(transform, 1, priority=1)
        self.assertEqual(self.config.get(transform), 2)

    def test_set_overwrites_config_value_only_if_priority_is_higher(self):
        self.config.set(option1, 'value', priority=1)
        self.assertEqual(self.config.get(option1), 'value')
        self.config.set(option1, 'value2', priority=1)
        self.assertEqual(self.config.get(option1), 'value')
        self.config.set(option1, 'value3', priority=2)
        self.assertEqual(self.config.get(option1), 'value3')
        self.config.set(option1, 'value4', priority=1)
        self.assertEqual(self.config.get(option1), 'value3')

    def test_get_multiple_combines_values_with_highest_priority_and_lowest_load_order_values_last(
            self):
        self.config.set(multiple, ['a', 'b'], priority=2)
        self.assertEqual(self.config.get(multiple), ('a', 'b'))
        self.config.set(multiple, ['c'], priority=2)
        self.assertEqual(self.config.get(multiple), ('a', 'b', 'c'))
        self.config.set(multiple, ['d'], priority=3)
        self.assertEqual(self.config.get(multiple), ('d', 'a', 'b', 'c'))
        self.config.set(multiple, ['e'], priority=1)
        self.assertEqual(self.config.get(multiple), ('d', 'a', 'b', 'c', 'e'))

    def test_get_multiple_filters_duplicates_when_coming_from_different_sources(self):
        self.config.set(multiple, ['a', 'b'], priority=1)
        self.assertEqual(self.config.get(multiple), ('a', 'b'))
        self.config.set(multiple, ['b'], priority=1)
        self.assertEqual(self.config.get(multiple), ('a', 'b'))
        self.config.set(multiple, ['a'], priority=1)
        self.assertEqual(self.config.get(multiple), ('a', 'b'))
        self.config.set(multiple, ['b'], priority=2)
        self.assertEqual(self.config.get(multiple), ('b', 'a'))

    def test_get_multiple_keeps_duplicates_when_coming_from_same_source(self):
        self.config.set(multiple, ['a', 'a', 'b'], priority=2)
        self.assertEqual(self.config.get(multiple), ('a', 'a', 'b'))

    def test_get_multiple_keeps_duplicates_only_from_highest_priorty_source(self):
        self.config.set(multiple, ['a', 'a', 'b'], priority=2)
        self.assertEqual(self.config.get(multiple), ('a', 'a', 'b'))
        self.config.set(multiple, ['a', 'b', 'b'], priority=1)
        self.assertEqual(self.config.get(multiple), ('a', 'a', 'b'))

    def test_get_multiple_includes_default_values(self):
        self.config.set(multiple_with_defaults, ['a', 'b'], priority=1)
        self.assertEqual(
            self.config.get(multiple_with_defaults), ('a', 'b', 'default1', 'default2'))


class ExpandValuesTest(unittest.TestCase):

    def setUp(self):
        self.config = ConfigManager()

    def test_get_value_with_reference(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/value2')
        self.assertEqual(self.config.get(option2), 'value1/value2')

    def test_get_value_with_reference_to_no_string_value_converts_value_to_string(self):
        self.config.set(option1, '1')
        self.config.set(option2, '${1}/value2')
        self.assertEqual(self.config.get(option2), '1/value2')

    def test_get_value_with_duplicate_references(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/${1}/value2')
        self.assertEqual(self.config.get(option2), 'value1/value1/value2')

    def test_get_value_with_transient_references(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/value2')
        self.config.set(option3, '${2}/value3')
        self.assertEqual(self.config.get(option3), 'value1/value2/value3')

    def test_get_multiple_value_with_reference(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/value2')
        self.config.set(option3, '${2}/value3')
        self.config.set(multiple, ['${1}', '${2}', '${3}'])
        self.assertCountEqual(
            self.config.get(multiple), ['value1', 'value1/value2', 'value1/value2/value3'])

    def test_raw_get_value_with_reference(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/value2')
        self.assertEqual(self.config._raw_get('2'), 'value1/value2')

    def test_raw_get_value_with_duplicate_references(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/${1}/value2')
        self.assertEqual(self.config._raw_get('2'), 'value1/value1/value2')

    def test_raw_get_value_with_transient_references(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/value2')
        self.config.set(option3, '${2}/value3')
        self.assertEqual(self.config._raw_get('3'), 'value1/value2/value3')

    def test_raw_get_multiple_value_with_reference(self):
        self.config.set(option1, 'value1')
        self.config.set(option2, '${1}/value2')
        self.config.set(option3, '${2}/value3')
        self.config.set(multiple, ['${1}', '${2}', '${3}'])
        self.assertCountEqual(
            self.config._raw_get('multiple'), ['value1', 'value1/value2', 'value1/value2/value3'])

    def test_expand_raises_exception_if_referenced_value_not_in_config(self):
        self.config.set(option2, '${1}/value2')
        self.assertRaises(InvalidReference, self.config.get, option2)


class TestSetDefaultValues(unittest.TestCase):

    def setUp(self):
        self.config = ConfigManager()

    def test_set_default_values_deals_with_entity_options_first(self):
        self.config.set_default_values([dependent, entity])
        self.assertEqual(self.config.get(dependent, entity='entity1'), 'dependent')

    def test_set_default_values_stores_the_default_value_from_the_option_id(self):
        self.config.set_default_values([option1])
        self.assertEqual(self.config.get(option1), 'default1')

    def test_set_default_values_does_not_store_values_that_does_not_have_defaults(self):
        self.config.set_default_values([option2])
        self.assertNotIn(self.config._option_key(option2), self.config._config)

    def test_get_with_default_returns_specified_default_when_key_does_not_exist_in_config(self):
        self.config.set_default_values([option2])
        self.assertEqual(self.config.get(option2, default='mydefault'), 'mydefault')


class TestUpdateConfig(unittest.TestCase):

    def setUp(self):
        self.config = ConfigManager()

    def test_update_config_writes_raw_values(self):
        self.config.update_config({'entity1.dependent': 'value'}, priority=2, source='unittest')

        self.assertEqual(self.config.get(dependent, entity='entity1'), 'value')
        self.assertEqual(self.config.get(dependent, entity='entity2'), 'dependent')


class TestFilterConfig(unittest.TestCase):

    def setUp(self):
        self.config = ConfigManager()

    def test_raises_key_error_on_missing_option_id(self):
        self.config.set_default_values([option1])
        filtered_config = self.config.filter_config([option1])
        with self.assertRaises(KeyError):
            filtered_config.get(option2)

    def test_filter_config_on_simple_value(self):
        self.config.set_default_values([option1, option2, entity, dependent, transform])
        filtered_config = self.config.filter_config([option1])
        self.assertEqual(filtered_config.get(option1), 'default1')

    def test_filter_config_on_transformed_value(self):
        self.config.set_default_values([option1, option2, entity, dependent, transform])
        filtered_config = self.config.filter_config([transform])
        self.assertEqual(filtered_config.get(transform), 2)

    def test_filter_config_on_dependent_on_entity_filters_out_only_the_value_for_the_entity(self):
        self.config.set_default_values([option1, option2, entity, dependent, transform])
        filtered_config = self.config.filter_config(
            [dependent], entity_option=entity, entity='entity1')
        self.assertEqual(filtered_config.get(dependent), 'dependent')


option1 = ConfigOptionId('1', 'description', default='default1')
option2 = ConfigOptionId('2', 'description')
option3 = ConfigOptionId('3', 'description')
entity = ConfigOptionId(
    'entity', 'description', default=['entity1', 'entity2'], entity=True, multiple=True)
entity2 = ConfigOptionId(
    'entity', 'description', default=['entity1', 'entity2'], entity=True, multiple=True)
dependent = ConfigOptionId('dependent', 'description', at=entity, default='dependent')
dependent2 = ConfigOptionId('dependent', 'description', at=entity2, default='dependent')
transform = ConfigOptionId(
    'transform', 'description', option_type=int, default=1, transform=lambda x: x + 1)
multiple = ConfigOptionId('multiple', 'description', multiple=True)
multiple_with_defaults = ConfigOptionId(
    'multiple', 'description', multiple=True, default=['default1', 'default2'])
