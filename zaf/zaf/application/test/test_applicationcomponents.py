import unittest

from ..application import Application, ApplicationConfiguration, ApplicationContext


class ApplicationComponentsTest(unittest.TestCase):

    def get_app(self):
        app = Application(
            ApplicationConfiguration('test', application_context=ApplicationContext.EXTENDABLE))
        return app

    def assert_is_component(self, component_name):
        app = self.get_app()
        self.assertIn(component_name, app.component_manager.COMPONENT_REGISTRY.keys())

    def test_messagebus_is_a_component(self):
        self.assert_is_component('MessageBus')

    def test_component_manager_is_a_component(self):
        self.assert_is_component('ComponentManager')

    def test_component_factory_is_a_component(self):
        self.assert_is_component('ComponentFactory')

    def test_config_manager_is_a_component(self):
        self.assert_is_component('Config')

    def test_extension_manager_is_a_component(self):
        self.assert_is_component('ExtensionManager')
