"""Extension providing functionality for generating and displaying application changelog."""
import importlib
from collections import namedtuple

from zaf.application import APPLICATION_CHANGELOG_TYPE, APPLICATION_ROOT
from zaf.builtin.changelog import CHANGELOG_CHANGES, CHANGELOG_DATE, CHANGELOG_VERSION, \
    ChangeLogType
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, ExtensionConfig, \
    FrameworkExtension


@FrameworkExtension('changelog', load_order=9, groups=['changelog'])
class ChangeLogExtension(AbstractExtension):
    """Handles default configuration for the changelog."""

    def get_config(self, config, requested_config_options, requested_command_config_options):
        changelog_type = config.get(APPLICATION_CHANGELOG_TYPE)
        changelog_config = {}

        if changelog_type == ChangeLogType.ZNAKE:

            root_package = config.get(APPLICATION_ROOT)
            version_module_name = '{root}.version'.format(root=root_package)
            version_module = importlib.import_module(version_module_name)

            versions = []
            changelog_config = {}
            for version_info in version_module.changelog:
                version = version_info['version']
                versions.append(version)
                changelog_config['.'.join(['changelog', version, 'date'])] = version_info['date']
                changelog_config['.'.join(['changelog', version,
                                           'changes'])] = version_info['changes']

            changelog_config['changelog.versions'] = versions

        if changelog_type != ChangeLogType.NONE:
            changelog_config['ext.changelogcommand.enabled'] = True

        return ExtensionConfig(
            changelog_config,
            priority=9,
        )


VersionInfo = namedtuple('VersionInfo', ['version', 'date', 'short_date', 'changes'])


@component(name='ChangeLog', provided_by_extension='changelog')
@requires(config='Config')
class ChangeLog(object):

    def __init__(self, config):
        self._config = config

    @property
    def changelog(self):
        changelog = []
        for version in self._config.get(CHANGELOG_VERSION):
            date = self._config.get(CHANGELOG_DATE, entity=version)
            short_date = ' '.join(date.split(' ')[0:4])
            changelog.append(
                VersionInfo(
                    version=version,
                    date=date,
                    short_date=short_date,
                    changes=self._config.get(CHANGELOG_CHANGES, entity=version),
                ))
        return changelog


@CommandExtension(
    'changelog',
    extends=['changelog'],
    config_options=[
        ConfigOption(CHANGELOG_VERSION, required=False, instantiate_on=CHANGELOG_VERSION),
        ConfigOption(CHANGELOG_DATE, required=False),
        ConfigOption(CHANGELOG_CHANGES, required=False),
    ],
    default_enabled=False,
    groups=['changelog'])
class ChangeLogConfigExtension(AbstractExtension):
    """Provides changelog configurability to commands that needs it."""
    pass
