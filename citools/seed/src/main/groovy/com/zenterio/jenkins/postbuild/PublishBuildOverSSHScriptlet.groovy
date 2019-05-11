package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

import com.zenterio.jenkins.configuration.PublishBuildOverSSH
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.jobtype.JobTypeDocumentation

/**
 * Publish build over ssh Scriptlet
 */
class PublishBuildOverSSHScriptlet extends PublishBaseOverSSHScriptlet {

    public PublishBuildOverSSHScriptlet(IScriptlet template,
            PublishBuildOverSSH build, Boolean prepareForTestReport,
            JobType jobType, BuildType buildType) {
        super(template, build.rootDir, build.productAltName, jobType, buildType)

        this.addMacroDefinitions([
            (token('NUMBER_OF_BUILDS_TO_KEEP')): escape(build.numberOfBuildsToKeep.toString()),
            (token('PREPARE_FOR_TEST_REPORT')): escape( (prepareForTestReport) ? "true" : "false" )
        ])
    }

}
