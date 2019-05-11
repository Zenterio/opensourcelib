from zaf.component.decorator import component, requires

from k2.runner.decorator import foreach

foreach_config_entity_called_with = []


@foreach(s='Sut')
def test_foreach_config_entity(s):
    assert s.entity in ['one', 'two']
    assert s.entity not in foreach_config_entity_called_with, \
        'Has already been called with {entity}'.format(entity=s.entity)
    foreach_config_entity_called_with.append(s.entity)

    if s.entity == 'one':
        assert False, 'Intentionally fail if sut one to illustrate failed tests.'


def format_fn(obj):
    return '_{val}_'.format(val=str(obj))


@foreach(s='Sut', format=format_fn)
def test_foreach_format(s):
    assert s.entity in ['one', 'two']


foreach_mixed_list_data_with_config_entity_called_with = []


@foreach(s='Sut')
@foreach(d=range(2))
def test_foreach_mixed_list_data_with_config_entity(s, d):
    assert d >= 0, d
    assert d < 2, d
    assert s.entity in ['one', 'two']

    assert (s.entity, d) not in foreach_mixed_list_data_with_config_entity_called_with, \
        'Has already been called with {entity} and {data}'.format(entity=s.entity, data=d)
    foreach_mixed_list_data_with_config_entity_called_with.append((s.entity, d))


@component(name='SutComponent')
@requires(sut='Sut')
def sut_component(sut):
    return sut.entity


dependency_on_foreached_entity_called_with = []


@foreach(s='Sut')
@requires(sc='SutComponent', uses=['s'])
def test_dependency_on_foreached_entity(s, sc):
    assert sc in ['one', 'two']
    assert sc not in dependency_on_foreached_entity_called_with, \
        'Has already been called with {entity}'.format(entity=sc)
    dependency_on_foreached_entity_called_with.append(sc)
    assert s not in dependency_on_foreached_entity_called_with, \
        'Has already been called with {sut}'.format(sut=s)
    dependency_on_foreached_entity_called_with.append(s)


@component(name='SutCanComponent')
@requires(s='Sut', can=['one'])
def one_sut_component(s):
    return s.entity


@component(name='SutCanComponent')
@requires(s='Sut', can=['two'])
def two_sut_component(s):
    return s.entity


foreached_component_depends_on_can_filtered_entity_called_with = []


@foreach(scc='SutCanComponent')
def test_foreached_component_depends_on_can_filtered_entity(scc):
    assert scc in ['one', 'two']
    assert scc not in foreached_component_depends_on_can_filtered_entity_called_with, \
        'Has already been called with {item}'.format(item=scc)
    foreached_component_depends_on_can_filtered_entity_called_with.append(scc)


@component(name='ArgumentComponent')
def arg_component1(arg):
    return arg * 1


@component(name='ArgumentComponent')
def arg_component2(arg):
    return arg * 2


foreach_argument_component_called_with = []


@foreach(ac='ArgumentComponent', args=[1])
def test_foreach_argument_component(ac):
    assert ac in [1, 2]
    assert ac not in foreach_argument_component_called_with, \
        'Has already been called with {ac}'.format(ac=ac)
    foreach_argument_component_called_with.append(ac)


def test_no_parameterization():
    """Plain test should still work."""
    pass
