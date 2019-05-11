package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.*
import com.zenterio.jenkins.appliers.PublishOverSSHApplier
import com.zenterio.jenkins.appliers.RepositoryJobParametersApplier
import com.zenterio.jenkins.appliers.ResourcesApplier
import com.zenterio.jenkins.buildstep.BuildInfoBuildStepScriptlet
import com.zenterio.jenkins.buildstep.BuildStepFactory
import com.zenterio.jenkins.buildstep.DocumentationBuildStepScriptlet
import com.zenterio.jenkins.buildstep.GitIndexUpdateScriptlet
import com.zenterio.jenkins.buildstep.RepositoryJobParametersCheckScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeDocumentation
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.*
import com.zenterio.jenkins.scriptlet.*

/**
 * Assembles the model for a Documentation job.
 */
class DocumentationJobBuilder  extends BaseCompilationJobBuilder {

    private Doc doc = null

    public DocumentationJobBuilder(Product product,
                                   BuildType buildType, String scriptletsDirectory,
                                   JenkinsUrl url, JobName jobName, DisplayName displayName) {
        super(product,
                new JobTypeDocumentation(),
                buildType,
                scriptletsDirectory,
                url,
                jobName,
                displayName,
                null,
                new BuildStepFactory(scriptletsDirectory, product.variables,
                        { IScriptlet template, int swUpgradeOffset ->
                            new DocumentationBuildStepScriptlet(
                                    template,
                                    buildType,
                                    product, swUpgradeOffset)
                        }),
                ['abs-doc'],
                product.cache.createDisabled(),
                product.concurrentBuilds,
                product.doc.credentials,
                product.doc.customBuildSteps,
                product.retentionPolicy,
                product.startedBy,
                product.buildNodes,
                product.doc.buildTimeout,
                product.workspaceBrowsing,
                product.priority)
        this.doc = product.doc
    }

    public IModel build() {
        IModel job = new DocJobModel()
        job << new JobPreBuildWorkspaceCleanupModel()
        BuildInfoBuildStepScriptlet bi =
                new BuildInfoBuildStepScriptlet("${this.scriptletsDirectory}/buildsteps",
                        this.product.name,
                        this.product.origin.name,
                        this.product.repositories)
        job << new JobShellStepModel(new GitIndexUpdateScriptlet(this.scriptletsDirectory, this.product.origin.repositories, doc.buildEnv))
        job << new JobShellStepModel(bi)
        this.buildBase(job)
        ResourcesApplier.apply(this.doc.resources, job)
        RepositoryJobParametersApplier.applyRepositories(job, this.product.origin.repositories)
        job << new JobParameterModel('external_build_number','','Build number of trigger job')

        IModel preScmWrapper = new JobPreScmBuildStepWrapperModel(true)
        preScmWrapper << new JobPreScmShellStepModel(new RepositoryJobParametersCheckScriptlet(this.scriptletsDirectory, this.product.origin.repositories))
        job << preScmWrapper


        job << new JobGitScmBranchBasedModel(this.product.repositories,
            false, false, true, RepositoryConfigurable.OPTIONAL)
        job << new JobArtifactModel('result/**/*', false)

        PublishOverSSHApplier publishOverSSHApplier = new PublishOverSSHApplier(
            this.scriptletsDirectory, null, this.jobType, this.buildType)
        publishOverSSHApplier.apply(doc, job)

        job << new JobPostBuildWorkspaceCleanupModel()
        return job
    }
}
