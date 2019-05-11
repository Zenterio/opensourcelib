import fnmatch
import json
import os
import re
from collections import OrderedDict


class CoverityComponent(object):

    def __init__(self, name):
        self._name = name

    def to_coverity(self):
        return OrderedDict([
            ('name', self.name),
            ('defaultOwner', None),
            ('rbacSettings', []),
        ])

    @property
    def name(self):
        return re.sub(r"""[./\s*'":`]""", '_', self._name.lower())


class CoverityFileRule(object):

    def __init__(self, root, component, file_rule, prio):
        self.root = root
        self.component = component
        self._file_rule = file_rule
        self.prio = prio

    def to_coverity(self):
        return OrderedDict(
            [
                ('componentName', self.component.name),
                ('pathPattern', self.as_regex()),
            ])

    def as_regex(self):
        """
        Convert the file rule from fnmatch syntax to a regex.

        Also replaces a lot of unnecessarily escaped characters to clean up
        the regex and make it more readable.

        :return: regex version of the file rule
        """
        path = self._file_rule
        prefix = os.path.basename(self.root)

        if path.endswith('/'):
            path = path + '*'
        elif os.path.isdir(os.path.join(self.root, path)):
            path = path + '/*'

        if not path.startswith('*') or path == '*' or path == '*.*':
            path = '*/' + prefix + '/' + path
        else:
            path = '*/' + path

        regex = fnmatch.translate(path)
        regex = regex.replace(r'\Z(?ms)', r'')  # Remove ugly suffix
        regex = regex.replace(r'(?s:', r'')  # Remove 3.6 prefix
        regex = regex.replace(r')\\Z', r'')  # Remove 3.6 suffix
        regex = regex.replace(r')\Z', r'')  # Remove 3.6 suffix
        regex = regex.replace(r'\/', r'/')  # Slash doesn't need to be escaped when used in this way
        regex = regex.replace(r'.*\..*', r'[^/]*\.[^/]*')  # *.* shouldn't match slashes
        regex = regex.replace(
            r'\-', r'-')  # Dash does not need to be escaped outside of character groups
        regex = regex.replace(r'.*\.', r'[^/]*\.')  # *.<name> should not match slashes
        regex = regex.replace(r'\..*', r'\.[^/]*')  # <name>.* should not match slashes

        return regex


class CoverityRenderer(object):

    def __init__(self, output, root, component_list_name):
        self.root = root
        self.output = output
        self.component_list_name = component_list_name
        self._coverity_components = []
        self._coverity_file_rules = []

    def renderFiles(self, entrylist):
        raise NotImplementedError()

    def renderComponent(self, component, files, owner, guild):
        coverity_component = CoverityComponent(component.name)
        self._coverity_components.append(coverity_component)
        for file_rule, prio in component.files:
            if file_rule is not None and file_rule != 'None':
                self._coverity_file_rules.append(
                    CoverityFileRule(self.root, coverity_component, file_rule, prio))

    def renderOwner(self, owner, components):
        raise NotImplementedError()

    def renderGuild(self, guild, components):
        raise NotImplementedError()

    def renderError(self, error):
        self.output.write(error + '\n')

    def _renderlist(self, entrylist):
        raise NotImplementedError()

    def _makeseparator(self):
        raise NotImplementedError()

    def _renderentry(self, entrylist):
        raise NotImplementedError()

    def finalize(self):
        data = self._default_data()
        data['components'].extend(
            [
                cov_comp.to_coverity()
                for cov_comp in sorted(self._coverity_components, key=lambda c: c.name)
            ])
        data['fileRules'].extend(
            [
                file_rule.to_coverity()
                for file_rule in sorted(
                    self._coverity_file_rules,
                    key=lambda f: (f.prio, len(f.as_regex())),
                    reverse=True)
            ])

        self.output.write(json.dumps(data, indent=4))

    def _default_data(self):
        return OrderedDict(
            [
                ('version', 1), ('name', self.component_list_name), (
                    'description',
                    '{name} Compiz file map'.format(name=os.path.basename(self.root).capitalize())),
                ('forceDeleteComponents', True), (
                    'components', [
                        {
                            'name':
                            '3pp code',
                            'defaultOwner':
                            None,
                            'rbacSettings': [
                                {
                                    'groupOrUser': 'group',
                                    'principalName': 'System Administrators',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'user',
                                    'principalName': 'testuser',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'group',
                                    'principalName': 'Users',
                                    'roles': ['noAccess']
                                }
                            ]
                        }, {
                            'name':
                            'Intermediate',
                            'defaultOwner':
                            None,
                            'rbacSettings': [
                                {
                                    'groupOrUser': 'group',
                                    'principalName': 'System Administrators',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'user',
                                    'principalName': 'testuser',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'group',
                                    'principalName': 'Users',
                                    'roles': ['noAccess']
                                }
                            ]
                        }, {
                            'name':
                            'Other',
                            'defaultOwner':
                            None,
                            'rbacSettings': [
                                {
                                    'groupOrUser': 'group',
                                    'principalName': 'System Administrators',
                                    'roles': ['sysAdmin']
                                }, {
                                    'groupOrUser': 'user',
                                    'principalName': 'testuser',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'group',
                                    'principalName': 'Users',
                                    'roles': ['noAccess']
                                }
                            ]
                        }, {
                            'name':
                            'ooipf',
                            'defaultOwner':
                            None,
                            'rbacSettings': [
                                {
                                    'groupOrUser': 'group',
                                    'principalName': 'System Administrators',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'user',
                                    'principalName': 'testuser',
                                    'roles': ['observer']
                                }, {
                                    'groupOrUser': 'group',
                                    'principalName': 'Users',
                                    'roles': ['noAccess']
                                }
                            ]
                        }
                    ]), (
                        'fileRules', [
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/usr/include/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/pf/crypt/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/base/m2mhandler/crypt/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/build/.*/modules/base.m2mhandler/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/host-tools/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/3pp/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/build/.*/modules/3pp\\..*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/build/.*/modules/.*\\.3pp\\..*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/sysroot/usr/include/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/sysroot/usr/share/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/zac/thrift/gen-cpp/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/build/.*/modules/pf\\.proto/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/zids/build/.*/modules/pf/proto/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/usr/local/share/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/usr/lib/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/tmp/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/output/external-toolchain/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/opt/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/cov-intermediate/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '/home/hudson/coverity/temp-.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/output/host/usr/share/cmake-2.8/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/ztart-unified/all-builds/3pp-src/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/ztart-unified/.*/gmock.*/.*'
                            },
                            {
                                'componentName': '3pp code',
                                'pathPattern': '.*/ztart-unified/all-builds/.*/gen/.*'
                            },
                            {
                                'componentName': 'Intermediate',
                                'pathPattern': '/intermediate/emit/.*'
                            },
                            {
                                'componentName':
                                'ooipf',
                                'pathPattern':
                                '.*/zids/build/.*/modules/externals.plenty.jsplugins.oipf.ooipf/.*'
                            },
                        ])
            ])
