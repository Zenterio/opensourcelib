package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.DescriptionDisplayName
import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobIcon
import com.zenterio.jenkins.JobLabel
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.RetentionPolicy
import com.zenterio.jenkins.appliers.BuildStepApplier
import com.zenterio.jenkins.appliers.BuildTimeoutApplier
import com.zenterio.jenkins.appliers.ConcurrentBuildsApplier
import com.zenterio.jenkins.appliers.CoreDumpHandlingApplier
import com.zenterio.jenkins.appliers.LogParsingApplier
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.BuildStepScriptlet
import com.zenterio.jenkins.buildstep.SetExternalBuildNumberAndStartedByScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.buildtype.BuildTypeDebug
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.jobtype.JobTypeCompile
import com.zenterio.jenkins.jobtype.JobTypeFlash
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayNameModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.postbuild.FlashScriptlet
import com.zenterio.jenkins.postbuild.Link2CoreDumpsScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptlet

import groovy.util.logging.Log


/**
 * Abstract base class for the type of builders that build models for what
 * can be considered compilation jobs such as regular compilation, incremental
 * etc.
 */
@Log
abstract class BaseCompilationJobBuilder implements IModelBuilder {

    protected BaseProduct product
    protected BuildType buildType
    protected JenkinsUrl url
    protected JobName jobName
    protected DisplayName displayName
    protected ContactInformationCollection watchers
    protected String scriptletsDirectory
    protected JobType jobType
    protected BuildStepFactory buildStepFactory
    protected List<String> defaultBuildSteps
    protected Cache cache
    protected ConcurrentBuilds concurrentBuilds
    protected CredentialList credentials
    protected CustomBuildStepList customBuildSteps
    protected RetentionPolicy jobRetentionPolicy
    protected StartedBy startedBy
    protected BuildNodeList buildNodes
    protected BuildTimeout buildTimeout
    protected BuildStepApplier buildStepApplier
    protected WorkspaceBrowsing workspaceBrowsing
    protected Priority priority

    public BaseCompilationJobBuilder(BaseProduct product,
                                     JobType jobType,
                                     BuildType buildType,
                                     String scriptletsDirectory,
                                     JenkinsUrl url,
                                     JobName jobName,
                                     DisplayName displayName,
                                     ContactInformationCollection watchers,
                                     BuildStepFactory buildStepFactory,
                                     List<String> defaultBuildSteps,
                                     Cache cache,
                                     ConcurrentBuilds concurrentBuilds,
                                     CredentialList credentials,
                                     CustomBuildStepList customBuildSteps,
                                     RetentionPolicy jobRetentionPolicy,
                                     StartedBy startedBy,
                                     BuildNodeList buildNodes,
                                     BuildTimeout buildTimeout,
                                     WorkspaceBrowsing workspaceBrowsing,
                                     Priority priority) {
        this.product = product
        this.jobType = jobType
        this.buildType = buildType
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.watchers = watchers
        this.scriptletsDirectory = scriptletsDirectory
        this.buildStepFactory = buildStepFactory
        this.defaultBuildSteps = defaultBuildSteps
        this.cache = cache
        this.concurrentBuilds = concurrentBuilds
        this.credentials = credentials
        this.customBuildSteps = customBuildSteps
        this.jobRetentionPolicy = jobRetentionPolicy
        this.startedBy = startedBy
        this.buildNodes = buildNodes
        this.buildTimeout = buildTimeout
        this.buildStepApplier = new BuildStepApplier(buildStepFactory)
        this.workspaceBrowsing = workspaceBrowsing
        this.priority = priority
    }

    /**
     * The specific behavior of how the model is actually built should be
     * handled in the specialization (sub-class). The implementation should
     * call buildBase(job) to get all the base aspects of a compilation job.
     */
    abstract public IModel build()

    public IModel buildBase(IModel job, SwUpgrades swUpgrades=new SwUpgrades()) {
        String jobName = this.jobName.getName(this.product, this.jobType, this.buildType)
        String displayName = this.displayName.getName(this.product, this.jobType,
                        this.buildType)
        String descDisplayName = (new DescriptionDisplayName()).getName(this.jobType, this.buildType)
        String url = this.url.getUrl(this.product, this.jobType, this.buildType)
        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(false)
        preScmWrapper << new JobPreScmSystemGroovyScriptStepModel(new SetExternalBuildNumberAndStartedByScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/SetBuildDisplayName.groovy"),
                this.startedBy, false))
        CoreDumpHandlingApplier.applyPreScmSetup(this.scriptletsDirectory, preScmWrapper)
        job << preScmWrapper
        job << new JobNameModel(jobName)
        job << new JobDisplayNameModel(displayName)
        job << new JobUrlModel(url)

