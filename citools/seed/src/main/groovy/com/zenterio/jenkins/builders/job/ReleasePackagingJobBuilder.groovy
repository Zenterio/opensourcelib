package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.BuildTimeoutApplier
import com.zenterio.jenkins.appliers.BuildStepApplier
import com.zenterio.jenkins.appliers.LogParsingApplier
import com.zenterio.jenkins.appliers.PublishOverSSHApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.buildstep.AnnotateBuildChainBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.BuildStepScriptlet
import com.zenterio.jenkins.buildstep.CopyArtifactsFromBuildFlowBuildStepScriptlet
import com.zenterio.jenkins.buildstep.GenerateChangelogScriptlet
import com.zenterio.jenkins.buildstep.PromoteBuildChainBuildStepScriptlet
import com.zenterio.jenkins.buildstep.ReleasePackagingCheckIfTargetExistsScriptlet
import com.zenterio.jenkins.buildstep.SetBuildDescriptionScriptlet
import com.zenterio.jenkins.buildstep.TagBuildChainBuildStepScriptlet
import com.zenterio.jenkins.buildstep.PublishReleasePackagingScriptlet
import com.zenterio.jenkins.buildstep.ReleasePackagingBuildStepScriptlet
import com.zenterio.jenkins.configuration.Credential
import com.zenterio.jenkins.configuration.CredentialType
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Priority
import com.zenterio.jenkins.configuration.PublishOverSSH
import com.zenterio.jenkins.configuration.PublishOverSSHList
import com.zenterio.jenkins.configuration.ReleasePackaging
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.configuration.TransferSet
import com.zenterio.jenkins.jobtype.JobTypeReleasePackaging
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.postbuild.ReleasePackagingPingBackScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.scriptlet.IScriptlet

import static com.zenterio.jenkins.builders.GroovyStatementBuilder.curlify
import static com.zenterio.jenkins.builders.GroovyStatementBuilder.getBuild
import static com.zenterio.jenkins.builders.GroovyStatementBuilder.getCurrentBuildParameter


class ReleasePackagingJobBuilder implements IModelBuilder {

    private static final String RESULT_DIR = 'result'
    private static final String GA_RELEASE_PROMOTION_LEVEL = '3'
    private static final String PUBLISH_ROOT = '/mnt/externals_projects'
    private static final int PUBLISH_TIMEOUT = 30 * 60 * 1000

    Origin origin
    JenkinsUrl url
    JobName jobName
    DisplayName displayName
    String scriptletsDirectory
    ReleasePackaging releasePackaging

    public ReleasePackagingJobBuilder(Origin origin,
                                      String scriptletsDirectory,
                                      JenkinsUrl url,
                                      JobName jobName,
                                      DisplayName displayName,
                                      ReleasePackaging releasePackaging) {
        this.origin = origin
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
        this.releasePackaging = releasePackaging
    }

    IModel build() {
        ModelEntity job = new ReleasePackagingJobModel(this.scriptletsDirectory, this.releasePackaging, this.origin)
        JobTypeReleasePackaging jobType = new JobTypeReleasePackaging()
        String name = this.jobName.getName(this.origin, jobType)
        String displayName = this.displayName.getName(this.origin, jobType)
        String url = this.url.getUrl(this.origin, jobType)
        JobIcon icon = JobIcon.getIcon(jobType)

        IModel desc = new StandardJobDescriptionModel(jobType)

        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        desc << new DescriptionDisplayModel(this.origin.releasePackaging?.description?.description)
        desc << new HtmlCrumbDisplayModel("Release Packaging", true)
        job << desc
        job << new JobPriorityModel(Priority.HIGH)

        job << new JobTimeStampModel(true)
        job << new JobLogSizeCheckerModel(200, false)
        job << new JobRetentionModel(RetentionPolicyFactory.create(RetentionPolicyType.LONG, true))
        BuildTimeoutApplier.apply(origin.releasePackaging.buildTimeout, job)
        job << new JobLabelModel((new JobLabel(jobType)).getLabel())
        ResourcesApplier.apply(origin.releasePackaging.resources, job)
        job << new JobIconModel(icon)
        job << new JobGitScmBranchBasedModel((this.origin.repositories + this.origin.releasePackaging.repositories) as Repository[],
            false, false, false, RepositoryConfigurable.OPTIONAL)
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                this.origin.watchers, this.origin.pm, this.origin.techLead)
        Credential jenkins_jira_credential = new Credential(CredentialType.USERNAME_PASSWORD, "jenkins-jira-user", "JIRA", true)
        job << new JobCredentialListModel(origin.releasePackaging.credentials + jenkins_jira_credential)

        // Parameters...
        job << new JobParameterModel("target_build_number", "", "The number of the origin build to package.")
        job << new JobParameterTextModel("description", "", "A short description to be included as release notes.")
        job << new JobParameterModel("annotation", "", "A short description to be added to all affected jenkins builds.")
        job << new JobParameterModel("git_tag_name", "", "The name of the git-tag to mark this release.")
        job << new JobParameterModel("previous_git_tag_name", "", "The name of the git-tag of the previous release (Optional)")
        job << new JobParameterModel("source_tag", "", "The tag to use as reference, e.g. JENKINS_XX.")

        // Sanity check on input parameters
        job << new JobSystemGroovyScriptStepModel(new FileScriptlet("${this.scriptletsDirectory}/CheckInputParameters.groovy"))

