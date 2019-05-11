from unittest import TestCase

from ..interpreter import find_where_instance_is_defined

OBJECT = object()

ANOTHER_OBJECT = object()
REFERENCE_TO_ANOTHER_OBJECT = ANOTHER_OBJECT


class TestFindWhereInstanceIsDefined(TestCase):

    def test_instance_can_not_be_found(self):
        assert len(find_where_instance_is_defined(object())) == 0

    def test_instance_can_be_found(self):
        locations = find_where_instance_is_defined(OBJECT)
        assert len(locations) == 1
        assert locations[0].module == TestFindWhereInstanceIsDefined.__module__
        assert locations[0].name == 'OBJECT'

    def test_multiple_instances_can_be_found(self):
        locations = sorted(find_where_instance_is_defined(ANOTHER_OBJECT))
        assert len(locations) == 2
        assert locations[0].module == TestFindWhereInstanceIsDefined.__module__
        assert locations[0].name == 'ANOTHER_OBJECT'
        assert locations[1].module == TestFindWhereInstanceIsDefined.__module__
        assert locations[1].name == 'REFERENCE_TO_ANOTHER_OBJECT'
