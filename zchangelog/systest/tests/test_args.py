from zaf.component.decorator import requires


@requires(zchangelog='Zchangelog')
def test_start_tag_required(zchangelog):
    try:
        zchangelog('changelog', expected_exit_code=2)
    except AssertionError as e:
        assert 'Missing argument "start_tag"' in str(e)


@requires(zchangelog='Zchangelog')
def test_end_tag_not_required(zchangelog):
    try:
        zchangelog('changelog start_tag', expected_exit_code=3)
    except AssertionError as e:
        assert 'Start point start_tag not found in' in str(e)


@requires(zchangelog='Zchangelog')
def test_jira_query_and_filter_id_mutually_exclusive(zchangelog):
    try:
        zchangelog(
            'changelog start_tag end_tag --jira-query test --jira-filter-id 2',
            expected_exit_code=1)
    except AssertionError as e:
        print(str(e))
        assert 'Only one of --jira-query and --jira-filter-id allowed' in str(e)
