import logging
import re
from textwrap import dedent

from k2.runner.decorator import foreach
from zaf.component.decorator import requires

from systest.lib.httpmock import HttpMock
from systest.lib.znake import CreateFullZnakeBuild, ZnakePipeline

logger = logging.getLogger('testcase')


class JenkinsException(Exception):
    pass


@requires(build=CreateFullZnakeBuild, scope='session')
def test_all_znake_steps_are_run(build):
    console_log = build.console_log
    assert 'source ./activate' in console_log
    assert "Running 'static'" in console_log
    assert "Running 'test'" in console_log
    assert "Running 'systest'" in console_log
    assert "Running 'pypi'" in console_log
    assert "Running 'doc'" in console_log
    assert "Running 'deb'" in console_log
    assert "Running 'debtest'" in console_log


@requires(build=CreateFullZnakeBuild)
def test_all_znake_artifacts_are_created(build):
    artifacts = build.artifacts
    assert 'build/dist/xenial/zenterio-znake_0.19.0+0+xenial_amd64.deb' in artifacts
    assert 'build/doc/user_guide.tar.gz' in artifacts
    assert 'build/pypi/sdist/zenterio-znake-0.25.0+0.tar.gz' in artifacts
    assert 'build/pypi/wheel/zenterio_znake-0.25.0+0-py3-none-any.whl' in artifacts
    # assert 'build/test/output-local/reports/testng/testng-results.xml' in artifacts
    # assert 'build/test/output-u16/reports/testng/testng-results.xml' in artifacts
    assert 'build/test/output-u16/logs/all.log' in artifacts


@requires(znake=ZnakePipeline)
def test_setup_step_can_be_skipped(znake):
    znake.jenkinsfile("znake(name: 'project', skipStages: ['Setup'])")
    build_info = znake.build()
    assert 'source ./activate' not in build_info.console_log


@foreach(step=['Static', 'Test', 'Systest', 'Pypi', 'Doc', 'Deb', 'Debtest', 'Publish'])
@requires(znake=ZnakePipeline)
def test_step_can_be_skipped(step, znake):
    znake.jenkinsfile("znake(name: 'project', skipStages: ['{step}'])".format(step=step))
    build_info = znake.build()
    assert "Running '{step}'".format(step=step.lower()) not in build_info.console_log


@requires(znake=ZnakePipeline)
def test_systest_coverage_enabled_by_default(znake):
    znake.jenkinsfile("znake(name: 'project', systestCoverage: true)")
    build_info = znake.build()
    assert "Running 'systest': -e --root --coverage systest" in build_info.console_log
    assert "Running 'systest': -e --root systest" not in build_info.console_log


@requires(znake=ZnakePipeline)
def test_systest_coverage_can_be_disabled(znake):
    znake.jenkinsfile("znake(name: 'project', systestCoverage: false)")
    build_info = znake.build()
    assert "Running 'systest': -e --root --coverage systest" not in build_info.console_log
    assert "Running 'systest': -e --root systest" in build_info.console_log


@requires(znake=ZnakePipeline)
def test_running_znake_in_sub_directory(znake):
    znake.file('subdir/.placeholder', '')
    znake.jenkinsfile("znake(name: 'project', dir: 'subdir', skipStages: ['Setup'])")
    build_info = znake.build()
    assert re.search(r'cd [\w\d_@/]+/subdir', build_info.console_log) is not None


@requires(znake=ZnakePipeline)
def test_running_znake_with_znake_prefix(znake):
    znake.jenkinsfile("znake(name: 'project', znakePrefix: '/znake/')")
    build_info = znake.build()
    assert '/znake/znake' in build_info.console_log


@requires(znake=ZnakePipeline)
@requires(http_mock=HttpMock)
def test_znake_can_publish_docs(znake, http_mock):
    znake.jenkinsfile(
        dedent(
            """\
        znake(
            name: 'project',
            artifactoryUrl: '{artifactor_url}',
            skipStages: [
               'Deb', 'Pypi'
            ])
        """.format(artifactor_url=http_mock.pretend_url)))
    http_mock.when('POST .*/artifactory/.*').reply(status=200)
    znake.build(publish=True)

    request = http_mock.get_request(0)

    assert request.method == 'PUT', request.method
    m = re.match(r'/artifactory/docs/Project/user_guide-(\d+).tar.gz', request.url)
    assert m is not None, request.url
    assert int(m.group(1)) > 1000 and int(m.group(1)) < 2000, m.group(1)


@requires(znake=ZnakePipeline)
@requires(http_mock=HttpMock)
def test_znake_can_publish_debs(znake, http_mock):
    znake.jenkinsfile(
        dedent(
            """\
        znake(
            name: 'project',
            artifactoryUrl: '{artifactor_url}',
            skipStages: [
               'Doc', 'Pypi'
            ])
        """.format(artifactor_url=http_mock.pretend_url)))
    http_mock.when('PUT .*/artifactory/.*').reply(status=200)
    znake.build(publish=True)

    request = http_mock.get_request(0)

    assert request.method == 'PUT', request.method
    assert request.url == (
        '/artifactory/debian-local/pool/zenterio-znake_0.19.0+0+xenial_amd64.deb;'
        'deb.distribution=xenial;deb.component=main;deb.architecture=amd64'), request.url


@requires(znake=ZnakePipeline)
def test_znake_can_publish_pypi(znake):
    znake.jenkinsfile(
        dedent(
            """\
        znake(
            name: 'project',
            znakePrefix: '/znake/',
            skipStages: [
               'Doc', 'Deb'
            ])
        """))

    build_info = znake.build(publish=True)
    assert (
        "Running 'twine': "
        'upload build/pypi/sdist/zenterio-znake-0.25.0+0.tar.gz '
        'build/pypi/wheel/zenterio_znake-0.25.0+0-py3-none-any.whl '
        '--repository-url http://pip.zenterio.lan/artifactory/api/pypi/pypi-local '
        '-u **** -p ****') in build_info.console_log
