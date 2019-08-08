import os

from zaf.component.decorator import requires

from k2.builtin.systestutils.workspace import CallableWorkspace, TestWorkspace
from k2.runner.decorator import foreach


@requires(workspace='Workspace')
def test_test_workspace_basename_is_qualified_name_of_test_case(workspace):
    assert os.path.basename(workspace.path) == \
        'systest.feature.workspace.test_test_workspace_basename_is_qualified_name_of_test_case', \
        os.path.basename(workspace.path)


@requires(workspace='Workspace')
def test_get_test_workspace_in_test_cases_due_to_highest_priority_on_test_scope(workspace):
    assert type(workspace) == TestWorkspace, f'{type(workspace)} is not TestWorkspace'


@requires(workspace='Workspace', scope='module')
def test_get_callable_workspace_when_scope_is_different_from_test(workspace):
    assert type(workspace) == CallableWorkspace, f'{type(workspace)} is not Workspace'


@requires(workspace='Workspace')
@foreach(a=['b'])
def test_test_workspace_basename_is_qualified_with_parameters(workspace):
    assert os.path.basename(workspace.path) == \
        'systest.feature.workspace.test_test_workspace_basename_is_qualified_with_parameters-a_b', \
        os.path.basename(workspace.path)


@requires(workspace=CallableWorkspace)
@foreach(a=['b'])
def test_workspace_basename_does_not_contain_parameters(workspace):
    assert os.path.basename(workspace.path) == \
        'systest.feature.workspace.test_workspace_basename_does_not_contain_parameters', \
        os.path.basename(workspace.path)
