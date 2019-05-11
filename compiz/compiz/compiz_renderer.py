class CompizRenderer(object):

    def __init__(self, verbosity, output):
        self.verbosity = verbosity
        self.output = output

    def renderFiles(self, entrylist):
        renderlist = self._renderlist(entrylist)
        self._renderentry(renderlist)

    def renderComponent(self, component, files, owner, guild):
        if self.verbosity == 2:
            premessage = 'Component "{name}" is owned by: \n{owner}\n{guild}\n'.format(
                name=component.name, owner=owner, guild=guild)
        elif self.verbosity == 1:
            premessage = '[{name}]\n{owner}\n{guild}\n'.format(
                name=component.name, owner=owner, guild=guild)
        else:
            premessage = '{owner}\n{guild}\n'.format(owner=owner, guild=guild)

        self.output.write(premessage)
        if self.verbosity == 2:
            self.output.write('\nFiles:\n')
            for file in files:
                self.output.write(file + '\n')
        separator = self._makeseparator()
        self.output.write(separator)

    def renderOwner(self, owner, components):
        if self.verbosity == 2:
            premessage = '{owner} is an owner in the following components: \n'.format(owner=owner)
            postmessage = '\n'
        elif self.verbosity == 1:
            premessage = '[{owner}]\n'.format(owner=owner)
            postmessage = '\n'
        else:
            premessage = ''
            postmessage = ''

        self.output.write(premessage)
        for component in components:
            self.output.write(component + '\n')
        self.output.write(postmessage)

    def renderGuild(self, guild, components):
        if self.verbosity == 2:
            premessage = '{guild} is an owner in the following components: \n'.format(guild=guild)
            postmessage = '\n'
        elif self.verbosity == 1:
            premessage = '[{guild}]\n'.format(guild=guild)
            postmessage = '\n'
        else:
            premessage = ''
            postmessage = ''

        self.output.write(premessage)
        for component in components:
            self.output.write(component + '\n')
        self.output.write(postmessage)

    def renderError(self, error):
        self.output.write(error + '\n')

    def finalize(self):
        pass

    def _renderlist(self, entrylist):
        renderlist = []
        for file, entries in entrylist.items():
            result = ''
            if self.verbosity == 0:
                for entry in entries:
                    for owner in entry.owner.split('\n'):
                        result += owner.split(', ')[1] + '\n'
                    for guild in entry.guild.split('\n'):
                        result += guild.split(', ')[1] + '\n'
            else:
                result += ('[{file}]\n'.format(file=file))
                for entry in entries:
                    result += (
                        'Component: {name}\nOwner: {owner}\nGuild: {guild}\n\n'.format(
                            owner=entry.owner, name=entry.name, guild=entry.guild))
                    if self.verbosity == 2:
                        result += (
                            'Files: \n{files}\n\n'
                            .format(files='\n'.join([pair[0] for pair in entry.files])))
            renderlist.append(result)
        return renderlist

    def _makeseparator(self):
        if self.verbosity == 1:
            separator = '\n'
        elif self.verbosity == 2:
            separator = '\n------------------------------------\n'
        else:
            separator = '\n'
        return separator

    def _renderentry(self, entrylist):
        separator = self._makeseparator()
        for entry in entrylist:
            self.output.write(entry + separator)
