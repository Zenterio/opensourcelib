package com.zenterio.jenkins.application

import com.zenterio.jenkins.dispatcher.ExactMatchDispatcher
import com.zenterio.jenkins.generators.dsl.DescriptionDisplayGenerator
import com.zenterio.jenkins.generators.dsl.HtmlCrumbDisplayGenerator
import com.zenterio.jenkins.generators.dsl.job.*
import com.zenterio.jenkins.generators.dsl.view.ViewColumnsGenerator
import com.zenterio.jenkins.generators.dsl.view.ViewDescriptionGenerator
import com.zenterio.jenkins.generators.dsl.view.ViewGenerator
import com.zenterio.jenkins.generators.dsl.view.ViewJobSelectionGenerator
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.display.HtmlCrumbDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.models.job.flowdsl.FlowJobFlowDslStepModel
import com.zenterio.jenkins.models.view.ViewColumnsModel
import com.zenterio.jenkins.models.view.ViewDescriptionModel
import com.zenterio.jenkins.models.view.ViewJobSelectionModel
import com.zenterio.jenkins.models.view.ViewModel

import groovy.util.logging.Log


/**
 * Seed application that reads XML configuration files and
 * generates jenkins configuration using the Job DSL jenkins plugin.
 *
 * <p>
 * This application interacts with the Job DSL jenkins plugin via a set of
 * factory methods for creating jobs and views.
 * <p>
 * The application is also dependent on path to where the scriptlet files
 * are located. See also {@link com.zenterio.jenkins.scriptlet}.
 * <p>
 * This class is a specialization of the XmlSeedBaseApplication using an
 * ExactMatchDispatcher.
 */
@Log
class XmlSeedDslApplication extends XmlSeedBaseApplication {

    /**
     * Factory method in the form of a closure. It takes no arguments and
     * should return a job DSL job instance.
     */
    protected Closure jobCreator

    /**
     * Factory method in the form of a closure. It takes no arguments and
     * should return a job DSL build-flow job instance.
     */
    protected Closure buildFlowCreator

    /**
     * Factory method in the form of a closure. It takes no arguments and
     * should return a job DSL view instance.
     */
    protected Closure viewCreator


    /**
     *
     * @param scriptletsDirectory   Path to scriptlet directory
     * @param jobCreator            Closure factory method for job instantiation.
     * @param buildFlowCreator      Closure factory method for build-flow job instantiation.
     * @param viewCreator           Closure factory method for view instantiation.
     */
    public XmlSeedDslApplication(String scriptletsDirectory,
            Closure jobCreator,
            Closure buildFlowCreator,
            Closure viewCreator)  {

        super(new ExactMatchDispatcher(false), scriptletsDirectory)

        this.jobCreator = jobCreator
        this.buildFlowCreator = buildFlowCreator
        this.viewCreator = viewCreator

        this.configureDispatcher()

    }

