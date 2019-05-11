import copy
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from functools import wraps
from os import makedirs
from os.path import getmtime

import glob2
from invoke import Call, Config, Task, UnexpectedExit
from invoke.executor import Executor

from znake.builddir import BuildDir

from .docker import docker_run

logger = logging.getLogger('znake')
logger.addHandler(logging.NullHandler())


def run(ctx, image, command, interactive=False, use_venv=False, force_volume=False):
    """
    Run arbitrary shell commands.

    If the target is the local environment, run the command directly.
    If the target is not the local environment, run in a Docker container.
    """
    if use_venv:
        with _activate_venv(ctx):
            return _run(ctx, image, command, interactive, use_venv, force_volume)
    else:
        return _run(ctx, image, command, interactive, use_venv, force_volume)


def _run(ctx, image, command, interactive=False, use_venv=False, force_volume=False):
    if image == 'local':
        return ctx.run(command, pty=interactive, env={'PYTHONDONTWRITEBYTECODE': 'true'})
    else:
        if ctx.command_prefixes:
            return docker_run(
                ctx,
                image,
                '/bin/bash -c "{command_prefix} && {command}"'.format(
                    command_prefix=' && '.join(ctx.command_prefixes), command=command),
                interactive=interactive,
                use_volume=use_venv or force_volume)
        else:
            return docker_run(
                ctx,
                image,
                '/bin/bash -c "{command}"'.format(command=command),
                interactive=interactive,
                use_volume=use_venv or force_volume)


@contextmanager
def _activate_venv(ctx):
    """Activate the virtual environment in the current context."""
    command_prefix = 'source .venv/bin/activate'
    already_exists = command_prefix in ctx.command_prefixes
    if not already_exists:
        ctx.command_prefixes.append(command_prefix)
    yield
    if not already_exists:
        ctx.command_prefixes.remove(command_prefix)


def skip_if_up_to_date(target_pattern):
    """
    Decorate a task with this to check if a target is up to date.

    A target and its dependencies is defined by the Znake configuration. Each
    target consist of a target glob pattern and a list of dependency glob
    patterns.

    Each file matching the target glob pattern is compared to each file
    matching the dependency glob patterns. If any dependency file is newer than
    any target file, the decorated task is performed. If not, the decorated
    task is skipped.
    """

    def _wrapper(fn):

        @wraps(fn)
        def _internal_wrapper(ctx, *args, **kwargs):
            config_target = None
            if 'target' in kwargs:
                config_target = kwargs['target']
            check_in_docker = config_target and 'image' in config_target and config_target['image'] != 'local'
            targets = _get_targets(check_in_docker, config_target, ctx)

            if not targets:
                fn(ctx, *args, **kwargs)
            else:
                all_targets_up_to_date = True
                for target in targets:
                    if not _is_target_up_to_date(ctx, target, check_in_docker, config_target):
                        all_targets_up_to_date = False

                if not all_targets_up_to_date:
                    fn(ctx, *args, **kwargs)

        def _is_target_up_to_date(ctx, target, check_in_docker, config_target):
            for dependency_patterns in _get_dependencies_for_target(ctx, target):
                dependencies = _get_dependencies(
                    check_in_docker, config_target, ctx, dependency_patterns)
                for dependency in dependencies:
                    dependency_mtime, target_mtime = _get_mtimes(
                        check_in_docker, config_target, ctx, dependency, target)

                    if target_mtime < dependency_mtime:
                        logger.debug(
                            '{target}{docker} is not up to date due to dependency {dependency}'.
                            format(
                                target=target,
                                dependency=dependency,
                                docker=' in docker' if check_in_docker else ''))

                        return False
            return True

        def _get_dependencies_for_target(ctx, target):
            target_dependencies = []

            for target_key in ctx.dependencies.keys():
                rendered_key = _render_config_pattern(target_key, ctx)
                # target[2:] is used to de-duplicate targets starting with ./
                if rendered_key in [target, target[2:]]:
                    target_dependencies.extend(ctx.dependencies.get(target_key, []))
            return target_dependencies

        def _get_targets(check_in_docker, config_target, ctx):
            target_glob_pattern = _render_config_pattern(target_pattern, ctx)
            if check_in_docker:
                try:
                    targets = run(
                        ctx,
                        config_target['image'],
                        'find {pattern}'.format(pattern=target_glob_pattern),
                        force_volume=True)
                except UnexpectedExit:
                    targets = []
                else:
                    targets = targets.stdout.split('\n')
            else:
                targets = _glob_recursively_and_remove_non_existing(target_glob_pattern)
            return targets

        def _get_dependencies(check_in_docker, config_target, ctx, dependency_patterns):
            dependency_glob_patterns = _render_config_pattern(dependency_patterns, ctx)
            if check_in_docker:
                dependencies = run(
                    ctx,
                    config_target['image'],
                    'find {pattern}'.format(pattern=dependency_glob_patterns),
                    force_volume=True).stdout
            else:
                dependencies = _glob_recursively_and_remove_non_existing(dependency_glob_patterns)
            return dependencies

        def _get_mtimes(check_in_docker, config_target, ctx, dependency, target):
            if check_in_docker:
                target_mtime = run(
                    ctx,
                    config_target['image'],
                    'stat -c %Y {target}'.format(target=target),
                    force_volume=True).stdout
                dependency_mtime = run(
                    ctx,
                    config_target['image'],
                    'stat -c %Y {dependency}'.format(dependency=dependency),
                    force_volume=True).stdout
            else:
                target_mtime = getmtime(target)
                dependency_mtime = getmtime(dependency)

            return dependency_mtime, target_mtime

        return _internal_wrapper

    return _wrapper


