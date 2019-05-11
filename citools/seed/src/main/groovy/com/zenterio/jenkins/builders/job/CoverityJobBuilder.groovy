package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.PublishOverSSHApplier
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.CoverityBuildStepScriptlet
import com.zenterio.jenkins.buildstep.CoverityRunIfChangesScriptlet
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeCoverity
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslExcludeFromFlowModel
import com.zenterio.jenkins.scriptlet.*

/**
 * Assembles the model for a Coverity job.
 */
class CoverityJobBuilder extends BaseCompilationJobBuilder {

    JobModel parentJob

    public CoverityJobBuilder(Product product,
        BuildType buildType, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName,
        JobModel parentJob) {
        super(product,
                new JobTypeCoverity(),
                buildType,
                scriptletsDirectory,
                url,
                jobName,
                displayName,
                null,
                new BuildStepFactory(scriptletsDirectory, product.variables,
                        { IScriptlet template, int swUpgradeOffset ->
                            new CoverityBuildStepScriptlet(
                                    template,
                                    new JobTypeCoverity(),
                                    buildType,
                                    product,
                                    product.coverity.stream,
                                    product.coverity.aggressiveness)
                        }),
                ['abs-target', 'coverity'],
                product.cache.createDisabled(),
                product.concurrentBuilds,
                product.coverity.credentials,
                product.coverity.customBuildSteps,
                product.retentionPolicy,
                product.startedBy,
                product.buildNodes,
                product.coverity.buildTimeout,
                product.coverity.workspaceBrowsing,
                product.priority)
        this.parentJob = parentJob
    }

    public IModel build() {
        IModel job = new CoverityJobModel(this.product.coverity.upstream, this.parentJob)
        ResourcesApplier.apply(this.product.coverity.resources, job)
        RepositoryJobParametersApplier.applyRepositories(job, this.product.origin.repositories)
        job << new JobParameterModel("external_build_number", "", "Build number of trigger job")
        job << new JobPreBuildWorkspaceCleanupModel()
        setUpstreamTrigger(job, this.product.coverity.upstream)
        BuildInfoBuildStepScriptlet bi =
                new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps",
                        this.product.name,
                        this.product.origin.name,
                        this.product.repositories)
        job << new JobShellStepModel(bi)
        this.buildBase(job)
        setBuildResultPostBuildStep(job)
        job << new JobArtifactModel('result/**/*', true)

        PublishOverSSHApplier publishOverSSHApplier = new PublishOverSSHApplier(
            this.scriptletsDirectory, null, this.jobType, this.buildType)
        publishOverSSHApplier.apply(this.product.coverity, job)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.UTILITY,
                [new Watcher("Engineering services", "engineering-services@zenterio.com", new EmailPolicy(EmailPolicyWhen.NEVER,EmailPolicyWhen.NEVER,EmailPolicyWhen.FAILURE, EmailPolicyWhen.FAILURE))] as ContactInformationCollection,
                null, null)
        job << new JobPostBuildWorkspaceCleanupModel()
        return job
    }

    private void setBuildResultPostBuildStep(CoverityJobModel job) {
        if (this.product.coverity.upstream == Upstream.FALSE) {
            job << new JobGroovyPostBuildModel(new StringScriptlet(
                    """{ it ->
                        if(manager.logContains(\".*Build interrupted due to no changes.*\")) {
                            manager.build.@result = hudson.model.Result.NOT_BUILT
                        }
                    }();"""))
        }
    }

    private void setUpstreamTrigger(IModel job, Upstream upstream) {
        if (upstream in [Upstream.TRUE, Upstream.ASYNC]) {
            job << new JobGitScmBranchBasedModel(this.product.repositories,
                false, false, true, RepositoryConfigurable.OPTIONAL)

            IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
            preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, this.product.origin.repositories))
            job << preScmWrapper

            if (upstream == Upstream.ASYNC) {
                job << new JobBuildFlowDslExcludeFromFlowModel()
            }
        } else if (upstream == Upstream.FALSE) {
            job << new JobGitScmBranchBasedModel(this.product.repositories,
                false, false, true, RepositoryConfigurable.FORCE_TRUE)
            job << new JobBuildFlowDslExcludeFromFlowModel()
            job << new JobCronTriggerModel(this.product.coverity.periodic)
            IModel wrapper = new JobPreScmBuildStepWrapperModel(false)
            wrapper << new JobPreScmCopyArtifactsFromBuildNumberModel(
                    this.parentJob,
                    "lastSuccessfulBuild",
                    "result/build-info.txt",
                    "source/debug")
            wrapper << new JobPreScmCopyArtifactsFromBuildNumberModel(
                    job,
                    "lastSuccessfulBuild",
                    "result/build-info.txt",
                    "source/coverity")
            wrapper << new JobPreScmSystemGroovyScriptStepModel(new CoverityRunIfChangesScriptlet(
                    new FileScriptlet("${this.scriptletsDirectory}", "CoverityRunIfChanges.groovy"),
                    this.product.repositories))
            job << wrapper
        }
    }
}
