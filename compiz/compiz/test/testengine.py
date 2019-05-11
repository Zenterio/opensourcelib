from os import path
from unittest import TestCase, main

from compiz.compizprofilehandler import COMPIZ_PROFILE

from ..compiz_engine import CompizEngine, FileNotFoundError, FileNotInProjectPath
from ..compizparser import Parser
from ..section import Section
from ..simpleconfigcompizparser import SimpleConfigCompizParser


class CompizEngineTestWithParser(TestCase):

    def setUp(self):
        db = 'compiz/test/resources/testdir/dbdir/compiz_db.cfg'
        root = path.abspath('compiz/test/resources/testdir')
        parser = SimpleConfigCompizParser(db)
        self.engine = CompizEngine(parser.parse_db(), root)

    def testFileNotFound(self):
        file = self.engine.root + '/subfolder_level1a/nothere.txt'
        with self.assertRaises(FileNotFoundError):
            self.engine.find(file)

    def testFindOwner(self):
        file = self.engine.root + '/subfolder_level1a/file_subfolder_level1.cc'
        target = 'TestOwnerA'
        result = self.engine.find(file)
        self.assertEqual(result[0].owner.split(',')[0], target)

    def testFindGuild(self):
        file = self.engine.root + '/subfolder_level1b/subfolder_level2/file_subfolder_level2a.txt'
        target = 'TestGuildB'
        result = self.engine.find(file)
        self.assertEqual(result[0].guild, target)

    def testFindFileOutsideProject(self):
        file = '/etc/group'
        with self.assertRaises(FileNotInProjectPath):
            self.engine.find(file)

    def testFindParents(self):
        file = self.engine.root + '/file3.txt'
        result = self.engine.find(file, 2)
        target = 'Parent'
        self.assertEqual(result[2].name, target)

    def testPrio(self):
        file = self.engine.root + '/subfolder_level1a/subfolder_level2/file_subfolder_level3.sh'
        result = self.engine.find(file)
        target = 'TestItemG'
        self.assertEqual(result[0].name, target)

    def testPrio2(self):
        file = self.engine.root + '/subfolder_level1a/script.sh'
        result = self.engine.find(file)
        target = 'TestItemF'
        self.assertEqual(result[0].name, target)

    def testNonPrio(self):
        file = self.engine.root + '/subfolder_level1a/file_subfolder_level1.cc'
        result = self.engine.find(file)
        target = 'TestItemA'
        self.assertEqual(result[0].name, target)

    def testFindExistingComponent(self):
        section = 'TestItemE'
        result = self.engine.findsection(section)
        self.assertEqual(result[0].name, section)

    def testFindNonexistingComponent(self):
        section = 'Not in db'
        result = self.engine.findsection(section)
        self.assertTrue(len(result) == 0)

    def testFindExistingOwner(self):
        owner = 'TestOwnerB'
        result = self.engine.findowner(owner)
        self.assertTrue('TestItemC' in result[owner] and 'TestItemB' in result[owner])

    def testFindExistingGuild(self):
        correct_sections = ['TestItemB', 'TestItemA', 'TestItemH']
        guild = 'TestGuildA'
        result = self.engine.findguild(guild)
        self.assertTrue(len(result[guild]) == 3)
        for section in result[guild]:
            self.assertTrue(section in correct_sections)

    def testFindNonexistingOwner(self):
        owner = 'Fake McFakeson'
        result = self.engine.findowner(owner)
        self.assertTrue(len(result) == 0)

    def testFindNonexistingGuild(self):
        guild = 'FooGuild'
        result = self.engine.findguild(guild)
        self.assertTrue(len(result) == 0)

    def testExpandPaths(self):
        root = path.abspath('../../../')
        owner = 'Patrik Lindblom'
        returned_paths = ['zac/doc/zac.*', 'zac/thrift/server/zacthriftMasterServer.*']
        correct_result = [
            root + '/zac/doc/zac.dox', root + '/zac/doc/zac.dxg',
            root + '/zac/thrift/server/zacthriftMasterServer.cc',
            root + '/zac/thrift/server/zacthriftMasterServer.hh'
        ]
        returned_paths = self.engine.expandpaths(returned_paths, owner)
        for returned_path in returned_paths:
            self.assertTrue(returned_path in correct_result)

    def testFindAll(self):
        components = self.engine.findall()
        self.assertEqual(len(components), 10)


