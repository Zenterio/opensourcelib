package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.RetentionPolicy
import com.zenterio.jenkins.appliers.ConcurrentBuildsApplier
import com.zenterio.jenkins.appliers.LogParsingApplier
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.configuration.ConcurrentBuilds
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobDisplayNameModel
import com.zenterio.jenkins.models.job.JobNameModel
import com.zenterio.jenkins.models.job.JobNeedWorkspaceModel
import com.zenterio.jenkins.models.job.JobPostBuildScriptWrapperModel
import com.zenterio.jenkins.models.job.JobPreBuildWorkspaceCleanupModel
import com.zenterio.jenkins.models.job.JobRetentionModel
import com.zenterio.jenkins.models.job.JobTimeStampModel
import com.zenterio.jenkins.models.job.JobUrlModel
import com.zenterio.jenkins.models.job.flowdsl.BuildFlowDslVariable

/**
 * Abstract base class for origin flow job builders
 */
abstract class BaseOriginFlowJobBuilder implements IModelBuilder {

    protected static final String RESULT_DIR = 'result'

    protected Origin origin
    protected JenkinsUrl url
    protected JobName jobName
    protected DisplayName displayName
    protected String scriptletsDirectory
    protected RetentionPolicy jobRetentionPolicy
    protected ConcurrentBuilds concurrentBuilds

    public BaseOriginFlowJobBuilder(Origin origin, String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName, RetentionPolicy jobRetentionPolicy,
        ConcurrentBuilds concurrentBuilds) {
        this.origin = origin
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
        this.jobRetentionPolicy = jobRetentionPolicy
        this.concurrentBuilds = concurrentBuilds
    }

    abstract public IModel build()

    public IModel buildBase(IModel job) {
        String name = this.jobName.getName(this.origin)
        String displayName = this.displayName.getName(this.origin)
        String url = this.url.getUrl(this.origin)

        ConcurrentBuildsApplier.apply(this.concurrentBuilds, job)
        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobNameModel(name)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)
        job << new JobTimeStampModel(true)
        job << new JobRetentionModel(this.jobRetentionPolicy)
        job << new JobNeedWorkspaceModel(true)

        IModel wrapper = new JobPostBuildScriptWrapperModel(true, true, true)
        job << wrapper
        LogParsingApplier.applyLogParsingAnalysisPostBuildShellStep(wrapper, this.scriptletsDirectory, this.origin.logParsing, false)
        LogParsingApplier.applyBuildFlowLogAnalysisSummary(job, name, RESULT_DIR, this.scriptletsDirectory)

    }

    protected BuildFlowDslVariable[] repositoryVariables(Repository[] repositories) {
        return repositories.toList().withIndex().collect({ Repository repo, Integer index ->
            new BuildFlowDslVariable(repo.envName, (index == 0)?"build.environment.get(\"GIT_COMMIT\")":"build.environment.get(\"GIT_COMMIT_${index}\")")
        })
    }
}
