import os

from invoke import task


class BuildDir(object):

    def __init__(self, build_dir='./build'):
        self._build_dir = build_dir

    @property
    def build_dir(self):
        return self._build_dir

    @property
    def debian_dir(self):
        return '{build_dir}/debian'.format(build_dir=self._build_dir)

    @property
    def dist_dir(self):
        return '{build_dir}/dist'.format(build_dir=self._build_dir)

    @property
    def pypi_dir(self):
        return '{build_dir}/pypi'.format(build_dir=self._build_dir)

    @property
    def doc_dir(self):
        return '{build_dir}/doc'.format(build_dir=self._build_dir)

    @property
    def test_dir(self):
        return '{build_dir}/test'.format(build_dir=self._build_dir)

    @property
    def coverage_dir(self):
        return '{build_dir}/coverage'.format(build_dir=self._build_dir)

    @property
    def requirements_dir(self):
        return '{build_dir}/requirements'.format(build_dir=self._build_dir)

    def templating_kwargs(self):
        relative_dirs = {
            'build_dir': self._build_dir,
            'debian_dir': self.debian_dir,
            'dist_dir': self.dist_dir,
            'pypi_dir': self.pypi_dir,
            'doc_dir': self.doc_dir,
            'test_dir': self.test_dir,
            'coverage_dir': self.coverage_dir,
            'requirements_dir': self.requirements_dir,
        }

        all_dirs = {}
        for name, dir in relative_dirs.items():
            all_dirs['{name}_abs'.format(name=name)] = os.path.abspath(dir)

        all_dirs.update(relative_dirs)
        return all_dirs


@task
def clean(ctx):
    ctx.run('rm -rf {dir}'.format(dir=ctx.build_dir.build_dir))
