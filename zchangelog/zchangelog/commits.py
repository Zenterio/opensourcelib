import logging
import os
from re import match

from git import Repo

JIRA_ISSUE_ID_PATTERN = r'([A-Z0-9]+-[0-9]+)[:, ](.*)'

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_jira_issue_ids(repos, start, end):
    """
    Retrieve the jira id reference from the commit messages of all commits between the tags.

    :param repos: List of repositories
    :param start: Initial tag, or end tag if end is not given
    :param end: End tag. Optional
    :return: A set of jira issue keys
    """
    jira_issue_ids = set()
    for repo in repos:
        cur_repo = Repo(repo)
        if _refs_exist(cur_repo, start, end):
            issues = _get_jira_issue_ids(cur_repo, start, end)
            if issues:
                for issue in issues:
                    jira_issue_ids.add(issue)
    return jira_issue_ids


def _get_jira_issue_ids(cur_repo, start, end):
    if end is not None:
        rev = '{start}...{end}'.format(start=start, end=end)
    else:
        rev = '{start}'.format(start=start)
    commits = list(cur_repo.iter_commits(rev))
    result = []
    for commit in commits:
        jira_ref = match(JIRA_ISSUE_ID_PATTERN, commit.message)
        if jira_ref is not None:
            result.append(jira_ref.group(1))
    return result or None


def _refs_exist(repo, start, end):
    refs = [x.name for x in repo.refs]
    start_found = start in refs
    end_found = end in refs
    if not start_found:
        logger.warning(
            'Start point {start} not found in {repo}.'.format(start=start, repo=repo.working_dir))
    if end is not None and not end_found:
        logger.warning(
            'End point {end} not found in {repo}.'.format(end=end, repo=repo.working_dir))
    return start_found and (end_found or end is None)


def _find_repos(path):
    result = []
    for root, dirs, files in os.walk(path):
        if '.git' in dirs:
            result.append(root)
    return result
