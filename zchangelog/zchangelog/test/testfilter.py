from unittest.mock import MagicMock, call, patch

from zchangelog.jira.filter import _generate_jql, filter_tickets


def test_generate_jql_no_filter_ORs_keys():
    refs = ['test1', 'test2']
    expected_result = '(key = test1 OR key = test2)'
    result = _generate_jql(None, None, None, refs)
    assert result == expected_result


def test_generate_jql_ANDs_with_given_filter():
    refs = ['test1', 'test2']
    filter = 'project = TEST'
    expected_result = '(project = TEST) AND (key = test1 OR key = test2)'
    result = _generate_jql(None, None, filter, refs)
    assert result == expected_result


def test_generate_jql_with_filter_id_gets_from_jira_and_removes_order_by():
    jira = MagicMock()
    jira.filter = MagicMock()
    filter = MagicMock()
    filter.jql = 'project = TEST ORDER BY desc'
    jira.filter.return_value = filter
    refs = ['test1', 'test2']
    expected_result = '(project = TEST ) AND (key = test1 OR key = test2)'
    result = _generate_jql(jira, 3, None, refs)
    assert result == expected_result
    jira.filter.assert_called_once_with(3)


def test_filter_tickets_generates_jql_and_searches_jira():
    jira = MagicMock()
    mock_issue = MagicMock()
    mock_issue.key = 'fake jira search result'
    jira.search_issues.return_value = [mock_issue]
    issues = ['issue1', 'issue2', 'issue3', 'issue4']
    expected_result = ['fake jira search result']
    with patch('zchangelog.jira.filter._generate_jql') as mock_jql:
        mock_jql.return_value = 'test'
        result = filter_tickets(issues, None, None, jira)
        assert result == expected_result
        mock_jql.assert_has_calls(
            [
                call(jira, None, None, ['issue1', 'issue2', 'issue3', 'issue4']),
            ])
