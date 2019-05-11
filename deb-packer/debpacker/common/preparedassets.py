import logging
import os
import shutil
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class OutputExists(Exception):
    pass


class WorkspaceExists(Exception):
    pass


def prepared_output_file(output_file, force=False):
    """Make sure that the output file does not exists if force is not selected."""
    if output_file:
        logger.debug('Checking if output file "{file}" already exists'.format(file=output_file))
        if os.path.isfile(output_file) and not force:
            raise OutputExists(
                'Output file "{file}" already exists and force was not given'.format(
                    file=output_file))


def prepare_output_dir(output_dir: str):
    """Make sure the output dir exists."""
    if os.path.isfile(output_dir):
        raise OutputExists(
            'The output directory {dir} is a file not a directory'.format(dir=output_dir))
    os.makedirs(output_dir, exist_ok=True)


class PreparedWorkspace:
    """
    Create a workspace environment.

    This is done either by using a temporary directory or by making sure that a provided
    directory is empty.
    If the force option is True, content in the provided directory will be clear instead of
    causing an exception.
    """

    def __init__(self, workspace=None, force=False):
        self.workspace_path = workspace
        self.force = force
        self.workspace_handle = None

    def __enter__(self):
        logger.debug('Creating workspace directory')
        if self.workspace_path:
            if os.path.isdir(self.workspace_path):
                if not self.force:
                    msg = 'Workspace "{workspace}" already exists and force was not given'.format(
                        workspace=self.workspace_path)
                    raise WorkspaceExists(msg.format(self.workspace_path))
                else:
                    logger.debug('Clearing workspace directory')
                    shutil.rmtree(self.workspace_path)
            os.makedirs(self.workspace_path)
            workspace = self.workspace_path
        else:
            self.workspace_handle = TemporaryDirectory()
            workspace = self.workspace_handle.name
            logger.debug('Temporary workspace directory created: %s', self.workspace_handle)

        workspace_output = os.path.join(workspace, 'output')
        os.makedirs(workspace_output)
        logger.debug("Workspace output directory created: '%s'", workspace_output)

        return workspace, workspace_output

    def __exit__(self, *args):
        if self.workspace_handle is not None:
            try:
                self.workspace_handle.cleanup()
            except PermissionError as e:
                logging.warning(
                    'Error: Could not remove {path}'.format(path=self.workspace_handle.name))
                logging.warning(e)
