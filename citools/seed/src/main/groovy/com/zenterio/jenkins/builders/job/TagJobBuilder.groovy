package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.buildstep.TagBuildChainBuildStepScriptlet
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.scriptlet.*
import com.zenterio.jenkins.jobtype.JobTypeTagBuild
import com.zenterio.jenkins.*

/**
 * Assembles the model for Project tag job.
 */
class TagJobBuilder implements IModelBuilder {

    private Project project
    private JenkinsUrl url
    private JobName jobName
    private DisplayName displayName
    private String scriptletsDirectory

    public TagJobBuilder(Project project, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        this.project = project
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
    }

    @Override
    public IModel build() {
        ModelEntity job = new TagJobModel()

        JobTypeTagBuild jobType = new JobTypeTagBuild()
        String name = this.jobName.getName(this.project, jobType)
        String displayName = this.displayName.getName(this.project, jobType)
        String url = this.url.getUrl(this.project, jobType)

        IModel desc = new StandardJobDescriptionModel(jobType)

        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << desc << new HtmlCrumbDisplayModel("tag-build", true)
        job << new JobLogSizeCheckerModel(1, false)
        job << new JobPriorityModel(Priority.HIGH)

        job << new JobTimeStampModel(true)
        job << new JobRetentionModel(RetentionPolicyFactory.create(RetentionPolicyType.LONG, true))
        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ELASTIC, 60, false, false)
        job << new JobLabelModel((new JobLabel(jobType)).getLabel())
        job << new JobIconModel(JobIcon.TAG)
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                this.project.watchers, this.project.pm, this.project.techLead)
        job << new JobParameterModel("tag_name", "", "The new tag to be set, e.g DROP_X_SPRINT_Y.")
        job << new JobParameterModel("repositories", "", "Space separated list of tuples (space separated) of name remote, that should be tagged; e.g zids git@server:zids fs git@server:fs.")
        job << new JobParameterModel("source_tag", "", "The tag to use as reference, e.g. JENKINS_XX.")
        job << new JobParameterModel("tag_build_job_name", "", "The name of original Jenkins job that should be tagged.")
        job << new JobParameterModel("tag_build_number", "", "The build number of the original Jenkins job that should be tagged. The build will be updated with a notification that it has been tagged.")
        job << new JobShellStepModel("#!/usr/bin/env bash\n# Clean workspace\n rm -rf ./*")
        job << new JobShellStepModel(new TagBuildChainBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/tag-build-step.sh"),
                '$repositories',
                '$tag_name',
                '$source_tag'
        ))
        job << new JobGroovyPostBuildModel(new FileScriptlet("${this.scriptletsDirectory}/TagBuildPingBack.groovy"))
        job << new JobPostBuildWorkspaceCleanupModel()

        return job
    }
}
