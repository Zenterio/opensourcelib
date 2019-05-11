import os

from zaf.component.decorator import requires


@requires(zebra='Zebra')
def test_make_command_pulls_default_image(zebra):
    result = zebra('-v make help')
    assert 'pull <YOUR_REGISTRY>/<YOUR_IMAGE>:latest' in result.stderr


@requires(zebra='Zebra')
def test_make_command_pulls_image_using_options(zebra):
    result = zebra('-v --image <YOUR_IMAGE> --tag tag --registry <YOUR_REGISTRY> make help')
    assert 'pull <YOUR_REGISTRY>/<YOUR_IMAGE>:tag' in result.stderr


@requires(zebra='Zebra')
def test_make_command_pulls_image_with_no_registry(zebra):
    result = zebra('-v --image <YOUR_IMAGE> --tag tag --no-use-registry make help')
    assert 'pull <YOUR_IMAGE>:tag' in result.stderr


@requires(zebra='Zebra')
def test_make_command_pulls_image_from_proxy(zebra):
    result = zebra('-v --image <YOUR_IMAGE> --tag tag --registry-cache dockercache make help')
    assert 'pull dockercache/<YOUR_IMAGE>:tag' in result.stderr


@requires(zebra='Zebra')
def test_proxy_image_is_renamed_using_tag_after_pull(zebra):
    result = zebra('-v --image <YOUR_IMAGE> --tag tag --registry-cache dockercache make help')
    assert 'tag dockercache/<YOUR_IMAGE>:tag <YOUR_REGISTRY>/<YOUR_IMAGE>:tag' in result.stderr


@requires(zebra='Zebra')
def test_make_command_fails_to_pull_image(zebra):
    zebra('make help', expected_exit_code=1, override_pull='false')


@requires(zebra='Zebra')
def test_make_command_fails_to_in_docker_run(zebra):
    zebra('make help', expected_exit_code=1, override_run='false')


@requires(zebra='Zebra')
def test_make_command_supports_fowarding_of_environment_variables(zebra):
    result = zebra('-e VARIABLE make help')

    assert '-e VARIABLE' in result.stdout


@requires(zebra='Zebra')
def test_make_command_runs_docker_with_current_user_by_default(zebra):
    """Test that the current user is mapped into the docker container."""
    result = zebra('make help')

    assert '-u' in result.stdout, result.stdout
    assert '-e TAR_OPTIONS=' not in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_make_command_can_run_docker_with_root_user(zebra):
    """Test that the current user is not mapped into the docker container which makes it run as root."""
    result = zebra('--root make help')

    assert '-u' not in result.stdout, result.stdout
    assert '-e TAR_OPTIONS=' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_make_can_forward_additional_mounts(zebra):
    """Test that mounts are forwarded to docker run."""
    result = zebra('--mount type=bind,source=source,target=target,readonly make help')

    assert '--mount type=bind,source=source,target=target,readonly' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_make_can_set_hostname(zebra):
    """Test that hostname can be set."""
    result = zebra('--hostname my_host make help')

    assert '--hostname my_host' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_make_hostname_is_not_set_by_default(zebra):
    """Test that hostname is not set by default."""
    result = zebra('make help')

    assert '--hostname' not in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_root_dir_and_workdir_default_to_parent_of_current_working_directory(zebra):
    """Test that root and workdir set to parent of current working directory by default."""
    result = zebra('make help')

    cwd = os.getcwd()
    assert '--workdir /zebra/workspace/{cwd_in_docker}' \
        .format(cwd_in_docker=os.path.basename(cwd)) in result.stdout, result.stdout
    assert '--mount type=bind,source={parent},target=/zebra/workspace'.format(
        parent=os.path.dirname(cwd)) in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_root_dir_can_be_overridden_to_parent_directory_of_current_working_directory(zebra):
    """Test that root and workdir are calculated from the root dir option."""
    result = zebra('--root-dir .. make help')

    cwd = os.getcwd()
    expected_workdir = '--workdir /zebra/workspace/{cwd_in_docker}'.format(
        cwd_in_docker=os.path.basename(cwd))
    assert expected_workdir in result.stdout, '{expected} not found in {stdout}'.format(
        expected=expected_workdir, stdout=result.stdout)

    expected_mount = '--mount type=bind,source={root_dir},target=/zebra/workspace'.format(
        root_dir=os.path.abspath('..'))
    assert expected_mount in result.stdout, '{expected} not found in {stdout}'.format(
        expected=expected_mount, stdout=result.stdout)


@requires(zebra='Zebra')
def test_project_dir_must_be_a_parent_directory_of_current_working_directory(zebra):
    """Test that project dir must be a parent directory of the current working directory."""
    zebra('--project-dir systest make help', expected_exit_code=1)


@requires(zebra='Zebra')
def test_root_dir_must_be_a_parent_directory_of_current_working_directory(zebra):
    """Test that root dir must be a parent directory of the current working directory."""
    zebra('--root-dir systest make help', expected_exit_code=1)


