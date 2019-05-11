package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.Repository


class JobGitScmBranchBasedModel extends JobGitScmModel {

    final Boolean createBuildTag
    final Boolean useParameters
    final RepositoryConfigurable repoConfigurable

    /**
     * Used to add GIT configuration to the Jenkins job
     * @param repositories          List of the repositories to use
     * @param createBuildTag        Used to create a tag for this build
     * @param acceptNotifyCommit    Configures the job to be triggered by notifyCommit
     * @param useParameters         Creates job parameters for each repository making it
     *                              possible to trigger the job on different branches, or
     *                              for specific commits.
     * @param forceConfigurable     If null, repository settings are respected,
     *                              otherwise use this value for all repositories.

     */
    public JobGitScmBranchBasedModel(Repository[] repositories,
            Boolean createBuildTag,
            Boolean acceptNotifyCommit,
            Boolean useParameters,
            RepositoryConfigurable repoConfigurable) {
        super(repositories, acceptNotifyCommit)
        this.createBuildTag = createBuildTag
        this.useParameters = useParameters
        this.repoConfigurable = repoConfigurable
    }

}
