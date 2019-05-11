package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

class LogParserBuildStepScriptlet extends BaseBuildStepScriptlet {

    public LogParserBuildStepScriptlet(IScriptlet template, String configurationFile, Boolean saveReport) {
        super(template)
        this.addMacroDefinitions(tokenizeAndEscape('ARTIFACTS_DIR', 'result'))
        this.addMacroDefinitions([(token('ARTIFACTS_PATH')): escape('${WORKSPACE}/${ARTIFACTS_DIR}')])
        this.addMacroDefinitions([(token('CONFIGURATION_FILE')): escape(configurationFile)])
        this.addMacroDefinitions(tokenizeAndEscape('SUMMARY_FILE', '${ARTIFACTS_PATH}/LogAnalysisSummary.txt'))
        if (saveReport) {
            this.addMacroDefinitions(tokenizeAndEscape('REPORT_FILE', '${ARTIFACTS_PATH}/LogAnalysisReport.txt'))
        } else {
            this.addMacroDefinitions(tokenizeAndEscape('REPORT_FILE', '/dev/null'))
        }
        this.addMacroDefinitions(tokenizeAndEscape('LOGANALYZER_WATCHERS_FILE', '${WORKSPACE}/LogAnalyzerWatchers.txt'))
    }
}
