import json
from tempfile import TemporaryDirectory

from zaf.component.decorator import component, requires


@component
class Sut(object):

    def __init__(self):
        pass

    @property
    def ip(self):
        return 'localhost'


SERVER_INFO = json.dumps({
    'versionNumbers': [7, 11, 1],
}).encode('utf-8')

FIELD = json.dumps([{
    'id': 'summary',
}]).encode('utf-8')

TEST1 = json.dumps({'fields': {'summary': 'summary 1'}}).encode('utf-8')

TEST2 = json.dumps({'fields': {'summary': 'summary 2'}}).encode('utf-8')

TEST3 = json.dumps({'fields': {'summary': 'summary 3'}}).encode('utf-8')

SEARCH = json.dumps(
    {
        'startAt':
        0,
        'maxResults':
        50,
        'total':
        0,
        'issues': [
            {
                'id': '72074',
                'self': 'https://jira.zenterio.lan/rest/api/2/issue/72074',
                'key': 'PRZ-7044',
                'fields': {
                    'summary': 'summary 2'
                }
            }
        ]
    })


@requires(Git='GitRepo', instance=False)
@requires(server='HttpFileServer')
@requires(zchangelog='Zchangelog')
def test_generate_changelog_with_two_branches_uses_commits_since_first_branch(
        Git, server, zchangelog):
    server.serve_data('/rest/api/2/serverInfo', data=SERVER_INFO)
    server.serve_data('/rest/api/2/field', data=FIELD)
    server.serve_data('/rest/api/2/issue/TEST-1', data=TEST1)
    server.serve_data('/rest/api/2/issue/TEST-2', data=TEST2)
    server.serve_data('/rest/api/2/issue/TEST-3', data=TEST3)
    with TemporaryDirectory() as workspace:
        with Git.temporary_init() as origin:
            last_commit_of_first_branch = origin.add_commit('TEST-1: test')
            origin.add_branch('release1', last_commit_of_first_branch)
            origin.add_commit('TEST-2: test')
            last_commit_of_second_branch = origin.add_commit('TEST-3: test')
            origin.add_branch('release2', last_commit_of_second_branch)
            zchangelog(
                '--repo {path} --password test changelog --server {url} --txt {text} release1 release2'.
                format(path=origin.path, url=server.base_url, text=workspace + '/changelog.txt'))
        changelog = open(workspace + '/changelog.txt').read()
        assert 'summary 1' not in changelog
        assert 'summary 2' in changelog
        assert 'summary 3' in changelog


@requires(Git='GitRepo', instance=False)
@requires(server='HttpFileServer')
@requires(zchangelog='Zchangelog')
def test_generate_changelog_with_only_second_branch_specified_gets_commits_from_start(
        Git, server, zchangelog):
    server.serve_data('/rest/api/2/serverInfo', data=SERVER_INFO)
    server.serve_data('/rest/api/2/field', data=FIELD)
    server.serve_data('/rest/api/2/issue/TEST-1', data=TEST1)
    server.serve_data('/rest/api/2/issue/TEST-2', data=TEST2)
    server.serve_data('/rest/api/2/issue/TEST-3', data=TEST3)
    with TemporaryDirectory() as workspace:
        with Git.temporary_init() as origin:
            last_commit_of_first_branch = origin.add_commit('TEST-1: test')
            origin.add_branch('release1', last_commit_of_first_branch)
            origin.add_commit('TEST-2: test')
            last_commit_of_second_branch = origin.add_commit('TEST-3: test')
            origin.add_branch('release2', last_commit_of_second_branch)
            zchangelog(
                '--repo {path} --password test changelog --server {url} --txt {text} release2'.
                format(path=origin.path, url=server.base_url, text=workspace + '/changelog.txt'))
        changelog = open(workspace + '/changelog.txt').read()
        assert 'summary 1' in changelog
        assert 'summary 2' in changelog
        assert 'summary 3' in changelog
