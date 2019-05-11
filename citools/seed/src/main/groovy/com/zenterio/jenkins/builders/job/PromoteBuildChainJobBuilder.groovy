package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.buildstep.PromoteBuildChainBuildStepScriptlet
import com.zenterio.jenkins.configuration.BuildTimeoutPolicy
import com.zenterio.jenkins.configuration.Priority
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.jobtype.JobTypePromoteBuildChain
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.postbuild.PromoteBuildChainPingBackScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptlet

import static com.zenterio.jenkins.builders.GroovyStatementBuilder.curlify

/**
 * Assembles the model for Project promote build chain job.
 */
class PromoteBuildChainJobBuilder implements IModelBuilder {

    private Project project
    private JenkinsUrl url
    private JobName jobName
    private DisplayName displayName
    private String scriptletsDirectory

    public PromoteBuildChainJobBuilder(Project project, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        this.project = project
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
    }

    @Override
    public IModel build() {
        ModelEntity job = new PromoteBuildChainJobModel()

        JobTypePromoteBuildChain jobType = new JobTypePromoteBuildChain()
        String name = this.jobName.getName(this.project, jobType)
        String displayName = this.displayName.getName(this.project, jobType)
        String url = this.url.getUrl(this.project, jobType)

        IModel desc = new StandardJobDescriptionModel(jobType)

        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << desc << new HtmlCrumbDisplayModel("promote-build", true)
        job << new JobPriorityModel(Priority.HIGH)

        job << new JobLogSizeCheckerModel(1, false)
        job << new JobTimeStampModel(true)
        job << new JobRetentionModel(RetentionPolicyFactory.create(RetentionPolicyType.LONG, true))
        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ELASTIC, 5, false, false)
        job << new JobLabelModel((new JobLabel(jobType)).getLabel())
        job << new JobIconModel(JobIcon.getIcon(jobType))
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                this.project.watchers, this.project.pm, this.project.techLead)
        job << new JobParameterModel("top_job_name", "", "The name of origin Jenkins job with correct promotion.")
        job << new JobParameterModel("top_build_number", "", "The build number of the origin Jenkins job.")
        job << new JobSystemGroovyScriptStepModel(new PromoteBuildChainBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/PromoteBuildChain.groovy"),
                curlify('build.buildVariableResolver.resolve("top_job_name")'),
                curlify('build.buildVariableResolver.resolve("top_build_number")')))
        job << new JobGroovyPostBuildModel(new PromoteBuildChainPingBackScriptlet(new FileScriptlet("${this.scriptletsDirectory}/PromoteBuildChainPingBack.groovy")))

        return job
    }
}
