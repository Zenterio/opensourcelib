import logging
import sys

import click

from zchangelog.commits import get_jira_issue_ids
from zchangelog.jira.filter import filter_tickets
from zchangelog.jira.server import connect_to_jira
from zchangelog.jira.summary import get_issue_summaries
from zchangelog.output import write_changelog

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@click.command('changelog')
@click.option(
    '--show-issue-id',
    is_flag=True,
    required=False,
    default=False,
    help='Can be turned on to include jira issue ID in output')
@click.option(
    '--jira-query',
    type=str,
    required=False,
    default=None,
    help='JQL search string to generate list of allowed tickets.')
@click.option(
    '--jira-filter-id',
    type=int,
    required=False,
    default=None,
    help='ID of a jira filter to list allowed tickets. To find a filter ID,'
    'look for \'filter=NUM\' in the url in jira when viewing the filter')
@click.option(
    '--json', type=str, default=None, help='json file to put results in', show_default=True)
@click.option('--xml', type=str, default=None, help='xml file to put results in', show_default=True)
@click.option(
    '--txt', type=str, default=None, help='text file to put results in', show_default=True)
@click.option(
    '--server',
    type=str,
    default='https://jira.zenterio.lan',
    help='Jira instance to get summaries from',
    show_default=True)
@click.argument(
    'start_tag',
    type=str,
    required=True,
)
@click.argument('end_tag', required=False, default=None)
@click.pass_context
def changelog(
        ctx, show_issue_id, jira_query, jira_filter_id, json, xml, txt, server, start_tag, end_tag):
    """Retrieve Jira summaries for tickets referenced in the commits between two tags."""
    if jira_query and jira_filter_id:
        print('Only one of --jira-query and --jira-filter-id allowed', file=sys.stderr)
        exit(1)
    issue_ids = get_jira_issue_ids(ctx.obj['repo'], start_tag, end_tag)
    if len(issue_ids) == 0:
        logger.error('No jira references were found, exiting')
        exit(3)
    jira = connect_to_jira(ctx.obj['username'], ctx.obj['password'], server)
    if jira_query or jira_filter_id:
        issue_ids = filter_tickets(issue_ids, jira_query, jira_filter_id, jira)
    descriptions = get_issue_summaries(issue_ids, jira, show_issue_id)

    write_changelog(descriptions, start_tag, end_tag, json, txt, xml)
