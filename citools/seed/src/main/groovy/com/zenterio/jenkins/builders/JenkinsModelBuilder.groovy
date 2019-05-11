package com.zenterio.jenkins.builders

import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.builders.job.*
import com.zenterio.jenkins.builders.view.*
import com.zenterio.jenkins.buildtype.*
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.*
import com.zenterio.jenkins.models.*
import com.zenterio.jenkins.models.common.*
import com.zenterio.jenkins.models.job.JobBuildFlowJoinModel
import com.zenterio.jenkins.models.job.JobModel
import com.zenterio.jenkins.models.job.JobNameModel

import groovy.util.logging.*

/**
 * The Jenkins Model Builder creates a full model tree based on the
 * projects configuration passed to it.
 */
@Log
class JenkinsModelBuilder implements IModelBuilder {

    private Project[] projects
    private String scriptletsDirectory
    private JobName jobName
    private DisplayName displayName
    private JenkinsUrl jenkinsUrl
    private JobFactory jobFactory
    private ViewFactory viewFactory

    public JenkinsModelBuilder(Project[] projects, String scriptletsDirectory) {
        this.projects = projects
        JobTypeIncrementalCompile inc = new JobTypeIncrementalCompile()
        this.jobFactory = new JobFactory(scriptletsDirectory,
            new JenkinsUrl(), new JobName(), new DisplayName(),
            new JenkinsUrl(inc.shortName),
            new JobName(inc.shortName), new DisplayName(inc.name)
            )
        this.viewFactory = new ViewFactory(scriptletsDirectory,
            new JenkinsUrl(), new JobName(),
            new JenkinsUrl(inc.shortName), new JobName(inc.shortName))
    }

    /**
     * Create a model for all projects.
     * @return root model for all projects
     */
    public IModel build() {
        RootModel root = new RootModel()
        this.projects.each { proj ->
            root << this.buildProject(proj)
        }
        this.viewFactory.getOwnerGroupViews().each { name, view ->
            root << view.build()
        }
        root << this.viewFactory.getOwnerlessView().build()

        return root
    }

    /**
     * Create a model for a project
     * @param project
     * @return a new model for this project
     */
    private IModel buildProject(Project project) {
        ProjectModel projectModel = new ProjectModel()
        projectModel << this.viewFactory.getProjView(project).with({
            add this.jobFactory.getTag(project)
            add this.jobFactory.getPromotion(project)
            add this.jobFactory.getAnnotation(project)
            add this.jobFactory.getCollectArtifacts(project)
            add this.jobFactory.getFlash(project)
            bindOrigins(it, project.origins)
            bindIncOrigins(it, project.origins)
        })
        return projectModel
    }

    /**
     * Bind the origins to a project view
     * @param projectView
     * @param origins
     * @return the project view
     */
    private IModel bindOrigins(IModel projectView, Origin[] origins) {
        origins.each { origin ->
            IModel originModel = this.jobFactory.getOriginFlow(origin)
            origin.products.each { Product product ->
                originModel << this.bindProduct(product)
            }
            if (origin.releasePackaging.enabled) {
                originModel << this.jobFactory.getReleasePackaging(origin, origin.releasePackaging)
            }
            projectView.add(originModel)
        }
        return projectView
    }

    /**
     * Bind the incremental origins to a project view
     * @param projectView
     * @param origins
     * @return the project view
     */
    private IModel bindIncOrigins(IModel projectView, Origin[] origins) {
        origins.each { origin ->
            if (origin.isIncrementalActive()) {
                IModel incOriginModel = this.jobFactory.getIncOriginFlow(origin)
                origin.products.each { Product product ->
                    if (product.isIncrementalActive()) {
                        incOriginModel <<  this.bindIncProduct(product)
                    }
                }
                projectView.add(incOriginModel)
            }
        }
        return projectView
    }