class CompizEngineTestWithStubbedParser(TestCase):

    class ParserStub(Parser):

        def parse_db(self):
            """
            Set up components for the files in the testdir.

            ./file1.txt <= TestItem
            ./file2.txt <= TestItemA
            ./file3.txt <= TestItemB
            ./subfolder_level1a
            ./subfolder_level1a/file_subfolder_level1.cc <= testItemA
            ./subfolder_level1a/file_subfolder_level1.hh <= testItem
            ./subfolder_level1a/script.sh <= TestItemF
            ./subfolder_level1a/subfolder_level2
            ./subfolder_level1a/subfolder_level2/file_subfolder_level2a.txt <= TestItemC
            ./subfolder_level1a/subfolder_level2/file_subfolder_level2b.txt <= TestItemC
            ./subfolder_level1b
            ./subfolder_level1b/file_subfolder_level1.txt <= Parent
            ./subfolder_level1b/script.sh <= TestItemF
            ./subfolder_level1b/subfolder_level2
            ./subfolder_level1b/subfolder_level2/file_subfolder_level2a.txt <= TestItemD
            ./subfolder_level1b/subfolder_level2/file_subfolder_level2b.txt <= TestItemD
            ./subfolder_level1b/subfolder_level2b
            ./subfolder_level1b/subfolder_level2b/file_subfolder_level2a.txt <=TestItemE


            """
            stublist = {
                'TestItem':
                Section(
                    'TestItem', 'TestOwner', 'None', 'Parent', [
                        'file1.txt', 'subfolder_level1a/file_subfolder*',
                        'subfolder_level1a/file_subfolder_level1.hh'
                    ], 0),
                'TestItemA':
                Section(
                    'TestItemA', 'TestOwnerA', 'TestGuildA', 'Parent',
                    ['file2.txt', 'subfolder_level1a/file_subfolder_level1*'], 0),
                'TestItemB':
                Section(
                    'TestItemB', 'TestOwnerB', 'TestGuildA', 'Parent', ['file3.txt', 'file3.txt'],
                    0),
                'Parent':
                Section('Parent', 'TestOwner', 'None', 'None', ['*'], 0),
                'TestItemC':
                Section(
                    'TestItemC', 'TestOwnerC', 'None', 'None',
                    ['subfolder_level1a/subfolder_level2/*'], 0),
                'TestItemD':
                Section(
                    'TestItemD', 'TestOwnerD', 'TestGuildB', 'None',
                    ['subfolder_level1b/subfolder_level2/'], 0),
                'TestItemE':
                Section(
                    'TestItemE', 'TestOwnerE', 'None', 'None',
                    ['subfolder_level1b/subfolder_level2b'], 0),
                'TestItemF':
                Section('TestItemF', 'TestOwnerF', 'None', 'None', ['*.sh'], 10),
                'TestItemG':
                Section(
                    'TestItemG', 'TestOwnerG', 'None', 'None',
                    ['subfolder_level1a/sub*/file_subfolder_level3.sh'], 10),
                'TestItemH':
                Section(
                    'TestItemH', 'TestOwnerH', 'TestGuildA', 'None', ['file4.txt', 'file4.txt'], 0)
            }
            # Used to test file expand of path: <something>/*
            # Used to test file expand of path: <something>/
            # Used to test file expand of path: <something> where it is a directory,
            # shall be treated as <something>/*
            # Used to test priority and file expansion
            # Used to test priority and file expansion
            # Used to test guild belonging

            return stublist

    def setUp(self):
        root = path.abspath('compiz/test/resources/testdir/')
        parser = self.ParserStub(None)
        self.engine = CompizEngine(parser.parse_db(), root)

    def testFileNotFound(self):
        file = self.engine.root + '/nope.h'
        with self.assertRaises(FileNotFoundError):
            self.engine.find(file)

    def testFindOwner(self):
        file = self.engine.root + '/file2.txt'
        target = 'TestOwnerA'
        result = self.engine.find(file)
        self.assertEqual(result[0].owner.split(',')[0], target)

    def testFindGuild(self):
        file = self.engine.root + '/file4.txt'
        target = 'TestGuildA'
        result = self.engine.find(file)
        self.assertEqual(result[0].guild.split(',')[0], target)

    def testFindFileOutsideProject(self):
        file = '/etc/group'
        with self.assertRaises(FileNotInProjectPath):
            self.engine.find(file)

    def testFindParents(self):
        file = self.engine.root + '/file2.txt'
        result = self.engine.find(file, 1)
        target = 'Parent'
        self.assertEqual(result[1].name, target)

    def testFindExistingComponent(self):
        section = 'TestItemA'
        result = self.engine.findsection(section)
        self.assertEqual(result[0].name, section)

    def testFindMultipleExistingComponentsUsingRegExp(self):
        correct_sections = [
            'TestItem', 'TestItemA', 'TestItemB', 'TestItemC', 'TestItemD', 'TestItemE',
            'TestItemF', 'TestItemG', 'TestItemH'
        ]
        section = 'TestItem.*'
        result = self.engine.findsection(section)
        self.assertEqual(len(result), 9)
        for s in result:
            self.assertTrue(s.name in correct_sections)
            correct_sections.remove(s.name)

    def testFindOneExistingComponentUsingRegExp(self):
        section = 'Test.*A'
        result = self.engine.findsection(section)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0].name, 'TestItemA')

    def testFindFindExistingComponentExactMatch(self):
        section = 'TestItem'
        result = self.engine.findsection(section)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0].name, 'TestItem')

    def testFindNonexistingComponent(self):
        section = 'ZAC'
        result = self.engine.findsection(section)
        self.assertTrue(len(result) == 0)

    def testFindExistingOwner(self):
        owner = 'TestOwnerA'
        result = self.engine.findowner(owner)
        self.assertTrue('TestItemA' in result[owner])

    def testFindNonexistingOwner(self):
        owner = 'Fake McFakeson'
        result = self.engine.findowner(owner)
        self.assertTrue(len(result) == 0)

    def testFindExistingGuild(self):
        guild = 'TestGuildA'
        result = self.engine.findguild(guild)
        self.assertTrue('TestItemA' in result[guild])

    def testFindNonExistingGuild(self):
        guild = 'FooGuild'
        result = self.engine.findguild(guild)
        self.assertTrue(len(result) == 0)

    def testFindFileWithMultipleMatchesInComponent(self):
        file = self.engine.root + '/file3.txt'
        result = self.engine.find(file)
        expected = 'TestItemB'
        self.assertEqual(result[0].name, expected)

    def testBetterMatchInSameComponent(self):
        file = self.engine.root + '/subfolder_level1a/file_subfolder_level1.hh'
        result = self.engine.find(file)
        expected = 'TestItem'
        self.assertEqual(result[0].name, expected)

    def testFindExistingOwnerUsingRegExp(self):
        correct_owners = [
            'TestOwner', 'TestOwnerA', 'TestOwnerB', 'TestOwnerC', 'TestOwnerD', 'TestOwnerE',
            'TestOwnerF', 'TestOwnerG', 'TestOwnerH'
        ]
        result = self.engine.findowner('TestOwner.*')
        self.assertEqual(len(result), 9)
        for owner in result:
            self.assertTrue(owner in correct_owners)
            correct_owners.remove(owner)

    def testFindExistingGuildUsingRegExp(self):
        """Test that sections with guild=None are filtered."""
        correct_guilds = ['TestGuildA', 'TestGuildB']
        result = self.engine.findguild('.*[A|B]')
        self.assertEqual(len(result), 2)
        for guild in result:
            self.assertTrue(guild in correct_guilds)
            correct_guilds.remove(guild)

    def testFindExistingOwnerExactMatch(self):
        """Test that there is only one match and not several, e.g. that the match is ^name$."""
        owner = 'TestOwnerA'
        result = self.engine.findowner(owner)
        self.assertTrue(len(result) == 1)

    def testExpandPathFindUnmappedFilesUsingTopLevelStar(self):
        """Find all files unmapped, e.g. belongs to component with the rule '*' [('*', 0)]."""
        file = self.engine.root + '/' + COMPIZ_PROFILE
        section = self.engine.findsection('Parent')
        paths = [pair[0] for pair in section[0].files]
        pathlist = self.engine.expandpaths(paths, 'Parent')
        self.assertEqual(pathlist[0], file)

    def _testExpandPathForComponent(self, sectionname, correctfiles):
        section = self.engine.findsection(sectionname)
        paths = [pair[0] for pair in section[0].files]
        expanded_paths = self.engine.expandpaths(paths, sectionname)
        self.assertEqual(len(expanded_paths), len(correctfiles))
        for expanded_path in expanded_paths:
            self.assertTrue(expanded_path in correctfiles)
            correctfiles.remove(expanded_path)

    def testExpandPathWithRuleThatEndWithSlashStar(self):
        """Test that file rules that end with '/*' work."""
        correct_files = [
            self.engine.root + '/subfolder_level1a/subfolder_level2/file_subfolder_level2a.txt',
            self.engine.root + '/subfolder_level1a/subfolder_level2/file_subfolder_level2b.txt'
        ]
        self._testExpandPathForComponent('TestItemC', correct_files)

    def testExpandPathWithRuleThatEndWithSlash(self):
        """Test that file rules that end with '/' is treated as '/*'."""
        correct_files = [
            self.engine.root + '/subfolder_level1b/subfolder_level2/file_subfolder_level2a.txt',
            self.engine.root + '/subfolder_level1b/subfolder_level2/file_subfolder_level2b.txt'
        ]
        self._testExpandPathForComponent('TestItemD', correct_files)

    def testExpandPathWithRuleThatEndWithoutSlash(self):
        """Test that file rules that end with a directory name without '/' nor '/*' is treated as '/*'."""
        correct_files = [
            self.engine.root + '/subfolder_level1b/subfolder_level2b/file_subfolder_level2a.txt'
        ]
        self._testExpandPathForComponent('TestItemE', correct_files)

    def testExpandPathStarWithPrio(self):
        """Test that a rule with higher priority than all other rules work, e.g. '*.sh' with prio 10."""
        correct_files = [
            self.engine.root + '/subfolder_level1a/script.sh',
            self.engine.root + '/subfolder_level1b/script.sh'
        ]
        self._testExpandPathForComponent('TestItemF', correct_files)

    def testFindAll(self):
        components = self.engine.findall()
        self.assertEqual(len(components), 10)


if __name__ == '__main__':
    main()
