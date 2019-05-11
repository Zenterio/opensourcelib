import getpass
import logging
import os

import click
import coloredlogs

import zchangelog
from zchangelog.credentials import read_credentials, read_default_username
from zchangelog.ui.credentials.credentials import credentials

from .changelog import changelog


def _get_default_ldap_username():
    username = read_default_username()
    if username is None:
        username = getpass.getuser()
    return username


CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(zchangelog.__version__)
@click.option(
    '-u',
    '--username',
    type=str,
    default=_get_default_ldap_username(),
    help='Jira username',
    show_default=True)
@click.option(
    '-p',
    '--password',
    type=str,
    default=None,
    help='The password to use to connect to jira. Will prompt if not supplied')
@click.option(
    '--repo',
    type=str,
    default=[os.getcwd()],
    multiple=True,
    help='The top folder of the repo to operate on, default current working directory',
    show_default=True)
@click.option(
    '-v',
    '--verbose',
    count=True,
    type=click.IntRange(0, 2, clamp=True),
    help='Increase output verbosity.')
@click.pass_context
def main(ctx, username, password, repo, verbose):
    verbosity_levels = (logging.WARNING, logging.INFO, logging.DEBUG)
    coloredlogs.install(level=verbosity_levels[verbose])
    if password is None:
        password = read_credentials(username)
    ctx.obj = {'repo': repo, 'username': username, 'password': password}


main.add_command(changelog)
main.add_command(credentials)
