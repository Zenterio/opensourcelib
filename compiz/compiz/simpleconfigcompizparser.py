import configparser

from .compizparser import Parser
from .section import Section


class SimpleConfigCompizParser(Parser):

    def parse_db(self):
        if not self.db:
            raise NoFileSpecifiedError
        parser = configparser.ConfigParser()
        success = parser.read(self.db, encoding='utf-8')
        if not success:
            raise FileNotFoundError(self.db)
        objlist = {}
        for section in parser.sections():
            parent = 'None'
            owner = 'None'
            guild = 'None'
            files = ['None']
            if parser.has_option(section, 'owner'):
                owner = parser.get(section, 'owner')
            if parser.has_option(section, 'guild'):
                guild = parser.get(section, 'guild')
            if parser.has_option(section, 'parent'):
                parent = parser.get(section, 'parent')
            default_prio = int(parser.get(section, 'prio', fallback='0'))
            if parser.has_option(section, 'files'):
                files = parser.get(section, 'files').split('\n')

            objlist[section] = Section(section, owner, guild, parent, files, default_prio)
        return objlist


class FileNotFoundError(Exception):
    pass


class NoFileSpecifiedError(Exception):
    pass
