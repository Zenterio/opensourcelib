from unittest.mock import Mock

from znake.format import get_namespace


def test_get_namespace():
    config = Mock()
    namespace = get_namespace(config)
    assert len(namespace.tasks) == 3
