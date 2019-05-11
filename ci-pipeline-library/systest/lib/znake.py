from zaf.component.decorator import component, requires

from systest.lib.git import JenkinsFileRepo, SystemUnderTestRepo


@component(name='CreateFullZnakeBuild', scope='session')
@requires(jenkins='Jenkins')
@requires(_update_vars=SystemUnderTestRepo)
@requires(jenkinsfile=JenkinsFileRepo, args=['full_znake_pipeline'], scope='session')
class CreateFullZnakeBuild(object):
    """
    Runs a full znake build as a pre-step to the test cases.

    This can be used to run multiple test cases towards a pre-made build,
    that includes all steps, to assert different things.
    """

    def __init__(self, jenkins, _update_vars, jenkinsfile):
        self._jenkins = jenkins
        self._jenkinsfile = jenkinsfile

    def __enter__(self):
        self._jenkinsfile.update_jenkins_file("znake(name: 'project', skipStages: ['Publish'])")
        build_info = self._jenkins.build_job(
            'default', {'BRANCH': self._jenkinsfile.branch,
                        'PUBLISH': False},
            build_timeout=10,
            name_suffix=':' + self._jenkinsfile.branch)
        assert build_info.result == 'SUCCESS', build_info.result
        return build_info

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@component(name='ZnakePipeline', scope='test')
@requires(jenkins='Jenkins')
@requires(_update_vars=SystemUnderTestRepo)
@requires(jenkinsfile=JenkinsFileRepo)
class ZnakePipeline(object):
    """Component that can be used to build a znake pipeline with configurable Jenkinsfile content."""

    def __init__(self, jenkins, _update_vars, jenkinsfile):
        self._jenkins = jenkins
        self._jenkinsfile = jenkinsfile

    def jenkinsfile(self, command):
        self._jenkinsfile.update_jenkins_file(command)

    def file(self, file, content):
        self._jenkinsfile.update_file(file, content)

    def build(self, publish=False):
        job_parameters = {'BRANCH': self._jenkinsfile.branch, 'PUBLISH': publish}
        build_info = self._jenkins.build_job(
            'default', job_parameters, build_timeout=10, name_suffix=self._jenkinsfile.branch)
        assert build_info.result == 'SUCCESS', build_info.result
        return build_info
