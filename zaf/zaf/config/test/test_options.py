import unittest

from zaf.application import ApplicationContext

from ..options import ConfigOption, ConfigOptionId, handle_duplicate_config_options


class TestHandleDuplicateConfigOptions(unittest.TestCase):

    def test_handle_duplicate_config_options(self):
        actual_config_options = handle_duplicate_config_options(
            [
                ConfigOption(option1, required=True),
                ConfigOption(option2, required=False),
                ConfigOption(option1, required=False),
            ])
        self.assertCountEqual(
            actual_config_options,
            [ConfigOption(option1, required=True),
             ConfigOption(option2, required=False)])


class TestIncludeOption(unittest.TestCase):

    def test_include_option_created_for_entity_options(self):
        include = ConfigOptionId('entity1', 'description', entity=True).include
        self.assertIsNotNone(include)
        self.assertEqual(include.name, 'include.files')

    def test_include_option_not_created_for_non_entity_options(self):
        self.assertIsNone(ConfigOptionId('notentity', 'description').include)


class TestApplicationContexts(unittest.TestCase):

    def test_application_contexts_not_given_gives_empty_tuple(self):
        self.assertEqual(ConfigOptionId('opt', 'desc').application_contexts, ())

    def test_single_application_context_is_wrapped_in_tuple(self):
        self.assertEqual(
            ConfigOptionId('opt', 'desc',
                           application_contexts=ApplicationContext.EXTENDABLE).application_contexts,
            (ApplicationContext.EXTENDABLE, ))

    def test_multiple_application_contexts_is_converted_to_tuple(self):
        self.assertEqual(
            ConfigOptionId(
                'opt',
                'desc',
                application_contexts=[ApplicationContext.INTERNAL,
                                      ApplicationContext.EXTENDABLE]).application_contexts,
            (ApplicationContext.INTERNAL, ApplicationContext.EXTENDABLE))

    def test_not_applicable_for_application_context_that_is_not_specified(self):
        command = ConfigOptionId('opt', 'desc', application_contexts=ApplicationContext.EXTENDABLE)
        self.assertFalse(command.is_applicable_for_application(ApplicationContext.STANDALONE))

    def test_applicable_for_application_context_when_none_are_specified(self):
        command = ConfigOptionId('opt', 'desc')
        self.assertTrue(command.is_applicable_for_application(ApplicationContext.STANDALONE))

    def test_applicable_for_application_context_when_context_is_specified(self):
        command = ConfigOptionId('opt', 'desc', application_contexts=ApplicationContext.STANDALONE)
        self.assertTrue(command.is_applicable_for_application(ApplicationContext.STANDALONE))


option1 = ConfigOptionId('1', 'description')
option2 = ConfigOptionId('2', 'description')
