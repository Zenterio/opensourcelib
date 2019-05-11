package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeIncrementalTestBuild
import com.zenterio.jenkins.jobtype.JobTypeTestBuild
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobModel

class JobFactory {

    private String scriptletsDirectory
    private JenkinsUrl url
    private JobName jobName
    private DisplayName displayName
    private JenkinsUrl incUrl
    private JobName incJobName
    private DisplayName incDisplayName

    public JobFactory(String scriptletsDirectory,
        JenkinsUrl url, JobName jobName, DisplayName displayName,
        JenkinsUrl incUrl, JobName incJobName, DisplayName incDisplayName) {
        super()
        this.scriptletsDirectory = scriptletsDirectory
        this.url = url
        this.jobName = jobName
        this.displayName = displayName
        this.incUrl = incUrl
        this.incJobName = incJobName
        this.incDisplayName = incDisplayName
    }

    public IModel getOriginFlow(Origin origin) {
        return (new OriginFlowJobBuilder(origin,
            this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getProdFlow(Product product) {
        return (new ProductFlowJobBuilder(product,
            this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getCompile(ProductVariant product, boolean unittest, boolean coverage) {
        return (new CompilationJobBuilder(product,
                this.scriptletsDirectory, this.url, this.jobName, this.displayName,
                product.watchers, product.swUpgrades, unittest, coverage)).build()
    }

    public IModel getTag(Project project) {
        return (new TagJobBuilder(project,
            this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getPromotion(Project project) {
        return (new PromoteBuildChainJobBuilder(project,
                this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getAnnotation(Project project) {
        return (new AnnotateBuildChainJobBuilder(project,
                this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getCollectArtifacts(Project project) {
        return (new CollectArtifactsJobBuilder(project, this.scriptletsDirectory,
                this.url, this.jobName, this.displayName)).build()
    }

    public IModel getFlash(Project project) {
        return (new FlashJobBuilder(project, this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getCoverity(Product product, BuildType buildType, JobModel parentJob) {
        return (new CoverityJobBuilder(product, buildType,
            this.scriptletsDirectory, this.url, this.jobName, this.displayName, parentJob)).build()
    }

    public IModel getDocumentation(Product product, BuildType buildType) {
        return (new DocumentationJobBuilder(product, buildType,
            this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getUnitTest(UnitTest unitTest, BuildType buildType) {
        return (new UnitTestJobBuilder(unitTest, buildType,
            this.scriptletsDirectory, this.url, this.jobName, this.displayName)).build()
    }

    public IModel getTest(ProductVariant product, TestContext testContext,
            JobTypeTestBuild jobType, JobModel parentJob) {
        return (new TestJobBuilder(product, testContext,
                this.scriptletsDirectory, this.url, this.jobName, this.displayName,
                testContext.buildTimeout, jobType, parentJob)).build()
    }

    public IModel getTest(ProductVariant product, TestContext testContext,
            JobTypeIncrementalTestBuild jobType, JobModel parentJob) {
        return (new IncrementalTestJobBuilder(product, testContext,
                this.scriptletsDirectory, this.url, this.jobName, this.displayName,
                testContext.buildTimeout, jobType, parentJob)).build()
    }

    public IModel getReleasePackaging(Origin origin, ReleasePackaging releasePackaging) {
        return (new ReleasePackagingJobBuilder(origin,
                this.scriptletsDirectory, this.url, this.jobName, this.displayName, releasePackaging)).build()
    }

    // -- Section incremental

    public IModel getIncOriginFlow(Origin origin) {
        return (new IncrementalOriginFlowJobBuilder(origin,
            this.scriptletsDirectory, this.incUrl,
            this.incJobName, this.incDisplayName)).build()
    }

    public IModel getIncProdFlow(Product product) {
        return (new IncrementalProductFlowJobBuilder(product,
            this.scriptletsDirectory, this.incUrl,
            this.incJobName, this.incDisplayName)).build()
    }

    public IModel getIncCompile(ProductVariant product, boolean unittest) {
        return (new IncrementalCompilationJobBuilder(product,
            this.scriptletsDirectory, this.incUrl,
            this.incJobName, this.incDisplayName, product.watchers, unittest)).build()
    }

    public IModel getIncUnitTest(UnitTest unitTest, BuildType buildType) {
        return (new IncrementalUnitTestJobBuilder(unitTest, buildType,
            this.scriptletsDirectory, this.url, this.incJobName, this.incDisplayName)).build()
    }

    // --

}
