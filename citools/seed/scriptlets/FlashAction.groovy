/**
 * Auto-generated script from template FlashAction.groovy
 *      FLASH_JOB_NAME: #FLASH_JOB_NAME#
 *      ICON: #ICON#
 */
// Class definitions

// logic wrapped in closure to avoid polluting global scope
{ it ->
    String flashJobName = "#FLASH_JOB_NAME#"
    String iconPath = "#ICON#"
    String defaultKfsFileName = "result/kfs.zmg"

    String latestFlashJobURI = "/job/${flashJobName}/lastBuild"
    String buildFlashJobPostURI = "/job/${flashJobName}/build?delay=0sec"
    String buildJobName = URLEncoder.encode(manager.build.getEnvironment(manager.listener)['JOB_NAME'], 'utf-8')
    String buildNumber = manager.build.getEnvironment(manager.listener)['BUILD_NUMBER']
    String returnURI = "/job/${buildJobName}/${buildNumber}/"

    String flashHtml = """\
<a onclick="toggle_flash_parameter_form_${buildNumber}()" href="javascript:;">
    <div onMouseOver="this.style.backgroundColor='#D3D4FF';" onMouseOut="this.style.backgroundColor='#FFFFFF';" style="padding: 10px; min-width: 200px; display: inline-block; border: 1px solid; border-radius:5px;">
        <b>Flash STB</b>
    </div>
</a>

<form action="#" onSubmit="flash_POST_${buildNumber}(this); return false;" id="flash_parameter_form_${buildNumber}" style="display: none;">
    Image file:<br><input type="text" name="kfs_file" style="display:table-cell; width:100%" required value="${defaultKfsFileName}">
    <br>
    STB IP-address:<br><input type="text" name="ip_address" style="display:table-cell; width:100%" required>
    <p>
    <input type="submit" value="Flash">
</form>
<script>
function toggle_flash_parameter_form_${buildNumber}() {
    Q('#flash_parameter_form_${buildNumber}').toggle(300);
}

function flash_POST_${buildNumber}(parameter_form) {
    var form = Q('#flash_form_${buildNumber}')[0];
    var flash_JSONEscape = function(str) {
        return str.replace(/\\n/g, "\\\\n")
                  .replace(/\\"/g, '\\\\"')
                  .replace(/\\r/g, "\\\\r")
                  .replace(/\\t/g, "\\\\t");
    };

    form.elements['json'].value = form.elements['json'].value.replace('KFS_FILE', flash_JSONEscape(parameter_form.kfs_file.value));
    form.elements['json'].value = form.elements['json'].value.replace('IP_ADDRESS', flash_JSONEscape(parameter_form.ip_address.value));

    Q.post(form.action, 'json=' + form.elements['json'].value)
        .done(function() {
            var result = confirm('Flash job has been scheduled. The results will be published on this page. ' +
                                 'The flash job is available in this location: ${latestFlashJobURI}\\n\\n'+
                                 'To be redirected to the latest flash job, press OK.\\n' +
                                 'To stay on this page, press Cancel.');

            if (result) {
                location.replace('${latestFlashJobURI}');
            }
        })
        .fail(function() {
            alert('The flash packaging job could not be scheduled. Are you sure you are logged in?');
        });
}
</script>
"""

    def params = []
    params.add([name: "kfs_job_name", value: buildJobName])
    params.add([name: "kfs_build_number", value: buildNumber])
    params.add([name: "kfs_file", value: "KFS_FILE"])
    params.add([name: "ip_address", value: "IP_ADDRESS"])

    def jsonBuilder = new groovy.json.JsonBuilder(parameter: params, statusCode: "303", redirectTo: returnURI)
    def formHtml = """\
<form class="no-json" style="display:inline" id="flash_form_${buildNumber}" method="POST" action="${buildFlashJobPostURI}"><input type="hidden" name="json" value='${jsonBuilder.toString()}' /></form>"""

    def summary = manager.createSummary(iconPath)
    summary.appendText(formHtml + flashHtml, false)
}();
