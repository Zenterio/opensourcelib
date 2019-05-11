/**
 *  Auto-generated script from template SetBuildDisplayName.groovy
 *
 * setStartedBy: #SET_STARTED_BY#
 *
 * @Summary
 * Description:
 *
 * This groovy pre scm script changes the short display name of
 * a build to include the number of the external build number and
 * optionally the user that triggered the build.
 *
 * The script is intentionally a setter, because the display name
 * should be kept short and exact.
 *
 **/
// logic wrapped in closure to avoid polluting global scope
{ it ->
    String setStartedBy = "#SET_STARTED_BY#"
    def setName = "#${build.getNumber()}"
    def externalBuildNumber = "#EXT_BUILD_NUMBER#"
    if (externalBuildNumber != "null" && externalBuildNumber != "") {
        setName += " (#${externalBuildNumber})"
    }
    if (setStartedBy == "true") {
        def startedBy = findUserId(build)
        if (startedBy != null) {
            setName += " [${startedBy}]"
        }
    }
    build.setDisplayName(setName)
}();

def findUserId(build) {
    for (cause in build.getCauses()) {
        if (cause instanceof com.cloudbees.plugins.flow.FlowCause) {
            flowRun = ((com.cloudbees.plugins.flow.FlowCause) cause).getFlowRun()
            return findUserId(flowRun.getStartJob().getBuild())
        } else if (cause instanceof hudson.model.Cause.UpstreamCause) {
            return findUserId(cause.getUpstreamRun())
        } else if (cause instanceof hudson.model.Cause.UserIdCause) {
            return cause.userId
        }
    }
    return null
}