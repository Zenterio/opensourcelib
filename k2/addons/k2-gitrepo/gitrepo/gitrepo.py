"""
A wrapper around the GitPython module.

Provides a component that holds a GitPython Repo instance and provides some helper methods for interacting with it

"""

import datetime
import logging
import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from zaf.component.decorator import component
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'gitrepo'))
logger.addHandler(logging.NullHandler())


@component(provided_by_extension='gitrepo')
class GitRepo(object):
    """A helper/wrapper component around the GitPython module."""

    def __init__(self, repodir, remote_name=None):
        from git import Repo

        self.path = repodir
        self.remote_name = remote_name
        self.repo = Repo.init(repodir)
        self.user = None

    @classmethod
    def clone(cls, repodir, original, remote_name='origin'):
        """
        Make a clone of a GitRepo into a different directory.

        :param repodir: Directory to clone into
        :param original: GitRepo to clone
        :param remote_name: The remote name of the original in the clone
        :return: the new GitRepo instance
        """
        original.repo.clone(repodir, origin=remote_name)
        return GitRepo(repodir, remote_name=remote_name)

    @classmethod
    @contextmanager
    def temporary_init(cls, remote_name=None):
        """
        Create an empty GitRepo in a temporary directory. Acts as a context manager.

        :param remote_name: Name of remote.
        :return: The GitRepo instance
        """
        with TemporaryDirectory() as repodir:
            yield GitRepo(repodir, remote_name=remote_name)

    @classmethod
    @contextmanager
    def temporary_clone(cls, original, remote_name='origin'):
        """
        Create a clone of a GitRepo in a temporary directory. Acts as a context manager.

        :param original: GitRepo to clone
        :param remote_name: The remote name of the original in the clone
        :return: the new GitRepo instance
        """
        with TemporaryDirectory() as repodir:
            yield GitRepo.clone(repodir, original, remote_name=remote_name)

    def set_user(self, user='test', email='test@test'):
        from git import Actor

        self.user = Actor(user, email)
        config = self.repo.config_writer()
        config.set_value('user', 'name', user)
        config.set_value('user', 'email', email)
        config.release()

    def add_branch(self, branch, commit='HEAD', push=False):
        """
        Add a branch to the repo.

        :param branch: The name of the branch
        :param commit: The commit the branch should point to
        :param push: if True, push the branch to the configured remote
        """
        self.repo.git.branch(branch, commit)
        if push and self.remote_name:
            self.repo.git.push(self.remote_name, branch)

    def show_branches(self):
        """Return a list of branches in the repo."""
        return [str(x) for x in self.repo.heads]

    def add_commit(self, message, days_old=0):
        """
        Add a commit to the repo.

        :param message: The commit message
        :param days_old: How many days old the commit should be
        :return: the commit object
        """
        now = datetime.datetime.now() - datetime.timedelta(days_old)
        now = now.isoformat().split('.')[0]
        commit = self.repo.index.commit(
            message, author_date=now, commit_date=now, committer=self.user)
        self.repo.index.write()
        return commit

    def create_and_add_file(self, file):
        """
        Touch and stage a file in the repo.

        :param file: the relative path to the file. Intermediate directories are created
        """
        path = os.path.join(self.path, file)
        basedir = os.path.dirname(path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        open(path, 'x').close()
        self.repo.git.add(file)


@FrameworkExtension(name='gitrepo', config_options=[], endpoints_and_messages={})
class GitRepoAddon(AbstractExtension):

    def __init__(self, config, instances):
        pass
