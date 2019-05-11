import click

from zchangelog import credentials


@click.command(name='remove')
@click.option(
    '--all',
    '-a',
    help='Remove all credentials instead of only the one for the specified user',
    is_flag=True)
@click.pass_context
def remove(ctx, all):
    """
    Remove credentials in ~/.config/zchangelog/ for either the specified user or for all users.

    \b
    Examples
    zchangelog credentials remove
    zchangelog --username <user> credentials remove
    zchangelog credentials remove --all
    """
    # retrieving from parameter because host_info is already overwritten
    # with old password from credential file
    credentials.remove_credentials(ctx.obj['username'], all)
