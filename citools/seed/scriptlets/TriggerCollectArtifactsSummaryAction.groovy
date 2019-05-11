/**
 * Auto-generated script from template TriggerCollectArtifactsSummaryAction.groovy (Seed scriptlet)
 *      job-name: #JOB-NAME#
 *      Icon: #ICON#
 */
// Class definitions
class CollectArtifactsFormParameter
{
    String name
    String value

    CollectArtifactsFormParameter(String name, String value) {
        this.name = name
        this.value = value
    }
}
// logic wrapped in closure to avoid polluting global scope
{ it ->
    if (manager.build.result == hudson.model.Result.FAILURE) {
        return
    }

    String latestCollectArtifactsJobURI = "/job/#JOB-NAME#/lastBuild"
    String buildJobPostURI = "/job/#JOB-NAME#/build?delay=0sec"
    String buildJobName = manager.build.getEnvironment(manager.listener)['JOB_NAME']
    String buildNumber = manager.build.getEnvironment(manager.listener)['BUILD_NUMBER']
    String returnURI = "/job/#JOB-NAME#/lastBuild/"
    String html = """\
<a onclick="collect_artifacts_POST_${buildNumber}()" href="#">
<div onMouseOver="this.style.backgroundColor='#D3D4FF';" onMouseOut="this.style.backgroundColor='#FFFFFF';" style="padding: 10px; min-width: 200px; display: inline-block; border: 1px solid; border-radius:5px;">
<b>Collect artifacts for this build flow</b>
</div></a><script>
function collect_artifacts_POST_${buildNumber}() {
    var form = \$('collect_artifacts_POST_${buildNumber}');

    Q.post(form.action, 'json=' + form.elements['json'].value)
        .done(function(response) {
            var result = confirm('The collect artifacts job has been scheduled. The results will be published on this page. ' +
                                 'For large projects this may take some time.\\n\\n' +
                                 'The latest collect artifacts job is available in this location: ${latestCollectArtifactsJobURI}\\n\\n' +
                                 'To be redirected to the latest collect artifacts job, press OK.\\n' +
                                 'To stay on this page, press Cancel.');

            if (result) {
                location.replace('${latestCollectArtifactsJobURI}');
            }
        })
        .fail(function() {
            alert('The collect artifacts job could not be scheduled.');
        });
}</script>
"""

    def params = []
    params.add(new CollectArtifactsFormParameter("target_build_name", buildJobName))
    params.add(new CollectArtifactsFormParameter("target_build_number", buildNumber))

    def jsonBuilder = new groovy.json.JsonBuilder(parameter: params,
            statusCode: "303", redirectTo: returnURI)
    def formHtml = """\
<form class="no-json" style="display:inline" id="collect_artifacts_POST_${buildNumber}" method="POST" action="${buildJobPostURI}"><input type="hidden" name="json" value='${jsonBuilder.toString()}' /></form>"""

    def summary = manager.createSummary("#ICON#")
    summary.appendText(formHtml + html, false)
}();
