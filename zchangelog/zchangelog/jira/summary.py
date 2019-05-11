import logging

from jira import JIRAError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_issue_summaries(refs, jira, show_issue_id):
    """
    Retrieve the 'summary' field for all jira tickets referenced in refs.

    :param refs: List of jira references
    :param jira: A jira connection instance
    :param show_issue_id: If the jira issue key should be included in the results
    :return: List of issue summaries, optionally with keys
    """
    results = []
    for ref in refs:
        try:
            result = {}
            issue = jira.issue(ref)
            if show_issue_id:
                result['issue_id'] = ref
            result['summary'] = issue.fields.summary
            # if show_executive_summary # TODO: ZMT-5938
            #   result['executive_summary'] = issue.fields.executive_summary
            results.append(result)
        except JIRAError as e:
            logger.warning(
                'Issue {ref} could not be found. Error: {error}'.format(ref=ref, error=e.text))
    return results
