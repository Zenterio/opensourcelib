import unittest
from unittest.mock import patch

from ..decorator import component
from ..manager import ComponentManager, create_entity_map, create_registry


class TestComponentManager(unittest.TestCase):

    @staticmethod
    def get_component_manager():
        return ComponentManager(create_registry(), create_entity_map())

    def test_clear_component_registry(self):
        component_manager = self.get_component_manager()
        component_manager.COMPONENT_REGISTRY['some'] = 'data'
        component_manager.clear_component_registry()
        self.assertEqual(len(component_manager.COMPONENT_REGISTRY), 0)

    def test_log_component_info(self):
        with patch('zaf.component.manager.logger') as mock_logger:
            captured = []

            def capture_log(msg):
                captured.append(msg)

            mock_logger.debug = capture_log
            cm = self.get_component_manager()

            def c():
                pass

            component(name='B')(c, component_manager=cm)
            component(name='A')(c, component_manager=cm)

            cm.log_components_info()
            self.assertEqual(len(captured), 2)
            self.assertEqual(captured[0].name, 'A')
            self.assertEqual(captured[1].name, 'B')
