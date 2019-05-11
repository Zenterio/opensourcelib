import json
import os
from collections import defaultdict

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_foreach(zk2):
    result = zk2(
        [
            'runcommand',
            'testrunner',
            'testfinder',
            'testscheduler',
            'testresults',
            'textreport',
            'sut',
        ], 'run --suts-ids one --suts-ids two systest.data.suites.test_foreach')
    stdout = result.stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_config_entity[s=one]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_config_entity[s=two]') in stdout, stdout
    assert 'systest.data.suites.test_foreach.test_foreach_format[s=_one_]' in stdout, stdout
    assert 'systest.data.suites.test_foreach.test_foreach_format[s=_two_]' in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity[s=one, d=0]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity[s=one, d=1]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity[s=two, d=0]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity[s=two, d=1]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_dependency_on_foreached_entity[s=one]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_dependency_on_foreached_entity[s=two]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreached_component_depends_on_can_filtered_entity[scc=one_sut_component]'
    ) in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreached_component_depends_on_can_filtered_entity[scc=two_sut_component]'
    ) in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_argument_component[ac=arg_component1]') in stdout, stdout
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_argument_component[ac=arg_component2]') in stdout, stdout
    assert ('systest.data.suites.test_foreach.' 'test_no_parameterization') in stdout, stdout
    assert 'Passed:  14' in stdout, stdout
    assert 'Failed:  1' in stdout, stdout
    assert 'Total:   15' in stdout, stdout


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_foreach_with_logs_per_test_case(zk2, workspace):
    zk2(
        [
            'runcommand',
            'testrunner',
            'testfinder',
            'testscheduler',
            'testresults',
            'textreport',
            'sut',
        ],
        '--logdefaults-enabled true --log-dir {workspace} '
        'run --suts-ids one --suts-ids two systest.data.suites.test_foreach'.format(
            workspace=workspace.path))
    log_files = os.listdir(os.path.join(workspace.path, 'testrun'))
    assert 'systest.data.suites.test_foreach.test_foreach_config_entity-s_one.log' in log_files, log_files
    assert 'systest.data.suites.test_foreach.test_foreach_config_entity-s_two.log' in log_files, log_files
    assert 'systest.data.suites.test_foreach.test_foreach_format-s__one_.log' in log_files, log_files
    assert 'systest.data.suites.test_foreach.test_foreach_format-s__two_.log' in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity-s_one-d_0.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity-s_one-d_1.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity-s_two-d_0.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity-s_two-d_1.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_dependency_on_foreached_entity-s_one.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_dependency_on_foreached_entity-s_two.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreached_component_depends_on_can_filtered_entity-scc_one_sut_component.log'
    ) in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreached_component_depends_on_can_filtered_entity-scc_two_sut_component.log'
    ) in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_argument_component-ac_arg_component1.log') in log_files, log_files
    assert (
        'systest.data.suites.test_foreach.'
        'test_foreach_argument_component-ac_arg_component2.log') in log_files, log_files
    assert 'systest.data.suites.test_foreach.test_no_parameterization.log' in log_files, log_files


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_foreach_with_z2reporter(zk2, workspace):
    z2_report_file = os.path.join(workspace.path, 'report.json')

    zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport',
            'sut', 'z2report'
        ],
        'run '
        '--reports-z2 true '
        '--reports-z2-file {z2_report_file} '
        '--suts-ids one --suts-ids two systest.data.suites.test_foreach'.format(
            z2_report_file=z2_report_file))

    with open(z2_report_file, 'r') as f:
        data = json.loads(f.read())

    params_data = defaultdict(list)
    for tc in data['testCases']:
        params_data[tc['name']].append(tc['params'])

    assert params_data[('systest.data.suites.test_foreach.'
                        'test_foreach_config_entity')] == [['s=one'], ['s=two']]
    assert params_data['systest.data.suites.test_foreach.test_foreach_format'] == [
        ['s=_one_'], ['s=_two_']
    ]
    assert params_data[(
        'systest.data.suites.test_foreach.'
        'test_foreach_mixed_list_data_with_config_entity')] == [
            ['s=one', 'd=0'], ['s=one', 'd=1'], ['s=two', 'd=0'], ['s=two', 'd=1']
        ]
    assert params_data[('systest.data.suites.test_foreach.'
                        'test_dependency_on_foreached_entity')] == [['s=one'], ['s=two']]
    assert params_data[(
        'systest.data.suites.test_foreach.'
        'test_foreached_component_depends_on_can_filtered_entity')] == [
            ['scc=one_sut_component'], ['scc=two_sut_component']
        ]
    assert params_data[('systest.data.suites.test_foreach.'
                        'test_foreach_argument_component')] == [
                            ['ac=arg_component1'], ['ac=arg_component2']
                        ]
    assert params_data['systest.data.suites.test_foreach.test_no_parameterization'] == [[]]
