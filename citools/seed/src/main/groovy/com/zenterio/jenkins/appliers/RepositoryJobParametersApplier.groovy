package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.configuration.TestRepositoryInfo
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobParameterModel
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslParameterFromVariableModel

class RepositoryJobParametersApplier {

    /**
     * Applies the repositories as job parameters and to generate the call parameters
     * in the triggering flow
     * @param job the job
     * @param repositories repositories array
     */
    public static void applyRepositories(IModel job, Repository[] repositories) {
        repositories.each({ Repository repo ->
            applyRepositoryParameter(job, repo.envName, repo.envName, repo.branch, repo.name)
        })
    }

    /**
     * When the test jobs are upstream trigger they need to tell the product flow how to
     * map from the <repo>_<testgroup> variable name in the flow to the <repo> parameter
     * in the test job.
     * @param job the test job
     * @param repositories list of TestRepositoryInfo
     */
    public static void applyRepositoriesForTestsWithUpstream(IModel job, TestRepositoryInfo[] repositories) {
        repositories.each({ TestRepositoryInfo repoInfo ->
            def repo = repoInfo.repository
            applyRepositoryParameter(job, repo.envName, repoInfo.paramName, repo.branch, repo.name)
        })
    }

    private static void applyRepositoryParameter(IModel job, String name, String value, String branch, String repoName) {
        job << new JobParameterModel(name,
                "refs/heads/${branch}",
                "Do NOT leave blank! Revision to build from for ${repoName} repository. Format: refs/heads/BRANCH, refs/tags/TAG, SHA")
        job << new JobBuildFlowDslParameterFromVariableModel(name, value)
    }
}
