from textwrap import dedent

from zaf.component.decorator import requires


@requires(app='ZafApp')
def test_internal_changelog(app):
    result = app(['changelog', 'changelogcommand'], 'changelog')
    assert 'First Open source release.' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_configurable_changelog(app):
    result = app(
        ['changelog', 'changelogcommand'],
        'changelog '
        '--changelog-versions version '
        '--changelog-version@date date '
        '--changelog-version@changes "This is a change" '
        '--changelog-version@changes "This is another change" ',
        application_context='standalone')

    expected = dedent(
        """\
        version: date

          This is a change
          This is another change
        """)

    assert expected in result.stdout, "Expected '{expected}' not found in '{stdout}'".format(
        expected=expected, stdout=result.stdout)
