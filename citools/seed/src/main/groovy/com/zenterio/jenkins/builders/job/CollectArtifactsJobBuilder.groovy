package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.LogParsingApplier
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.buildstep.CopyArtifactsFromBuildFlowBuildStepScriptlet
import com.zenterio.jenkins.configuration.BuildTimeoutPolicy
import com.zenterio.jenkins.configuration.Priority
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.jobtype.JobTypeCollectArtifacts
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.buildstep.BuildStepScriptlet
import com.zenterio.jenkins.postbuild.CollectArtifactsScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptlet

import static com.zenterio.jenkins.builders.GroovyStatementBuilder.curlify
import static com.zenterio.jenkins.builders.GroovyStatementBuilder.getCurrentBuildParameter

class CollectArtifactsJobBuilder implements IModelBuilder {

    private static final String RESULT_DIR = 'result'

    Project project
    JenkinsUrl url
    JobName jobName
    DisplayName displayName
    String scriptletsDirectory

    public CollectArtifactsJobBuilder(Project project,
                                      String scriptletsDirectory,
                                      JenkinsUrl url,
                                      JobName jobName,
                                      DisplayName displayName) {
        this.project = project
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
    }

    IModel build() {
        ModelEntity job = new CollectArtifactsJobModel()
        JobType jobType = new JobTypeCollectArtifacts()
        String name = this.jobName.getName(this.project, jobType)
        String displayName = this.displayName.getName(this.project, jobType)
        String url = this.url.getUrl(this.project, jobType)
        JobIcon icon = JobIcon.getIcon(jobType)

        IModel desc = new StandardJobDescriptionModel(jobType)

        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << desc << new HtmlCrumbDisplayModel("Collect Artifacts", true)
        job << new JobPriorityModel(Priority.HIGH)

        job << new JobTimeStampModel(true)
        job << new JobLogSizeCheckerModel(1, false)
        job << new JobRetentionModel(RetentionPolicyFactory.create(RetentionPolicyType.SHORT, false))
        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ELASTIC, 15, false, false)
        job << new JobLabelModel((new JobLabel(jobType)).getLabel())
        job << new JobIconModel(icon)
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                this.project.watchers, this.project.pm, this.project.techLead)

        // Parameters...
        String target_build_name = "target_build_name"
        String target_build_number = "target_build_number"
        job << new JobParameterModel(target_build_name, "", "The name of the flow job to package")
        job << new JobParameterModel(target_build_number, "", "The number of the build to package.")

        // Sanity check on input parameters
        job << new JobSystemGroovyScriptStepModel(new FileScriptlet("${this.scriptletsDirectory}/CheckInputParameters.groovy"))

        // Collect artifacts
        job << new JobSystemGroovyScriptStepModel(new CopyArtifactsFromBuildFlowBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/CopyAllArtifactsFromBuildFlow.groovy"),
                curlify(getCurrentBuildParameter(target_build_name)),
                curlify(getCurrentBuildParameter(target_build_number)),
                RESULT_DIR
        ))

        IModel wrapper = new JobPostBuildScriptWrapperModel(true, true, true)
        this.addMd5sum(wrapper)
        LogParsingApplier.applyLogParsingAnalysisPostBuildShellStep(wrapper, this.scriptletsDirectory, this.project.logParsing)
        job << wrapper

        job << new JobArtifactModel("${RESULT_DIR}/**/*", false)

        LogParsingApplier.applyLogParsingPublishPostBuildGroovyStep(job, this.scriptletsDirectory, this.project.logParsing)

        // Summary
        job << new JobGroovyPostBuildModel(new CollectArtifactsScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/CollectArtifactsSummaryAction.groovy"),
            curlify(getCurrentBuildParameter(target_build_name, true)),
            curlify(getCurrentBuildParameter(target_build_number, true)),
            icon.getPath()))

        job << new JobPostBuildWorkspaceCleanupModel()
        return job
    }

    protected void addMd5sum(IModel parent) {
        parent << new JobPostBuildShellStepModel(new BuildStepScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "md5sum"),
            "",
            0))
    }
}
