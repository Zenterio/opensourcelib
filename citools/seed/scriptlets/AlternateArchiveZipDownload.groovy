/**
 * @Summary
 * Publish a link that give a renamed archive.zip
 */
// logic wrapped in closure to avoid polluting global scope
{  it ->
    def build = manager.build
    def workspace = build.project.getWorkspace()
    if (workspace.child("result").exists()) {
        def zidsVersionFile = workspace.child("result/configuration.mk")
        def zidsVersion = "UNKNOWN"
        if (zidsVersionFile.exists()) {
            zidsVersion = zidsVersionFile.readToString().find("ZSYS_SW_MODEL_VERSION = .*").substring(24)
        }
        def env = build.getEnvironment(manager.listener)
        def buildJobName = env['JOB_NAME']
        def buildNumber = env['BUILD_NUMBER']
        def externalBuildNumber = env['external_build_number']
        def dateString = new java.text.SimpleDateFormat("yyyyMMdd").format(build.getTime())
        def newFileName = "${buildJobName}-build-${buildNumber}-ext-${externalBuildNumber}-v${zidsVersion}-${dateString}.zip"
        summary = manager.createSummary("package.png")
        html = """<a href="artifact/*zip*/${newFileName}">${newFileName}</a>"""
        summary.appendText(html, false)
    }
}();
