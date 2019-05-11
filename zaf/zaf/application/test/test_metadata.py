import unittest
from unittest.mock import ANY, Mock

from zaf.application.context import ApplicationContext
from zaf.application.metadata import MetadataFilter, ZafMetadata
from zaf.application.test.utils import Ext3, all_contexts, c3, extendable_context

from .utils import Ext1, Ext2, all_components, all_extensions, bools, c1, c2, comp1, comp2, e1, \
    e2, entity, m1, m2, m3, path


class ZafMetadataTest(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_metadata_extension_classes(self):
        ext_classes = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extension_classes
        self.assertEqual(ext_classes[0]._extension_class, Ext1)
        self.assertEqual(ext_classes[1]._extension_class, Ext2)

    def test_metadata_get_extensions(self):
        self.assertEqual(
            ZafMetadata(
                all_extensions, [], Mock(), 'zaf', self.extension_manager,
                self.metadata_filter).extension_names, ['ext1', 'ext2', 'ext3'])

    def test_metadata_commands(self):
        commands = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[0]._command.name, 'zaf')
        self.assertEqual(commands[1]._command, c1)
        self.assertEqual(commands[2]._command, c2)

    def test_metadata_config_option_ids(self):
        config_option_ids = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).config_option_ids
        self.assertEqual(config_option_ids[0]._option_id, all_contexts)
        self.assertEqual(config_option_ids[1]._option_id, bools)
        self.assertEqual(config_option_ids[2]._option_id, extendable_context)
        self.assertEqual(config_option_ids[3]._option_id, path)
        self.assertEqual(config_option_ids[4]._option_id, entity)

    def test_metadata_components(self):
        components = ZafMetadata(
            [], all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(components[0]._component_info, comp1)
        self.assertEqual(components[1]._component_info, comp2)

    def test_metadata_endpoints(self):
        endpoints = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).endpoints
        self.assertEqual(endpoints[0]._endpoint_id, e1)
        self.assertEqual(endpoints[0]._messages, [m1, m3])
        self.assertEqual(endpoints[1]._endpoint_id, e2)
        self.assertEqual(endpoints[1]._messages, [m2, m3])

    def test_metadata_messages(self):
        messages = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).messages
        self.assertEqual(messages[0]._message_id, m1)
        self.assertEqual(messages[0]._endpoints, [e1])
        self.assertEqual(messages[1]._message_id, m2)
        self.assertEqual(messages[1]._endpoints, [e2])
        self.assertEqual(messages[2]._message_id, m3)
        self.assertEqual(messages[2]._endpoints, [e1, e2])

    def test_metadata_extensions(self):
        extensions = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].name, 'ext1')
        self.assertEqual(extensions[0].groups, ['group'])
        self.assertEqual(extensions[0].extension_classes[0]._extension_class, Ext1)
        self.assertEqual(extensions[1].name, 'ext2')
        self.assertEqual(extensions[1].groups, ['group'])
        self.assertEqual(extensions[1].extension_classes[0]._extension_class, Ext2)

    def test_extension_with_name(self):
        metadata = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager, self.metadata_filter)
        self.assertEqual(metadata.extension_with_name('ext1').name, 'ext1')
        self.assertEqual(metadata.extension_with_name('ext2').name, 'ext2')

    def test_extensions_with_group(self):
        metadata = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager, self.metadata_filter)
        extensions = metadata.extensions_with_group('group')
        self.assertEqual(extensions[0].name, 'ext1')
        self.assertEqual(extensions[1].name, 'ext2')

        self.assertEqual(metadata.extensions_with_group('invalid group'), [])


class TestExtensionMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_extension_description(self):
        extensions = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(
            extensions[0].description, 'module description.\n\nextended module description')

    def test_extension_short_description(self):
        extensions = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].short_description, 'module description.')

    def test_extension_extension_classes(self):
        extensions = ZafMetadata(
            all_extensions, [], Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].extension_classes, [Ext1])
        self.assertEqual(extensions[1].extension_classes, [Ext2])
        self.assertEqual(extensions[2].extension_classes, [Ext3])

    def test_extension_components(self):
        extensions = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].components[0]._component_info, comp1)
        self.assertEqual(extensions[1].components[0]._component_info, comp2)

    def test_extension_commands(self):
        extensions = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].commands[0]._command, c1)
        self.assertEqual(extensions[0].commands[1]._command, c2)
        self.assertEqual(extensions[1].commands, [])

    def test_extension_config_option_ids(self):
        extensions = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].config_option_ids[0]._option_id, path)
        self.assertEqual(extensions[1].config_option_ids[0]._option_id, bools)
        self.assertEqual(extensions[1].config_option_ids[1]._option_id, entity)

    def test_extension_endpoints(self):
        extensions = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].endpoints[0]._endpoint_id, e1)
        self.assertEqual(extensions[1].endpoints[0]._endpoint_id, e2)

    def test_extension_messages(self):
        extensions = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].messages[0]._message_id, m1)
        self.assertEqual(extensions[0].messages[1]._message_id, m3)
        self.assertEqual(extensions[1].messages[0]._message_id, m2)
        self.assertEqual(extensions[1].messages[1]._message_id, m3)

    def test_extension_group_members(self):
        extensions = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extensions
        self.assertEqual(extensions[0].group_members('group'), ['ext2'])
        self.assertEqual(extensions[1].group_members('group'), ['ext1'])


class TestExtensionClassMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_extension_class_class_name(self):
        extension_classes = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extension_classes
        self.assertEqual(extension_classes[0].class_name, 'Ext1')
        self.assertEqual(extension_classes[1].class_name, 'Ext2')

    def test_extension_class_module(self):
        extension_classes = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extension_classes
        self.assertEqual(extension_classes[0].module.__name__, 'zaf.application.test.utils')
        self.assertEqual(extension_classes[1].module.__name__, 'zaf.application.test.utils')

    def test_extension_class_description(self):
        extension_classes = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extension_classes
        self.assertEqual(
            extension_classes[0].description, 'ext1 description.\n\next1 extended description')
        self.assertEqual(extension_classes[1].description, 'No description')

    def test_extension_class_short_description(self):
        extension_classes = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).extension_classes
        self.assertEqual(extension_classes[0].short_description, 'ext1 description.')
        self.assertEqual(extension_classes[1].short_description, 'No description')


class TestCommandMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_command_name(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[0].name, 'zaf')
        self.assertEqual(commands[1].name, 'zaf c1')
        self.assertEqual(commands[2].name, 'zaf c2')
        self.assertEqual(commands[3].name, 'zaf c2 c3')

    def test_command_short_name(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[0].short_name, 'zaf')
        self.assertEqual(commands[1].short_name, 'c1')
        self.assertEqual(commands[2].short_name, 'c2')
        self.assertEqual(commands[3].short_name, 'c3')

    def test_command_extension_name(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertIsNone(commands[0].extension_name)
        self.assertEqual(commands[1].extension_name, 'ext1')
        self.assertEqual(commands[2].extension_name, 'ext1')
        self.assertEqual(commands[3].extension_name, 'ext3')

    def test_command_extension_class(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertIsNone(commands[0].extension_class)
        self.assertEqual(commands[1].extension_class, Ext1)
        self.assertEqual(commands[2].extension_class, Ext1)
        self.assertEqual(commands[3].extension_class, Ext3)

    def test_command_config_option_ids(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[1].config_option_ids[0]._option_id, bools)
        self.assertEqual(commands[1].config_option_ids[1]._option_id, extendable_context)
        self.assertEqual(len(commands[1].config_option_ids), 2)
        self.assertEqual(commands[2].config_option_ids[0]._option_id, path)
        self.assertEqual(commands[2].config_option_ids[1]._option_id, entity)
        self.assertEqual(len(commands[2].config_option_ids), 2)

    def test_command_description(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[1].description, 'c1 description\n\nc1 extended description')
        self.assertEqual(
            commands[2].description,
            'c2 description\nc2 description continue\n\nc2 extended description')

    def test_command_short_description(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[1].short_description, 'c1 description')
        self.assertEqual(commands[2].short_description, 'c2 description\nc2 description continue')

    def test_command_extended_by(self):
        commands = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).commands
        self.assertEqual(commands[0].extension_names, [])
        self.assertEqual(commands[1].extension_names, ['ext2'])
        self.assertEqual(commands[2].extension_names, [])
        self.assertEqual(commands[3].extension_names, [])

    def test_config_option_ids_extension_classes(self):
        config_option_ids = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter)._config_option_ids

        self.assertEqual(config_option_ids[all_contexts].extension_classes, [Ext3])
        self.assertEqual(config_option_ids[bools].extension_classes, [Ext2])
        self.assertEqual(config_option_ids[extendable_context].extension_classes, [Ext3])
        self.assertEqual(config_option_ids[path].extension_classes, [Ext1])
        self.assertEqual(config_option_ids[entity].extension_classes, [Ext2])


class TestConfigOptionIdMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_config_option_id_types(self):
        config_option_ids = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).config_option_ids
        self.assertEqual(config_option_ids[0].type_string, 'str')
        self.assertEqual(config_option_ids[1].type_string, 'bool')
        self.assertEqual(config_option_ids[2].type_string, 'str')
        self.assertEqual(config_option_ids[3].type_string, 'Path(exists=False)')
        self.assertEqual(config_option_ids[4].type_string, 'Entity')


class TestComponentMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_component_extension_name(self):
        components = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(components[0].extension_name, 'ext1')
        self.assertEqual(components[1].extension_name, 'ext2')

    def test_component_name(self):
        components = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(components[0].name, 'comp1(call1)')
        self.assertEqual(components[1].name, 'comp2')

    def test_component_description(self):
        components = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(
            components[0].description, 'comp1 description\n\ncomp1 extended description')
        self.assertEqual(
            components[1].description, 'comp2 description\n\ncomp2 extended description')

    def test_component_short_description(self):
        components = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(components[0].short_description, 'comp1 description')
        self.assertEqual(components[1].short_description, 'comp2 description')

    def test_component_method(self):
        components = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(
            components[0].methods[0].path, 'zaf.application.test.utils.Comp1Class.method')

    def test_component_method_description(self):
        components = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).components
        self.assertEqual(components[0].methods[0].description, 'Do stuff.')


class TestEndpointsMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_endpoint_extension_names(self):
        endpoints = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).endpoints
        self.assertEqual(endpoints[0].extension_names, ['ext1'])
        self.assertEqual(endpoints[1].extension_names, ['ext2'])

    def test_endpoint_messages(self):
        endpoints = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).endpoints
        self.assertEqual(endpoints[0].messages[0].message_id, m1)
        self.assertEqual(endpoints[0].messages[1].message_id, m3)
        self.assertEqual(len(endpoints[0].messages), 2)
        self.assertEqual(endpoints[1].messages[0].message_id, m2)
        self.assertEqual(endpoints[1].messages[1].message_id, m3)
        self.assertEqual(len(endpoints[1].messages), 2)


class TestMessagesMetadata(unittest.TestCase):

    def setUp(self):
        self.extension_manager = Mock()

        def command_extensions(command, *args, **kwargs):
            if command.name == 'c1':
                return [Ext2]
            else:
                return []

        self.extension_manager.command_extensions.side_effect = command_extensions
        self.extension_manager.framework_extensions.return_value = [Ext1]

        self.metadata_filter = MetadataFilter()

    def test_message_extension_name(self):
        messages = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).messages
        self.assertEqual(messages[0].extension_names, ['ext1'])
        self.assertEqual(messages[1].extension_names, ['ext2'])
        self.assertEqual(messages[2].extension_names, ['ext1', 'ext2'])

    def test_messages_endpoints(self):
        messages = ZafMetadata(
            all_extensions, all_components, Mock(), 'zaf', self.extension_manager,
            self.metadata_filter).messages
        self.assertEqual(messages[0].endpoints[0].endpoint_id, e1)
        self.assertEqual(len(messages[0].endpoints), 1)
        self.assertEqual(messages[1].endpoints[0].endpoint_id, e2)
        self.assertEqual(len(messages[1].endpoints), 1)
        self.assertEqual(messages[2].endpoints[0].endpoint_id, e1)
        self.assertEqual(messages[2].endpoints[1].endpoint_id, e2)
        self.assertEqual(len(messages[2].endpoints), 2)


