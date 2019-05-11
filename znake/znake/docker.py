"""
Docker is used to allow testing and packaging Python projects in multiple environments.

Docker images are pulled from the Zenterio Docker registry (docker.zenterio.lan) and Znake
provides facilities for running tasks inside these containers.

.. autofunction:: docker_run

When running inside a Docker container, it is often neccessary to build a Python virtual
environment specifically for that container. For these purposes, a Docker volume intended
as storage for such environments is automatically created and mounted as the .venv directory.

.. autofunction:: create_venv_volume
"""
from contextlib import contextmanager

from invoke import Collection
from invoke.exceptions import UnexpectedExit


def docker_run(
        ctx,
        image,
        command,
        registry='docker.zenterio.lan/zenterio',
        interactive=False,
        use_volume=True):
    """
    Run a command in the target Docker environment.

    The specified image is pulled from the registry and
    """
    if image.startswith('docker.zenterio.lan'):
        full_image_name = image
    else:
        full_image_name = '/'.join([registry, image])

    docker_run_flags = ' '.join(ctx.znake.docker.run.flags)

    if ctx.core.args['root'].value is False:
        docker_run_flags += ' --user "$(id -u):$(id -g)"'
    if ctx.core.args['network'].value is not None:
        docker_run_flags += ' --network {nw}'.format(nw=ctx.core.args['network'].value)

    if interactive:
        docker_run_flags += ' -it'

    if ctx.core.args['no-pull'].value is False:
        _docker_pull(ctx, full_image_name)

    if use_volume:
        venv_volume_name = create_venv_volume(ctx, docker_run_flags, image)
        with ctx.prefix('export VENV_VOLUME_NAME={name} '.format(name=venv_volume_name)):
            return _docker_run(
                ctx, docker_run_flags, full_image_name, command, interactive=interactive)
    else:
        return _docker_run(ctx, docker_run_flags, full_image_name, command, interactive=interactive)


def get_venv_volume_name(ctx, image, root=False):
    package = ctx.znake.info.package
    root_suffix = '_root' if root else ''
    return '{package}_venv_volume_{image}{root_suffix}'.format(
        package=package, image=image, root_suffix=root_suffix).replace('/', '_').replace(':', '_')


def create_venv_volume(ctx, flags, image):
    """
    Create a Docker volume suitable for storing the Python virtual environment.

    If the Docker volume already exists, no action is taken.
    """
    volume_name = get_venv_volume_name(ctx, image, ctx.core.args['root'].value)
    with _deactivate_venv(ctx):
        try:
            ctx.run('docker inspect {volume_name}'.format(volume_name=volume_name), hide='stdout')
        except UnexpectedExit:
            ctx.run(
                'docker volume create {volume_name}'.format(volume_name=volume_name), hide='stdout')
            if not ctx.core.args['root'].value:
                _fixup_venv_volume_permissions(ctx, flags, image, volume_name)

    return volume_name


def clean_venv_volume(ctx, image):
    """Clean up a Docker volume."""
    volume_name = get_venv_volume_name(ctx, image, ctx.core.args['root'].value)
    ctx.run(
        'docker volume remove --force {volume_name}'.format(volume_name=volume_name), hide='stdout')


def _fixup_venv_volume_permissions(ctx, flags, image, volume_name):
    uid_and_gid = ctx.run('echo "$(id -u):$(id -g)"').stdout.strip()
    with ctx.prefix('export VENV_VOLUME_NAME={volume_name} '.format(volume_name=volume_name)):
        return _docker_run(
            ctx,
            '--mount type=volume,source=$(echo ${VENV_VOLUME_NAME}),target=$(pwd)/.venv --rm',
            'docker.zenterio.lan/ubuntu:16.04',
            'chown {uid_and_gid} \"$(pwd)/.venv\"'.format(uid_and_gid=uid_and_gid))


def _docker_pull(ctx, image, seen_images=[]):
    # Poor mans version of LRU cache. ctx is unfortunately an unhashable type.
    if image in seen_images:
        return
    with _deactivate_venv(ctx):
        result = ctx.run('docker pull {image}'.format(image=image))
        seen_images.append(image)
        return result


@contextmanager
def _deactivate_venv(ctx):
    """
    Deactivate the virtual environment in the current context.

    The docker command does not require the local venv even though
    the venv should be used inside docer.
    """
    before = ctx.command_prefixes
    without_activate = [prefix for prefix in before if prefix != 'source .venv/bin/activate']
    ctx.command_prefixes = without_activate
    yield
    ctx.command_prefixes = before


def _docker_run(ctx, flags, image, command, interactive=False):
    with _deactivate_venv(ctx):
        return ctx.run(
            'docker run {flags} {image} {command}'.format(
                flags=flags, image=image, command=command),
            pty=interactive)


def get_namespace(config):
    namespace = Collection('docker')
    return namespace
