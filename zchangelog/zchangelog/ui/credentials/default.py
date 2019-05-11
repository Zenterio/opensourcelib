import click

from zchangelog import credentials


@click.command(name='default')
@click.pass_context
def default(ctx):
    """
    Store a default username in ~/.config/zchangelog/.

    This name is used automatically in later calls to zchangelog if no explicit username is provided.

    \b
    Examples
    zchangelog --username <user> credentials default
    """
    credentials.write_default_username(ctx.obj['username'])