def _glob_recursively_and_remove_non_existing(glob_pattern):
    return [path for path in glob2.glob(glob_pattern, recursive=True) if os.path.exists(path)]


def _render_config_pattern(pattern, ctx):
    return pattern.format(package=ctx.znake.info.package, **ctx.build_dir.templating_kwargs())


def render_template(template_string, **kwargs):
    """Render a jinja2 template."""
    import jinja2
    template = jinja2.Template(template_string)
    return template.render(**kwargs)


class ZnakeConfig(Config):
    """
    Config with reasonable defaults for Znake.

    This is a drop-in replacement for Invokes default Config class.
    """

    prefix = 'znake'

    def __init__(
            self,
            overrides=None,
            defaults=None,
            project_location=None,
            runtime_path=None,
            lazy=False,
    ):
        super().__init__(
            overrides=overrides,
            defaults=defaults,
            system_prefix=os.path.join(os.path.dirname(__file__), 'data') + '/',
            user_prefix='./',
            project_location=project_location,
            runtime_path=runtime_path,
            lazy=lazy,
        )


class ExecutionSummary(Executor):

    def __init__(self, calls):
        self.calls = calls
        self.completed_futures = []

    def register_completed_future(self, future):
        self.completed_futures.append(future)

    @property
    def all(self):
        return self.calls

    @property
    def successful(self):
        return [future.call for future in self.completed_futures if future.exception() is None]

    @property
    def failed(self):
        return [future.call for future in self.completed_futures if future.exception() is not None]

    @property
    def skipped(self):
        completed_calls = self.successful + self.failed
        return [call for call in self.calls if call not in completed_calls]

    @property
    def success(self):
        return len(self.failed) == 0

    @property
    def verdict(self):
        return 'SUCCESS' if self.success else 'ERROR'


