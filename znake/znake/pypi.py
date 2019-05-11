"""
Znake provides facilities for creating Debian packages.

Each Debian package targets a specific architecture and environment.
Each environment is defined as a Docker container and is assumed to have all
neccessary tools pre-installed.

.. autofunction:: pypi
.. autofunction:: sdist
.. autofunction:: wheel
.. autofunction:: clean
"""
from invoke import Collection, call, task

from .util import run, skip_if_up_to_date
from .venv import create_venv


@task
def clean(ctx):
    """Remove all Pypi packaging build artifacts."""
    ctx.run('rm -rf {dir}'.format(dir=ctx.build_dir.pypi_dir))


@task(pre=[call(create_venv, target={'name': 'local', 'image': 'local'})])
def sdist(ctx):
    """Build a pypi sdist package."""
    skip_if_up_to_date(
        '{pypi_dir}/sdist'.format(pypi_dir=ctx.build_dir.pypi_dir))(_build_sdist_package)(
            ctx)


@task(
    pre=[
        call(
            create_venv,
            target={
                'image': 'docker.zenterio.lan/pypa/manylinux1_x86_64:latest',
                'interpreter': '/opt/python/cp36-cp36m/bin/python3'
            }),
    ])
def wheel(ctx):
    """Build a pypi wheel."""
    skip_if_up_to_date(
        '{pypi_dir}/wheel'.format(pypi_dir=ctx.build_dir.pypi_dir))(_build_wheel_package)(
            ctx)


@task(default=True, pre=[sdist, wheel])
def pypi(ctx):
    pass


def _build_sdist_package(ctx):
    run(ctx, 'local', _render_build_sdist_package_command(ctx), use_venv=True)


def _build_wheel_package(ctx):
    run(
        ctx,
        'docker.zenterio.lan/pypa/manylinux1_x86_64:latest',
        _render_build_bdist_package_command(ctx),
        use_venv=True)


def _render_build_sdist_package_command(ctx):
    return 'mkdir -p {pypi_dir}/sdist && python3 setup.py sdist -d {pypi_dir}/sdist && touch {pypi_dir}/sdist'.format(
        pypi_dir=ctx.build_dir.pypi_dir)


def _render_build_bdist_package_command(ctx):
    return (
        'mkdir -p {pypi_dir}/wheel && python3 setup.py bdist_wheel '
        '-d {pypi_dir}/wheel && touch {pypi_dir}/wheel').format(pypi_dir=ctx.build_dir.pypi_dir)


def get_namespace(config):
    namespace = Collection('pypi')

    namespace.add_task(pypi)
    namespace.add_task(wheel)
    namespace.add_task(sdist)
    namespace.add_task(clean)
    return namespace
