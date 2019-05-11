package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.buildstep.SetExternalBuildNumberAndStartedByScriptlet
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeAnnotateBuildChain
import com.zenterio.jenkins.jobtype.JobTypeCollectArtifacts
import com.zenterio.jenkins.jobtype.JobTypePromoteBuildChain
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.DescriptionDisplayNameModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslParameter
import com.zenterio.jenkins.models.job.flowdsl.FlowJobFlowDslStepModel
import com.zenterio.jenkins.postbuild.*
import com.zenterio.jenkins.scriptlet.*

/**
 * Assembles the model for a Product Flow Job.
 */
class ProductFlowJobBuilder extends BaseProductFlowJobBuilder {

    public ProductFlowJobBuilder(Product product, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        super(product, scriptletsDirectory, url, jobName, displayName, product.retentionPolicy, product.concurrentBuilds)
    }

    @Override
    public IModel build() {
        ModelEntity job = new ProductFlowJobModel()
        job << new JobPreBuildWorkspaceCleanupModel()
        this.buildBase(job)
        IModel wrapper = new JobPreScmBuildStepWrapperModel(false)
        wrapper << new JobPreScmSystemGroovyScriptStepModel(new SetExternalBuildNumberAndStartedByScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}", "SetBuildDisplayName.groovy"),
                this.product.startedBy, false))
        job << wrapper

        job << new JobLabelModel('default')
        job << new JobIconModel(JobIcon.FLOW_PRODUCT)

        IModel desc = new ProductFlowJobDescriptionModel(this.product.pm, this.product.techLead,
            this.product.watchers)
        desc << new DescriptionDisplayNameModel((new DescriptionDisplayName()).getName(this.product))
        desc << new HtmlCrumbDisplayModel(this.product.name)
        desc << new DescriptionDisplayModel(this.product.description.description)
        job << desc

        def allRepositories = RepositoryUtilities.allFlowRepositories(this.product, false)
        RepositoryJobParametersApplier.applyRepositories(job, allRepositories)
        job << new JobParameterModel('external_build_number','','Build number of trigger job')

        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ABSOLUTE, 12*60, false, false)

        this.addBuildFlowDslParameters(job, allRepositories)

        if (this.product.retentionPolicy.saveArtifacts) {
            IScriptlet tca = new SummaryActionScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/TriggerCollectArtifactsSummaryAction.groovy"),
                this.jobName.getName(this.product.origin.project, new JobTypeCollectArtifacts()), JobIcon.PACKAGE)
            job << new JobGroovyPostBuildModel(tca)
        }

        PromoteBuildChainScriptlet pbc = new PromoteBuildChainScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/PromoteBuildChainSummaryAction.groovy"),
            this.jobName.getName(this.product.origin.project, new JobTypePromoteBuildChain()))
        job << new JobGroovyPostBuildModel(pbc)

        AnnotateBuildChainScriptlet abc = new AnnotateBuildChainScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/AnnotateBuildChainSummaryAction.groovy"),
            this.jobName.getName(this.product.origin.project, new JobTypeAnnotateBuildChain()))
        job << new JobGroovyPostBuildModel(abc)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.SLOW_FEEDBACK,
                this.product.watchers, this.product.pm, this.product.techLead)
        job << new JobPostBuildWorkspaceCleanupModel()

        return job
    }

    private void addBuildFlowDslParameters(ProductFlowJobModel job, Repository[] repositories) {
        def parameters = [new BuildFlowDslParameter("external_build_number", "params[\"external_build_number\"]")]
        job << new FlowJobFlowDslStepModel(
                parameters as BuildFlowDslParameter[],
                repositoryVariables(repositories),
                CompileJobModel)
    }
}