@requires(zebra='Zebra')
def test_root_dir_must_be_a_parent_directory_of_project_dir(zebra):
    """Test that root dir must be a parent directory of the current working directory."""
    zebra('--root-dir . --project-dir .. make help', expected_exit_code=1)


@requires(workspace='Workspace')
@requires(zebra='Zebra')
def test_root_dir_is_parent_of_directory_with_dot_zebra_file(zebra, workspace):
    workspace.create_file('.zebra', 'image: abs.u16\n')
    workspace.create_dir('child')
    result = zebra('make help', cwd=os.path.join(workspace.path, 'child'))

    assert '--mount type=bind,source={parent},target=/zebra/workspace'.format(
        parent=os.path.abspath(os.path.dirname(workspace.path))) in result.stdout

    assert '--workdir /zebra/workspace' in result.stdout


@requires(workspace='Workspace')
@requires(zebra='Zebra')
def test_project_dir_option_overrides_zebra_file(zebra, workspace):
    workspace.create_file('.zebra', 'image: abs.u16\n')
    workspace.create_dir('child')

    child_dir = os.path.join(workspace.path, 'child')
    result = zebra('--project-dir . make help', cwd=child_dir)

    assert '--workdir /zebra/workspace/child' in result.stdout


@requires(zebra='Zebra')
def test_make_container_root_dir_can_be_overridden(zebra):
    """Test that root dir inside the container can be overridden."""
    result = zebra('--container-root-dir /override/to/path make help')

    cwd = os.getcwd()
    expected_workdir = '--workdir /override/to/path'
    assert expected_workdir in result.stdout, '{expected} not found in {stdout}'.format(
        expected=expected_workdir, stdout=result.stdout)

    expected_mount = '--mount type=bind,source={root_dir},target=/override/to/path'.format(
        root_dir=os.path.dirname(cwd))
    assert expected_mount in result.stdout, '{expected} not found in {stdout}'.format(
        expected=expected_mount, stdout=result.stdout)


@requires(zebra='Zebra')
def test_make_container_root_dir_default_value(zebra):
    """Test that the correct default value is used for container root dir."""
    result = zebra('make help')

    cwd = os.getcwd()
    expected_workdir = '--workdir /zebra/workspace'
    assert expected_workdir in result.stdout, '{expected} not found in {stdout}'.format(
        expected=expected_workdir, stdout=result.stdout)

    expected_mount = '--mount type=bind,source={root_dir},target=/zebra/workspace'.format(
        root_dir=os.path.dirname(cwd))
    assert expected_mount in result.stdout, '{expected} not found in {stdout}'.format(
        expected=expected_mount, stdout=result.stdout)


@requires(zebra='Zebra')
def test_make_docker_run_called_with_add_cap_sys_ptrace(zebra):
    result = zebra('make help')

    assert '--cap-add SYS_PTRACE' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_default_network_is_host(zebra):
    result = zebra('make help')

    assert '--network host' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_make_can_set_network(zebra):
    result = zebra('--network bridge make help')

    assert '--network bridge' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_image_override_can_take_any_image(zebra):
    result = zebra('--image-override "directory/image" make help')
    assert 'docker.zenterio.lan/directory/image' in result.stdout, result.stdout


@requires(workspace='Workspace')
@requires(zebra='Zebra')
def test_default_image_read_from_dot_zebra_file(zebra, workspace):
    workspace.create_file('.zebra', 'image: abs.u16\n')
    result = zebra('make help', cwd=workspace.path)
    assert 'abs.u16' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_project_dir_mounted_as_project_dir_name(zebra, workspace):
    result = zebra('--project-dir-name PROJECT_DIR_NAME make help')

    cwd = os.getcwd()
    expected_mount = '--mount type=bind,source={cwd},target=/zebra/workspace/PROJECT_DIR_NAME'.format(
        cwd=cwd)

    assert expected_mount in result.stdout, result.stdout
    assert '--workdir /zebra/workspace/PROJECT_DIR_NAME/.' in result.stdout, result.stdout


@requires(workspace='Workspace')
@requires(zebra='Zebra')
def test_default_project_dir_name_read_from_dot_zebra_file(zebra, workspace):
    workspace.create_file('.zebra', 'project.dir.name: PROJECT_DIR_NAME\n')

    result = zebra('make help', cwd=workspace.path)
    assert '--workdir /zebra/workspace/PROJECT_DIR_NAME/.' in result.stdout, result.stdout


@requires(zebra='Zebra')
def test_project_dir_name_not_used_if_relative_project_dir_is_dot(zebra):
    result = zebra('--project-dir . --root-dir . --project-dir-name PROJECT_DIR_NAME make help')
    assert 'PROJECT_DIR_NAME' not in result.stdout, result.stdout