    private void configureDispatcher() {
        this.dispatcher.with {

            // Entities
            reg ViewModel, new ViewGenerator(this.viewCreator)
            reg OriginFlowJobModel, new FlowJobGenerator(this.buildFlowCreator)
            reg ProductFlowJobModel, new FlowJobGenerator(this.buildFlowCreator)
            reg JobModel, new JobGenerator(this.jobCreator)
            reg UnitTestJobModel, new JobGenerator(this.jobCreator)
            reg TriggerJobModel, new JobGenerator(this.jobCreator)
            reg TagJobModel, new JobGenerator(this.jobCreator)
            reg FlashJobModel, new JobGenerator(this.jobCreator)
            reg CompileJobModel, new JobGenerator(this.jobCreator)
            reg TestJobModel, new JobGenerator(this.jobCreator)
            reg CoverityJobModel, new JobGenerator(this.jobCreator)
            reg DocJobModel, new JobGenerator(this.jobCreator)
            reg PromoteBuildChainJobModel, new JobGenerator(this.jobCreator)
            reg AnnotateBuildChainJobModel, new JobGenerator(this.jobCreator)
            reg ReleasePackagingJobModel, new JobGenerator(this.jobCreator)
            reg CollectArtifactsJobModel, new JobGenerator(this.jobCreator)

            // Standard View properties
            reg ViewDescriptionModel, new ViewDescriptionGenerator()
            reg ViewColumnsModel, new ViewColumnsGenerator()
            reg ViewJobSelectionModel, new ViewJobSelectionGenerator()

            // Flow control properties
            reg JobBuildFlowForkModel, new JobBuildFlowForkGenerator()
            reg JobBuildFlowJoinModel, new JobBuildFlowJoinGenerator()

            // Free style job properties
            reg JobDescriptionModel, new JobDescriptionGenerator()

            // Origin Flow Jobs properties
            reg OriginFlowJobDescriptionModel, new JobDescriptionGenerator()

            // Product Flow Jobs properties
            reg ProductFlowJobDescriptionModel, new JobDescriptionGenerator()

            // Common properties for most jobs
            reg JobDisplayNameModel, new JobDisplayNameGenerator()
            reg JobParameterModel, new JobParameterGenerator()
            reg JobBuildTimeoutParameterModel, new JobParameterGenerator()
            reg JobParameterChoiceModel, new JobParameterChoiceGenerator()
            reg JobParameterTextModel, new JobParameterTextGenerator()
            reg JobTimeStampModel, new JobTimeStampGenerator()
            reg JobRetentionModel, new JobRetentionGenerator()
            reg JobBuildTimeoutModel, new JobBuildTimeoutGenerator()
            reg JobLabelModel, new JobLabelGenerator()
            reg JobResourcesModel, new JobResourcesGenerator()
            reg JobNeedWorkspaceModel, new JobNeedWorkspaceGenerator()
            reg JobIconModel, new JobIconGenerator()
            reg JobPostBuildWorkspaceCleanupModel, new JobPostBuildWorkspaceCleanupGenerator()
            reg JobPreBuildWorkspaceCleanupModel, new JobPreBuildWorkSpaceCleanupGenerator()
            reg JobBlockOnDownStreamProjectsModel, new JobBlockOnDownstreamProjectGenerator()

            // Temporarily disabled because of memory leak in plugin
            // reg JobLogSizeCheckerModel, new JobLogSizeCheckerGenerator()

            reg JobExecuteConcurrentBuildModel, new JobExecuteConcurrentBuildGenerator()
            reg JobDefaultLoadBalancingModel, new JobDefaultLoadBalancingGenerator()
            reg JobCredentialListModel, new JobCredentialListGenerator()
            reg JobWorkspaceBrowsingModel, new JobWorkspaceBrowsingGenerator()
            reg JobPriorityModel, new JobPriorityGenerator()


            // Display properties
            reg StandardJobDescriptionModel, new JobDescriptionGenerator()
            reg HtmlCrumbDisplayModel, new HtmlCrumbDisplayGenerator()
            reg DescriptionDisplayModel, new DescriptionDisplayGenerator()

            // pre-scm
            reg JobPreScmBuildStepWrapperModel, new JobPreScmBuildStepWrapperGenerator()
            reg JobEnvInjectionModel, new JobEnvInjectionGenerator()

            // SCM
            reg JobGitScmBranchBasedModel, new JobGitScmBranchBasedGenerator()

            // Triggers
            reg JobCronTriggerModel, new JobCronTriggerGenerator()
            reg JobScmTriggerModel, new JobScmTriggerGenerator()

            // Build steps
            reg JobCopyArtifactsFromBuildNumberModel, new JobCopyArtifactsFromBuildNumberGenerator()
            reg JobShellStepModel, new JobShellStepGenerator()
            reg FlowJobFlowDslStepModel, new FlowJobFlowDslStepGenerator()
            reg JobSystemGroovyScriptStepModel, new JobSystemGroovyStepGenerator()
            reg JobDownStreamTriggerModel, new JobDownStreamTriggerBuildStepGenerator()

            // Job Post-build Actions
            reg ConsoleLogToWorkspaceModel, new ConsoleLogToWorkspaceGenerator()
            reg JobArtifactModel, new JobArtifactGenerator()
            reg JobCoberturaCoverageModel, new JobCoberturaCoverageGenerator()
            reg JobCompilerWarningsModel, new JobCompilerWarningsGenerator()
            reg JobCsvDataPlotModel, new JobCsvDataPlotGenerator()
            reg JobEmailNotificationModel, new JobEmailNotificationGenerator()
            reg JobFingerPrintingModel, new JobFingerPrintingGenerator()
            reg JobGroovyPostBuildModel, new JobGroovyPostBuildGenerator()
            reg JobJUnitTestReportModel, new JobJUnitTestReportGenerator()
            reg JobTestNgTestReportModel, new JobTestNgTestReportGenerator()
            reg JobPostBuildScriptWrapperModel, new JobPostBuildScriptWrapperGenerator()
            reg JobPublishOverSSHListModel, new JobPublishOverSSHListGenerator()
        }
    }
}