class ParallelExecutor(Executor):
    """
    Executor with support for parallel execution.

    This is a drop-in replacement for Invokes default Executor class.

    The parallel executor computes what tasks are to be run. All tasks with no
    dependencies are scheduled for execution by a thread pool. As each task is
    completed, it is removed from the dependency list and any task with no
    dependencies is scheduled for execution. This process repeats until all
    tasks are completed.
    """

    def __init__(self, collection, config=None, core=None, namespace=None):
        super().__init__(collection, config, core)
        self.namespace = namespace

    def execute(self, *tasks):
        calls = self.expand_names(self.dedupe(self.expand_calls(self.normalize(tasks))))
        result = ExecutionSummary(calls[::])
        futures = []

        logger.info('Starting execution with {count} scheduled tasks'.format(count=len(calls)))

        executor = ThreadPoolExecutor(max_workers=self._max_workers())
        while calls:
            calls_ready_to_execute = [call for call in calls if not call.pre]
            futures.extend(self._schedule_calls(executor, calls_ready_to_execute))

            for call in calls_ready_to_execute:
                calls.remove(call)
            try:
                future = next(as_completed(futures))
            except StopIteration:
                raise Exception(
                    (
                        'There are unmet dependencies but there are no tasks '
                        'ready to execute. The executor is deadlocked. '
                        'The remaining tasks are: {calls}'.format(calls=calls))) from None

            result.register_completed_future(future)
            if future.exception() is not None:
                logger.info(
                    "Task '{task}' error: {why}".format(
                        task=future.call.name, why=str(future.exception())))
                logger.info('Exiting')
                break

            logger.info('Completed {task}'.format(task=future.call.name))
            futures.remove(future)

            for call in calls:
                try:
                    while future.call in call.pre:
                        call.pre.remove(future.call)
                except (AttributeError, ValueError):
                    pass
                try:
                    while future.call.task in call.pre:
                        call.pre.remove(future.call.task)
                except (AttributeError, ValueError):
                    pass

        if self._graceful_shutdown():
            executor.shutdown(wait=True)
            for future in futures:
                result.register_completed_future(future)
        else:
            executor.shutdown(wait=False)

        logger.info('Execution ended with result: {result}'.format(result=result.verdict))
        return result

    def expand_calls(self, calls, parent=None):
        ret = []
        for call in calls:
            if isinstance(call, Task):
                call = Call(task=call)
            call.parent = parent
            ret.extend(self.expand_calls(call.pre, call))
            ret.append(call)
            ret.extend(self.expand_calls(call.post, call))
        return ret

    def _namespace_path_for_call(self, call, namespace):
        for candidate_call in namespace.tasks.values():
            if candidate_call.body == call.body:
                return candidate_call.name
        for name, subnamespace in namespace.collections.items():
            subname = self._namespace_path_for_call(call, subnamespace)
            if subname:
                return '.'.join([name, subname])

    def expand_names(self, calls):
        if self.namespace:
            for call in calls:
                qualified_name = self._namespace_path_for_call(call, self.namespace)
                if qualified_name:
                    call.name = qualified_name
        return calls

    def _schedule_calls(self, executor, calls):

        def make_wrapper(fn, name):

            def _wrapper(*args, **kwargs):
                logger.info('Starting {task}'.format(task=name))
                fn(*args, **kwargs)

            return _wrapper

        futures = []
        for call in calls:
            # The Invoke config object is *not* thread safe in any way.
            # Make sure to make a copy of it before proceeding with parallel execution.
            config = copy.deepcopy(self.config)
            collection_config = self.collection.configuration(call.called_as)
            config.load_collection(collection_config)
            config.load_shell_env()
            config.core = self.core[0]
            config.build_dir = BuildDir(config.core.args['build-dir'].value)
            context = call.make_context(config)
            args = (context, ) + call.args
            future = executor.submit(make_wrapper(call.task, call.name), *args, **call.kwargs)
            future.call = call
            futures.append(future)
        return futures

    def _graceful_shutdown(self):
        return self.core[0].args['graceful'].value

    def _max_workers(self):
        return self.core[0].args['tasks'].value


def znake_tool_path(tool_name):
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), tool_name)


def generate_test_command(ctx, test_ctx, target_name):
    packages = ' '.join(test_ctx.packages)
    command_pattern = test_ctx.command_pattern

    output_dir = '{test_dir}/output-{target}'.format(
        test_dir=ctx.build_dir.test_dir, target=target_name)

    combined_kwargs = {}
    combined_kwargs.update(test_ctx.vars)
    combined_kwargs.update(ctx.build_dir.templating_kwargs())

    if ctx.core.args['coverage'].value is True:
        makedirs(ctx.build_dir.coverage_dir, exist_ok=True)
        coverage_flags = test_ctx.coverage_flags.format(
            packages=packages, output_dir=output_dir, image=target_name, **combined_kwargs)
    else:
        coverage_flags = ''

    if ctx.core.args['tests'].value is not None and 'tests_flags' in test_ctx:
        tests_flags = test_ctx.tests_flags.format(
            tests=ctx.core.args['tests'].value,
            packages=packages,
            output_dir=output_dir,
            image=target_name,
            **combined_kwargs)
    else:
        tests_flags = ''

    return command_pattern.format(
        packages=packages,
        output_dir=output_dir,
        coverage_flags=coverage_flags,
        image=target_name,
        tests_flags=tests_flags,
        **combined_kwargs)


# Nosetest discovers that this is a test because it contains the word "test".
generate_test_command.__test__ = False  # It is not a test.
