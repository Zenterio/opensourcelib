import json
import os
from unittest import TestCase

from compiz.systest.utils import AssertCompizStartsMixin, invoke_for_output, squeeze_whitespace


class CompizSysTest(TestCase, AssertCompizStartsMixin):

    testroot = os.path.abspath(os.path.dirname(__file__) + '/../test/resources')

    query_options = '[-h] [-p] [-l N] [-x] [-v | -q] [--version] [--db DB] ' \
                    '[--show-db-path] [--root ROOT] [-c] [-n] [-g] [-a] ' \
                    '[--coverity] [--coverity-name COVERITY_NAME] ' \
                    '[file [file ...]]'

    git_options = '[-h] [-p] [-l N] [-x] [-v | -q] [--version] [--db DB] ' \
                  '[--show-db-path] [--root ROOT] [-c] [-n] [-g] [-a] ' \
                  '[--coverity] [--coverity-name COVERITY_NAME] [--staged | --workspace] ' \
                  '[hash [hash ...]]'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def testPrintsQueryHelpWithNoArgs(self):
        expected = 'usage: zcompiz query ' + self.query_options
        output = invoke_for_output('zcompiz')
        self.assertIn(expected, squeeze_whitespace(output))

    def testPrintsGenericHelpWithH(self):
        expected = 'usage: zcompiz [-h] {query,git}'
        output = invoke_for_output('zcompiz -h')
        self.assertIn(expected, output)
        output = invoke_for_output('zcompiz --help')
        self.assertIn(expected, output)

    def testPrintsQueryHelpWithQueryH(self):
        expected = 'usage: zcompiz query ' + self.query_options
        output = invoke_for_output('zcompiz query -h')
        self.assertIn(expected, squeeze_whitespace(output))
        output = invoke_for_output('zcompiz query --help')
        self.assertIn(expected, squeeze_whitespace(output))

    def testPrintsGitHelpWithGitH(self):
        expected = 'usage: zcompiz git ' + self.git_options
        output = invoke_for_output('zcompiz git -h')
        self.assertIn(expected, squeeze_whitespace(output))
        output = invoke_for_output('zcompiz git --help')
        self.assertIn(expected, squeeze_whitespace(output))

    def testQueryAboutFileReturnsOwner(self):
        expected = 'Owner: TestOwnerB'
        output = invoke_for_output(
            'zcompiz {testroot}/testdir/file3.txt'.format(testroot=self.testroot))
        self.assertIn(expected, output)

    def testQueryAboutMultipleFilesReturnsOwners(self):
        expected1 = 'Owner: TestOwnerB'
        expected2 = 'Owner: TestOwnerA'
        output = invoke_for_output(
            'zcompiz {testroot}/testdir/file3.txt '
            '{testroot}/testdir/file2.txt'.format(testroot=self.testroot))
        self.assertIn(expected1, output)
        self.assertIn(expected2, output)

    def testQueryWorksWithDifferentDBsInDifferentFoldersSeperateCalls(self):
        expected1 = 'Owner: TestOwnerB'
        expected2 = 'Owner: TestOwnerA'
        output1 = invoke_for_output(
            'zcompiz {testroot}/testdir/file3.txt'.format(testroot=self.testroot))
        output2 = invoke_for_output(
            'zcompiz {testroot}/testdir2/file3.txt'.format(testroot=self.testroot))
        self.assertIn(expected1, output1)
        self.assertIn(expected2, output2)

    def testQueryWorksWithDifferentDBsInDifferentFoldersSameCall(self):
        expected1 = 'Owner: TestOwnerB'
        expected2 = 'Owner: TestOwnerA'
        output1 = invoke_for_output(
            'zcompiz {testroot}/testdir/file3.txt '
            '{testroot}/testdir2/file3.txt'.format(testroot=self.testroot))
        self.assertIn(expected1, output1)
        self.assertIn(expected2, output1)

    def testQueryByOwnerInNonCompizDirectory(self):
        expected = 'No Compiz profile found for'
        output = invoke_for_output('zcompiz -n "TestOwnerB"', expected_exit_code=1)
        self.assertIn(expected, output)

    def testQueryByOwnerInCompizDirectory(self):
        cwd = '{testroot}/testdir/subfolder_level1a'.format(testroot=self.testroot)
        expected = 'TestItemB'
        output = invoke_for_output('zcompiz -n "TestOwnerB"', cwd=cwd)
        self.assertIn(expected, output)

    def testQueryByComponentInNonCompizDirectory(self):
        expected = 'No Compiz profile found for'
        output = invoke_for_output('zcompiz -c "TestItemA"', expected_exit_code=1)
        self.assertIn(expected, output)

    def testQueryByComponentInCompizDirectory(self):
        cwd = '{testroot}/testdir/subfolder_level1b'.format(testroot=self.testroot)
        expected = 'TestOwnerA'
        output = invoke_for_output('zcompiz -c "TestItemA"', cwd=cwd)
        self.assertIn(expected, output)

    def testQueryByGuildInNonCompizDirectory(self):
        expected = 'No Compiz profile found for'
        output = invoke_for_output('zcompiz -g "TestGuildA"', expected_exit_code=1)
        self.assertIn(expected, output)

    def testQueryByGuildInCompizDirectory(self):
        cwd = '{testroot}/testdir/'.format(testroot=self.testroot)
        expected1 = 'TestItemA'
        expected2 = 'TestItemB'
        expected3 = 'TestItemH'
        output = invoke_for_output('zcompiz -g "TestGuildA"', cwd=cwd)
        self.assertIn(expected1, output)
        self.assertIn(expected2, output)
        self.assertIn(expected3, output)

    def testComponentQueryListsFilesWithVerbose(self):
        cwd = '{testroot}/testdir/'.format(testroot=self.testroot)
        expected = 'file2.txt\n' \
                   'subfolder_level1a/file_subfolder_level1*'
        output = invoke_for_output('zcompiz -cvvv "TestItemA"', cwd=cwd)
        self.assertIn(expected, output)

    def testFileSearchShowsParents(self):
        expected1 = 'Component: TestItemB'
        expected2 = 'Component: TestItemA'
        expected3 = 'Component: Parent'
        output = invoke_for_output(
            'zcompiz -p {testroot}/testdir/file3.txt'.format(testroot=self.testroot))
        self.assertIn(expected1, output)
        self.assertIn(expected2, output)
        self.assertIn(expected3, output)

    def testFileSearchShowsParentsWithLimit(self):
        expected1 = 'Component: TestItemB'
        expected2 = 'Component: TestItemA'
        expected3 = 'Component: Parent'
        output = invoke_for_output(
            'zcompiz -p -l1 {testroot}/testdir/file3.txt'.format(testroot=self.testroot))
        self.assertIn(expected1, output)
        self.assertIn(expected2, output)
        self.assertNotIn(expected3, output)

    def testFileDoesNotExist(self):
        path = '{testroot}/testdir/file_that_does_not_exist.txt'.format(testroot=self.testroot)
        expected = 'File "{path}" not found'.format(path=path)
        output = invoke_for_output('zcompiz {path}'.format(path=path))
        self.assertIn(expected, output)

    def testFileInFolderThatDoesNotExist(self):
        path = '{testroot}/folder_that_does_not_exist/file3.txt'.format(testroot=self.testroot)
        expected = 'File "{path}" not found'.format(path=path)
        output = invoke_for_output('zcompiz {path}'.format(path=path))
        self.assertIn(expected, output)

    def testQueryAllComponents(self):
        output = invoke_for_output(
            'zcompiz --root {testroot}/testdir --all'.format(testroot=self.testroot))

        self.assertIn('[Parent]', output)
        self.assertIn('[TestItem]', output)
        self.assertIn('[TestItemA]', output)
        self.assertIn('[TestItemB]', output)
        self.assertIn('[TestItemC]', output)
        self.assertIn('[TestItemD]', output)
        self.assertIn('[TestItemE]', output)
        self.assertIn('[TestItemF]', output)
        self.assertIn('[TestItemG]', output)
        self.assertIn('[TestItemH]', output)

    def testCoverityRenderer(self):
        output = invoke_for_output(
            'zcompiz --root {testroot}/testdir --all --coverity --coverity-name "Coverity Component List"'.
            format(testroot=self.testroot))

        data = json.loads(output)

        self.assertEqual(data['version'], 1)
        self.assertEqual(data['name'], 'Coverity Component List')
        self.assertEqual(data['description'], 'Testdir Compiz file map')
        self.assertEqual(data['forceDeleteComponents'], True)
        self.assertIn('components', data)
        self.assertEqual(len(data['components']), 4 + 10)
        self.assertIn('fileRules', data)
        self.assertEqual(len(data['fileRules']), 26 + 15)
