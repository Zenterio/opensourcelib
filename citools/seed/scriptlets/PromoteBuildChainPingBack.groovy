/**
 * This script writes a result summary to the source build of a build chain promotion.
 *
 * It is a groovy post build step.
 *
 * Environment variables/job arguments used:
 * top_job_name : Name of job to propagate information from
 * top_build_number : Number of the build.
 *
 * Icon: #ICON#
 */
// logic wrapped in closure to avoid polluting global scope
{ it ->
    def env = manager.build.getEnvironment(manager.listener)
    def build = manager.build
    def promoteBuildUrl = build.getUrl()
    def topJobName = env['top_job_name']
    def topBuildNumber = env['top_build_number']
    def topBuild = manager.hudson.getItem(topJobName).getBuildByNumber(Integer.parseInt(topBuildNumber))
    def topBuildUrl = topBuild.getUrl()
    def icon = "#ICON#"

    def success = (build.result == hudson.model.Result.SUCCESS)

    def htmlLinkToTopBuild = "<a href='/${topBuildUrl}'>${topJobName} #${topBuildNumber}</a>"
    def htmlLinkToDetails = "<a href='/${promoteBuildUrl}console'>details</a>"

    def message = ""
    def reason = ""
    def summary = null

    if (success) {
        def matcher = manager.getLogMatcher("Propagating promotion status for .* #.* to (.*)\$")
        level = matcher.group(1)

        /* promote-build */
        message = "Promoted build chain to level ${level}, ${htmlLinkToTopBuild}"
        summary = manager.createSummary(icon)
        summary.appendText(message + ' ', false)

        /* top job that is being promoted */
        manager.setBuild(topBuild)
        summary = manager.createSummary(icon)
        message = "Setting whole build chain to promotion ${level}."
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)
    } else {
        /* promote-build */
        message = "Error: promoting build chain ${htmlLinkToTopBuild} failed."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)

        /* top job that is being promoted */
        manager.setBuild(topBuild)

        def index = manager.build.getActions(summary.getClass()).size()
        def htmlDeleteImage = "<img src='${manager.hudson.RESOURCE_PATH}/images/16x16/stop.png' alt='Remove notification' title='Remove notification'/>"
        def htmlRemoveSummary = "<a href='/${topBuildUrl}parent/parent/plugin/groovy-postbuild/removeSummary?index=${index}'>${htmlDeleteImage}</a>"

        message = "Error: promoting build chain failed."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)
        summary.appendText("${htmlRemoveSummary} ", false)
    }

    // Restore global state
    manager.setBuild(build)
}();
