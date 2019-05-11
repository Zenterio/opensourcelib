package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.buildstep.LogParserBuildStepScriptlet
import com.zenterio.jenkins.configuration.LogParsing
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.ConsoleLogToWorkspaceBuildStepModel
import com.zenterio.jenkins.models.job.JobGroovyPostBuildModel
import com.zenterio.jenkins.models.job.JobPostBuildShellStepModel
import com.zenterio.jenkins.scriptlet.FileScriptlet

import groovy.util.logging.Log

@Log
class LogParsingApplier {

    public static void applyLogParsingAnalysisPostBuildShellStep(IModel postBuildShellStepWrapper,
            String scriptletsDirectory, LogParsing logParsing, Boolean saveReport=true) {
        if (logParsing.enabled) {
            postBuildShellStepWrapper << new ConsoleLogToWorkspaceBuildStepModel("console.log")
            postBuildShellStepWrapper << new JobPostBuildShellStepModel(new LogParserBuildStepScriptlet(
                    new FileScriptlet("${scriptletsDirectory}/buildsteps", "log-analyzer"),
                    logParsing.configurationFile,
                    saveReport))
        }
    }

    public static void applyLogParsingPublishPostBuildGroovyStep(IModel job, String scriptletsDirectory, LogParsing logParsing) {
        if (logParsing.enabled) {
            job << new JobGroovyPostBuildModel(new FileScriptlet("${scriptletsDirectory}", "PublishLogAnalysis.groovy"))
        }
    }

    public static applyBuildFlowLogAnalysisSummary(IModel job, String name, String resultDir, String scriptletsDirectory) {
        job << new JobGroovyPostBuildModel(
            new FileScriptlet("${scriptletsDirectory}/FlowJobLogAnalysisSummary.groovy"),
        )
    }
}
