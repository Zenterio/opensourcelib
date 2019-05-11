import logging
import os
import signal
import sys
import termios

import coloredlogs
import invoke.exceptions
from invoke import Collection, Program, task
from invoke.parser import Argument

import znake.baseline
import znake.builddir
import znake.deb
import znake.debtest
import znake.doc
import znake.docker
import znake.format
import znake.pypi
import znake.static
import znake.systest
import znake.test
import znake.venv
from znake import __version__
from znake.util import ParallelExecutor, ZnakeConfig


@task(pre=[znake.deb.clean, znake.doc.clean, znake.builddir.clean])
def clean(ctx):
    """Clean all build and test related artifacts."""
    pass


@task(pre=[znake.venv.cleanup, clean])
def cleanup(ctx):
    """Cleanup the complete environment."""
    pass


@task(pre=[znake.static.static, znake.test.test, znake.systest.systest])
def check(ctx):
    """Run static checks and quick tests."""
    pass


@task(
    pre=[
        znake.static.static, znake.doc.doc, znake.test.test_all, znake.systest.systest,
        znake.deb.deb, znake.debtest.debtest, znake.pypi.pypi
    ])
def package(ctx):
    """Run everything needed to package and verify the package."""
    pass


def set_top_level_namespace(namespace):
    namespace.add_task(clean)
    namespace.add_task(cleanup)
    namespace.add_task(check)
    namespace.add_task(package)


class ZnakeProgram(Program):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execution_results = None

    def core_args(self):
        core_args = super().core_args()

        extra_args = [
            Argument(names=('tasks', 'j'), kind=int, default=8, help='Allow N tasks at once.'),
            Argument(
                names=('graceful', ),
                kind=bool,
                default=True,
                help='Allow any already scheduled tasks to run to completion before exiting.'),
            Argument(
                names=('root', 'r'),
                kind=bool,
                default=False,
                help='Run as root inside the Docker containers.'),
            Argument(name='coverage', kind=bool, default=False, help='Run with coverage'),
            Argument(
                name='tests',
                kind=str,
                default=None,
                help='Only run matching tests. Matching logic will be test runner specific.'),
            Argument(
                name='no-pull',
                kind=bool,
                default=False,
                help="Don't pull new version of the docker image"),
            Argument(name='network', help='Run docker with provided network'),
            Argument(name='build-dir', default='./build', help='The build directory'),
            Argument(
                name='summary',
                kind=bool,
                default=True,
                help='Print a summary of how the build went on exit')
        ]

        return core_args + extra_args

    def execute(self):
        executor = self.executor_class(self.collection, self.config, self.core, self.namespace)
        self.execution_results = executor.execute(*self.tasks)


def _main():
    coloredlogs.install(level=logging.INFO)

    if not os.path.isfile('znake.yaml'):
        print('Current working directory does not contain a znake.yaml file.')
        exit(1)

    modules = [
        znake.baseline,
        znake.deb,
        znake.debtest,
        znake.doc,
        znake.docker,
        znake.format,
        znake.pypi,
        znake.static,
        znake.systest,
        znake.test,
        znake.venv,
    ]

    # When running the znake executable as installed by the Debian package, all
    # tools required for znake to work are located under /opt/venvs/zenterio-znake/bin
    bin_directory = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'bin')
    os.environ['PATH'] = ':'.join([bin_directory, os.environ['PATH']])

    program = ZnakeProgram(
        namespace=Collection(),
        config_class=ZnakeConfig,
        executor_class=ParallelExecutor,
        version=__version__)

    # Do a "dry-run" of the program, to get it to parse all its config.
    try:
        program.create_config()
        program.parse_core(None)
        program.parse_collection()
        program.update_config()
    except invoke.exceptions.Exit:
        sys.exit(0)

    for module in modules:
        program.namespace.add_collection(module.get_namespace(program.config))
    set_top_level_namespace(program.namespace)
    program.run()

    results = program.execution_results
    results.summary = program.core[0].flags['--summary'].value
    results.graceful = program.core[0].flags['--graceful'].value
    return results


def _task_verdict(results, task):
    if task in results.failed:
        return '(failed)'
    if task in results.skipped:
        return '(skipped)'
    return ''


def _print_task(results, task, indentation_level):
    print(
        ' -  {indentation}{name} {verdict}'.format(
            indentation='  ' * indentation_level,
            name=task.name,
            verdict=_task_verdict(results, task)))


def _do_print_task_summary(results, parent_task, indentation_level=0):
    _print_task(results, parent_task, indentation_level)
    for t in results.all:
        if t.parent and t.parent == parent_task:
            _do_print_task_summary(results, parent_task=t, indentation_level=indentation_level + 1)


def _print_task_summary(results):
    for t in results.all:
        if not t.parent:
            _do_print_task_summary(results, t)


def _print_execution_summary(results, exception=None):
    print('')
    print('Znake summary:')
    print('')
    _print_task_summary(results)
    print('')
    if exception is None and results.success is True:
        print('Znake done: success')
    else:
        if exception is not None:
            print('Internal error: ' + str(exception))
            print('')
        print('Znake done: failure')


def main():
    try:
        old_settings = termios.tcgetattr(sys.stdin)
    except termios.error:
        old_settings = None

    results = None
    try:
        results = _main()
    except Exception:
        raise
    else:
        if results.summary:
            _print_execution_summary(results)
    finally:
        if old_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        if results:
            if not results.graceful:
                os.killpg(os.getpgid(0), signal.SIGKILL)
            if not results.success:
                exit(1)


if __name__ == '__main__':
    main()
