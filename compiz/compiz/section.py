class Section(object):

    def __init__(
            self, name='None', owner='None', guild='None', parent='None', files='None',
            default_prio=0):
        self.name = name
        self.owner = owner
        self.guild = guild
        self.parent = parent
        self.files = []
        for file in files:
            fp = file.split(':')
            if len(fp) == 2:
                self.files.append((fp[0], int(fp[1])))
            elif len(fp) == 1:
                self.files.append((file, default_prio))
            else:
                raise IOError(
                    'Illegal prio syntax "{file}". Max one colon per line allowed.'.format(
                        file=file))

    def __repr__(self):
        return 'Name: {name} \n Owner: {owner} \n Guild: {guild} \n Parent: ' \
               '{parent} \n Files: \n {files} \n'\
            .format(name=self.name, owner=self.owner, guild=self.guild,
                    parent=self.parent, files=self.files)
