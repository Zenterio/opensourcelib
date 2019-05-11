def filter_tickets(issues, jira_query, jira_filter_id, jira):
    """
    Filter list of issues based on a jira query or saved filter.

    :param issues: List of jira items
    :param jira_query: JQL string to filter with
    :param jira_filter_id: Jira filter to filter with
    :param jira: Jira instance to talk to
    :return:
    """
    jql = _generate_jql(jira, jira_filter_id, jira_query, issues)
    result = [x.key for x in jira.search_issues(jql, maxResults=0)]

    return result


def _generate_jql(jira, jira_filter_id, jira_query, jira_refs):
    filter_keys = []
    for ref in jira_refs:
        if ref:
            filter_keys.append('key = ' + ref)
    if jira_query:
        jql = '(' + jira_query + ')' + ' AND (' + ' OR '.join(filter_keys) + ')'
    elif jira_filter_id:
        jira_filter = jira.filter(jira_filter_id)
        jql = '(' + jira_filter.jql.split('ORDER BY')[0] + ')' + ' AND (' + ' OR '.join(
            filter_keys) + ')'
    else:
        jql = '(' + ' OR '.join(filter_keys) + ')'
    return jql