        // Only allow changing node for jobs where workspace doesn't contain secrets
        job << new JobLabelModel((new JobLabel(this.jobType, this.buildNodes)).getLabel(), workspaceBrowsing.getEnabled())
        job << new JobIconModel(JobIcon.getIcon(this.jobType, this.buildType))
        job << new JobLogSizeCheckerModel(100, false)
        job << new JobWorkspaceBrowsingModel(this.workspaceBrowsing.enabled)
        job << new JobPriorityModel(this.priority)
        CoreDumpHandlingApplier.applyEnvInjection(this.product.origin.project.name, job)

        IModel desc = new StandardJobDescriptionModel(this.product,
                        this.jobType, this.buildType, this.watchers)
        desc << new HtmlCrumbDisplayModel("${this.jobType} ${this.buildType}", true)
        desc << new DescriptionDisplayNameModel(descDisplayName)
        job << desc

        ConcurrentBuildsApplier.apply(this.concurrentBuilds, job)

        job << new JobTimeStampModel(true)
        job << new JobRetentionModel(this.jobRetentionPolicy)

        CredentialList credentialList = this.credentials.clone()
        if (cache.mcacheEnabled && cache.mcachePublish) {
            credentialList.add(new Credential(CredentialType.USERNAME_PASSWORD, Cache.ARTIFACTORY_CREDENTIAL_ID, 'ARTIFACTORY', true))
        }

        job << new JobCredentialListModel(credentialList)

        BuildTimeoutApplier.apply(buildTimeout, job)
        this.addCacheInitBuildSteps(job)
        this.allBuildSteps(job, swUpgrades)

        /*
         * TODO: This class should not have knowledge about specific build and job types,
         * but this is the only way to get the flash button to appear at the top of
         * custom content on the build-status page.
         */
        if (this.jobRetentionPolicy.saveArtifacts &&
            this.buildType == new BuildTypeDebug() &&
            this.jobType == new JobTypeCompile()) {
            job << new JobGroovyPostBuildModel(new FlashScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/FlashAction.groovy"),
                this.jobName.getName(this.product.origin.project, new JobTypeFlash())))
        }

        IModel wrapper = new JobPostBuildScriptWrapperModel(true, true, true)
        this.addCacheCleanupBuildSteps(wrapper)
        CoreDumpHandlingApplier.applyPostBuildScriptTearDown(this.scriptletsDirectory, wrapper)
        LogParsingApplier.applyLogParsingAnalysisPostBuildShellStep(wrapper, this.scriptletsDirectory, this.product.logParsing)
        this.addMd5sum(wrapper)
        job << wrapper

        job << new JobGroovyPostBuildModel(new Link2CoreDumpsScriptlet(new FileScriptlet("${this.scriptletsDirectory}/Link2CoreDumpsSummaryAction.groovy"),
            this.product.origin.project.name, "build"))

        if (this.jobRetentionPolicy.saveArtifacts) {
            job << new JobGroovyPostBuildModel(new FileScriptlet("${this.scriptletsDirectory}/AlternateArchiveZipDownload.groovy"))
        }

        LogParsingApplier.applyLogParsingPublishPostBuildGroovyStep(job, this.scriptletsDirectory, this.product.logParsing)

        return job
    }

    /**
     * This method adds sets of build-steps to the supplied job-model
     * for default build and sw upgrades.
     * @param job   The job which to add the build steps to.
     * @param swUpgrades List of <sw-upgrade> configuration items.
     */
    protected void allBuildSteps(IModel job, SwUpgrades swUpgrades) {
        this.buildStepApplier.applyBuildSteps(this.defaultBuildSteps, this.customBuildSteps, 0, job)
        swUpgrades.getEnabled().each { SwUpgrade swUpgrade ->
            this.buildStepApplier.applyNamedBuildSteps(job, ['abs-clean'], new CustomBuildStepList(), swUpgrade.offset)
            this.buildStepApplier.applyBuildSteps(this.defaultBuildSteps, this.customBuildSteps, swUpgrade.offset, job)
        }
    }

    protected void addCacheInitBuildSteps(job) {
        if (this.cache.getCcacheEnabled()) {
            job << new JobShellStepModel(this.buildStepFactory.fromName('ccache-init', 0))
        }
        if (this.cache.getMcacheEnabled()) {
            job << new JobShellStepModel(this.buildStepFactory.fromName('mcache-init', 0))
        }
    }

    protected void addCacheCleanupBuildSteps(IModel parent) {
        if (this.cache.getCcacheEnabled()) {
            parent << new JobPostBuildShellStepModel(this.buildStepFactory.fromName('ccache-cleanup', 0))
        }
        if (this.cache.getMcacheEnabled() && this.cache.getMcachePublish()) {
            parent << new JobPostBuildShellStepModel(this.buildStepFactory.fromName('mcache-publish', 0))
        }
    }

    protected void addMd5sum(IModel parent) {
        parent << new JobPostBuildShellStepModel(new BuildStepScriptlet(
            new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "md5sum"),
            this.product.name,
            0))
    }
}
