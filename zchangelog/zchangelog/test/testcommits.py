import os
from tempfile import TemporaryDirectory

from zchangelog.commits import _find_repos


def test_find_repos_finds_repos():
    with TemporaryDirectory() as tmpdir:
        top = os.path.join(tmpdir, 'top_repo')
        subrepo = os.path.join(top, 'subrepo')
        notrepo = os.path.join(top, 'not_a_repo')
        subsubrepo = os.path.join(top, notrepo, 'subsubrepo')
        expected_result = {
            os.path.join(tmpdir, top),
            os.path.join(tmpdir, subrepo),
            os.path.join(tmpdir, subsubrepo)
        }
        os.makedirs(os.path.join(top, '.git'))
        os.makedirs(os.path.join(subrepo, '.git'))
        os.makedirs(notrepo)
        os.makedirs(os.path.join(subsubrepo, '.git'))
        res = set(_find_repos(top))
        assert res == expected_result
