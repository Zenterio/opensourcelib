from unittest import TestCase

from pypsi.namespace import Namespace

from ..addon import _merge_namespaces


class TestMergeNamespaces(TestCase):

    def test_merge_single_namespace(self):
        namespace = _merge_namespaces(Namespace(key='value'))
        assert namespace.key == 'value'

    def test_merge_multiple_namespaces(self):
        namespace = _merge_namespaces(Namespace(key='value'), Namespace(other_key='other_value'))
        assert namespace.key == 'value'
        assert namespace.other_key == 'other_value'

    def test_raises_value_error_on_duplicate_key(self):
        with self.assertRaises(ValueError):
            _merge_namespaces(Namespace(key='value'), Namespace(key='value'))
