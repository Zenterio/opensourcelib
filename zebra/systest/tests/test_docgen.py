import os
from os.path import exists, join

from zaf.component.decorator import requires


@requires(zebra='Zebra')
@requires(workspace='Workspace')
def test_docgen_commands_creates_all_files(zebra, workspace):
    dir = workspace.path
    zebra('docgen --doc-dir {dir}'.format(dir=dir))

    commands_content = os.listdir(join(dir, 'commands'))
    assert exists(join(dir, 'commands', 'zebra_exec.rst')), str(commands_content)
    assert exists(join(dir, 'commands', 'zebra_help.rst')), str(commands_content)
    assert exists(join(dir, 'commands', 'zebra_make.rst')), str(commands_content)
    assert exists(join(dir, 'commands', 'zebra_shell.rst')), str(commands_content)
    assert exists(join(dir, 'commands', 'zebra_changelog.rst')), str(commands_content)
    assert exists(join(dir, 'command_list.rst')), str(os.listdir(dir))
    assert exists(join(dir, 'extension_list.rst')), str(os.listdir(dir))
    assert exists(join(dir, 'config_option_id_list.rst')), str(os.listdir(dir))
    assert exists(join(dir, 'changelog.rst')), str(os.listdir(dir))
