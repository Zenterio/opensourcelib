import configparser
import unittest

from compiz.simpleconfigcompizparser import FileNotFoundError, NoFileSpecifiedError, \
    SimpleConfigCompizParser


class SimpleConfigParserTest(unittest.TestCase):

    def testFileNotFound(self):
        db = 'not a file'
        parser = SimpleConfigCompizParser(db)
        with self.assertRaises(FileNotFoundError):
            parser.parse_db()

    def testFileNotSpecified(self):
        db = None
        parser = SimpleConfigCompizParser(db)
        with self.assertRaises(NoFileSpecifiedError):
            parser.parse_db()

    def testParseDB(self):
        db = 'compiz/test/resources/minimal_working_db.cfg'
        parser = SimpleConfigCompizParser(db)
        parser.parse_db()

    def testIncorrectDBFormat(self):
        db = __file__
        parser = SimpleConfigCompizParser(db)
        with self.assertRaises(configparser.MissingSectionHeaderError):
            parser.parse_db()

    def testBrokenDBFile(self):
        db = 'compiz/test/resources/broken_db.cfg'
        parser = SimpleConfigCompizParser(db)
        with self.assertRaises(configparser.ParsingError):
            parser.parse_db()


if __name__ == '__main__':
    unittest.main()
