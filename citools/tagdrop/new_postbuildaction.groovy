def buildJobPostURI = "/job/tag-build/build?delay=0sec"
def returnURI = "/job/" + manager.build.getEnvironment(manager.listener)['JOB_NAME']
def buildJobName = manager.build.getEnvironment(manager.listener)['JOB_NAME']
def buildNumber = manager.build.getEnvironment(manager.listener)['BUILD_NUMBER']
def inputString = ""
def params = []
def jsonBuilder = new groovy.json.JsonBuilder()
def tagHTML = """\
<a onclick="scm_tag_POST_${buildNumber}()" href="#">tag</a><script>
function scm_tag_POST_${buildNumber}()
        {
            var tagName="DROP_0_SPRINT_0";

            while (true)
            {
                tagName=prompt("Please enter your tag name to be pushed to all build repositories.",tagName);
                if (tagName!=null && tagName!="")
                {
                    var form = \$('scm_tag_form_${buildNumber}');
                    form.elements['json'].value = form.elements['json'].value.replace('JENKINS_TAG_NAME', tagName);
                    //crumb.appendToForm(form);
                    form.submit();
                    return true;
                }
                else
                {
                    return false;
                }
            }
            return false;
        }</script>
"""

class MyPara
{
  def name
  def value
}
params.add(new MyPara(name: "original_tag", value: manager.build.buildVariableResolver.resolve("tag")))
params.add(new MyPara(name: "tag_name", value: "JENKINS_TAG_NAME"))
params.add(new MyPara(name: "tag_build_job_name", value: buildJobName))
params.add(new MyPara(name: "tag_build_number", value: buildNumber))
params.add(new MyPara(name: "repositories", value: "zids fs"))
jsonBuilder(parameter: params, statusCode: "303", redirectTo: returnURI)
inputString += """\
<form class="no-json" style="display:inline" id="scm_tag_form_${buildNumber}" method="POST" action="${buildJobPostURI}"><input type="hidden" name="json" value='${jsonBuilder.toString()}' /></form>"""
manager.addShortText(inputString+ tagHTML)

