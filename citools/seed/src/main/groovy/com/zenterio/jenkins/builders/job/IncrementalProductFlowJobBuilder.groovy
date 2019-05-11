package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.DescriptionDisplayNameModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslParameter
import com.zenterio.jenkins.models.job.flowdsl.FlowJobFlowDslStepModel

/**
 * Assembles the model for a Product Flow Job.
 */
class IncrementalProductFlowJobBuilder extends BaseProductFlowJobBuilder {

    public IncrementalProductFlowJobBuilder(Product product,
        String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        super(product, scriptletsDirectory, url, jobName, displayName, RetentionPolicyFactory.createIncrementalPolicy(),
              new ConcurrentBuilds(false))
    }

    @Override
    public IModel build() {
        ModelEntity job = new ProductFlowJobModel()
        def allRepositories = RepositoryUtilities.allFlowRepositories(this.product, true)
        RepositoryJobParametersApplier.applyRepositories(job, allRepositories)

        this.buildBase(job)

        job << new JobLabelModel('incremental')
        job << new JobDefaultLoadBalancingModel()
        job << new JobIconModel(JobIcon.FLOW_PRODUCT_INC)

        IModel desc = new ProductFlowJobDescriptionModel(this.product.pm, this.product.techLead,
            null)
        desc << new DescriptionDisplayNameModel((new DescriptionDisplayName()).getName(this.product))
        desc << new HtmlCrumbDisplayModel(this.product.name)
        desc << new DescriptionDisplayModel(this.product.description.description)
        job << desc

        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ABSOLUTE, 3*60, false, false)

        job << new FlowJobFlowDslStepModel(
                [] as BuildFlowDslParameter[],
                this.repositoryVariables(allRepositories),
                CompileJobModel)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.FAST_FEEDBACK_CONTROL,
                this.product.watchers, this.product.pm, this.product.techLead)

        return job
    }
}
