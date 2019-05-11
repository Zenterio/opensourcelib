package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.FlowJobFlowDslStepModel
import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslParameter
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.*

/**
 * Assembles the model for a Origin Flow job.
 */
class IncrementalOriginFlowJobBuilder extends BaseOriginFlowJobBuilder {

    public IncrementalOriginFlowJobBuilder(Origin origin, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName) {
        super(origin, scriptletsDirectory, url, jobName, displayName, RetentionPolicyFactory.createIncrementalPolicy(),
              new ConcurrentBuilds(false))
    }

    @Override
    public IModel build() {
        ModelEntity job = new OriginFlowJobModel();
        this.buildBase(job)

        job << new JobLabelModel('incremental')
        job << new JobDefaultLoadBalancingModel()
        job << new JobIconModel(JobIcon.FLOW_ORIGIN_INC)

        IModel desc = new OriginFlowJobDescriptionModel(origin.pm,
            origin.techLead, null)
        desc << new HtmlCrumbDisplayModel('Incremental ' + origin.name)
        desc << new DescriptionDisplayModel(origin.description.description)
        job << desc

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.FAST_FEEDBACK_CONTROL,
                origin.watchers, origin.pm, origin.techLead)

        job << new JobBuildTimeoutModel(BuildTimeoutPolicy.ABSOLUTE, 3*60, false, false)

        def allRepositories = RepositoryUtilities.allFlowRepositories(this.origin, true)
        job << new JobGitScmBranchBasedModel(allRepositories, false,
            this.origin.incTrigger.acceptNotifyCommit, false, RepositoryConfigurable.FORCE_FALSE)

        job << new FlowJobFlowDslStepModel(
                [] as BuildFlowDslParameter[],
                this.repositoryVariables(allRepositories),
                ProductFlowJobModel)

        if (origin.incTrigger.enabled) {
            job << new JobScmTriggerModel(origin.incTrigger.polling)
            job << new JobCronTriggerModel(origin.incTrigger.periodic)
        }

        job << new JobPostBuildWorkspaceCleanupModel()

        return job;
    }
}
