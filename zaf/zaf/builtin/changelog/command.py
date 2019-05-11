"""Extension providing the changelog command."""
from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.extensions.extension import AbstractExtension, FrameworkExtension


@requires(changelog='ChangeLog')
def changelog(application, changelog):
    """Print the changelog."""

    for version_info in reversed(changelog.changelog):
        print('{version}: {date}'.format(version=version_info.version, date=version_info.date))
        print()
        for change in version_info.changes:
            print(' ', change)
        print()


CHANGELOG_COMMAND = CommandId(
    'changelog', changelog.__doc__, changelog, config_options=[], uses=['changelog'])


@FrameworkExtension(
    'changelogcommand', commands=[CHANGELOG_COMMAND], default_enabled=False, groups=['changelog'])
class ChangeLogCommandExtension(AbstractExtension):
    """Providing the changelog command."""
    pass
