from textwrap import dedent

from zaf.component.decorator import requires

from systest.localtests import ZpiderYamlBackendAppliedToSampleDocument
from systest.localtests.test_document_structure import _flat_value_map

_SAMPLE_ADOC_DOCUMENT_WITH_IDS = dedent(
    """
    = Top Level

    [.level,id=1]
    == Level Section

    level summary

    level second paragraph

    [.sublevel, id=2]
    === Level Subsection

    sublevel summary

    sublevel second paragraph

    [.subsublevel, id=3]
    ==== Level Subsubsection 3

    id 3 content

    [.subsublevel, id=4]
    ==== Level Subsubsection 4

    id 4 content
    """)

_SAMPLE_ADOC_DOCUMENT_WITH_UNIQUE_NON_VERSIONED_IDS = dedent(
    """
    = Top Level

    [.level,id=1]
    == ID 1 Section

    [.level,id=2]
    == ID 2 Section
    """)

_SAMPLE_ADOC_DOCUMENT_WITH_UNIQUE_VERSIONED_IDS = dedent(
    """
    = Top Level

    [.level,id=1,version=1]
    == ID 1 Version 1 Section

    [.level,id=1,version=2]
    == ID 1 Version 2 Section
    """)

_SAMPLE_ADOC_DOCUMENT_WITH_NON_UNIQUE_VERSIONED_IDS = dedent(
    """
    = Top Level

    [.level,id=1,version=1]
    == ID 1 Version 1 Section

    [.level,id=1,version=1]
    == ID 1 Version 1 Section
    """)

_SAMPLE_ADOC_DOCUMENT_WITH_NON_UNIQUE_NON_VERSIONED_IDS = dedent(
    """
    = Top Level

    [.level,id=1]
    == ID 1 Section

    [.level,id=1]
    == Second ID 1 Section
    """)

_SAMPLE_ADOC_DOCUMENT_WITH_MIXED_VERSIONED_AND_NON_VERSIONED_IDS = dedent(
    """
    = Top Level

    [.level,id=1]
    == ID 1 Section

    [.level,id=1,version=1]
    == ID 1 Version 1 Section
    """)


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_IDS])
def test_everything_included(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend())
    assert 'Top Level' in data, data
    assert 'Level Section' in data, data
    assert 'level summary' in data, data
    assert 'level second paragraph' in data, data
    assert 'Level Subsection' in data, data
    assert 'sublevel summary' in data, data
    assert 'sublevel second paragraph' in data, data
    assert 'Level Subsubsection 3' in data, data
    assert 'id 3 content' in data, data
    assert 'Level Subsubsection 4' in data, data
    assert 'id 4 content' in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_IDS])
def test_exclude_id_removes_section_and_subsections(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--exclude-ids 1 --keep-empty-sections true'))
    assert 'Top Level' in data, data
    assert 'Level Section' not in data, data
    assert 'level summary' not in data, data
    assert 'level second paragraph' not in data, data
    assert 'Level Subsection' not in data, data
    assert 'sublevel summary' not in data, data
    assert 'sublevel second paragraph' not in data, data
    assert 'Level Subsubsection 3' not in data, data
    assert 'id 3 content' not in data, data
    assert 'Level Subsubsection 4' not in data, data
    assert 'id 4 content' not in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_IDS])
def test_include_subsection_id_in_excluded_section_has_no_effect(zpider_yaml_backend):
    data = _flat_value_map(
        zpider_yaml_backend('--exclude-ids 1 --include-ids 2 --keep-empty-sections true'))
    assert 'Top Level' in data, data
    assert 'Level Section' not in data, data
    assert 'level summary' not in data, data
    assert 'level second paragraph' not in data, data
    assert 'Level Subsection' not in data, data
    assert 'sublevel summary' not in data, data
    assert 'sublevel second paragraph' not in data, data
    assert 'Level Subsubsection 3' not in data, data
    assert 'id 3 content' not in data, data
    assert 'Level Subsubsection 4' not in data, data
    assert 'id 4 content' not in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_IDS])
