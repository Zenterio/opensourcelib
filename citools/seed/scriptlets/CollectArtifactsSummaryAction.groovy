/**
 * Auto-generated script from template CollectArtifactsSummaryAction.groovy
 *
 * topJobName:      #TOP_JOB_NAME#
 * topBuildNumber:  #TOP_BUILD_NUMBER#
 * iconPath:        #ICON#
 *
 *
 * This script writes a result summary to the collect-artifacts build page.
 *
 * It is a groovy post build step.
 *
 * Environment variables/job arguments used:
 * top_job_name : Name of flow-job to copy artifacts from.
 * top_build_number : Number of the build.
 *
 */
// logic wrapped in closure to avoid polluting global scope
{ it ->
    def build = manager.build
    String topJobName = "#TOP_JOB_NAME#"
    String topBuildNumber = "#TOP_BUILD_NUMBER#"
    def topBuild = manager.hudson.getItem(topJobName).getBuildByNumber(topBuildNumber.toInteger())

    String topBuildUrl = topBuild.getUrl()
    String iconPath = "#ICON#"

    boolean success = (build.result == hudson.model.Result.SUCCESS)

    String htmlLinkToTopBuild = "<a href='/${topBuildUrl}'>${topJobName} #${topBuildNumber}</a>"
    String htmlLinkToDetails = "<a href='console'>details</a>"
    String externalBuildNumber = topBuildNumber
    String dateString = new java.text.SimpleDateFormat("yyyyMMdd").format(build.getTime())
    String newFileName = "${topJobName}-build-${topBuildNumber}-ext-${externalBuildNumber}-${dateString}.zip"
    String htmlLinkToDownload = "<a href='artifact/*zip*/${newFileName}'>${newFileName}</a>"
    String message = ""
    def summary = null

    if (success) {
        /* release packaging build */
        message = """Packaging of build ${htmlLinkToTopBuild} completed.
Please note that the artifacts are only saved for the
last build so make sure to download ${htmlLinkToDownload} now."""
        summary = manager.createSummary(iconPath)
        summary.appendText(message + ' ', false)
    } else {
        /* release packaging build */
        message = "Error: release packaging ${htmlLinkToTopBuild} failed."
        summary = manager.createSummary("error.png")
        summary.appendText(message + ' ', false)
        summary.appendText("(${htmlLinkToDetails}) ", false)
    }

}();
