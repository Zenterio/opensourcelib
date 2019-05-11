package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.BuildStepApplier
import com.zenterio.jenkins.appliers.BuildTimeoutApplier
import com.zenterio.jenkins.appliers.CoreDumpHandlingApplier
import com.zenterio.jenkins.appliers.LogParsingApplier
import com.zenterio.jenkins.appliers.PublishOverSSHApplier
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.builders.IModelBuilder
import com.zenterio.jenkins.builders.JasmineCommandBuilder
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.BuildStepScriptlet
import com.zenterio.jenkins.buildstep.K2BuildStepScriptlet
import com.zenterio.jenkins.buildstep.KazamBuildStepScriptlet
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.buildstep.STBPortalBuildStepScriptlet
import com.zenterio.jenkins.buildstep.SetExternalBuildNumberAndStartedByScriptlet
import com.zenterio.jenkins.buildstep.XmlToCsvBuildStepScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.BuildTimeout
import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.configuration.Duration
import com.zenterio.jenkins.configuration.Epg
import com.zenterio.jenkins.configuration.Owner
import com.zenterio.jenkins.configuration.ProductVariant
import com.zenterio.jenkins.configuration.RepositoryUtilities
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.configuration.TestGroupType
import com.zenterio.jenkins.configuration.TestJobInputParameter
import com.zenterio.jenkins.configuration.TestReportType
import com.zenterio.jenkins.configuration.TestSuite
import com.zenterio.jenkins.configuration.Upstream
import com.zenterio.jenkins.configuration.XmlToCsv
import com.zenterio.jenkins.jobtype.JobType
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.DescriptionDisplayNameModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslExcludeFromFlowModel
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslParameterBuildNumberModel
import com.zenterio.jenkins.postbuild.Link2CoreDumpsScriptlet
import com.zenterio.jenkins.postbuild.Link2ZintoScriptlet
import com.zenterio.jenkins.postbuild.STBPortalCommand
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.scriptlet.IScriptlet

/**
 * Assembles the model for a Test job.
 */
class TestJobBuilder implements IModelBuilder {

    protected ProductVariant product
    protected BuildType buildType
    protected JenkinsUrl url
    protected JobName jobName
    protected DisplayName displayName
    protected String scriptletsDirectory
    protected TestContext testContext
    protected BuildTimeout buildTimeout
    protected JobType jobType
    protected JobModel parentJob

    public TestJobBuilder(ProductVariant product,
                          TestContext testContext,
                          String scriptletsDirectory,
                          JenkinsUrl url,
                          JobName jobName,
                          DisplayName displayName,
                          BuildTimeout buildTimeout,
                          JobType jobType,
                          JobModel parentJob) {
        this.product = product
        this.buildType = product.buildType
        this.testContext = testContext
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.scriptletsDirectory = scriptletsDirectory
        this.buildTimeout = buildTimeout
        this.jobType = jobType
        this.parentJob = parentJob
    }

