/**
 * Auto-generated script from template FlowJobLogAnalysisSummary.groovy
 *
 * This script agregates all the LogAnalysis summary file from all the jobs in a build-flow (build-flow-plugin)
 * and creates a new summary file based on that.
 */

import java.nio.charset.Charset

import com.cloudbees.plugins.flow.FlowRun
import hudson.FilePath
import hudson.Launcher
import hudson.plugins.copyartifact.SpecificBuildSelector
import hudson.plugins.copyartifact.CopyArtifact
import hudson.remoting.VirtualChannel

/**
 * Append the log items found in the summary file (inFile) and write plain text (textResult) and HTML (htmlResult)
 * @param inFile        FilePath object to the summary file to read from
 * @param textResult    StringBuilder for storing plain text
 * @param htmlResult    StringBUilder for storing HTML text
 * @param level         The indentation level
 * @return
 */
def appendSummaryToResult(FilePath inFile, StringBuilder textResult, StringBuilder htmlResult, int level) {
    final String indent = '    ' * (level + 1)
    final String summaryStartHtml = "<div style='margin: 0 0 0 25px; padding: 0px;'><pre style='font-size: smaller;'>"
    final String summaryEndHtml = "</pre></div>"
    final String reportNotFoundStartHtml = "<div style='margin: 0 0 0 25px; padding: 0px;'>"
    final String reportNotFoundEndHtml = "</div>"
    if (inFile.exists()) {
        def lines = inFile.readToString().readLines().findResults({ String line ->
            String trimmed = line.trim()
            if (
                trimmed != 'SUMMARY:' &&
                trimmed != '--------' &&
                trimmed != 'To learn more about the log-analysis, see https://wiki.zenterio.lan/index.php/LogAnalyzer' &&
                trimmed != 'Nothing to report' &&
                trimmed != ''
            ) {
                return trimmed
            } else {
                return null
            }
        })
        if (lines.size() > 0) {
            htmlResult.append(summaryStartHtml)
            lines.each { String line ->
                textResult.append("${indent}${line}\n")
                htmlResult.append("${line}\n")
            }
            htmlResult.append(summaryEndHtml)
        }
    } else {
        textResult.append("${indent}No report summary found\n")
        htmlResult.append(reportNotFoundStartHtml)
        htmlResult.append("No report summary found")
        htmlResult.append(reportNotFoundEndHtml)
    }
}

/**
 * Copy log-summary file from specified build number artifacts to workspace
 * @param jobName
 * @param buildNumber
 * @param target
 * @param summaryFileName
 * @return
 */
def copySummaryFileFromBuild(jobName, int buildNumber, String target, String summaryFileName) {

    // Doc: https://github.com/jenkinsci/copyartifact-plugin/blob/master/src/main/java/hudson/plugins/copyartifact/CopyArtifact.java
    CopyArtifact copyArtifact = new CopyArtifact(jobName)

    copyArtifact.setSelector(new SpecificBuildSelector(buildNumber.toString()))
    copyArtifact.setOptional(true)
    copyArtifact.setTarget(target)
    copyArtifact.setFilter("result/${summaryFileName}")
    copyArtifact.setFlatten(true)
    copyArtifact.setFingerprintArtifacts(false)

    // "build" is a global jenkins variable
    // "listener" is a global jenkins variable
    copyArtifact.perform(manager.build, manager.build.workspace, new Launcher.DummyLauncher(manager.listener), manager.listener)
}

/**
 * Processes each downstream job in the declarer, copy the summary file from each job and add to plain text and HTML results.
 * @param declarer          Job declarer
 * @param workspace         Workspace reference
 * @param topBuild          The top build
 * @param summaryFileName   Name of log summary file
 * @param textResult        StringBuilder for storing plain text
 * @param htmlResult        StringBuilder for string HTML text
 * @param level             Indentation level
 * @return
 */
def processDeclarer(declarer, FilePath workspace, topBuild, String summaryFileName, StringBuilder textResult,
        StringBuilder htmlResult, int level, processedJobs) {
    def downstreamBuilds = declarer.getDownStream(topBuild) - null
    downstreamBuilds.each { downstreamBuild ->
        if (downstreamBuild in processedJobs) {
            return
        }
        processedJobs.add(downstreamBuild)
        htmlResult.append("<div style='margin: 0 0 0 ${25*level}px; padding: 0px;'>")
        addTextHeader(textResult, downstreamBuild, level)
        addHtmlHeader(htmlResult, downstreamBuild, level)
        int nextLevel = level
        if (downstreamBuild in FlowRun) {
            nextLevel += 1
        } else {
            String projectDir = "summaries/${downstreamBuild.project.name}"
            copySummaryFileFromBuild(downstreamBuild.project.name, downstreamBuild.number, projectDir, summaryFileName)
            appendSummaryToResult(workspace.child("${projectDir}/${summaryFileName}"), textResult, htmlResult, level)
        }
        htmlResult.append('</div>')
        findAllDownstreamBuilds(downstreamBuild, workspace, summaryFileName, textResult, htmlResult, nextLevel, processedJobs)
    }
}

