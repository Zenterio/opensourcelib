/**
 * Auto-generated script from template ReleasePackagingPingBack.groovy
 *
 * topJobName:      #TOP_JOB_NAME#
 * topBuildNumber:  #TOP_BUILD_NUMBER#
 * iconPath:        #ICON#
 * publishPath:     #PUBLISH_PATH#
 *
 *
 * This script writes a result summary to the source build of an release packaging.
 *
 * It is a groovy post build step.
 *
 * Environment variables/job arguments used:
 * top_job_name : Name of job to propagate information from
 * top_build_number : Number of the build.
 *
 */
// logic wrapped in closure to avoid polluting global scope
{ it ->
    def build = manager.build
    def releasePackagingBuildUrl = build.getUrl()
    String topJobName = "#TOP_JOB_NAME#"
    String topBuildNumber = "#TOP_BUILD_NUMBER#"
    def topBuild = manager.hudson.getItem(topJobName).getBuildByNumber(topBuildNumber.toInteger())
    def topBuildUrl = topBuild.getUrl()
    String iconPath = "#ICON#"
    String publishPath = "#PUBLISH_PATH#"
    String escapedPath = new URI(null, publishPath, null).toASCIIString()

    def htmlLinkToTopBuild = "<a href='/${topBuildUrl}'>${topJobName} #${topBuildNumber}</a>"
    def htmlLinkToDetails = "<a href='/${releasePackagingBuildUrl}console'>details</a>"

    def message = ""
    def summary = null

    if (build.result == hudson.model.Result.SUCCESS) {
        /* release packaging build */
        message = "Packaging of build ${htmlLinkToTopBuild} completed.\n"
        summary = manager.createSummary(iconPath)
        summary.appendText(message + ' ', false)

        /* top job which was packaged for release */
        manager.setBuild(topBuild)
        summary = manager.createSummary(iconPath)
        message = """\
<div style="padding: 10px; border: 1px solid; border-radius: 5px; background-color: rgb(255, 255, 255);">
    ${build.buildVariableResolver.resolve("annotation")}  (${build.buildVariableResolver.resolve("git_tag_name")})
    <p>${build.buildVariableResolver.resolve("description").replace("\n", "<br />")}</p>
    <p><b>Published at: </b></p>
    <ul>
        <li>linna001.zenterio.lan/Gemensam/Externals/projects/${publishPath}</li>
        <li><a href="http://releases.zenterio.lan/${escapedPath}">releases.zenterio.lan/${publishPath}</a></li>
    </ul>
    <p>${htmlLinkToDetails}</p>
</div>
"""
        summary.appendText(message + ' ', false)
    } else {
        /* release packaging build */
        packagingBuildMessage = "Error: release packaging ${htmlLinkToTopBuild} failed."
        topBuildMessage = "Error: release packaging failed."
        if (manager.logContains(".*Destination folder.*already exists, aborting.*")) {
            errMsg = " Destination folder '${publishPath}' already exists. If you still wish to create another package from this build, rename or delete the previous one."
            packagingBuildMessage += errMsg
            topBuildMessage += errMsg
        }


        summary = manager.createSummary("error.png")
        summary.appendText(packagingBuildMessage + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)

        /* top job which was packaged for release */
        manager.setBuild(topBuild)

        def index = manager.build.getActions(summary.getClass()).size()
        def htmlDeleteImage = "<img src='${manager.hudson.RESOURCE_PATH}/images/16x16/stop.png' alt='Remove notification' title='Remove notification'/>"
        def htmlRemoveSummary = "<a href='/${topBuildUrl}parent/parent/plugin/groovy-postbuild/removeSummary?index=${index}'>${htmlDeleteImage}</a>"


        summary = manager.createSummary("error.png")
        summary.appendText(topBuildMessage + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)
        summary.appendText("${htmlRemoveSummary} ", false)
    }

    // Restore global state
    manager.setBuild(build)
}();