class TestMetdataFiltering(unittest.TestCase):

    def test_include_extensions_matching_namespaces(self):
        metadata1 = create_metadata(MetadataFilter(namespaces=['namespace1']))
        self.assertEqual(metadata1.extension_classes, [Ext1, Ext2])
        self.assertEqual(metadata1.extension_names, ['ext1', 'ext2'])

        metadata2 = create_metadata(MetadataFilter(namespaces=['namespace2']))
        self.assertEqual(metadata2.extension_classes, [Ext3])
        self.assertEqual(metadata2.extension_names, ['ext3'])

    def test_include_extensions_in_additional_extensions(self):
        metadata1 = create_metadata(
            MetadataFilter(namespaces=['namespace1'], additional_extensions=['ext3']))
        self.assertEqual(metadata1.extension_classes, [Ext1, Ext2, Ext3])
        self.assertEqual(metadata1.extension_names, ['ext1', 'ext2', 'ext3'])

    def test_include_command_that_is_applicable_for_application(self):
        metadata1 = create_metadata(
            MetadataFilter(application_context=ApplicationContext.STANDALONE))
        self.assertEqual(metadata1.commands, [ANY, c1, c2])
        self.assertEqual(metadata1._extension_classes[Ext1].commands, [c1, c2])
        self.assertEqual(metadata1._extension_classes[Ext3].commands, [])

        metadata2 = create_metadata(
            MetadataFilter(application_context=ApplicationContext.EXTENDABLE))
        self.assertEqual(metadata2.commands, [ANY, c1, c2, c3])
        self.assertEqual(metadata2._extension_classes[Ext1].commands, [c1, c2])
        self.assertEqual(metadata2._extension_classes[Ext3].commands, [c3])

    def test_do_not_include_command_that_is_hidden(self):
        metadata1 = create_metadata(MetadataFilter(include_hidden_commands=False))
        self.assertEqual(metadata1.commands, [ANY, c1, c3])
        self.assertEqual(metadata1._extension_classes[Ext1].commands, [c1])
        self.assertEqual(metadata1._extension_classes[Ext3].commands, [c3])

    def test_include_option_that_is_applicable_for_application(self):
        metadata1 = create_metadata(
            MetadataFilter(application_context=ApplicationContext.STANDALONE))
        self.assertEqual(metadata1.config_option_ids, [all_contexts, bools, path, entity])
        self.assertEqual(metadata1._extension_classes[Ext3].config_option_ids, [all_contexts])
        self.assertEqual(metadata1._commands[c1].config_option_ids, [bools])

        metadata2 = create_metadata(
            MetadataFilter(application_context=ApplicationContext.EXTENDABLE))
        self.assertEqual(
            metadata2.config_option_ids, [all_contexts, bools, extendable_context, path, entity])
        self.assertEqual(
            metadata2._extension_classes[Ext3].config_option_ids,
            [all_contexts, extendable_context])
        self.assertEqual(metadata2._commands[c1].config_option_ids, [bools, extendable_context])

    def test_do_not_include_option_that_is_hidden(self):
        metadata1 = create_metadata(MetadataFilter(include_hidden_options=False))
        self.assertEqual(metadata1.config_option_ids, [extendable_context, path, entity])
        self.assertEqual(metadata1._extension_classes[Ext3].config_option_ids, [extendable_context])
        self.assertEqual(metadata1._commands[c1].config_option_ids, [extendable_context])


def create_metadata(filter=MetadataFilter()):
    extension_manager = Mock()

    def command_extensions(command, *args, **kwargs):
        if command.name == 'c1':
            return [Ext2]
        else:
            return []

    extension_manager.command_extensions.side_effect = command_extensions
    extension_manager.framework_extensions.return_value = [Ext1]

    return ZafMetadata(all_extensions, all_components, Mock(), 'zaf', extension_manager, filter)
