import itertools

from zaf.component.decorator import requires

from systest.localtests import ZpiderYamlBackendAppliedToSampleDocument


def _flat_value_map(collection):
    items = []
    if hasattr(collection, 'values'):
        items.extend(itertools.chain(*map(_flat_value_map, collection.values())))
    elif type(collection) in (list, tuple):
        items.extend(itertools.chain(*map(_flat_value_map, collection)))
    else:
        items.append(collection)
    return items


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_everything_included(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend())
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' in data
    assert 'sublevel second paragraph' in data
    assert 'Magictitle' in data
    assert 'magictitle content' in data
    assert 'Other Subsection' in data
    assert 'other subsection summary' in data
    assert 'other subsection second paragraph' in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_everything_excluded(zpider_yaml_backend):
    data = _flat_value_map(
        zpider_yaml_backend(
            '--levels-level@excludes all --levels-sublevel@excludes all --keep-empty-sections true')
    )
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' not in data
    assert 'level second paragraph' not in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' not in data
    assert 'sublevel second paragraph' not in data
    assert 'Magictitle' not in data
    assert 'magictitle content' not in data
    assert 'Other Subsection' not in data
    assert 'other subsection summary' not in data
    assert 'other subsection second paragraph' not in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_summary_excluded(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--levels-sublevel@excludes summary'))
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' not in data
    assert 'sublevel second paragraph' in data
    assert 'Magictitle' in data
    assert 'magictitle content' in data
    assert 'Other Subsection' in data
    assert 'other subsection summary' in data
    assert 'other subsection second paragraph' in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_other_excluded(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--levels-sublevel@excludes other'))
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' in data
    assert 'sublevel second paragraph' not in data
    assert 'Magictitle' in data
    assert 'magictitle content' in data
    assert 'Other Subsection' not in data
    assert 'other subsection summary' not in data
    assert 'other subsection second paragraph' not in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_magic_title_excluded(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--levels-sublevel@excludes magictitle'))
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' in data
    assert 'sublevel second paragraph' in data
    assert 'Magictitle' not in data
    assert 'magictitle content' not in data
    assert 'Other Subsection' in data
    assert 'other subsection summary' in data
    assert 'other subsection second paragraph' in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_summary_included(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--levels-sublevel@includes summary'))
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' in data
    assert 'sublevel second paragraph' not in data
    assert 'Magictitle' not in data
    assert 'magictitle content' not in data
    assert 'Other Subsection' not in data
    assert 'other subsection summary' not in data
    assert 'other subsection second paragraph' not in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_other_included(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--levels-sublevel@includes other'))
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' not in data
    assert 'sublevel second paragraph' in data
    assert 'Magictitle' not in data
    assert 'magictitle content' not in data
    assert 'Other Subsection' in data
    assert 'other subsection summary' in data
    assert 'other subsection second paragraph' in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_magic_title_included(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--levels-sublevel@includes magictitle'))
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' in data
    assert 'level second paragraph' in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' not in data
    assert 'sublevel second paragraph' not in data
    assert 'Magictitle' in data
    assert 'magictitle content' in data
    assert 'Other Subsection' not in data
    assert 'other subsection summary' not in data
    assert 'other subsection second paragraph' not in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_empty_sections_removed(zpider_yaml_backend):
    data = _flat_value_map(
        zpider_yaml_backend('--levels-sublevel@excludes all --levels-level@excludes all'))
    assert 'Top Level' in data
    assert 'Level Section' not in data
    assert 'level summary' not in data
    assert 'level second paragraph' not in data
    assert 'Level Subsection' not in data
    assert 'sublevel summary' not in data
    assert 'sublevel second paragraph' not in data
    assert 'Magictitle' not in data
    assert 'magictitle content' not in data
    assert 'Other Subsection' not in data
    assert 'other subsection summary' not in data
    assert 'other subsection second paragraph' not in data


@requires(zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument)
def test_keep_empty_sections(zpider_yaml_backend):
    data = _flat_value_map(
        zpider_yaml_backend(
            '--levels-sublevel@excludes all --levels-level@excludes all --keep-empty-sections true')
    )
    assert 'Top Level' in data
    assert 'Level Section' in data
    assert 'level summary' not in data
    assert 'level second paragraph' not in data
    assert 'Level Subsection' in data
    assert 'sublevel summary' not in data
    assert 'sublevel second paragraph' not in data
    assert 'Magictitle' not in data
    assert 'magictitle content' not in data
    assert 'Other Subsection' not in data
    assert 'other subsection summary' not in data
    assert 'other subsection second paragraph' not in data
