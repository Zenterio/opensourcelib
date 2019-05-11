package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.buildstep.FlashBuildStepScriptlet
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.scriptlet.*
import com.zenterio.jenkins.jobtype.JobTypeFlash
import com.zenterio.jenkins.*

/**
 * Assembles the model for Project tag job.
 */
class FlashJobBuilder implements IModelBuilder {

    private Project project
    private JenkinsUrl url
    private JobName jobName
    private DisplayName displayName
    private String scriptletsDirectory

    public FlashJobBuilder(Project project, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        this.project = project
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
    }

    @Override
    public IModel build() {

        ModelEntity job = new FlashJobModel()
        JobTypeFlash jobType = new JobTypeFlash()
        IModel desc = new StandardJobDescriptionModel(jobType)

        String name = this.jobName.getName(this.project, jobType)
        String displayName = this.displayName.getName(this.project, jobType)
        String url = this.url.getUrl(this.project, jobType)

        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << desc << new HtmlCrumbDisplayModel("flash", true)
        job << new JobLogSizeCheckerModel(1, false)
        job << new JobPriorityModel(Priority.HIGH)
        job << new JobTimeStampModel(true)
        job << new JobRetentionModel(RetentionPolicyFactory.create(RetentionPolicyType.LONG, true))
        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ABSOLUTE, 10, false, false)
        job << new JobLabelModel((new JobLabel(jobType)).getLabel())
        job << new JobIconModel(JobIcon.FLASH)

        job << new JobParameterModel("kfs_job_name", "", "The name of Jenkins job where to fetch the image binary from.")
        job << new JobParameterModel("kfs_build_number", "lastSuccessfulBuild", "The build number of the Jenkins job where to fetch the image binary from.")
        job << new JobParameterModel("kfs_file", "result/kfs.zmg", "The image/kfs file to be flashed, relative artifacts root")
        job << new JobParameterModel("ip_address", "", "The IP address to the STB")

        String destination = "source"

        job << new JobCopyArtifactsFromBuildNumberModel(
                "\${kfs_job_name}",
                "\${kfs_build_number}",
                "result/build-info.txt, \${kfs_file}",
                destination, true)
        job << new JobShellStepModel(new FlashBuildStepScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/flash-build-step.sh"),
            destination))

        job << new JobArtifactModel('result/**/*', true)

        String customEmailContent = """\
You flashed STB with IP: \${ip_address}

\${FILE, path="result/build-info.txt", fileNotFoundMessage=""}
"""
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                this.project.watchers, this.project.pm, this.project.techLead,
                customEmailContent)
        job << new JobPostBuildWorkspaceCleanupModel()

        return job
    }
}
