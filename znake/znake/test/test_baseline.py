import unittest
from unittest.mock import Mock

from znake.baseline import get_namespace


class TestBaseline(unittest.TestCase):

    def test_get_namespace(self):
        config = Mock()
        config.znake.baseline = [{'source': 's', 'target': 't'}]
        namespace = get_namespace(config)
        assert len(namespace.tasks) == 2
