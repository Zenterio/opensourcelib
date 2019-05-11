from textwrap import dedent

from zaf.component.decorator import requires

from systest.localtests import ZpiderYamlBackendAppliedToSampleDocument
from systest.localtests.test_document_structure import _flat_value_map

_SAMPLE_ADOC_DOCUMENT_WITH_VERSIONED_IDS = dedent(
    """
    = Top Level

    [.level]
    == Level 1 Section

    feature 1 summary

    [.subsublevel, id=1, version=1]
    === Feature 1 Version 1 Subsection

    feature 1 version 1 content

    [.subsublevel, id=1, version=2]
    === Feature 1 Version 2 Subsection

    feature 1 version 2 content

    [.level]
    == Level 2 Section

    feature 2 summary

    [.subsublevel, id=2, version=2]
    === Feature 2 Version 2 Subsection

    feature 2 version 2 content

    [.subsublevel, id=2, version=3]
    === Feature 2 Version 3 Subsection

    feature 2 version 3 content
    """)


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_VERSIONED_IDS])
def test_everything_is_included_by_default(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--keep-all-versions true'))
    assert 'Top Level' in data, data
    assert 'Level 1 Section' in data, data
    assert 'feature 1 summary' in data, data
    assert 'Feature 1 Version 1 Subsection' in data, data
    assert 'feature 1 version 1 content' in data, data
    assert 'Feature 1 Version 2 Subsection' in data, data
    assert 'feature 1 version 2 content' in data, data
    assert 'Level 2 Section' in data, data
    assert 'feature 2 summary' in data, data
    assert 'Feature 2 Version 2 Subsection' in data, data
    assert 'feature 2 version 2 content' in data, data
    assert 'Feature 2 Version 3 Subsection' in data, data
    assert 'feature 2 version 3 content' in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_VERSIONED_IDS])
def test_keep_highest_version_filters_out_everything_but_the_highest_version(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend())
    assert 'Top Level' in data, data
    assert 'Level 1 Section' in data, data
    assert 'feature 1 summary' in data, data
    assert 'Feature 1 Version 1 Subsection' not in data, data
    assert 'feature 1 version 1 content' not in data, data
    assert 'Feature 1 Version 2 Subsection' in data, data
    assert 'feature 1 version 2 content' in data, data
    assert 'Level 2 Section' in data, data
    assert 'feature 2 summary' in data, data
    assert 'Feature 2 Version 2 Subsection' not in data, data
    assert 'feature 2 version 2 content' not in data, data
    assert 'Feature 2 Version 3 Subsection' in data, data
    assert 'feature 2 version 3 content' in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_VERSIONED_IDS])
def test_max_allowed_version_caps_what_versions_are_included(zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--max-allowed-version 2'))
    assert 'Top Level' in data, data
    assert 'Level 1 Section' in data, data
    assert 'feature 1 summary' in data, data
    assert 'Feature 1 Version 1 Subsection' not in data, data
    assert 'feature 1 version 1 content' not in data, data
    assert 'Feature 1 Version 2 Subsection' in data, data
    assert 'feature 1 version 2 content' in data, data
    assert 'Level 2 Section' in data, data
    assert 'feature 2 summary' in data, data
    assert 'Feature 2 Version 2 Subsection' in data, data
    assert 'feature 2 version 2 content' in data, data
    assert 'Feature 2 Version 3 Subsection' not in data, data
    assert 'feature 2 version 3 content' not in data, data


@requires(
    zpider_yaml_backend=ZpiderYamlBackendAppliedToSampleDocument,
    args=[_SAMPLE_ADOC_DOCUMENT_WITH_VERSIONED_IDS])
def test_max_allowed_version_excludes_everything_that_is_a_higher_version_number(
        zpider_yaml_backend):
    data = _flat_value_map(zpider_yaml_backend('--max-allowed-version 0.1'))
    assert 'Top Level' in data, data
    assert 'Level 1 Section' in data, data
    assert 'feature 1 summary' in data, data
    assert 'Feature 1 Version 1 Subsection' not in data, data
    assert 'feature 1 version 1 content' not in data, data
    assert 'Feature 1 Version 2 Subsection' not in data, data
    assert 'feature 1 version 2 content' not in data, data
    assert 'Level 2 Section' in data, data
    assert 'feature 2 summary' in data, data
    assert 'Feature 2 Version 2 Subsection' not in data, data
    assert 'feature 2 version 2 content' not in data, data
    assert 'Feature 2 Version 3 Subsection' not in data, data
    assert 'feature 2 version 3 content' not in data, data
