package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.jobtype.JobTypeDocumentation

/**
 * Base class for Publish over SSH scriptlets
 */
class PublishBaseOverSSHScriptlet extends TemplateScriptlet {

    public PublishBaseOverSSHScriptlet(IScriptlet template,
            String rootDir, String productAltName,
            JobType jobType, BuildType buildType) {
        super(template)

        this.addMacroDefinitions([
            (token("ROOT_DIR")): escape(rootDir),
            (token("PRODUCT_ALT_NAME")): escape(productAltName),
            (token("PUBLISH_TYPE")): escape(this.getPublishType(jobType, buildType)),
            (token("TEST_REPORT_FORMAT")): escape("%-25s %-19s %-36s\\n"),
            (token("TEST_RESULT_FILE")): escape("testresults.txt"),
            (token("WORKSPACE_PATH")): escape('${JOB_BASE_NAME}_${BUILD_ID}'),
        ])
    }

    /**
     * Defaults to build type name
     */
    protected String getPublishType(JobType jobType, BuildType buildType) {
        return buildType.name
    }

    /**
     * In case of document job, the publish type name is based on the job type.
     */
    protected String getPublishType(JobTypeDocumentation doc, BuildType buildType) {
        return doc.name
    }
}
