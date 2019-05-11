/**
 * @Summary
 * Display the log analysis summary and link to the full analysis.
 */
// logic wrapped in closure to avoid polluting global scope
{ it ->
    try {
        summary = manager.createSummary("clipboard.png")
        workspace = manager.build.getParent().getWorkspace()
        summaryText = workspace.child("${manager.build.workspace.getRemote()}/result/LogAnalysisSummary.txt").readToString()
        detailsExists = workspace.child("${manager.build.workspace.getRemote()}/result/LogAnalysisReport.txt").exists()
        html = """<h2>Log Analysis</h2>
<pre>${summaryText}</pre>
"""
        if (detailsExists) {
            html += """<a href=\"artifact/result/LogAnalysisReport.txt\">Details</a>"""
        }
        summary.appendText(html, false)
    }
    catch (Exception e) {
        //Do nothing
    }
}();
