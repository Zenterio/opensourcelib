/**
 * Auto-generated script from template TagBuildSummaryAction.groovy (Seed scriptlet)
 *      Tag-job-name: #TAG-JOB-NAME#
 *      Icon: #ICON#
 *      Repositories: #REPOSITORIES#
 *
 * This script assumes the existence of the BUILD_TAG environment variable created
 * by the git plugin currently only fulfilled by the Origin jobs.
 */
// Class definitions
class TagFormParameter
{
    String name
    String value

    TagFormParameter(String name, String value) {
        this.name = name
        this.value = value
    }
}
// logic wrapped in closure to avoid polluting global scope
{ it ->
    if (manager.build.result == hudson.model.Result.FAILURE) {
        return
    }

    String buildJobPostURI = "/job/#TAG-JOB-NAME#/build?delay=0sec"
    String buildJobName = manager.build.getEnvironment(manager.listener)['JOB_NAME']
    String buildNumber = manager.build.getEnvironment(manager.listener)['BUILD_NUMBER']
    String returnURI = "/job/${buildJobName}/${buildNumber}/"
    String sourceTag = manager.build.getEnvironment(manager.listener)['BUILD_TAG']
    String tagHtml = """\
<a onclick="scm_tag_POST_${buildNumber}()" href="#">
<div onMouseOver="this.style.backgroundColor='#D3D4FF';" onMouseOut="this.style.backgroundColor='#FFFFFF';" style="padding: 10px; min-width: 200px; display: inline-block; border: 1px solid; border-radius:5px;">
<b>Tag this build</b>
</div></a><script>
function scm_tag_POST_${buildNumber}()
        {
            if ("${sourceTag}" == "")
            {
                alert("This job did not receive a tag parameter (maybe because it was started without using a trigger job).\\nThis means that it can't be tagged using this mechanism.");
                return false;
            }
            var tagName="DROP_0_SPRINT_0";
            tagName=prompt("Please enter your tag name to be pushed to all build repositories (#REPOSITORIES#) for version ${sourceTag}.\\nThe tagging operation will take about a minute and status will be updated on the build page when completed.",tagName);
            if (tagName!=null && tagName!="")
            {
                var form = \$('scm_tag_form_${buildNumber}');
                form.elements['json'].value = form.elements['json'].value.replace('JENKINS_TAG_NAME', tagName);
                form.submit();
                return true;
            }
            return false;
        }</script>
"""

    def params = []
    params.add(new TagFormParameter("tag_name", "JENKINS_TAG_NAME"))
    params.add(new TagFormParameter("repositories", "#REPOSITORIES#"))
    params.add(new TagFormParameter("source_tag", sourceTag))
    params.add(new TagFormParameter("tag_build_job_name", buildJobName))
    params.add(new TagFormParameter("tag_build_number", buildNumber))

    def jsonBuilder = new groovy.json.JsonBuilder(parameter: params, statusCode: "303", redirectTo: returnURI)
    def formHtml = """\
<form class="no-json" style="display:inline" id="scm_tag_form_${buildNumber}" method="POST" action="${buildJobPostURI}"><input type="hidden" name="json" value='${jsonBuilder.toString()}' /></form>"""

    def summary = manager.createSummary("#ICON#")
    summary.appendText(formHtml + tagHtml, false)
}();
