package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.PublishOverSSHApplier
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.GitIndexUpdateScriptlet
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.buildstep.UnitTestBuildStepScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeUnitTest
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.scriptlet.*


/**
 * Assembles the model for a unit test job.
 */
class UnitTestJobBuilder extends BaseCompilationJobBuilder {

    UnitTest unitTest

    /**
     * @param unitTest The unit test definition to use
     * @param buildType
     * @param scriptletsDirectory
     * @param url Jenkins URL factory
     * @param jobName Job name factory
     * @param displayName Job display name factory
     */
    public UnitTestJobBuilder(UnitTest unitTest,
            BuildType buildType, String scriptletsDirectory,
            JenkinsUrl url, JobName jobName,
            DisplayName displayName) {
        super(unitTest.product,
            new JobTypeUnitTest(),
            buildType,
            scriptletsDirectory,
            url,
            jobName,
            displayName,
            unitTest.watchers,
            new BuildStepFactory(scriptletsDirectory, unitTest.variables,
                { IScriptlet template, int swUpgradeOffset ->
                    new UnitTestBuildStepScriptlet(
                            template,
                            buildType,
                            unitTest,
                            "xml-pretty",
                            "\${WORKSPACE}/result/configuration.mk",
                            unitTest.cache)
                }),
            [
                'abs-unit-test',
                'abs-unit-test-artifacts'
            ],
            unitTest.cache,
            unitTest.concurrentBuilds,
            unitTest.credentials,
            unitTest.customBuildSteps,
            unitTest.retentionPolicy,
            unitTest.startedBy,
            unitTest.product.buildNodes,
            unitTest.buildTimeout,
            unitTest.workspaceBrowsing,
            unitTest.priority)
        this.unitTest = unitTest
    }

    public IModel build() {
        IModel job = new UnitTestJobModel()

        ResourcesApplier.apply(this.unitTest.resources, job)

        Repository[] repositories = this.unitTest.product.origin.repositories

        RepositoryJobParametersApplier.applyRepositories(job, repositories)
        job << new JobParameterModel('external_build_number','','Build number of trigger job')

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
        preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, repositories))
        job << preScmWrapper

        BuildInfoBuildStepScriptlet bi =
                new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps",
                        this.unitTest.product.name,
                        this.unitTest.product.origin.name,
                        repositories)

        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobShellStepModel(new GitIndexUpdateScriptlet(this.scriptletsDirectory, repositories, unitTest.buildEnv))

        job << new JobShellStepModel(bi)

        this.buildBase(job)

        job.getChild(StandardJobDescriptionModel, false, false).with {
            add new DescriptionDisplayModel(this.unitTest?.description?.description)
        }

        job << new JobGitScmBranchBasedModel(repositories, false, false, true,
            RepositoryConfigurable.OPTIONAL)

        job << new JobCompilerWarningsModel('.*3pp.*')

        job << new JobCoberturaCoverageModel("**/${this.unitTest.makeRoot.name}/build/${this.unitTest.name}/${this.buildType.name}/unittest/**/*.coverage.xml")

        job << new JobArtifactModel('result/**/*', true)

        job << new JobJUnitTestReportModel("${this.unitTest.makeRoot.name}/build/${this.unitTest.name}/${this.buildType.name}/unittest/**/*.output.xml")

        job << new JobCsvDataPlotModel(this.unitTest.csvDataPlots)

        PublishOverSSHApplier publishOverSSHApplier = new PublishOverSSHApplier(
            this.scriptletsDirectory, null, this.jobType, this.buildType)
        publishOverSSHApplier.apply(this.unitTest, job)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.SLOW_FEEDBACK,
            this.unitTest.watchers, this.unitTest.pm, this.unitTest.techLead)

        job << new JobPostBuildWorkspaceCleanupModel()
        return job
    }

}
