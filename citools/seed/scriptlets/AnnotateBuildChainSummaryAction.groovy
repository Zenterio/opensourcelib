/**
 * Auto-generated script from template AnnotateBuildChainSummaryAction.groovy
 *      Annotate-job-name: #ANNOTATE_JOB_NAME#
 *      Icon: #ICON#
 */
// Class definitions
class AnnotateSummaryFormParameter
{
    String name
    String value

    AnnotateSummaryFormParameter(String name, String value) {
        this.name = name
        this.value = value
    }
}
// logic wrapped in closure to avoid polluting global scope
{ it ->
    if (manager.build.result == hudson.model.Result.FAILURE) {
        return
    }

    String buildJobName = manager.build.getEnvironment(manager.listener)['JOB_NAME']
    String buildJobPostURI = "/job/#ANNOTATE_JOB_NAME#/build?delay=0sec"
    String buildNumber = manager.build.getEnvironment(manager.listener)['BUILD_NUMBER']
    String returnURI = "/job/${buildJobName}/${buildNumber}/"
    String icon = "#ICON#"
    String iconHtml = """<img src="${icon}"/>"""
    String annotateHtml = """\
<a onclick="annotate_POST_${buildNumber}()" href="#">
<div onMouseOver="this.style.backgroundColor='#D3D4FF';" onMouseOut="this.style.backgroundColor='#FFFFFF';" style="padding: 10px; min-width: 200px; display: inline-block; border: 1px solid; border-radius:5px;">
<b>Annotate build chain</b>
</div></a>
<script>
function annotate_POST_${buildNumber}() {
    var form = \$('annotate_form_${buildNumber}');
    form.submit();
    return true;
}
</script>
"""

    def params = []
    params.add(new AnnotateSummaryFormParameter("top_build_number", buildNumber))
    params.add(new AnnotateSummaryFormParameter("top_job_name", buildJobName))

    def jsonBuilder = new groovy.json.JsonBuilder(parameter: params, statusCode: "303", redirectTo: returnURI)
    def formHtml = """\
<form class="no-json" style="display:inline" id="annotate_form_${buildNumber}" method="POST" action="${buildJobPostURI}"><input type="hidden" name="json" value='${jsonBuilder.toString()}' /></form>"""

    def summary = manager.createSummary(icon)
    summary.appendText(formHtml + annotateHtml, false)
}();
