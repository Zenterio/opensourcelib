package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.buildstep.UnitTestBuildStepScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeIncrementalUnitTest
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.scriptlet.*


/**
 * Assembles the model for an incremental unit test job.
 */
class IncrementalUnitTestJobBuilder extends BaseCompilationJobBuilder {

    UnitTest unitTest

    /**
     * @param unitTest The unit test definition to use
     * @param buildType
     * @param scriptletsDirectory
     * @param url Jenkins URL factory
     * @param jobName Job name factory
     * @param displayName Job display name factory
     */
    public IncrementalUnitTestJobBuilder(UnitTest unitTest,
            BuildType buildType, String scriptletsDirectory,
            JenkinsUrl url, JobName jobName,
            DisplayName displayName) {
        super(unitTest.product,
            new JobTypeIncrementalUnitTest(),
            buildType,
            scriptletsDirectory,
            url,
            jobName,
            displayName,
            unitTest.watchers,
            new BuildStepFactory(scriptletsDirectory, unitTest.variables, { IScriptlet template, int swUpgradeOffset ->
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

        job << new JobDefaultLoadBalancingModel()
        ResourcesApplier.apply(this.unitTest.resources, job)

        Repository[] repositories = this.unitTest.product.origin.repositories

        RepositoryJobParametersApplier.applyRepositories(job, repositories)

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
        preScmWrapper << new JobPreScmShellStepModel(new FileScriptlet("${this.scriptletsDirectory}/buildsteps/clear-incremental-workspace"))
        preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, repositories))
        job << preScmWrapper

        BuildInfoBuildStepScriptlet bi =
                new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps",
                        this.unitTest.product.name,
                        this.unitTest.product.origin.name,
                        repositories)
        job << new JobShellStepModel(bi)

        this.buildBase(job)

        job.getChild(StandardJobDescriptionModel, false, false).with {
            add new DescriptionDisplayModel(this.unitTest?.description?.description)
        }

        job << new JobGitScmBranchBasedModel(repositories,
            false, false, true, RepositoryConfigurable.FORCE_FALSE)

        job << new JobArtifactModel('result/**/*', true)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.FAST_FEEDBACK_ROOT_CAUSE,
            this.unitTest.watchers, this.unitTest.pm, this.unitTest.techLead)

        return job
    }

}
