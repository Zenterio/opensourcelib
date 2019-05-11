import logging
import os
import shutil

from zaf.builtin.output import OUTPUT_DIR
from zaf.component.decorator import component, requires
from zaf.extensions.extension import get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'systestuils', 'workspace'))
logger.addHandler(logging.NullHandler())


@component(name='Workspace', provided_by_extension='systestutils')
@requires(context='ComponentContext')
@requires(config='Config')
class Workspace(object):

    def __init__(self, context, config):
        output_dir = os.path.abspath(config.get(OUTPUT_DIR))
        workspace_root = os.path.join(output_dir, 'workspace')
        self.name = context.callable_qualname
        self.workspace = os.path.join(workspace_root, self.name)

    def __enter__(self):
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace)

        self.create()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def absolute_file_path(self, file):
        return os.path.abspath(os.path.join(self.workspace, file))

    def assert_file_exists(self, file):
        path = self.absolute_file_path(file)
        assert os.path.exists(path), 'File {path} does not exist'.format(path=path)

    def assert_is_link(self, link):
        path = self.absolute_file_path(link)
        assert os.path.islink(path), '{path} is not a symlink'.format(path=path)
        assert os.path.exists(path), '{path} does not exist'.format(path=path)

    def assert_in_file(self, file, content):
        path = self.absolute_file_path(file)
        with open(path) as f:
            assert content in f.read(), "Content '{content}' not found in '{path}'".format(
                content=content, path=path)

    def assert_file_not_exists(self, file):
        path = self.absolute_file_path(file)
        assert not os.path.exists(path), 'File {path} exists'.format(path=path)

    def create_file(self, file, content):
        path = self.absolute_file_path(file)
        logger.debug("Creating file '{path}'".format(path=path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def create_dir(self, dir):
        path = self.absolute_file_path(dir)
        logger.debug("Creating directory '{dir}'".format(dir=path))
        os.makedirs(path, exist_ok=True)
        return path

    def add_file(self, source_file, target_file):
        path = self.absolute_file_path(target_file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.debug(
            "Copying file '{source}' into workspace path '{target}".format(
                source=source_file, target=target_file))
        shutil.copy(source_file, path)

    def create(self):
        logger.debug("Copying workspace '{path}'".format(path=self.path))
        os.makedirs(self.path, exist_ok=True)

    @property
    def path(self):
        return self.workspace
