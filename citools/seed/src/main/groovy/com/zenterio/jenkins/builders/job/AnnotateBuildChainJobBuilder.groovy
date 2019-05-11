package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.buildstep.AnnotateBuildChainBuildStepScriptlet
import com.zenterio.jenkins.configuration.BuildTimeoutPolicy
import com.zenterio.jenkins.configuration.Priority
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.jobtype.JobTypeAnnotateBuildChain
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.postbuild.AnnotateBuildChainPingBackScriptlet


/**
 * Assembles the model for Project annotate build chain job.
 */
class AnnotateBuildChainJobBuilder implements IModelBuilder {

    private Project project
    private JenkinsUrl url
    private JobName jobName
    private DisplayName displayName
    private String scriptletsDirectory

    public AnnotateBuildChainJobBuilder(Project project, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        this.project = project
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
    }

    @Override
    public IModel build() {
        ModelEntity job = new AnnotateBuildChainJobModel()

        JobTypeAnnotateBuildChain jobType = new JobTypeAnnotateBuildChain()
        String name = this.jobName.getName(this.project, jobType)
        String displayName = this.displayName.getName(this.project, jobType)
        String url = this.url.getUrl(this.project, jobType)

        IModel desc = new StandardJobDescriptionModel(jobType)

        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << desc << new HtmlCrumbDisplayModel("annotate-build", true)
        job << new JobPriorityModel(Priority.HIGH)


        job << new JobTimeStampModel(true)
        job << new JobLogSizeCheckerModel(1, false)
        job << new JobRetentionModel(RetentionPolicyFactory.create(RetentionPolicyType.LONG, true))
        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ELASTIC, 5, false, false)
        job << new JobLabelModel((new JobLabel(jobType)).getLabel())
        job << new JobIconModel(JobIcon.ANNOTATE)
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                this.project.watchers, this.project.pm, this.project.techLead)
        job << new JobParameterModel("top_job_name", "", "The name of origin Jenkins job.")
        job << new JobParameterModel("top_build_number", "", "The build number of the origin Jenkins job with correct annotation.")
        job << new JobSystemGroovyScriptStepModel(new AnnotateBuildChainBuildStepScriptlet(new FileScriptlet("${this.scriptletsDirectory}/AnnotateBuildChain.groovy")))
        job << new JobGroovyPostBuildModel(new AnnotateBuildChainPingBackScriptlet(new FileScriptlet("${this.scriptletsDirectory}/AnnotateBuildChainPingBack.groovy")))

        return job
    }
}
