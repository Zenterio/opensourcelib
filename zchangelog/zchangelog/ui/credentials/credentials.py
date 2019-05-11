import click

from zchangelog.ui.credentials.default import default
from zchangelog.ui.credentials.remove import remove
from zchangelog.ui.credentials.store import store


@click.group(name='credentials', help='Handling credentials')
def credentials():
    pass


credentials.add_command(store)
credentials.add_command(remove)
credentials.add_command(default)
