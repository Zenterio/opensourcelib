import os

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_missing_optional_config_options(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withoptionalconfigoptions'],
        'run systest.data.suites.test_minimal',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_missing_required_config_options(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withrequiredconfigoptions'],
        'run systest.data.suites.test_minimal',
        2,
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_available_required_config_options(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withrequiredconfigoptions'],
        'run systest.data.suites.test_minimal --req-option1 a --req-option2 b',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_str_option(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --str-option a',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_int_option(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --int-option 1',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_int_option_can_not_be_parsed(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --int-option a',
        2,
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_float_option(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --float-option 1.23',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_float_option_can_not_be_parsed(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --float-option a',
        2,
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_path_option_exists(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --path-option systest',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_path_option_does_not_exist(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --path-option /a/b/c',
        2,
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_choice_option(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --choice-option b',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_choice_option_not_valid_choice(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --choice-option d',
        2,
        plugin_path=os.path.join('systest', 'data', 'plugins'))


@requires(zk2='Zk2')
def test_typed_bool_option(zk2):
    zk2(
        ['runcommand', 'testfinder', 'withtypedconfigoptions'],
        'run systest.data.suites.test_minimal --bool-option true',
        plugin_path=os.path.join('systest', 'data', 'plugins'))


# TODO: ZMT-6395
# Default values and transform doesn't work correctly. The transformed value
# is passed to click instead of the raw value. Hence, the transform-choice
# option will be blocked by click if the default value is used.
# As a temporary work-around, --transform-choice-option A is passed
# in test cases that doesn't care about it, to avoid the default value-problem.


@requires(zk2='Zk2')
def test_multiple_options(zk2):
    result = zk2(
        ['runcommand', 'testfinder', 'withconfigoptionfeatures'],
        'run systest.data.suites.test_minimal '
        '--transform-choice-option A '  # TODO: ZMT-6395: Remove, see above.
        '--multiple-option 1 --multiple-option 2 --multiple-option 3',
        plugin_path=os.path.join('systest', 'data', 'plugins'))
    assert 'multiple.option: (1, 2, 3)' in result.stdout


@requires(zk2='Zk2')
def test_default_option(zk2):
    result = zk2(
        ['runcommand', 'testfinder', 'withconfigoptionfeatures'],
        'run systest.data.suites.test_minimal '
        '--transform-choice-option A ',  # TODO: ZMT-6395: Remove, see above.
        plugin_path=os.path.join('systest', 'data', 'plugins'))
    assert 'default.option: default' in result.stdout


@requires(zk2='Zk2')
def test_transform_option(zk2):
    result = zk2(
        ['runcommand', 'testfinder', 'withconfigoptionfeatures'],
        'run systest.data.suites.test_minimal '
        '--transform-choice-option A '  # TODO: ZMT-6395: Remove, see above.
        '--transform-option t',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    assert 'transform.option: transformed t' in result.stdout


@requires(zk2='Zk2')
def test_transform_choice_option(zk2):
    result = zk2(
        ['runcommand', 'testfinder', 'withconfigoptionfeatures'],
        'run systest.data.suites.test_minimal '
        '--transform-choice-option B',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    assert 'transform.choice.option: transformed B' in result.stdout