/**
 * Iterates over all downstream builds and calls processDeclarer for each declarer found.
 * @param parentBuild
 * @param workspace
 * @param summaryFileName
 * @param textResult
 * @param htmlResult
 * @param level
 * @return
 */
def findAllDownstreamBuilds(parentBuild, FilePath workspace, String summaryFileName, StringBuilder textResult,
        StringBuilder htmlResult, int level, processedJobs) {

    if (jenkins.model.Jenkins.getInstance().getPlugin("build-flow-plugin") != null) {
        def declarer = new org.jenkinsci.plugins.buildgraphview.FlowDownStreamRunDeclarer()
        processDeclarer(declarer, workspace, parentBuild, summaryFileName, textResult, htmlResult, level, processedJobs)
    }

    org.jenkinsci.plugins.buildgraphview.DownStreamRunDeclarer.all().each { declarer ->
        processDeclarer(declarer, workspace, parentBuild, summaryFileName, textResult, htmlResult, level, processedJobs)
    }
}

/**
 * Adds plain text header with correct indentation
 * @param textResult    StringBuilder where the result is stored/written to
 * @param build         The build to add header for
 * @return
 */
def addTextHeader(StringBuilder textResult, build, int level) {
    final String indent = '    '
    textResult.append("${indent*level}${build.project.name}: ${build.getResult().toString()}\n")
}

/**
 * Get HTML/CSS RGB color string representing the result.
 * @param result
 * @return #RGB color string for the result
 */
def getHtmlColor(result) {
    return [SUCCESS: '#03ba03', UNSTABLE: '#efdc07', FAILURE: '#ba0303'][result.toString()]
}

/**
 * Adds HTML header with correct indentation and size
 * @param htmlResult    StringBuilder where the result is stored/written to
 * @param build         The build to add header for
 * @return
 */
def addHtmlHeader(StringBuilder htmlResult, build, int level) {
    String buildResult = build.getResult().toString()
    String color = getHtmlColor(build.getResult())
    htmlResult.append("<h${(3+level)} style='margin:0px;'><a style='text-decoration: none' href='/${build.getUrl()}'>${build.project.name} <span style='color: ${color}'>${buildResult}</span></a></h${(3+level)}>")
}

/**
 * Adds plain text footer
 * @param textResult    StringBuilder where the result is stored/written to
 * @return
 */
def addTextFooter(StringBuilder textResult) {
    textResult.append('\nTo learn more about the log-analysis, see https://wiki.zenterio.lan/index.php/LogAnalyzer\n')
}

/**
 * Add HTML footer
 * @param textResult    StringBuilder where the result is stored/written to
 * @return
 */
def addHtmlFooter(StringBuilder textResult) {
    textResult.append('\n<p>To learn more about the log-analysis, see <a href="https://wiki.zenterio.lan/index.php/LogAnalyzer">wiki</a></p>\n')
}

/**
 * Writes the result StringBuilder to the outFile FilePath object
 * @param outFile   File to write to
 * @param result    StringBuilder containing the content to be written
 * @return
 */
def writeToFile(FilePath outFile, StringBuilder result) {
    outFile.write(result.toString(), Charset.defaultCharset().toString())
}

/**
 * Renders the content in result
 * @param result    StringBuilder containing the content to be rendered
 * @return
 */
def renderHtml(StringBuilder result) {
    String html = "<div style='padding: 0 10px; overflow: auto; max-height: 400px; max-width: 695px; background: #FAFAFA; border: 1px solid #CCCCCC;'>"
    html += result.toString()
    html += '</div>'
    manager.createSummary("clipboard.png").appendText(html, false)
}

{ currentBuild ->

    try {

        final FilePath workspace = currentBuild.workspace
        final FilePath resultDir =  workspace.child('result')
        resultDir.mkdirs()
        final String summaryFileName = 'LogAnalysisSummary.txt'
        final FilePath txtFile = resultDir.child(summaryFileName)
        final StringBuilder textResult = new StringBuilder()
        final StringBuilder htmlResult = new StringBuilder()
        def processedJobs = []

        // The flow builds own loganalysis
        appendSummaryToResult(txtFile, textResult, htmlResult, -1)
        // Downstream builds
        findAllDownstreamBuilds(currentBuild, workspace, summaryFileName, textResult, htmlResult, 0, processedJobs)

        addTextFooter(textResult)
        addHtmlFooter(htmlResult)
        writeToFile(txtFile, textResult)
        renderHtml(htmlResult)

    } catch (Exception e) {
        manager.listener.logger.println("An error occurred while creating the log analysis summary: ${e.toString()}")
    }

}(manager.build);

return
