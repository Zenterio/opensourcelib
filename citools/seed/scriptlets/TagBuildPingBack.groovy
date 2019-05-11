/**
 * @Summary
 * The script writes a result summary to the tag-build (performing the tagging)
 * build and the source build (the build being tagged).
 * It parses the log from the tag-build to determine the cause of a failure to
 * be able to report it in the summary.
 *
 */
// logic wrapped in closure to avoid polluting global scope
{ it ->
    def env = manager.build.getEnvironment(manager.listener)
    def build = manager.build
    def tagBuildUrl = build.getUrl()
    def taggedBuildJobName = env['TAG_BUILD_JOB_NAME']
    def taggedBuildNumber = env['TAG_BUILD_NUMBER']
    def tagName = env['TAG_NAME']
    def sourceTag = env['SOURCE_TAG']
    def taggedBuild = manager.hudson.getItem(taggedBuildJobName).getBuildByNumber(Integer.parseInt(taggedBuildNumber))
    def taggedBuildUrl = taggedBuild.getUrl()

    def success = (build.result == hudson.model.Result.SUCCESS)

    def htmlLinkToTaggedBuild = "<a href='/${taggedBuildUrl}'>${taggedBuildJobName} #${taggedBuildNumber}</a>"
    def htmlLinkDetails = "<a href='/${tagBuildUrl}console'>details</a>"

    def message = ""
    def reason = ""
    def summary = null

    if (success)
    {
        /* tag-build */
        message = "Tagged ${htmlLinkToTaggedBuild} with ${tagName} in SCM, source tag ${sourceTag}."
        summary = manager.createSummary("attribute.png")
        summary.appendText(message + ' ', false)

        /* the source "tagged" build */
        manager.setBuild(taggedBuild)
        message = "Tagged build sources with ${tagName} in SCM, source tag ${sourceTag}."
        summary = manager.createSummary("attribute.png")
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkDetails}) ", false)
    }
    else
    {
        // parse the log for the cause of the failure
        if (manager.logContains(".*Error: Argument mismatch.*")) {
            // wrong configuration, should not happen
            reason = "Jenkins misconfiguration, please contact the Jenkins administrator."
        } else if (manager.logContains(".*Error: Source tag.*")) {
            // Source tag doesn't exist in one of the repositories
            reason = "The source tag (${sourceTag}) is not set in one or more of the repositories."
        } else if (manager.logContains(".*Error: Tag duplicate.*")) {
            // tag already exist in one of the repositories
            reason = "The tag to apply (${tagName}) is already in use in one or more of the repositories."
        } else {
            // operational failure most likely such as failing git command.
            reason = "The tagging operation failed for uknown reason. Please check the details."
        }

        /* tag-build */
        message = "Error: tagging ${htmlLinkToTaggedBuild} with ${tagName} failed, source tag ${sourceTag}."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText(reason + ' ', false)
        summary.appendText("(${htmlLinkDetails}) ", false)

        /* the source "tagged" build */
        manager.setBuild(taggedBuild)
        def index = manager.build.getActions(summary.getClass()).size()
        def htmlDeleteImage = "<img src='${manager.hudson.RESOURCE_PATH}/images/16x16/stop.png' alt='Remove notification' title='Remove notification'/>"
        def htmlRemoveSummary = "<a href='/${taggedBuildUrl}parent/parent/plugin/groovy-postbuild/removeSummary?index=${index}'>${htmlDeleteImage}</a>"

        message = "Error: tagging build with ${tagName} failed; source tag ${sourceTag}."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText(reason + ' ', false)
        summary.appendText("(${htmlLinkDetails}) ", false)
        summary.appendText("${htmlRemoveSummary} ", false)
    }
    // restore global state
    manager.setBuild(build)
}();
