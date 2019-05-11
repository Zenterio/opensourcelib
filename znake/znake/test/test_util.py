import unittest
from threading import Event
from unittest.mock import MagicMock, Mock, patch

from invoke import Collection, task

from znake.util import ParallelExecutor, render_template, run


class TestRun(unittest.TestCase):

    def test_run_calls_ctx_run_if_image_is_local(self):
        ctx = Mock()
        target = {'image': 'local'}
        with patch('znake.util.docker_run') as docker_run:
            run(ctx, target['image'], 'this is my command')
        assert not docker_run.called
        ctx.run.assert_called_once_with(
            'this is my command', env={'PYTHONDONTWRITEBYTECODE': 'true'}, pty=False)

    def test_run_calls_docker_run_if_image_is_non_local(self):
        ctx = Mock()
        ctx.command_prefixes = None
        target = {'image': 'my_image'}
        with patch('znake.util.docker_run') as docker_run:
            run(ctx, target['image'], 'this is my command')
        docker_run.assert_called_once_with(
            ctx,
            target['image'],
            '/bin/bash -c "this is my command"',
            interactive=False,
            use_volume=False)

    def test_run_respects_command_prefixes_when_running_in_docker(self):
        ctx = Mock()
        ctx.command_prefixes = ['X=3', 'Y=4']
        target = {'image': 'my_image'}
        with patch('znake.util.docker_run') as docker_run:
            run(ctx, target['image'], 'this is my command')
        docker_run.assert_called_once_with(
            ctx,
            target['image'],
            '/bin/bash -c "X=3 && Y=4 && this is my command"',
            interactive=False,
            use_volume=False)


class TestRenderTemplate(unittest.TestCase):

    def test_render_template_without_kwargs(self):
        template_string = 'this is my template'
        rendered_template = render_template(template_string)
        assert template_string == rendered_template

    def test_render_template_with_kwargs(self):
        template_string = '{{data}}'
        rendered_template = render_template(template_string, data='this is my data')
        assert 'this is my data' == rendered_template


class TestParallelExecutor(unittest.TestCase):

    def setUp(self):
        self.collection = Collection()
        self.executor = ParallelExecutor(self.collection)
        self.executor.core = MagicMock()
        self.executor._max_workers = Mock(return_value=8)

    def test_run_single_task(self):
        a_event = Event()

        @task
        def a(ctx):
            a_event.set()

        self.collection.add_task(a)
        self.executor.execute('a')
        a_event.wait(timeout=0.5)

    def test_run_multiple_dependant_tasks(self):
        a_event = Event()
        b_event = Event()
        c_event = Event()

        @task
        def a(ctx):
            a_event.set()

        @task(pre=[a])
        def b(ctx):
            b_event.set()

        @task(pre=[b])
        def c(ctx):
            c_event.set()

        self.collection.add_task(a)
        self.collection.add_task(b)
        self.collection.add_task(c)
        self.executor.execute('c')
        a_event.wait(timeout=0.5)
        b_event.wait(timeout=0.5)
        c_event.wait(timeout=0.5)
