#!/usr/bin/env python3

import argparse
import os
import sys

from compiz.coverity_renderer import CoverityRenderer

from . import __version__
from .compiz_engine import CompizEngine, FileNotFoundError, FileNotInProjectPath, \
    FileNotMatchedError, MultipleOwnersError
from .compiz_git import addgitparser
from .compiz_renderer import CompizRenderer
from .compizprofilehandler import ProfileNotFoundError, get_root_and_db
from .simpleconfigcompizparser import SimpleConfigCompizParser


class CompizCli(object):

    def __init__(self, argv, ostream):
        self.ostream = ostream
        self.argv = argv
        # Allow input redirection and pipes instead of commmandline arguments
        if not sys.stdin.isatty():
            for line in sys.stdin:
                line = line.replace('\n', '')
                self.argv.append(line)
        self.parser, self.subparser = self._createparser()
        # With no arguments, print help
        # Without submodule specified, default to 'query'
        if len(self.argv) < 2:
            self.argv.insert(1, 'query')
            self.argv.insert(2, '-h')
        elif self.argv[1] not in self.subparser.choices.keys() and argv[1] not in ('-h', '--help'):
            self.argv.insert(1, 'query')
        self.args = self.parser.parse_args(argv[1:])
        self.files = self.args.func(self.args)
        if self.args.root is None:
            pass
        elif self.args.db is None:
            _, db = get_root_and_db(self.args.root)
            self.engine = CompizEngine(SimpleConfigCompizParser(db).parse_db(), self.args.root)
        else:
            self.engine = CompizEngine(
                SimpleConfigCompizParser(self.args.db).parse_db(), self.args.root)
        # only one of verbose and quiet can be set, see _createparser()
        if self.args.verbose:
            self.verbosity = 2
        elif self.args.quiet:
            self.verbosity = 0
        else:
            self.verbosity = 1
        self.renderer = CompizRenderer(self.verbosity, ostream)

    def _createparser(self):
        parser = argparse.ArgumentParser()
        parentparser = argparse.ArgumentParser(add_help=False)
        parentparser.add_argument(
            '-p', '--parents', action='store_true', help='Prints parents. use -l to limit depth')
        parentparser.add_argument(
            '-l', '--limit', type=int, metavar='N', help='Limit depth of parent printing')
        parentparser.add_argument(
            '-x',
            '--expand',
            action='store_true',
            help='Expand the component file rules (Works with -c and -n)')
        group = parentparser.add_mutually_exclusive_group()
        group.add_argument('-v', '--verbose', action='store_true', help='More verbose output')
        group.add_argument('-q', '--quiet', action='store_true', help='Less verbose output')
        parentparser.add_argument('--version', action='version', version=__version__)
        parentparser.add_argument('--db', default=None, help='use a different database')
        parentparser.add_argument(
            '--show-db-path', action='store_true', help='Print the path to the database')
        parentparser.add_argument('--root', default=None, help='Specify project root')
        parentparser.add_argument(
            '-c',
            '--component',
            action='store_true',
            help='list files for given component(s), regexp okay to use in component name')
        parentparser.add_argument(
            '-n', '--name', action='store_true', help='list components NAME is an owner of')
        parentparser.add_argument(
            '-g', '--guild', action='store_true', help='list components GUILD is an owner of')
        parentparser.add_argument('-a', '--all', action='store_true', help='list all components')
        parentparser.add_argument(
            '--coverity',
            action='store_true',
            help='Print results in coverity component json format')
        parentparser.add_argument(
            '--coverity-name', default='Default', help='The name of the coverity component list')
        subparser = parser.add_subparsers()
        parser_query = subparser.add_parser('query', parents=[parentparser])

        parser_query.add_argument(
            'File', metavar='file', nargs='*', help='File to show ownership for')
        parser_query.set_defaults(func=self._queryhandler)
        addgitparser(subparser, parentparser)

        return parser, subparser

    def _queryhandler(self, null):
        return self.args.File

    def _findcomponent(self):
        if self.args.root is None:
            self._find_root_and_set_engine()
        for component in self.files:
            sections = self.engine.findsection(component)
            if len(sections) != 0:
                for section in sections:
                    paths = [pair[0] for pair in section.files]
                    if self.args.expand:
                        pathlist = self.engine.expandpaths(paths, section.name)
                    else:
                        pathlist = paths
                    self.renderer.renderComponent(section, pathlist, section.owner, section.guild)
            else:
                self.renderer.renderError(
                    'Component "{component}" not found'.format(component=component))
        self.renderer.finalize()

    def _findname(self):
        if self.args.root is None:
            self._find_root_and_set_engine()
        for name in self.files:
            componentsperowner = self.engine.findowner(name)
            if len(componentsperowner) != 0:
                for owner in componentsperowner:
                    self.renderer.renderOwner(owner, componentsperowner[owner])
            else:
                self.renderer.renderError(
                    '"{name}" is not the owner of any components'.format(name=name))
        self.renderer.finalize()

    def _findguild(self):
        if self.args.root is None:
            self._find_root_and_set_engine()
        for guild in self.files:
            componentsperguild = self.engine.findguild(guild)
            if len(componentsperguild) != 0:
                for guild in componentsperguild:
                    self.renderer.renderGuild(guild, componentsperguild[guild])
            else:
                self.renderer.renderError(
                    '"{guild}" is not the owner of any components'.format(guild=guild))
        self.renderer.finalize()

    def _findall(self):
        if self.args.root is None:
            self._find_root_and_set_engine()

        for section in self.engine.findall():
            paths = [pair[0] for pair in section.files]
            if self.args.expand:
                pathlist = self.engine.expandpaths(paths, section.name)
            else:
                pathlist = paths
            self.renderer.renderComponent(section, pathlist, section.owner, section.guild)
        self.renderer.finalize()

    def _findsection(self):
        resultlist = {}
        result = []
        prevroot = None
        for file in self.files:
            if not os.path.exists(file):
                self.renderer.renderError('File "{file}" not found'.format(file=file))
                continue

            if self.args.root is None:
                prevroot = self._find_root_and_set_engine(file, prevroot)
            try:
                if self.args.parents and self.args.limit is not None:
                    result = self.engine.find(file, self.args.limit)
                elif self.args.parents:
                    result = self.engine.find(file, -1)
                elif self.args.limit is not None:
                    self.renderer.renderError('-l not allowed without -p')
                    exit(1)
                else:
                    result = self.engine.find(file)
            except FileNotFoundError:
                self.renderer.renderError('File "{file}" not found'.format(file=file))
                continue
            except FileNotMatchedError:
                self.renderer.renderError('File "{file}" has no compiz'.format(file=file))
                continue
            except MultipleOwnersError as e:
                result = e.args[0]
            except FileNotInProjectPath:
                self.renderer.renderError('File "{file}" not in project path'.format(file=file))
                continue
            resultlist[file] = result
        self.renderer.renderFiles(resultlist)
        self.renderer.finalize()

    def _find_root_and_set_engine(self, target=os.getcwd(), prevroot=None):
        try:
            root, db = get_root_and_db(target)
        except ProfileNotFoundError:
            self.renderer.renderError('No Compiz profile found for {target}'.format(target=target))
            exit(1)
        if root != prevroot:
            if self.args.db is not None:
                self.engine = CompizEngine(SimpleConfigCompizParser(self.args.db).parse_db(), root)
            else:
                self.engine = CompizEngine(SimpleConfigCompizParser(db).parse_db(), root)
        return root

    def run(self):
        if self.args.coverity:
            self.renderer = CoverityRenderer(
                self.ostream, self.args.root
                if self.args.root else os.getcwd(), self.args.coverity_name)

        if self.args.show_db_path:
            print(self.args.db)
            exit(0)
        if self.args.component:
            self._findcomponent()
            exit(0)
        if self.args.name:
            self._findname()
            exit(0)
        if self.args.guild:
            self._findguild()
            exit(0)
        if self.args.all:
            self._findall()
            exit(0)
        self._findsection()


def main():
    CLI = CompizCli(sys.argv, sys.stdout)
    CLI.run()


if __name__ == '__main__':
    main()
