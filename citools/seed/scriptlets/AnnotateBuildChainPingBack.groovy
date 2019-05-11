/**
 * This script writes a result summary to the source build of an annotation update.
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
    def annotateBuildUrl = build.getUrl()
    def topJobName = env['top_job_name']
    def topBuildNumber = env['top_build_number']
    def topBuild = manager.hudson.getItem(topJobName).getBuildByNumber(Integer.parseInt(topBuildNumber))
    def topBuildUrl = topBuild.getUrl()
    def icon = "#ICON#"

    def success = (build.result == hudson.model.Result.SUCCESS)

    def htmlLinkToTopBuild = "<a href='/${topBuildUrl}'>${topJobName} #${topBuildNumber}</a>"
    def htmlLinkToDetails = "<a href='/${annotateBuildUrl}console'>details</a>"

    def message = ""
    def reason = ""
    def summary = null
    def annotation = ""

    if (success) {
        annotation = topBuild.getDescription()

        /* annotate-build */
        message = "Annotation from ${htmlLinkToTopBuild}\n${annotation}"
        summary = manager.createSummary(icon)
        summary.appendText(message + ' ', false)

        /* top job whose annotation was copied */
        manager.setBuild(topBuild)
        summary = manager.createSummary(icon)
        message = "Setting annotation for whole build chain to:\n${annotation}"
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)
    } else {
        /* annotate-build */
        message = "Error: annotating build chain ${htmlLinkToTopBuild} failed."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)

        /* top job that is being annotated */
        manager.setBuild(topBuild)

        def index = manager.build.getActions(summary.getClass()).size()
        def htmlDeleteImage = "<img src='${manager.hudson.RESOURCE_PATH}/images/16x16/stop.png' alt='Remove notification' title='Remove notification'/>"
        def htmlRemoveSummary = "<a href='/${topBuildUrl}parent/parent/plugin/groovy-postbuild/removeSummary?index=${index}'>${htmlDeleteImage}</a>"

        message = "Error: annotating build chain failed."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)
        summary.appendText("${htmlRemoveSummary} ", false)
    }

    // Restore global state
    manager.setBuild(build)
}();
