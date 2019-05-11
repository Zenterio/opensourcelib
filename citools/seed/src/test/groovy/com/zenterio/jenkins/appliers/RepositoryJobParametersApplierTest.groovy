package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.configuration.TestRepositoryInfo
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.job.JobParameterModel
import com.zenterio.jenkins.models.job.flowdsl.JobBuildFlowDslParameterModel


class RepositoryJobParametersApplierTest extends GroovyTestCase
{

    void testApplyRepositoriesAddsJobParameterModels() {
        IModel job = new ModelEntity()
        def repositories = [
                new Repository("name1", "dir1", "remote1", "branch1", false),
                new Repository("name2", "dir2", "remote2", "branch2", false),
        ] as Repository[]

        RepositoryJobParametersApplier.applyRepositories(job, repositories)
        def models = job.getProperties(JobParameterModel, false)
        assert models[0].name == "NAME1"
        assert models[0].defaultValue == "refs/heads/branch1"
        assert models[1].name == "NAME2"
        assert models[1].defaultValue == "refs/heads/branch2"
    }

    void testApplyRepositoriesAddsJobBuildFlowDslParameterModels() {
        IModel job = new ModelEntity()
        def repositories = [
                new Repository("name1", "dir1", "remote1", "branch1", false),
                new Repository("name2", "dir2", "remote2", "branch2", false),
        ] as Repository[]

        RepositoryJobParametersApplier.applyRepositories(job, repositories)
        def models = job.getProperties(JobBuildFlowDslParameterModel, false)
        assert models[0].parameterName == "NAME1"
        assert models[0].parameterValue == "NAME1"
        assert models[1].parameterName == "NAME2"
        assert job.getProperties(JobBuildFlowDslParameterModel, false)[1].parameterValue == "NAME2"
    }

    void testApplyTestJobRepositoriesAddsJobParameterModels() {
        IModel job = new ModelEntity()
        def repositories = [
                new TestRepositoryInfo("tgname1", new Repository("name1", "dir1", "remote1", "branch1", false)),
                new TestRepositoryInfo("tgname2", new Repository("name2", "dir2", "remote2", "branch2", false)),
        ] as TestRepositoryInfo[]

        RepositoryJobParametersApplier.applyRepositoriesForTestsWithUpstream(job, repositories)
        def models = job.getProperties(JobParameterModel, false)
        assert models[0].name == "NAME1"
        assert models[0].defaultValue == "refs/heads/branch1"
        assert models[1].name == "NAME2"
        assert models[1].defaultValue == "refs/heads/branch2"
    }

    void testApplyTestJobRepositoriesAddsJobBuildFlowDslParameterModels() {
        IModel job = new ModelEntity()
        def repositories = [
                new TestRepositoryInfo("tgname1", new Repository("name1", "dir1", "remote1", "branch1", false)),
                new TestRepositoryInfo("tgname2", new Repository("name2", "dir2", "remote2", "branch2", false)),
        ] as TestRepositoryInfo[]

        RepositoryJobParametersApplier.applyRepositoriesForTestsWithUpstream(job, repositories)
        def models = job.getProperties(JobBuildFlowDslParameterModel, false)
        assert models[0].parameterName == "NAME1"
        assert models[0].parameterValue == "NAME1_TGNAME1"
        assert models[1].parameterName == "NAME2"
        assert models[1].parameterValue == "NAME2_TGNAME2"
    }
}
