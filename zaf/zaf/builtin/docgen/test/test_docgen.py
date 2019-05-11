import unittest
from unittest.mock import Mock

from zaf.application.metadata import MetadataFilter, ZafMetadata
from zaf.application.test.utils import Ext1, Ext2, all_components, all_extensions
from zaf.builtin.docgen.docgen import DocFilter

from ..baselines import command, command_list, component, component_list, config_option_id_list, \
    endpoint_list, extension, extension_list, message_list
from ..template import render_sphinx_template


class TestDocGen(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        extension_manager.command_extensions.side_effect = command_extensions
        extension_manager.framework_extensions.return_value = [Ext1]

        self.docgen_filter = DocFilter(True, True, True)
        self.metadata = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', extension_manager, MetadataFilter())

    def test_generate_extension_rst(self):
        output = render_sphinx_template(
            'extension.rst',
            extension=self.metadata.extension_with_name('ext1'),
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, extension.expected_rst_output)

    def test_generate_command_rst(self):
        output = render_sphinx_template(
            'command.rst',
            command=self.metadata.commands[1],
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, command.expected_rst_output)

    def test_generate_components_rst(self):
        output = render_sphinx_template(
            'component.rst',
            component=self.metadata.components[0],
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, component.expected_rst_output)

    def test_generate_extension_list_rst(self):
        output = render_sphinx_template(
            'extension_list.rst',
            extensions=self.metadata.extensions,
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, extension_list.expected_rst_output)

    def test_generate_command_list_rst(self):
        output = render_sphinx_template(
            'command_list.rst',
            commands=self.metadata.commands,
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, command_list.expected_rst_output)

    def test_generate_components_list_rst(self):
        output = render_sphinx_template(
            'component_list.rst',
            components=self.metadata.components,
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, component_list.expected_rst_output)

    def test_generate_config_option_ids_list_rst(self):
        output = render_sphinx_template(
            'config_option_id_list.rst',
            config_option_ids=self.metadata.config_option_ids,
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, config_option_id_list.expected_rst_output)

    def test_generate_endpoints_list_rst(self):
        output = render_sphinx_template(
            'endpoint_list.rst',
            endpoints=self.metadata.endpoints,
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, endpoint_list.expected_rst_output)

    def test_generate_messages_list_rst(self):
        output = render_sphinx_template(
            'message_list.rst',
            messages=self.metadata.messages,
            metadata=self.metadata,
            filter=self.docgen_filter)
        self.assertEqual(output, message_list.expected_rst_output)