    @Override
    public IModel build() {
        IModel job = new TestJobModel(this.testContext.upstream, this.parentJob)
        String jobName = this.jobName.getName(this.product, this.jobType, this.buildType, this.testContext)
        String displayName = this.displayName.getName(this.product, this.jobType,
                this.buildType, this.testContext)
        String descDisplayName = (new DescriptionDisplayName()).getName(this.testContext, this.buildType)
        String url = this.url.getUrl(product, this.jobType, this.buildType, this.testContext)
        IModel desc = new StandardJobDescriptionModel(this.product, this.jobType,
                this.buildType, this.testContext.watchers, this.testContext.owners)
        desc << new DescriptionDisplayModel(this.testContext.description?.description)
        desc << new DescriptionDisplayNameModel(descDisplayName)
        job << new JobWorkspaceBrowsingModel(this.testContext.workspaceBrowsing.enabled)
        job << new JobPriorityModel(this.testContext.priority)
        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobShellStepModel(new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps", this.product.name, this.product.origin.name, this.testContext.repositories))
        job << new JobLogSizeCheckerModel(2500, false)
        job << new JobExecuteConcurrentBuildModel(true)
        if (this.testContext.coredumpHandling) {
            CoreDumpHandlingApplier.applyEnvInjection(this.product.origin.project.name, job)
        }

        job << new JobNameModel(jobName)
        job << new JobDisplayNameModel(displayName)
        job << desc << new HtmlCrumbDisplayModel("${this.jobType.name} (${buildType.name}) ${testContext.testGroup.name} ${testContext.name}", true)

        // Only allow changing node for jobs where workspace doesn't contain secrets
        job << new JobLabelModel((new JobLabel(this.jobType, this.testContext)).getLabel(), this.testContext.workspaceBrowsing.enabled)
        job << new JobUrlModel(url)
        job << new JobTimeStampModel()
        job << new JobIconModel(JobIcon.getIcon(this.jobType, this.buildType))
        job << new JobRetentionModel(testContext.retentionPolicy)
        addWatchers(job, this.testContext.watchers, this.testContext.owners)
        setUpstreamTrigger(job, this.testContext.upstream)
        job << new JobScmTriggerModel(this.testContext.polling)
        job << new JobCronTriggerModel(this.testContext.periodic)
        job << new JobGitScmBranchBasedModel(this.testContext.repositories,
            false, false, true, RepositoryConfigurable.OPTIONAL)
        addInputParameters(job, this.testContext.inputParameters)
        addImageRelatedParameters(job, this.testContext.image.enabled, this.testContext.image.flatten, this.testContext.image.artifact)
        if (this.testContext.upstream in [Upstream.TRUE, Upstream.ASYNC]) {
            RepositoryJobParametersApplier.applyRepositoriesForTestsWithUpstream(job, RepositoryUtilities.testRepositories(this.testContext.testGroup))
        } else {
            RepositoryJobParametersApplier.applyRepositories(job, this.testContext.repositories)
        }
        ResourcesApplier.apply(this.testContext.resources, job)

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
        preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, this.testContext.repositories))
        preScmWrapper << new JobPreScmSystemGroovyScriptStepModel(new SetExternalBuildNumberAndStartedByScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/SetBuildDisplayName.groovy"),
                this.product.startedBy, false))
        if (this.testContext.coredumpHandling) {
            CoreDumpHandlingApplier.applyPreScmSetup(this.scriptletsDirectory, preScmWrapper)
        }
        job << preScmWrapper

        addTestSuites(job, this.testContext.testSuites)
        addEpgs(job, this.testContext.epgs)

        addSTBBuildSteps(job, this.jobType)

        if (this.testContext.testGroup.type == TestGroupType.KAZAM) {
            this.applyKazamBuildSteps(job)
        } else {
            this.applyK2BuildSteps(job)
        }

        job << new JobCredentialListModel(this.testContext.credentials)

        BuildTimeoutApplier.apply(buildTimeout, job)

        IModel wrapper = new JobPostBuildScriptWrapperModel(true, true, true)
        if (this.testContext.coredumpHandling) {
            CoreDumpHandlingApplier.applyPostBuildScriptTearDown(this.scriptletsDirectory, wrapper)
        }
        wrapper << new JobPostBuildShellStepModel(new BuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "memlog-graph-generation"),
                this.product.name, 0))
        wrapper << new JobPostBuildShellStepModel(new BuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "cpulog-graph-generation"),
                this.product.name, 0))
        this.addXmlToCsv(wrapper, this.testContext.xmlToCsvs)
        LogParsingApplier.applyLogParsingAnalysisPostBuildShellStep(wrapper, this.scriptletsDirectory, this.testContext.logParsing)
        wrapper << new JobPostBuildShellStepModel(new BuildStepScriptlet(
                new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "md5sum"),
                this.product.name, 0))
        job << wrapper

        this.applyTestReport(job, this.testContext.testReport.type)

        job << new JobGroovyPostBuildModel(new FileScriptlet("${this.scriptletsDirectory}/AlternateArchiveZipDownload.groovy"))
        LogParsingApplier.applyLogParsingPublishPostBuildGroovyStep(job, this.scriptletsDirectory, this.testContext.logParsing)
        job << new JobGroovyPostBuildModel(new Link2ZintoScriptlet(new FileScriptlet("${this.scriptletsDirectory}/Link2ZintoSummaryAction.groovy")))
        if (this.testContext.coredumpHandling) {
            job << new JobGroovyPostBuildModel(new Link2CoreDumpsScriptlet(new FileScriptlet("${this.scriptletsDirectory}/Link2CoreDumpsSummaryAction.groovy"),
                this.product.origin.project.name, "kazam"))
        }
        job << new JobGroovyPostBuildModel(new FileScriptlet("${this.scriptletsDirectory}","PublishGraphReports.groovy"))
        job << new JobGroovyPostBuildModel(new STBPortalCommand(
                this.scriptletsDirectory,
                '${portalclient} software install complete ${resultDict[result]} ${stbIp} IMAGE',
                'def resultDict = ["UNSTABLE" : "s", "FAILURE": "f", "SUCCESS": "s", "ABORTED": "a"]',
                'manager.build.buildVariables.containsKey("kfs_build_number")'))
        job << new JobGroovyPostBuildModel(new STBPortalCommand(
                this.scriptletsDirectory,
                '${portalclient} test run complete ${resultDict[result]} ${stbIp}',
                'def resultDict = ["UNSTABLE" : "u", "FAILURE": "f", "SUCCESS": "s", "ABORTED": "a"]'))

        PublishOverSSHApplier publishOverSSHApplier = new PublishOverSSHApplier(
            this.scriptletsDirectory, this.product, this.jobType, this.buildType)
        publishOverSSHApplier.applyTestContext(testContext, job)

        job << new JobCsvDataPlotModel(this.testContext.csvDataPlots)

        job << new JobPostBuildWorkspaceCleanupModel()

        return job
    }

    private void applyKazamBuildSteps(IModel job) {
        String extraArguments = this.testContext.testCommandArgs?.extraArgs ?: ""
        extraArguments += addKazamDurationParameter(job, this.testContext.duration)

        def factory = new BuildStepFactory(this.scriptletsDirectory, this.testContext.variables,
                { IScriptlet template, int swUpgradeOffset ->
                    new KazamBuildStepScriptlet(template,
                            this.jobType, this.buildType, this.product, this.testContext.testGroup.productConfiguration,
                            this.testContext.testGroup.boxConfiguration,
                            "\$WORKSPACE/" + this.testContext.testGroup.testRoot,
                            "source",
                            new JasmineCommandBuilder(testContext.jasmine, testContext.repositories),
                            extraArguments, this.product.origin.project.name)
                })
        new BuildStepApplier(factory).applyBuildSteps(['kazam'], this.testContext.customBuildSteps, 0, job)
    }

    private void applyK2BuildSteps(IModel job) {
        String extraArguments = this.testContext.testCommandArgs?.extraArgs ?: ""
        String commandArguments = ""
        commandArguments += addK2DurationParameter(job, this.testContext.duration)

        def factory = new BuildStepFactory(this.scriptletsDirectory, this.testContext.variables,
                { IScriptlet template, int swUpgradeOffset ->
                    new K2BuildStepScriptlet(template,
                            this.jobType, this.buildType, this.product, this.testContext.testGroup.productConfiguration,
                            this.testContext.testGroup.boxConfiguration,
                            "\$WORKSPACE/" + this.testContext.testGroup.testRoot,
                            "source",
                            new JasmineCommandBuilder(testContext.jasmine, testContext.repositories),
                            extraArguments, commandArguments, this.product.origin.project.name, this.buildTimeout
                    )
                })
        new BuildStepApplier(factory).applyBuildSteps(['k2'], this.testContext.customBuildSteps, 0, job)
    }

    private void applyTestReport(IModel job, TestReportType type) {
        job << new JobArtifactModel('result/**/*', true)
        if (type == TestReportType.JUNIT) {
            job << new JobJUnitTestReportModel('result/KazamTest*.xml, result/Jasmine_*.xml, result/**/junit-*.xml, result/**/BrowserTest*.xml, result/YoutubeTest.xml, result/YouTubeConformance.xml, result/YoutubeMseEme*.xml, result/jenkinsresult.xml')
        } else if (type == TestReportType.TESTNG) {
            job << new JobTestNgTestReportModel('result/**/testng-*.xml')
        }
    }

    private void addSTBBuildSteps(TestJobModel job, JobType jobType) {
        String configDestDir = 'source'
        // copyArtifact to get access to configuration.mk and build-info.txt files from the stb-portal-* scripts
        job << new JobCopyArtifactsFromBuildNumberModel(
                this.parentJob,
                "\${kfs_build_number}",
                "result/configuration.mk, result/build-info.txt",
                configDestDir,
                true)
        job << new JobShellStepModel(
                new STBPortalBuildStepScriptlet(
                        new FileScriptlet("${this.scriptletsDirectory}/buildsteps/stb-portal-start-install-software"),
                        jobType,
                        buildType,
                        product,
                        "\${WORKSPACE}/${configDestDir}/configuration.mk",
                        "\${WORKSPACE}/${configDestDir}/build-info.txt"))

        job << new JobShellStepModel(
                new STBPortalBuildStepScriptlet(
                        new FileScriptlet("${this.scriptletsDirectory}/buildsteps/stb-portal-start-test-run"),
                        jobType,
                        buildType,
                        product,
                        null,
                        null
                )
        )
    }

    private void addImageRelatedParameters(IModel job, Boolean enabled, Boolean flatten, String artifact) {
        if (enabled) {
            job << new JobParameterModel("kfs_file", artifact,
                    "The path to the image file in the upstream job's artifacts. If left blank, the STB will not be flashed and rebooted.")
            job << new JobParameterModel("kfs_build_number", "lastSuccessfulBuild",
                    "The build number of the original Jenkins job that should be tested")
            job << new JobBuildFlowDslParameterBuildNumberModel("kfs_build_number", this.parentJob)
            job << new JobCopyArtifactsFromBuildNumberModel(
                    this.parentJob,
                    "\${kfs_build_number}",
                    "\${kfs_file}",
                    "source", flatten)
        }
    }

    private void addInputParameters(IModel job, TestJobInputParameter[] inputParameters) {
        inputParameters.each { parameter ->
            job << new JobParameterModel(parameter.name, parameter.defaultValue,
                    parameter.description)
        }
    }

    private void addTestSuites(IModel job, TestSuite[] testSuites) {
        List<String> suitePaths = testSuites.collect({ TestSuite suite ->
            suite.path
        }) as List<String>
        job << new JobParameterChoiceModel("test_suite", suitePaths, "Test suite")
    }

    private void addEpgs(IModel job, Epg[] epgs) {
        List<String> epgPaths = epgs.collect({ Epg epg ->
            epg.path
        }) as List<String>
        if (epgPaths.size() > 0) {
            if (!("DONT-UPGRADE" in epgPaths)) {
                epgPaths.add("DONT-UPGRADE")
            }
            job << new JobParameterChoiceModel("epg", epgPaths, "EPG")
        }
    }

    private void addXmlToCsv(IModel parent, XmlToCsv[] xmlToCsvs) {
        xmlToCsvs.each({ XmlToCsv config ->
            parent << new JobPostBuildShellStepModel(
                new XmlToCsvBuildStepScriptlet(
                    new FileScriptlet("${this.scriptletsDirectory}/buildsteps", "xml2csv"),
                    config))
        })
    }

    protected void addWatchers(IModel job, ContactInformationCollection watchers, ContactInformationCollection owners) {
        if (watchers.size() > 0 || owners?.size() > 0) {
            job << new JobEmailNotificationModel(JobEmailNotificationPolicy.TEST_CONTROL,
                    watchers, this.product.pm, this.product.techLead, "", owners)
        }
    }

    /**
     * Add parameters for the Kazam loopFor <duration> tag.
     * @param job
     * @param duration
     * @return string that should be added to the extra arguments macro
     */
    private String addKazamDurationParameter(IModel job, Duration duration)
    {
        String argument=""
        if (duration) {
            argument = ' --config loopFor="${duration}"'
            job << new JobParameterModel("duration", duration.time, "How long Kazam should loop for")
        }
        return argument
    }

    /**
     * Add parameters for the K2 <duration> tag.
     * @param job
     * @param duration
     * @return string that should be added to the extra arguments macro
     */
    private String addK2DurationParameter(IModel job, Duration duration)
    {
        String argument=""
        if (duration) {
            argument = ' --schedule-duration "${duration}"'
            job << new JobParameterModel("duration", duration.time, "How long K2 should loop for")
        }
        return argument
    }

    private void setUpstreamTrigger(IModel job, Upstream upstream) {
        if (upstream in [Upstream.TRUE, Upstream.ASYNC]) {
            job << new JobParameterModel("external_build_number", "",
                    "Build number of trigger job")

            if (upstream == Upstream.ASYNC) {
                job << new JobBuildFlowDslExcludeFromFlowModel()
            }
        } else {
            job << new JobBuildFlowDslExcludeFromFlowModel()
        }
    }
}