    /**
     * Create a product flow model for a product.
     * @param product
     * @return a new product flow model
     */
    private IModel bindProduct(Product product) {
        IModel productFlowModel = this.jobFactory.getProdFlow(product)
        IModel ut = null
        IModel dbg = null
        IModel dbgTest = null
        IModel rls = null
        IModel prd = null
        IModel cov = null
        IModel doc = null
        boolean unittest = (product.unitTest.enabled && product.unitTest.builtIn)
        boolean coverage = true

        ut = this.bindUnitTest(product.unitTest, new BuildTypeDebug())

        unittest = coverage = (unittest && (ut == null))
        dbg = this.bindCompile(product.debug, unittest, coverage, false)

        unittest = coverage = (unittest && (dbg == null))
        rls = this.bindCompile(product.release, unittest, coverage, true)

        unittest = coverage = (unittest && (rls == null))
        prd = this.bindCompile(product.production, unittest, coverage, true)

        cov = this.bindCoverity(product, dbg)

        doc = this.bindDocumentation(product)

        IModel[] childJobs = this.getTestJobs(product.debug, product.debug.testGroups, new JobTypeTestBuild(), dbg) +
            [rls, prd, cov, doc]
        this.addJobsToFlowModel(product.buildFlow, productFlowModel, ut, dbg, childJobs)

        return productFlowModel
    }

    /**
     * Create a coverity model if both coverity and debug are enabled
     * @param product
     * @return new coverity IModel or null
     */
    private IModel bindCoverity(Product product, JobModel parentJob) {
        IModel coverity = null
        if (product.coverity?.enabled &&
            product.debug?.enabled) {
            coverity = this.jobFactory.getCoverity(product, product.coverity.buildType, parentJob)
        }
        return coverity
    }

    /**
     * Create a documentation model if both documentation and debug are enabled
     * @param product
     * @return new documentation IModel or null
     */
    private IModel bindDocumentation(Product product) {
        IModel doc = null
        if (product.doc?.enabled && product.debug?.enabled) {
            doc = this.jobFactory.getDocumentation(product, new BuildTypeDebug())
        }
        return doc
    }

    /**
     * Bind incremental build for a product
     * @param product
     * @return the incremental product flow job model
     */
    private IModel bindIncProduct(Product product) {
        IModel incProductFlowModel = this.jobFactory.getIncProdFlow(product)
        IModel ut = null
        IModel dbg = null
        IModel prd = null
        boolean unittest = (product.unitTest.enabled && product.unitTest.builtIn)

        ut = this.bindIncUnitTest(product.unitTest, new BuildTypeDebug())

        unittest = (unittest && (ut == null))
        dbg = this.bindIncCompile(product.debug, unittest, false)

        unittest = (unittest && (dbg == null))
        prd = this.bindIncCompile(product.production, unittest, true)

        IModel[] childJobs = this.getTestJobs(product.debug,
            product.debug.incremental.testGroups, new JobTypeIncrementalTestBuild(), dbg) + [prd]
        this.addJobsToFlowModel(product.incBuildFlow, incProductFlowModel, ut, dbg, childJobs)

        return incProductFlowModel
    }

    /**
     * Bind a unit test job and return it. Returns null if unit test job is not applicable.
     * @param unitTest
     * @param bt
     * @return Unit Test job model
     */
    private IModel bindUnitTest(UnitTest unitTest, BuildType bt) {
        IModel ut = null
        if (unitTest.enabled && !unitTest.builtIn) {
            ut = this.jobFactory.getUnitTest(unitTest, bt)
        }
        return ut
    }

    /**
     * Bind a compile job and relevant feature jobs for a product variant.
     * @param prodVariant   Product variant configuration object
     * @param unittest      True if unit tests should be run and result collected
     * @param coverage      True if code coverage should be generated and coverage
     *                      report published
     * @param inlcudeTest   True if test jobs should be bound to the compile
     *                      job model.
     */
    private IModel bindCompile(ProductVariant prodVariant, boolean unittest, boolean coverage, boolean includeTest) {
        IModel comp = null
        if (prodVariant?.enabled) {
            comp = this.jobFactory.getCompile(prodVariant, unittest, coverage)
            if (includeTest) {
                this.bindTestGroupToCompile(prodVariant, prodVariant.testGroups,
                    comp, new JobTypeTestBuild())
            }
        }
        return comp
    }

