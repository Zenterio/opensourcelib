/**
 * Auto-generated script from template ReleasePackagingSummaryAction.groovy
 *      Release-Packaging-job-name: #RELEASE_PACKAGING_JOB_NAME#
 *      Icon-path: #ICON#
 *      Configurable: #RELEASE_PACKAGING_CONFIGURABLE#
 *      Project: #PROJECT#
 *      Origin: #ORIGIN#
 *
 * This script assumes the existence of the BUILD_TAG environment variable created
 * by the git plugin currently only fulfilled by the Origin jobs.
 */
// Class definitions
class ReleasePackagingParameter
{
    String name
    String value

    ReleasePackagingParameter(String name, String value) {
        this.name = name
        this.value = value
    }
}
// logic wrapped in closure to avoid polluting global scope
{ it ->
    /*
     * Disabled by ZMT-3206
     * TODO: Prevent release-packaging for failed builds
     * Enable this again when we have async tests.
     *
    if (manager.build.result == hudson.model.Result.FAILURE) {
        return
    }
    */
    Boolean configurable = "#RELEASE_PACKAGING_CONFIGURABLE#".toBoolean()
    String releasePackagingJobName = "#RELEASE_PACKAGING_JOB_NAME#"
    String latestReleasePackagingJobURI = "/job/${releasePackagingJobName}/lastBuild"
    String buildJobName = manager.build.getEnvironment(manager.listener)['JOB_NAME']
    String buildJobPostURI = "/job/${releasePackagingJobName}/build?delay=0sec"
    String buildNumber = manager.build.getEnvironment(manager.listener)['BUILD_NUMBER']
    String returnURI = "/job/${buildJobName}/${buildNumber}/"

    String readonly = configurable ? "" : "readonly"
    String default_annotation = configurable ? "" : buildNumber
    String default_tag = configurable ? "" : "#PROJECT#_#ORIGIN#_${buildNumber}".toUpperCase().replace("-", "")

    String iconPath = "#ICON#"
    String annotateHtml = """\
<a onclick="toggle_release_packaging_parameter_form_${buildNumber}()" href="javascript:;">
    <div onMouseOver="this.style.backgroundColor='#D3D4FF';" onMouseOut="this.style.backgroundColor='#FFFFFF';" style="padding: 10px; min-width: 200px; display: inline-block; border: 1px solid; border-radius:5px;">
        <b>Release package build chain</b>
    </div>
</a>
<form action="#" onSubmit="release_packaging_POST_${buildNumber}(this); return false;" id="release_packaging_parameter_form_${buildNumber}" style="display: none;">
    Release:<br><input type="text" name="annotation" style="display:table-cell; width:100%" required ${readonly} value="${default_annotation}">
    <br>
    Description:<br><textarea name="description" style="display:table-cell; width:100%" rows="10" required></textarea>
    <br>
    GIT Tag:<br><input type="text" name="git_tag_name" style="display:table-cell; width:100%" required ${readonly} value="${default_tag}">
    <br>
    GIT Tag of previous release (Optional):<br><input type="text" name="previous_git_tag_name" style="display:table-cell; width:100%">
    <p>
    <input type="submit" value="Package">
</form>
<script>
function toggle_release_packaging_parameter_form_${buildNumber}() {
    Q('#release_packaging_parameter_form_${buildNumber}').toggle(300);
}

function release_packaging_JSONEscape(str) {
    return encodeURIComponent(str.replace(/\\n/g, "\\\\n")
              .replace(/\\"/g, '\\\\"')
              .replace(/\\r/g, "\\\\r")
              .replace(/\\t/g, "\\\\t"));
}

function release_packaging_POST_${buildNumber}(parameter_form) {
    var form = Q('#release_packaging_form_${buildNumber}')[0];
    var json = form.elements['json'].value
    json = json.replace('DESCRIPTION', release_packaging_JSONEscape(parameter_form.description.value));
    json = json.replace('ANNOTATION', release_packaging_JSONEscape(parameter_form.annotation.value));
    json = json.replace('GIT_TAG_NAME', release_packaging_JSONEscape(parameter_form.git_tag_name.value));
    json = json.replace('PREVIOUS_GIT_TAG_NAME', release_packaging_JSONEscape(parameter_form.previous_git_tag_name.value));

    Q.post(form.action, 'json=' + json)
        .done(function() {
            var result = confirm('The release packaging job has been scheduled. The results will be published on this page. ' +
                                 'For large projects this may take some time.\\n\\n' +
                                 'The latest release packaging job is available in this location: ${latestReleasePackagingJobURI}\\n\\n'+
                                 'To be redirected to the latest release packaging job, press OK.\\n' +
                                 'To stay on this page, press Cancel.');

            if (result) {
                location.replace('${latestReleasePackagingJobURI}');
            }
        })
        .fail(function() {
            alert('The release packaging job could not be scheduled.');
        });
}
</script>
"""

    def params = []
    params.add(new ReleasePackagingParameter("target_build_number", buildNumber))
    params.add(new ReleasePackagingParameter("description", "DESCRIPTION"))
    params.add(new ReleasePackagingParameter("annotation", "ANNOTATION"))
    params.add(new ReleasePackagingParameter("git_tag_name", "GIT_TAG_NAME"))
    params.add(new ReleasePackagingParameter("previous_git_tag_name", "PREVIOUS_GIT_TAG_NAME"))
    params.add(new ReleasePackagingParameter("source_tag", manager.build.getEnvironment(manager.listener)['BUILD_TAG']))

    def jsonBuilder = new groovy.json.JsonBuilder(parameter: params, statusCode: "303", redirectTo: returnURI)
    def formHtml = """\
<form class="no-json" style="display:inline" id="release_packaging_form_${buildNumber}" method="POST" action="${buildJobPostURI}"><input type="hidden" name="json" value='${jsonBuilder.toString()}' /></form>"""

    def summary = manager.createSummary(iconPath)
    summary.appendText(formHtml + annotateHtml, false)
}();
