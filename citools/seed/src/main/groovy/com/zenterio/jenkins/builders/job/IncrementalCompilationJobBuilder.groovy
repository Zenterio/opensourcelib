package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.IncrementalCompileBuildStepScriptlet
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.buildstep.StoreAuthorsScriptlet
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeIncrementalCompile
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.display.DescriptionDisplayModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.scriptlet.*

/**
 * Assembles the model for a Compilation job.
 */
class IncrementalCompilationJobBuilder extends BaseCompilationJobBuilder {

    /**
     * @param product The product to compile
     * @param scriptletsDirectory
     * @param url Jenkins URL factory
     * @param jobName Job name factory
     * @param displayName Job display name factory
     * @param watchers
     * @param unittest True if unit tests should be run and result collected
     */
    public IncrementalCompilationJobBuilder(ProductVariant product,
                                            String scriptletsDirectory,
                                            JenkinsUrl url, JobName jobName, DisplayName displayName,
                                            ContactInformationCollection watchers,
                                            boolean unittest) {
        super(product,
                new JobTypeIncrementalCompile(),
                product.buildType,
                scriptletsDirectory,
                url,
                jobName,
                displayName,
                watchers,
                new BuildStepFactory(scriptletsDirectory, product.variables,
                        { IScriptlet template, int swUpgradeOffset ->
                            new IncrementalCompileBuildStepScriptlet(
                                    template,
                                    new JobTypeIncrementalCompile(),
                                    product.buildType,
                                    product,
                                    swUpgradeOffset,
                                    product.incremental.cache,
                                    unittest)
                        }),
                ['zformat', 'abs-target', 'abs-artifacts', 'stb-portal-add-software'],
                product.incremental.cache,
                new ConcurrentBuilds(false),
                product.credentials,
                product.customBuildSteps,
                RetentionPolicyFactory.createIncrementalPolicy(),
                product.startedBy,
                product.incremental.buildNodes,
                product.buildTimeout,
                product.workspaceBrowsing,
                product.priority)
    }

    public IModel build() {
        IModel job = new CompileJobModel()

        job << new JobDefaultLoadBalancingModel()
        ResourcesApplier.apply(this.product.incremental.resources, job)

        Repository[] repositories = this.product.origin.repositories

        RepositoryJobParametersApplier.applyRepositories(job, repositories)

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
        preScmWrapper << new JobPreScmShellStepModel(new FileScriptlet("${this.scriptletsDirectory}/buildsteps/clear-incremental-workspace"))
        preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, repositories))
        job << preScmWrapper

        job << new JobShellStepModel(
                new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps",
                        this.product.name,
                        this.product.origin.name,
                        this.product.repositories))

        this.buildBase(job)

        job << new JobShellStepModel(
                new StoreAuthorsScriptlet("${this.scriptletsDirectory}/buildsteps",
                        product.name,
                        0,
                        this.product.repositories
                ))
        job.getChild(StandardJobDescriptionModel, false, false).with {
            add new DescriptionDisplayModel(this.product?.description?.description)
        }

        job << new JobGitScmBranchBasedModel(repositories,
            false, false, true, RepositoryConfigurable.FORCE_FALSE)

        job << new JobArtifactModel('result/**/*', true)

        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.FAST_FEEDBACK_ROOT_CAUSE,
                this.watchers, this.product.pm, this.product.techLead)

        return job
    }
}
