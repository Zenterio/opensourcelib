import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.preparedassets import PreparedWorkspace, WorkspaceExists
from debpacker.common.test.utils import AssertFileExistsMixin, AssertFileNotExistsMixin


class TestPrepareWorkspace(TestCase, AssertFileExistsMixin, AssertFileNotExistsMixin):

    def test_prepare_temp_dir(self):
        with PreparedWorkspace() as (workspace, workspace_output):
            self.assert_file_exists(workspace)
            self.assertEqual(os.path.dirname(workspace), '/tmp')
            self.assertEqual(workspace_output, os.path.join(workspace, 'output'))
            self.assert_file_exists(workspace_output)
        self.assert_file_not_exists(workspace)
        self.assert_file_not_exists(workspace_output)

    def test_prepare_existing_workspace(self):
        with TemporaryDirectory() as test_dir, self.assertRaises(WorkspaceExists):
            with PreparedWorkspace(test_dir):
                pass

    def test_prepare_existing_workspace_using_force(self):
        with TemporaryDirectory() as test_dir:
            test_file = os.path.join(test_dir, 'file')
            open(test_file, 'w').close()
            with PreparedWorkspace(test_dir, True) as (workspace, workspace_output):
                self.assert_file_exists(workspace)
                self.assertEqual(workspace, test_dir)
                self.assertEqual(workspace_output, os.path.join(workspace, 'output'))
                self.assert_file_exists(workspace_output)
                self.assert_file_not_exists(test_file)
            self.assert_file_exists(workspace)
            self.assert_file_exists(workspace_output)