    /**
     * Bind test jobs to compile
     * @param prodVariant Product variant configuration object
     * @param bt Build type
     * @param comp
     */
    private void bindTestGroupToCompile(ProductVariant prodVariant, TestGroup[] testGroups,
            IModel comp, JobType jobType) {
        if (comp == null) {
            return
        }
        this.getTestJobs(prodVariant, testGroups, jobType, comp).each { IModel testJob ->
            comp << testJob
        }
    }

    /**
     * Bind an incremental compile job and relevant feature jobs for a product variant.
     * @param prodVariant Product variant configuration object
     * @param unittest True if unit tests should be run and result collected
     * @return IModel representation of the compilation job with features enabled.
     */
    private IModel bindIncCompile(ProductVariant prodVariant, boolean unittest, boolean includeTest) {
        IModel comp = null
        if (prodVariant?.isIncrementalActive()) {
            comp = this.jobFactory.getIncCompile(prodVariant, unittest)
            if (includeTest) {
                this.bindTestGroupToCompile(prodVariant, prodVariant.incremental.testGroups,
                    comp, new JobTypeIncrementalTestBuild())
            }
        }
        return comp
    }

    /**
     * Bind an incremental unit test job and return it. Returns null if unit test job is not applicable.
     * @param unitTest
     * @param bt
     * @return Unit Test job model
     */
    private IModel bindIncUnitTest(UnitTest unitTest, BuildType bt) {
        IModel ut = null
        if (unitTest.enabled && !unitTest.builtIn) {
            ut = this.jobFactory.getIncUnitTest(unitTest, bt)
        }
        return ut
    }


    /**
     * Create and return test jobs for the provided product variant and the specified test group.
     * @param prodVariant
     * @param testGroups
     * @param jobType
     * @return
     */
    private List<IModel> getTestJobs(ProductVariant prodVariant, TestGroup[] testGroups,
            JobType jobType, JobModel parentJob) {
        List<IModel> result = new ArrayList<IModel>()
        testGroups.each { TestGroup testGroup ->
            if (testGroup.enabled) {
                testGroup.testContexts.each { TestContext testContext ->
                    if (testContext.enabled) {
                        IModel testJob = this.jobFactory.getTest(prodVariant, testContext, jobType, parentJob)
                        result.add(testJob)
                        String jobName = testJob.getChild(JobNameModel).name
                        if (!testContext.owners) {
                            this.viewFactory.makeOwnerlessView(jobName)
                        } else {
                            testContext.owners.each { owner ->
                                this.viewFactory.makeOwnerGroupView(owner, jobName)
                            }
                        }
                    }
                }
            }
        }
        return result
    }


    /**
     * Add jobs to a product flow model.
     * If there is a debug build, the other jobs should be added to that instead of the product flow.
     * @param parentJob
     * @param unittest
     * @param debug
     * @param childJobs
     */
    static private void addJobsToFlowModel(BuildFlow flow, IModel parentFlow, IModel unittest, IModel debug, IModel[] childJobs) {
        switch(flow.style) {
            case BuildFlowStyle.ZIDS_UNIT_TEST_SERIAL:
                zidsUnitTestSerial(parentFlow, unittest, debug, childJobs)
                break
             case BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL:
                 zidsUnitTestParallel(parentFlow, unittest, debug, childJobs)
                 break
             default:
                 throw new Exception("Unknown BuildFlowStyle (style=${flow.style})")
        }
    }

    static private void zidsUnitTestParallel(IModel parentFlow, IModel unittest, IModel debug, IModel[] childJobs) {
        IModel parentJob = parentFlow
        parentJob << unittest
        parentJob << debug
        if (unittest && debug) {
            IModel join = new JobBuildFlowJoinModel()
            join.join(unittest, debug)
            parentJob = join
        } else if (unittest) {
            parentJob = unittest
        } else if (debug) {
            parentJob = debug
        }
        childJobs.each { IModel job ->
            parentJob << job
        }
    }

    static private void zidsUnitTestSerial(IModel parentFlow, IModel unittest, IModel debug, IModel[] childJobs) {
        IModel parentJob = parentFlow
        if (unittest) {
            parentJob << unittest
            parentJob = unittest
        }
        if (debug) {
            parentJob << debug
            parentJob = debug
        }
        childJobs.each { IModel job ->
            parentJob << job
        }
    }

}