        job << new JobSystemGroovyScriptStepModel(new ReleasePackagingCheckIfTargetExistsScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/ReleasePackagingCheckIfTargetExists.groovy"),
                PUBLISH_ROOT,
                getPublishPath(false)
        ))

        // Trigger tagging
        // Since this might fail it is important that this is run first in order to fail early.
        job << new JobShellStepModel(new TagBuildChainBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/tag-build-step.sh"),
                getRepositoriesParam(),
                '${git_tag_name}',
                '${source_tag}'
        ))

        // Generate changelog between tag and previous tag
        job << new JobShellStepModel(new GenerateChangelogScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/generate-changelog.sh"),
                getRepositoriesParam(),
                '${git_tag_name}',
                '${previous_git_tag_name:-}'
        ))

        // Collect artifacts
        job << new JobSystemGroovyScriptStepModel(new CopyArtifactsFromBuildFlowBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/CopyAllArtifactsFromBuildFlow.groovy"),
                getOriginJobName(),
                curlify(getCurrentBuildParameter('target_build_number')),
                RESULT_DIR
        ))

        // Save release description
        job << new JobShellStepModel(new BuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/save-release-description.sh"),
                "",
                0
        ))

        // Set description
        job << new JobSystemGroovyScriptStepModel(new SetBuildDescriptionScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/SetBuildDescription.groovy"),
                getOriginJobName(),
                curlify(getCurrentBuildParameter('target_build_number')),
                curlify(getCurrentBuildParameter('annotation'))
        ))

        // Trigger annotation
        job << new JobSystemGroovyScriptStepModel(new AnnotateBuildChainBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/AnnotateBuildChain.groovy"),
                getOriginJobName(),
                curlify(getCurrentBuildParameter('target_build_number'))
        ))

        // Promote build chain
        job << new JobSystemGroovyScriptStepModel(new PromoteBuildChainBuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/PromoteBuildChain.groovy"),
                getOriginJobName(),
                curlify('build.buildVariableResolver.resolve("target_build_number")'),
                GA_RELEASE_PROMOTION_LEVEL
        ))

        // Custom build steps
        this.applyBuildSteps(job)

        // MD5-sum
        job << new JobShellStepModel(new BuildStepScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "md5sum"),
            "",
            0))

        // Publish artifacts
        this.applyPublishingStep(job)

        IModel wrapper = new JobPostBuildScriptWrapperModel(true, true, true)
        LogParsingApplier.applyLogParsingAnalysisPostBuildShellStep(wrapper, this.scriptletsDirectory, this.origin.logParsing)
        job << wrapper
        // Ping-back
        job << new JobGroovyPostBuildModel(new ReleasePackagingPingBackScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/ReleasePackagingPingBack.groovy"),
                getOriginJobName(),
                curlify(getCurrentBuildParameter('target_build_number', true)),
                icon.getPath(),
                getPublishPath(true)
        ))

        LogParsingApplier.applyLogParsingPublishPostBuildGroovyStep(job, this.scriptletsDirectory, this.origin.logParsing)

        PublishOverSSHApplier publishOverSSHApplier = new PublishOverSSHApplier(
            this.scriptletsDirectory, null, jobType, null)
        publishOverSSHApplier.apply(this.origin.releasePackaging, job)

        job << new JobPostBuildWorkspaceCleanupModel()
        return job
    }

    private String getRepositoriesParam() {
        String repoInfo = this.origin.repositories.collect({ Repository repository ->
            "${repository.directory} ${repository.remote}"
        }).join(' ')
        return "${repoInfo}"
    }

    private String getOriginJobName() {
        return this.jobName.getName(this.origin)
    }

    private String getPublishPath(Boolean postBuildScript) {
        String dateString = "(new java.text.SimpleDateFormat(\"yyyy-MM-dd\")).format(${getBuild(postBuildScript)}.getTime())"
        String buildNumber = getCurrentBuildParameter('target_build_number', postBuildScript)
        String releaseName = getCurrentBuildParameter('annotation', postBuildScript)

        return "${origin.project.name}/${origin.name}/${curlify(dateString)}-build-${curlify(buildNumber)}-ext-${curlify(buildNumber)}-${curlify(releaseName)}"
    }

    private void applyBuildSteps(IModel job) {
        def factory = new BuildStepFactory(this.scriptletsDirectory, this.origin.variables,
            { IScriptlet template, int swUpgradeOffset ->
                new ReleasePackagingBuildStepScriptlet(template,
                        this.origin.project.name, this.origin.name)
            })
        def applier = new BuildStepApplier(factory)
        applier.applyBuildSteps([], this.origin.releasePackaging.customBuildSteps, 0, job)
    }

    private void applyPublishingStep(IModel job) {
        String contentDir = "release_packaging/${this.origin.project.name}/${this.origin.name}"
        String command = new PublishReleasePackagingScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/publish-release-packaging.sh"),
                this.origin.project.name,
                this.origin.name,
                this.getOriginJobName(),
                PUBLISH_ROOT,
                contentDir
        ).getContent()

        TransferSet transfer_config = new TransferSet(
                "${RESULT_DIR}/**/*", contentDir, RESULT_DIR, null, null, null, true, null, null, PUBLISH_TIMEOUT, null, command)


        PublishOverSSH publishConfig = new PublishOverSSH(true, 'master',null, null, null, [transfer_config])
        PublishOverSSHList publishOverSSHList = [publishConfig] as PublishOverSSHList

        job << new JobPublishOverSSHListModel(publishOverSSHList)

    }

}
