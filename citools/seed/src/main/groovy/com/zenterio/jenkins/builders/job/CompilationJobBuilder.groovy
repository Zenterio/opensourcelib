package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.PublishOverSSHApplier
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.CompileBuildStepScriptlet
import com.zenterio.jenkins.buildstep.GitIndexUpdateScriptlet
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeCompile
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.scriptlet.*


/**
 * Assembles the model for a Compilation job.
 */
class CompilationJobBuilder extends BaseCompilationJobBuilder {

    protected SwUpgrades swUpgrades
    protected boolean coverage
    protected boolean unittest

    /**
     * @param product The product to compile
     * @param scriptletsDirectory
     * @param url Jenkins URL factory
     * @param jobName Job name factory
     * @param displayName Job display name factory
     * @param watchers
     * @param SwUpgrades
     * @param unittest True if unit tests should be run and result collected
     * @param coverage True if coverage report should be generated and report collected
     */
    public CompilationJobBuilder(ProductVariant product,
                                 String scriptletsDirectory,
                                 JenkinsUrl url, JobName jobName,
                                 DisplayName displayName, ContactInformationCollection watchers,
                                 SwUpgrades swUpgrades,
                                 boolean unittest,
                                 boolean coverage) {
        super(product,
                new JobTypeCompile(),
                product.buildType,
                scriptletsDirectory,
                url,
                jobName,
                displayName,
                watchers,
                new BuildStepFactory(scriptletsDirectory, product.variables,
                        { IScriptlet template, int swUpgradeOffset ->
                            new CompileBuildStepScriptlet(
                                    template,
                                    new JobTypeCompile(),
                                    product.buildType,
                                    product,
                                    product.buildEnv,
                                    swUpgradeOffset,
                                    (coverage) ? "xml-pretty" : null,
                                    "\${WORKSPACE}/result/configuration.mk",
                                    product.cache,
                                    unittest)
                        }),
                ['zformat', 'abs-target', '3pp', 'abs-artifacts', 'stb-portal-add-software'],
                product.cache,
                product.concurrentBuilds,
                product.credentials,
                product.customBuildSteps,
                product.retentionPolicy,
                product.startedBy,
                product.buildNodes,
                product.buildTimeout,
                product.workspaceBrowsing,
                product.priority)
        this.swUpgrades = swUpgrades
        this.coverage = coverage
        this.unittest = unittest
    }

    public IModel build() {
        IModel job = new CompileJobModel()
        Repository[] repositories = this.product.origin.repositories
        BuildInfoBuildStepScriptlet bi =
                new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps",
                        this.product.name,
                        this.product.origin.name,
                        repositories)
        job << new JobPreBuildWorkspaceCleanupModel()
        job << new JobShellStepModel(new GitIndexUpdateScriptlet(this.scriptletsDirectory, repositories, product.buildEnv))

        job << new JobShellStepModel(bi)
        this.buildBase(job, this.swUpgrades)
        job.getChild(StandardJobDescriptionModel, false, false).with {
            add new DescriptionDisplayModel(this.product?.description?.description)
        }
        ResourcesApplier.apply(this.product.resources, job)
        RepositoryJobParametersApplier.applyRepositories(job, repositories)
        job << new JobParameterModel('external_build_number','','Build number of trigger job')

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
        preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, repositories))
        job << preScmWrapper

        job << new JobGitScmBranchBasedModel(repositories, false, false, true,
            RepositoryConfigurable.OPTIONAL)

        job << new JobCompilerWarningsModel('.*3pp.*')

        if (this.coverage) {
            job << new JobCoberturaCoverageModel("**/${this.product.makeRoot.name}/build/${this.product.name}/${this.buildType.name}/unittest/**/*.coverage.xml")
        }

        job << new JobArtifactModel('result/**/*', true)

        if (this.unittest) {
            job << new JobJUnitTestReportModel("${this.product.makeRoot.name}/build/${this.product.name}/${this.buildType.name}/unittest/**/*.output.xml")
        }

        job << new JobCsvDataPlotModel(this.product.csvDataPlots)

        PublishOverSSHApplier publishOverSSHApplier = new PublishOverSSHApplier(
            this.scriptletsDirectory, this.product, this.jobType, this.buildType)
        publishOverSSHApplier.applyProductVariant(job)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.SLOW_FEEDBACK,
                                             this.watchers,
                                             this.product.pm, this.product.techLead)
        job << new JobPostBuildWorkspaceCleanupModel()
        return job
    }
}
