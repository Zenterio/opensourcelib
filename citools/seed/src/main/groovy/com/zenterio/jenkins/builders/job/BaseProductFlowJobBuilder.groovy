package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.RetentionPolicy
import com.zenterio.jenkins.appliers.ConcurrentBuildsApplier
import com.zenterio.jenkins.appliers.LogParsingApplier
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.configuration.ConcurrentBuilds
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslVariable
import com.zenterio.jenkins.models.job.JobDisplayNameModel
import com.zenterio.jenkins.models.job.JobNameModel
import com.zenterio.jenkins.models.job.JobNeedWorkspaceModel
import com.zenterio.jenkins.models.job.JobPostBuildScriptWrapperModel
import com.zenterio.jenkins.models.job.JobRetentionModel
import com.zenterio.jenkins.models.job.JobTimeStampModel
import com.zenterio.jenkins.models.job.JobUrlModel

/**
 * Abstract base class for product flow job builders
 */
abstract class BaseProductFlowJobBuilder implements IModelBuilder {

    protected static final String RESULT_DIR = 'result'

    protected Product product
    protected JenkinsUrl url
    protected JobName jobName
    protected DisplayName displayName
    protected String scriptletsDirectory
    protected RetentionPolicy jobRetentionPolicy
    protected ConcurrentBuilds concurrentBuilds

    public BaseProductFlowJobBuilder(Product product, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName, RetentionPolicy jobRetentionPolicy,
        ConcurrentBuilds concurrentBuilds) {
        this.product = product
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
        this.jobRetentionPolicy = jobRetentionPolicy
        this.concurrentBuilds = concurrentBuilds
    }

    abstract public IModel build()

    public IModel buildBase(IModel job) {
        String name = this.jobName.getName(this.product)
        String displayName = this.displayName.getName(this.product)
        String url = this.url.getUrl(this.product)

        ConcurrentBuildsApplier.apply(this.concurrentBuilds, job)
        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << new JobNeedWorkspaceModel(true)
        job << new JobRetentionModel(this.jobRetentionPolicy)
        job << new JobTimeStampModel(true)

        IModel wrapper = new JobPostBuildScriptWrapperModel(true, true, true)
        job << wrapper
        LogParsingApplier.applyLogParsingAnalysisPostBuildShellStep(wrapper, this.scriptletsDirectory, this.product.logParsing, false)
        LogParsingApplier.applyBuildFlowLogAnalysisSummary(job, name, RESULT_DIR, this.scriptletsDirectory)

    }

    protected BuildFlowDslVariable[] repositoryVariables(Repository[] repositories) {
        return repositories.collect({repo ->
            new BuildFlowDslVariable(repo.envName, "params[\"${repo.envName}\"]")
        })
    }

}