def test_exclude_id_has_priority_over_include_id(zpider_yaml_backend):
    data = _flat_value_map(
        zpider_yaml_backend('--exclude-ids 1 --include-ids 1 --keep-empty-sections true'))
    assert 'Top Level' in data, data
    assert 'Level Section' not in data, data
    assert 'level summary' not in data, data
    assert 'level second paragraph' not in data, data
    assert 'Level Subsection' not in data, data
    assert 'sublevel summary' not in data, data
    assert 'sublevel second paragraph' not in data, data
    assert 'Level Subsubsection 3' not in data, data
    assert 'id 3 content' not in data, data
    assert 'Level Subsubsection 4' not in data, data
    assert 'id 4 content' not in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_IDS])
def test_excluded_subsection_in_included_section_is_excluded(zpider_yaml_backend):
    data = _flat_value_map(
        zpider_yaml_backend('--exclude-ids 2 --include-ids 1 --keep-empty-sections true'))
    assert 'Top Level' in data, data
    assert 'Level Section' in data, data
    assert 'level summary' in data, data
    assert 'level second paragraph' in data, data
    assert 'Level Subsection' not in data, data
    assert 'sublevel summary' not in data, data
    assert 'sublevel second paragraph' not in data, data
    assert 'Level Subsubsection 3' not in data, data
    assert 'id 3 content' not in data, data
    assert 'Level Subsubsection 4' not in data, data
    assert 'id 4 content' not in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_IDS])
def test_include_subsection_id_also_include_parent_id(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--include-ids 2 --keep-empty-sections true'))
    assert 'Top Level' in data, data
    assert 'Level Section' in data, data
    assert 'level summary' in data, data
    assert 'level second paragraph' in data, data
    assert 'Level Subsection' in data, data
    assert 'sublevel summary' in data, data
    assert 'sublevel second paragraph' in data, data
    assert 'Level Subsubsection 3' not in data, data
    assert 'id 3 content' not in data, data
    assert 'Level Subsubsection 4' not in data, data
    assert 'id 4 content' not in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_UNIQUE_NON_VERSIONED_IDS])
def test_unique_non_versioned_ids_are_allowed(zpider_yaml_backend):
    zpider_yaml_backend()


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_UNIQUE_VERSIONED_IDS])
def test_unique_versioned_ids_are_allowed(zpider_yaml_backend):
    zpider_yaml_backend()


@requires(zpider='Zpider')
@requires(workspace='Workspace')
def test_non_unique_versioned_ids_are_not_allowed(zpider, workspace):
    adoc_file = workspace.create_file(
        'input.adoc', content=_SAMPLE_ADOC_DOCUMENT_WITH_NON_UNIQUE_VERSIONED_IDS)
    result = zpider('yaml {adoc_file}'.format(adoc_file=adoc_file), expected_exit_code=1)
    assert 'ID version numbers must be unique. Seen version 1 for ID 1 multiple times' in result.stderr, result.stderr


@requires(zpider='Zpider')
@requires(workspace='Workspace')
def test_non_unique_non_versioned_ids_are_not_allowed(zpider, workspace):
    adoc_file = workspace.create_file(
        'input.adoc', content=_SAMPLE_ADOC_DOCUMENT_WITH_NON_UNIQUE_NON_VERSIONED_IDS)
    result = zpider('yaml {adoc_file}'.format(adoc_file=adoc_file), expected_exit_code=1)
    assert 'IDs must be unique. Seen ID 1 multiple times.' in result.stderr, result.stderr


@requires(zpider='Zpider')
@requires(workspace='Workspace')
def test_mixed_versioned_and_non_versioned_ids_are_not_allowed(zpider, workspace):
    adoc_file = workspace.create_file(
        'input.adoc', content=_SAMPLE_ADOC_DOCUMENT_WITH_MIXED_VERSIONED_AND_NON_VERSIONED_IDS)
    result = zpider('yaml {adoc_file}'.format(adoc_file=adoc_file), expected_exit_code=1)
    assert 'Versioned and non-versioned IDs can not be mixed. Mixed use for ID 1' in result.stderr, result.stderr
