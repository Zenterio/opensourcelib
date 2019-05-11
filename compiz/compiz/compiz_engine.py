import fnmatch
import os
import re


class CompizEngine:

    def __init__(self, objlist, root):
        self.objlist = objlist
        self.root = root

    def _recursive_find_files(self, folder):
        """
        Recursively find all files.

        To get absolute paths back, make sure 'folder' is an absolute path.
        Only files are returned no directories.
        """
        paths = []
        for dir, _, files in os.walk(folder):
            for file in files:
                paths.append(os.path.join(dir, file))
        return paths

    def _find_matches(self, target):
        matches = []
        # Check if target is inside the root path
        match = re.search(self.root, target)
        bestmatch = 0
        bestprio = 0
        if match:
            # Remove root path part of target
            target = target[match.end() + 1:]
        else:
            raise FileNotInProjectPath
        for section in self.objlist:
            for file in self.objlist[section].files:
                filename = file[0]
                prio = file[1]

                # If filename is a folder and does not end with '/*' add this to the filename
                # effectively making these rules get the same prio: <dir>, <dir>/, <dir>/*
                if filename.endswith('/'):
                    filename = filename + '*'
                elif os.path.isdir(self.root + '/' + filename):
                    filename = filename + '/*'

                m = re.match(fnmatch.translate(filename), target)
                if m:
                    length = len(filename.replace('*', ''))

                    # If prio is higher, all other matches are obsolete.
                    if prio > bestprio:
                        del matches[:]
                        bestprio = prio
                        bestmatch = length
                        matches.append(self.objlist[section])
                    # If prio is the same and length is longer (more special match),
                    # all old matches are obsolete
                    elif length > bestmatch and prio == bestprio:
                        del matches[:]
                        bestmatch = length
                        matches.append(self.objlist[section])

                    elif length == bestmatch and prio == bestprio:
                        if self.objlist[section] not in matches:
                            matches.append(self.objlist[section])

        return matches

    def _find_parents(self, match, parents):
        result = [match]
        parent = match.parent
        while parents:
            if parent != 'None':
                result.append(self.objlist[parent])
                parent = self.objlist[parent].parent
                parents -= 1
            else:
                break
        return result

    def find(self, target, parents=0):
        target = os.path.abspath(target)
        if os.path.isdir(target):
            target += '/'
        if not os.path.exists(target):
            raise FileNotFoundError
        matches = self._find_matches(target)
        if len(matches) == 0:
            raise FileNotMatchedError
        if len(matches) == 1:
            matches = self._find_parents(matches[0], parents)
        else:
            result = []
            for match in matches:
                result += self._find_parents(match, parents)
            raise MultipleOwnersError(result, target)
        return matches

    def findsection(self, target):
        sections = []
        reObj = re.compile('^' + target + '$')
        for key in self.objlist.keys():
            if (reObj.match(key)):
                sections.append(self.objlist[key])
        return sections

    def findowner(self, owner):
        componentsperowner = {}
        reObj = re.compile('^' + owner + '$')
        for section in self.objlist:
            for sectionOwnerEntry in self.objlist[section].owner.split('\n'):
                ownername = str.split(sectionOwnerEntry, ',')[0]
                if (reObj.match(ownername)):
                    if ownername in componentsperowner:
                        componentsperowner[ownername].append(section)
                    else:
                        componentsperowner[ownername] = [section]
        return componentsperowner

    def findguild(self, guild):
        componentsperguild = {}
        reObj = re.compile('^' + guild + '$')
        for section in self.objlist:
            for sectionGuildEntry in self.objlist[section].guild.split('\n'):
                guildname = str.split(sectionGuildEntry, ',')[0]
                if (reObj.match(guildname)):
                    if guildname in componentsperguild:
                        componentsperguild[guildname].append(section)
                    else:
                        componentsperguild[guildname] = [section]
        return componentsperguild

    def findall(self):
        return list(self.objlist.values())

    def expandpaths(self, paths, name):
        pathList = []
        fileList = []

        allfiles = self._recursive_find_files(self.root)

        for path in paths:
            abspath = os.path.join(self.root, path)

            # If filename is a folder and does not end with '/*' add this to the filename
            # effectively making these rules get the same prio: <dir>, <dir>/, <dir>/*
            if abspath.endswith('/'):
                abspath = abspath + '*'
            elif os.path.isdir(abspath):
                abspath = abspath + '/*'

            # Find all files that match the file path rule
            reobj = re.compile(fnmatch.translate(abspath))
            for file in allfiles:
                if reobj.match(file):
                    pathList.append(file)

        # Check each file and see if it actually belongs to the component with 'name'
        for file in pathList:
            fileSection = []
            try:
                fileSection = self.find(file)
            except MultipleOwnersError as e:
                for section in e.args[0]:
                    fileSection += [section]
            for section in fileSection:
                if name in section.name:
                    fileList.append(file)
                    break
        return fileList


class MultipleOwnersError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class FileNotInProjectPath(Exception):
    pass


class FileNotMatchedError(Exception):
    pass
