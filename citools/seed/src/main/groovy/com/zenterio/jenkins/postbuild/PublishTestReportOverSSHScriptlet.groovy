package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

import com.zenterio.jenkins.configuration.PublishBuildOverSSH
import com.zenterio.jenkins.configuration.PublishTestReportOverSSH
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.jobtype.JobTypeDocumentation

/**
 * Publish Test Report over SSH
 */
class PublishTestReportOverSSHScriptlet extends PublishBaseOverSSHScriptlet {

    public PublishTestReportOverSSHScriptlet(IScriptlet template,
            PublishBuildOverSSH build,
            PublishTestReportOverSSH testReport,
            JobType jobType, BuildType buildType) {
        super(template, build.rootDir, build.productAltName, jobType, buildType)

        this.addMacroDefinitions([
            (token("SUITE_NAME")): escape(testReport.suiteName),
            (token("REPORT_FILE_PATTERN")): escape(testReport.reportFilePattern),
            (token("BUILD_INFO_PATH")): escape('source/build-info.txt')
        ])
    }

}
