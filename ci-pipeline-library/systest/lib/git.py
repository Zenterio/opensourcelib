import os
import shutil
from tempfile import TemporaryDirectory

from zaf.component.decorator import component, requires


@component(name='GitBareRepo', scope='session')
@requires(process_runner='ProcessRunner')
class GitBareRepo(object):
    """Creates a bare repo with the path given as the first arg."""

    def __init__(self, path, process_runner):
        self._path = os.path.abspath(path)
        self._process_runner = process_runner

    @property
    def path(self):
        return self._path

    def __enter__(self):
        self._process_runner('git init --bare {path}'.format(path=self._path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._path)

    def clone(self, into_dir):
        self._process_runner(
            'git clone {bare_repo} {repo_dir}'.format(bare_repo=self._path, repo_dir=into_dir))
        self._process_runner('git config user.email "you@example.com"', cwd=into_dir)
        self._process_runner('git config user.name "Your Name"', cwd=into_dir)


@component(name='SystemUnderTestRepo', scope='session')
@requires(bare_repo=GitBareRepo, args=['systest/data/repos/ci-pipeline-library.git'])
@requires(process_runner='ProcessRunner')
class SystemUnderTestRepo(object):
    """
    Creates a repo with the files from the system under test.

    This copies the vars and Jenkinsfile from the ci-pipeline-library repo into
    a new bare repo that will be used as the Jenkinsfile system library in the
    the test Jenkins.
    """

    def __init__(self, bare_repo, process_runner):
        self._bare_repo = bare_repo
        self._process_runner = process_runner

    def __enter__(self):
        with TemporaryDirectory() as dir:
            repo_dir = os.path.join(dir, 'ci-pipeline-library')
            self._bare_repo.clone(repo_dir)
            vars_path = os.path.join(repo_dir, 'vars')
            shutil.copytree('vars', vars_path)
            jenkinsfile_path = os.path.join(repo_dir, 'Jenkinsfile')
            shutil.copy2('Jenkinsfile', jenkinsfile_path)
            self._process_runner('git add {vars_path}'.format(vars_path=vars_path), cwd=repo_dir)
            self._process_runner(
                'git commit -m "Creating initial content in repo from current project"',
                cwd=repo_dir)
            self._process_runner('git push origin master', cwd=repo_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@component(name='JenkinsFileBareRepo', scope='session')
@requires(bare_repo=GitBareRepo, args=['systest/data/repos/systest-job.git'])
@requires(process_runner='ProcessRunner')
class JenkinsFileBareRepo(object):
    """Creates a bare repo that will be used to run test the different pipeline variants."""

    def __init__(self, bare_repo, process_runner):
        self._bare_repo = bare_repo
        self._process_runner = process_runner

    def __enter__(self):
        with TemporaryDirectory() as dir:
            repo_dir = os.path.join(dir, 'systest-job')
            self._bare_repo.clone(repo_dir)
            activate_path = os.path.join(repo_dir, 'activate')
            open(activate_path, 'w').close()
            self._process_runner(
                'git add {activate_path}'.format(activate_path=activate_path), cwd=repo_dir)
            self._process_runner('git commit -m "Adding default repo files"', cwd=repo_dir)
            self._process_runner('git push origin master', cwd=repo_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def clone(self, into_dir):
        self._bare_repo.clone(into_dir)

    @property
    def path(self):
        return self._bare_repo.path


@component(name='JenkinsFileRepo', scope='test')
@requires(bare_repo=JenkinsFileBareRepo)
@requires(context='ComponentContext')
@requires(process_runner='ProcessRunner')
class JenkinsFileRepo(object):
    """
    Component that is used to update the Jenkinsfile used by the different tests.

    This creates test case specific branches to be able to support parallel tests.
    """

    def __init__(self, branch=None, bare_repo=None, context=None, process_runner=None):
        self._bare_repo = bare_repo
        self._context = context
        self._process_runner = process_runner
        if branch:
            self._branch_root = branch
        else:
            self._branch_root = context.callable_name

    @property
    def branch(self):
        if self._context.kwargs and 'step' in self._context.kwargs:
            return self._branch_root + '_' + self._context.kwargs['step']
        else:
            return self._branch_root

    def update_jenkins_file(self, content, header="@Library('ci-pipeline-library') _"):
        self.update_file(
            'Jenkinsfile', '{header}\n{content}'.format(header=header, content=content))

    def update_file(self, file, content):
        with TemporaryDirectory() as dir:
            repo_dir = os.path.join(dir, 'systest-job')
            self._bare_repo.clone(repo_dir)

            self._process_runner(
                'git checkout {branch} || git checkout -b {branch}'.format(branch=self.branch),
                cwd=repo_dir)

            path = os.path.join(repo_dir, file)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())

            self._process_runner('git add {path}'.format(path=path), cwd=repo_dir)
            self._process_runner(
                'git commit -m "Changing Jenkinsfile on branch {branch}"'.format(
                    branch=self.branch),
                cwd=repo_dir)
            self._process_runner(
                'git push -f origin {branch}'.format(branch=self.branch), cwd=repo_dir)
