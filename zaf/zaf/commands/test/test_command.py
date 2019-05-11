import unittest

from zaf.application import ApplicationContext
from zaf.commands.command import CommandId


class TestCommand(unittest.TestCase):

    def test_application_contexts_not_given_gives_empty_tuple(self):
        self.assertEqual(CommandId('command', 'desc', None, []).application_contexts, ())

    def test_single_application_context_is_wrapped_in_tuple(self):
        self.assertEqual(
            CommandId(
                'command', 'desc', None, [],
                application_contexts=ApplicationContext.EXTENDABLE).application_contexts,
            (ApplicationContext.EXTENDABLE, ))

    def test_multiple_application_contexts_is_converted_to_tuple(self):
        self.assertEqual(
            CommandId(
                'command',
                'desc',
                None, [],
                application_contexts=[ApplicationContext.INTERNAL,
                                      ApplicationContext.EXTENDABLE]).application_contexts,
            (ApplicationContext.INTERNAL, ApplicationContext.EXTENDABLE))

    def test_not_applicable_for_application_context_that_is_not_specified(self):
        command = CommandId(
            'command', 'desc', None, [], application_contexts=ApplicationContext.EXTENDABLE)
        self.assertFalse(command.is_applicable_for_application(ApplicationContext.STANDALONE))

    def test_applicable_for_application_context_when_none_arg_specified(self):
        command = CommandId('command', 'desc', None, [])
        self.assertTrue(command.is_applicable_for_application(ApplicationContext.STANDALONE))

    def test_applicable_for_application_context_when_context_is_specified(self):
        command = CommandId(
            'command', 'desc', None, [], application_contexts=ApplicationContext.STANDALONE)
        self.assertTrue(command.is_applicable_for_application(ApplicationContext.STANDALONE))
