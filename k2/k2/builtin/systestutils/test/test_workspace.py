import os
import unittest
from unittest.mock import Mock, mock_open, patch

from zaf.builtin.output import OUTPUT_DIR
from zaf.config.manager import ConfigManager

from ..workspace import Workspace


class TestWorkspace(unittest.TestCase):

    def setUp(self):
        output_dir = './output'

        config = ConfigManager()
        config.set(OUTPUT_DIR, output_dir)

        component_context = Mock()
        component_context.callable_qualname = 'package.module.test_case'

        self.workspace = Workspace(component_context, config)

    def test_workspace_directory_calculated_from_output_dir_and_component_context(self):
        self.assertEqual(
            self.workspace.workspace,
            os.path.join(os.getcwd(), 'output', 'workspace', 'package.module.test_case'))

    def test_path_property_contains_workspace_directory(self):
        self.assertEqual(
            self.workspace.path,
            os.path.join(os.getcwd(), 'output', 'workspace', 'package.module.test_case'))

    def test_workspace_created_on_enter(self):
        with patch('os.path.exists', return_value=False), \
                patch('os.makedirs') as makedirs:

            with self.workspace:
                makedirs.assert_called_with(self.workspace.workspace, exist_ok=True)

    def test_workspace_cleared_enter_if_already_exists(self):
        with patch('os.path.exists', return_value=True), \
                patch('shutil.rmtree') as rmtree, \
                patch('os.makedirs'):

            with self.workspace:
                rmtree.assert_called_with(self.workspace.workspace)

    def test_absolute_file_path_gives_absolute_path_to_file_in_workspace(self):
        self.assertEqual(
            self.workspace.absolute_file_path('path/to/file'),
            os.path.join(
                os.getcwd(), 'output', 'workspace', 'package.module.test_case', 'path/to/file'))

    def test_assert_file_exists_raises_exception_only_if_file_not_exists(self):

        def exists(file):
            return 'that_exists' in file

        with patch('os.path.exists', side_effect=exists):
            self.workspace.assert_file_exists('path/to/file_that_exists')

            with self.assertRaises(AssertionError):
                self.workspace.assert_file_exists('path/to/file_that_does_not_exist')

    def test_assert_file_not_exists_raises_exception_only_if_file_exists(self):

        def exists(file):
            return 'that_exists' in file

        with patch('os.path.exists', side_effect=exists):
            with self.assertRaises(AssertionError):
                self.workspace.assert_file_not_exists('path/to/file_that_exists')

            self.workspace.assert_file_not_exists('path/to/file_that_does_not_exist')

    def test_assert_is_links_raises_exception_if_not_link(self):
        with patch('os.path.exists', return_value=True):
            with patch('os.path.islink', return_value=True):
                self.workspace.assert_is_link('path/to/link')

            with patch('os.path.islink', return_value=False):
                with self.assertRaises(AssertionError):
                    self.workspace.assert_is_link('path/to/link')

    def test_assert_in_file_raises_exception_if_content_not_in_file(self):
        with patch('builtins.open', mock_open(read_data='file content')) as mock_file:
            self.workspace.assert_in_file('path/to/file', 'content')
            mock_file.assert_called_with(self.workspace.absolute_file_path('path/to/file'))

            with self.assertRaises(AssertionError):
                self.workspace.assert_in_file('path/to/file2', 'not in file')
            mock_file.assert_called_with(self.workspace.absolute_file_path('path/to/file2'))

    def test_create_file_opens_file_and_writes_content(self):
        with patch('builtins.open', mock_open()) as mock_file, \
                patch('os.makedirs'):
            self.workspace.create_file('path/to/file', 'content')
            mock_file.assert_called_with(self.workspace.absolute_file_path('path/to/file'), 'w')
            mock_file().write.assert_called_with('content')

    def test_create_file_creates_directory_before_writing_file(self):
        with patch('builtins.open', mock_open()), \
                patch('os.makedirs') as makedirs:
            self.workspace.create_file('path/to/file', 'content')
            makedirs.assert_called_with(
                os.path.dirname(self.workspace.absolute_file_path('path/to/file')), exist_ok=True)

    def test_create_dir_always_tries_to_create_dir(self):
        with patch('os.makedirs') as makedirs:
            with patch('os.path.exists', return_value=True):
                self.workspace.create_dir('path/to/dir')
                makedirs.assert_called_with(
                    self.workspace.absolute_file_path('path/to/dir'), exist_ok=True)

            with patch('os.path.exists', return_value=False):
                self.workspace.create_dir('path/to/dir')
                makedirs.assert_called_with(
                    self.workspace.absolute_file_path('path/to/dir'), exist_ok=True)

    def test_add_file_copies_file_into_workspace(self):
        with patch('shutil.copy') as copy, \
                patch('os.makedirs'):
            self.workspace.add_file('/source/path/to/file', 'target/path/to/file')
            copy.assert_called_with(
                '/source/path/to/file', self.workspace.absolute_file_path('target/path/to/file'))

    def test_add_file_creates_direcotry_before_writing_file(self):
        with patch('shutil.copy', mock_open()), \
                patch('os.makedirs') as makedirs:
            self.workspace.add_file('/source/path/to/file', 'target/path/to/file')
            makedirs.assert_called_with(
                os.path.dirname(self.workspace.absolute_file_path('target/path/to/file')),
                exist_ok=True)

    def test_create_creates_the_workspace_directory(self):
        with patch('os.makedirs') as makedirs:
            self.workspace.create()
            makedirs.assert_called_with(self.workspace.path, exist_ok=True)
