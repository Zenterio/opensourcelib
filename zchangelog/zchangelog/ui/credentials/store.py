from getpass import getpass

import click

from zchangelog import credentials


@click.command(name='store')
@click.pass_context
def store(ctx):
    """
    Store credentials in ~/.config/zchangelog/ so that they can be used automatically in later calls to zchangelog.

    \b
    Examples
    zchangelog credentials store
    zchangelog --username <user> credentials store
    zchangelog --username <user> --password <pwd> credentials store
    """
    password = ctx.obj['password']
    if not password:
        password = getpass('LDAP Password for user \'{user}\': '.format(user=ctx.obj['username']))

    credentials.write_credentials(ctx.obj['username'], password)
