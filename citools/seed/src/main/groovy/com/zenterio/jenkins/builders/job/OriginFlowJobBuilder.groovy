package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.buildstep.PushTagScriptlet
import com.zenterio.jenkins.buildstep.SetExternalBuildNumberAndStartedByScriptlet
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeAnnotateBuildChain
import com.zenterio.jenkins.jobtype.JobTypeCollectArtifacts
import com.zenterio.jenkins.jobtype.JobTypePromoteBuildChain
import com.zenterio.jenkins.jobtype.JobTypeTagBuild
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslParameter
import com.zenterio.jenkins.models.job.flowdsl.FlowJobFlowDslStepModel
import com.zenterio.jenkins.postbuild.*
import com.zenterio.jenkins.scriptlet.*

/**
 * Assembles the model for a Origin Flow job.
 */
class OriginFlowJobBuilder extends BaseOriginFlowJobBuilder {

    public OriginFlowJobBuilder(Origin origin, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        super(origin, scriptletsDirectory, url, jobName, displayName, origin.retentionPolicy, origin.concurrentBuilds)
    }

    @Override
    public IModel build() {
        ModelEntity job = new OriginFlowJobModel()
        this.buildBase(job)

        job << new JobLabelModel('default')
        job << new JobIconModel(JobIcon.FLOW_ORIGIN)

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(false)
        preScmWrapper << new JobPreScmSystemGroovyScriptStepModel(new SetExternalBuildNumberAndStartedByScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}", "SetBuildDisplayName.groovy"),this.origin.startedBy, true))
        job << preScmWrapper

        def allRepositories = RepositoryUtilities.allFlowRepositories(this.origin, false)
        configurableOrigin(job, allRepositories)

        IModel desc = new OriginFlowJobDescriptionModel(origin.pm,
            origin.techLead, origin.watchers)
        desc << new HtmlCrumbDisplayModel(origin.name)
        desc << new DescriptionDisplayModel(origin.description.description)
        job << desc

        if (origin.trigger.enabled) {
            job << new JobScmTriggerModel(origin.trigger.polling)
            job << new JobCronTriggerModel(origin.trigger.periodic)
        }

        job << new JobGitScmBranchBasedModel(allRepositories, origin.tagScm,
            origin.trigger.acceptNotifyCommit, origin.configurable, RepositoryConfigurable.OPTIONAL)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.SLOW_FEEDBACK,
            origin.watchers, origin.pm, origin.techLead)

        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ABSOLUTE, 12*60, false, false)

        this.addBuildFlowDslParameters(job, allRepositories)

        if (origin.tagScm) {
            def wrapper = new JobPostBuildScriptWrapperModel(true, true, false)
            wrapper << new JobPostBuildShellStepModel(new PushTagScriptlet(origin.repositories))
            job << wrapper
        }

        if (this.origin.retentionPolicy.saveArtifacts) {
            IScriptlet tca = new SummaryActionScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/TriggerCollectArtifactsSummaryAction.groovy"),
                this.jobName.getName(this.origin.project, new JobTypeCollectArtifacts()), JobIcon.PACKAGE)
            job << new JobGroovyPostBuildModel(tca)
        }

        if(origin.tagScm) {
            IScriptlet tb = new TagBuildScriptlet(
                    new FileScriptlet("${this.scriptletsDirectory}/TagBuildSummaryAction.groovy"),
                    origin.repositories,
                    this.jobName.getName(origin.project, new JobTypeTagBuild()))
            job << new JobGroovyPostBuildModel(tb)
        }

        IScriptlet pbc = new PromoteBuildChainScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/PromoteBuildChainSummaryAction.groovy"),
            this.jobName.getName(origin.project, new JobTypePromoteBuildChain()))
        job << new JobGroovyPostBuildModel(pbc)

        IScriptlet abc = new AnnotateBuildChainScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/AnnotateBuildChainSummaryAction.groovy"),
                this.jobName.getName(origin.project, new JobTypeAnnotateBuildChain()))
        job << new JobGroovyPostBuildModel(abc)

        job << new JobPostBuildWorkspaceCleanupModel()


        return job
    }

    private void addBuildFlowDslParameters(ModelEntity job, Repository[] repositories) {
        def parameters = [new BuildFlowDslParameter("external_build_number", "build.environment.get(\"BUILD_NUMBER\")")]
        job << new FlowJobFlowDslStepModel(
                parameters as BuildFlowDslParameter[],
                repositoryVariables(repositories),
                ProductFlowJobModel)
    }

    protected void configurableOrigin(ModelEntity job, Repository[] repositories) {
        if (origin.configurable) {
            RepositoryJobParametersApplier.applyRepositories(job, repositories)
        }
    }
}
