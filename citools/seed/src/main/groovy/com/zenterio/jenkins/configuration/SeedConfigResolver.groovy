package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.RetentionPolicy
import com.zenterio.jenkins.RetentionPolicyFactory
import com.zenterio.jenkins.RetentionPolicyType
import com.zenterio.jenkins.buildtype.BuildTypeDebug
import com.zenterio.jenkins.buildtype.BuildTypeProduction
import com.zenterio.jenkins.buildtype.BuildTypeRelease
import com.zenterio.jenkins.configuration.macroexpansion.ObjectVisitor
import com.zenterio.jenkins.configuration.macroexpansion.SeedContextTransform

import groovy.util.logging.*
import java.util.concurrent.CountDownLatch

@Log
class SeedConfigResolver implements IConfigResolver {

    public static final BuildFlow DEFAULT_BUILD_FLOW = new BuildFlow(BuildFlowStyle.ZIDS_UNIT_TEST_SERIAL)
    public static final BuildFlow DEFAULT_INC_BUILD_FLOW = new BuildFlow(BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL)
    public static final BuildTimeout DEFAULT_COMPILATION_TIMEOUT = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 4*60, false, false)
    public static final BuildTimeout DEFAULT_TEST_TIMEOUT = new BuildTimeout(null, null, null, null, false)
    public static final BuildTimeout DEFAULT_COVERITY_TIMEOUT = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 8*60, false, false)
    public static final BuildTimeout DEFAULT_DOCUMENTATION_TIMEOUT = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 1*60, false, false)
    public static final BuildTimeout DEFAULT_RELEASE_PACKAGING_TIMEOUT = new BuildTimeout(BuildTimeoutPolicy.ELASTIC, 180, false, false)
    public static final BuildTimeout DEFAULT_UNIT_TEST_TIMEOUT = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 2*60, false, false)

    public static final RetentionPolicy DEFAULT_COMPILATION_RETENTION_POLICY = RetentionPolicyFactory.create(RetentionPolicyType.SHORT, true)
    public static final RetentionPolicy DEFAULT_TEST_RETENTION_POLICY = RetentionPolicyFactory.create(RetentionPolicyType.LONG, true)

    public static final MakePrefix DEFAULT_MAKE_PREFIX = new MakePrefix('')
    public static final MakeRoot DEFAULT_MAKE_ROOT = new MakeRoot('zids')
    public static final MakeTarget DEFAULT_COMPILATION_MAKE_TARGET = new MakeTarget('bootimage')
    public static final MakeTarget DEFAULT_DOC_MAKE_TARGET = new MakeTarget('doc')

    public static final DEFAULT_CCACHE_STORAGE = '${PRODUCT}/${BUILD_TYPE}'
    public static final Cache DEFAULT_CACHE = new Cache(false, false, CcacheSize.MEDIUM, DEFAULT_CCACHE_STORAGE, false, false)
    public static final ConcurrentBuilds DEFAULT_CONCURRENT_BUILDS = new ConcurrentBuilds(false)
    public static final Resources DEFAULT_RESOURCES = new Resources(false, null, null, 0)

    public static final TestReport DEFAULT_KAZAM_TEST_REPORT = new TestReport(TestReportType.JUNIT)
    public static final TestReport DEFAULT_K2_TEST_REPORT = new TestReport(TestReportType.TESTNG)

    public static final UnitTest DEFAULT_UNIT_TEST = new UnitTest(true, true)
    public static final MakeTarget DEFAULT_UNIT_TEST_MAKE_TARGET = new MakeTarget('unittest')

    public static final String DEFAULT_BOX_CONFIGURATION = '${STB_ID}'
    public static final String DEFAULT_PRODUCT_CONFIGURATION = ''

    public static final String DEFAULT_BUILD_ENV_ENV = null
    public static final BuildEnv DEFAULT_BUILD_ENV = new BuildEnv(true, DEFAULT_BUILD_ENV_ENV, null)

    public SeedConfigResolver() {

    }

    @Override
    public void resolve(Project[] projects) {
        CountDownLatch latch = new CountDownLatch(projects.size())
        projects.each { Project project ->
            new Thread(new Runnable() {
                @Override
                public void run() {
                    resolveProject(project)
                    latch.countDown()
                }
            }).start()
        }
        latch.await()
    }

    private void resolveProject(Project project) {
        log.finer("Set missing tags: " + project.name)
        this.setMissingTags(project)
        log.finer("Inherit tags: " + project.name)
        this.inheritTags(project)
        log.finer("Set default attributes: " + project.name)
        this.setDefaultAttributes(project)
        log.finer("Macro context expansion: " + project.name)
        this.macroContextExpansion(project)
        log.finer("Resolve done: " + project.name)
    }

    /**
     * Set missing tags on the first level where they may occur.
     *
     * @param project
     */
    private void setMissingTags(Project project) {
        setIfNull(project, "buildEnv", DEFAULT_BUILD_ENV)
        setIfNull(project, "buildFlow", DEFAULT_BUILD_FLOW)
        setIfNull(project, "incBuildFlow", DEFAULT_INC_BUILD_FLOW)
        setIfNull(project, "coverity", new Coverity("", false, Upstream.FALSE, "", Aggressiveness.LOW, new BuildTypeDebug()))
        setIfNull(project, "incremental", new Incremental(true))
        setIfNull(project, "doc", new Doc(false))
        setIfNull(project, "releasePackaging", new ReleasePackaging(true))
        setIfNull(project, "cache", DEFAULT_CACHE.clone())
        setIfNull(project, "concurrentBuilds", DEFAULT_CONCURRENT_BUILDS)
        setIfNull(project, "logParsing", new LogParsing("/etc/zenterio-zloganalyzer/config/jenkins_compile_config.yaml", true))
        setIfNull(project, "makePrefix", DEFAULT_MAKE_PREFIX)
        setIfNull(project, "makeRoot", DEFAULT_MAKE_ROOT)
        setIfNull(project, "makeTarget", DEFAULT_COMPILATION_MAKE_TARGET)
        setIfNull(project, "trigger", new Trigger(null, "", false, false))
        setIfNull(project, "buildTimeout", DEFAULT_COMPILATION_TIMEOUT)
        setIfNull(project, "resources", DEFAULT_RESOURCES)
        setIfNull(project, "retentionPolicy", DEFAULT_COMPILATION_RETENTION_POLICY)
        setIfNull(project, "startedBy", new StartedBy(false))
        setIfNull(project, "unitTest", DEFAULT_UNIT_TEST)

        // inc-trigger is not possible to set via config file but should
        // always be on.
        setIfNull(project, "incTrigger", new Trigger(null, null, true, true))

        setMissingEmailPolicy(project)
        setMissingDescription(project)

        setIfNull(project, "workspaceBrowsing", new WorkspaceBrowsing(true))
        setIfNull(project, "debug", new ProductVariant(new BuildTypeDebug()))
        setIfNull(project, "release", new ProductVariant(new BuildTypeRelease()))
        setIfNull(project, "production", new ProductVariant(new BuildTypeProduction()))

        setMissingProductVariantsSubTags(project)

        project.origins.each { Origin origin ->
            setMissingDescription(origin)
            setMissingEmailPolicy(origin)
            setMissingProductVariantsSubTags(origin)
            setIfNull(origin, 'priority', Priority.MEDIUM)

            origin.products.each { Product product ->
                setMissingDescription(product)
                setMissingEmailPolicy(product)

                setMissingEmailPolicy(product.unitTest)
                setMissingDescription(product.unitTest)

                setMissingProductVariantsSubTags(product)
            }
        }
    }

    /**
     * Set missing tags for Product variants and all their sub-tags
     */
    private void setMissingProductVariantsSubTags(IProductVariantHolder holder) {
        [holder.debug,
            holder.release,
            holder.production].grep({it}).each { ProductVariant prodVariant ->
               setMissingEmailPolicy(prodVariant)
               setMissingDescription(prodVariant)

               removeAllNull([prodVariant.testGroups, prodVariant.incremental?.testGroups]).flatten().each { TestGroup testGroup ->
                   setMissingEmailPolicy(testGroup)
                   setMissingDescription(testGroup)
                   setIfNull(testGroup, "image", new Image("", false, true))
                   setIfNull(testGroup, "logParsing", new LogParsing("/etc/zenterio-zloganalyzer/config/jenkins_test_config.yaml", true))
                   setIfNull(testGroup, "buildTimeout", DEFAULT_TEST_TIMEOUT)
                   setIfNull(testGroup, "resources", DEFAULT_RESOURCES)
                   setIfNull(testGroup, "retentionPolicy", DEFAULT_TEST_RETENTION_POLICY)
                   setIfNull(testGroup, "testReport", (testGroup.type == TestGroupType.KAZAM)?DEFAULT_KAZAM_TEST_REPORT:DEFAULT_K2_TEST_REPORT)
                   setIfNull(testGroup, "workspaceBrowsing", new WorkspaceBrowsing(true))
                   testGroup.testContexts.each { TestContext context ->
                       setMissingEmailPolicy(context)
                       setMissingDescription(context)
                   }
               }
           }
    }


    /**
     * Inherits appropriate tags project -> origin -> product -> product variant -> test group -> test context
     * for attributes not specified on lower levels.
     * @param project
     */
    private void inheritTags(Project project) {
        project.origins.each { Origin origin ->
            this.inheritProjectToOrigin(project, origin)
            this.inheritReleasePackaging(origin)

            origin.products.each { Product product ->
                this.inheritOriginToProduct(origin, product)

                this.inheritProductToDoc(product, product.doc)
                this.inheritProductToCoverity(product, product.coverity)
                this.inheritProductToUnitTest(product, product.unitTest)
                this.inheritPublishOverSSH(product.doc)
                this.inheritPublishOverSSH(product.coverity)
                this.inheritPublishOverSSH(product.unitTest)

                [product.debug,
                 product.release,
                 product.production].grep({it}).each({ ProductVariant prodVariant ->
                    this.inheritProductToVariant(product, prodVariant)
                    this.inheritPublishOverSSH(prodVariant)
                    [prodVariant.testGroups, prodVariant.incremental.testGroups].flatten().each { TestGroup testGroup ->
                        this.inheritVariantToTestGroup(prodVariant, testGroup)
                    }
                    this.inheritTestGroups(prodVariant)
                    this.inheritTestGroups(prodVariant.incremental)
                })
            }
        }
    }

    /**
     * Inherit project -> origin for attributes not specified in origin.
     * @param project source
     * @param origin destination
     */
    private void inheritProjectToOrigin(Project project, Origin origin) {
        this.inheritCommonAttributes(project, origin, true)

        setIfNull(origin, "buildFlow", project.buildFlow)
        setIfNull(origin, "coverity", project.coverity)
        setIfNull(origin, "doc", project.doc)
        setIfNull(origin, "incBuildFlow", project.incBuildFlow)
        setIfNull(origin, "trigger", project.trigger)
        setIfNull(origin, "incTrigger", project.incTrigger)
        setIfNull(origin, "releasePackaging", project.releasePackaging)

        origin.addWatchers(project.watchers)

        setIfNull(origin, "debug", project.debug)
        setIfNull(origin, "release", project.release)
        setIfNull(origin, "production", project.production)
        setIfNull(origin, "unitTest", project.unitTest)
    }

    /**
     * Inherit origin -> product for attributes not specified in product.
     * @param origin source
     * @param product destination
     */
    private void inheritOriginToProduct(Origin origin, Product product) {
        this.inheritCommonAttributes(origin, product)

        setIfNull(product, "buildFlow", origin.buildFlow)
        setIfNull(product, "coverity", origin.coverity)
        setIfNull(product, "doc", origin.doc)
        setIfNull(product, "incBuildFlow", origin.incBuildFlow)
        setIfEmpty(product, "repositories", origin.repositories)
        setIfNull(product, "debug", origin.debug)
        setIfNull(product, "release", origin.release)
        setIfNull(product, "production", origin.production)
        setIfNull(product, "unitTest", origin.unitTest)
        setIfNull(product, 'priority', origin.priority)

    }

    /**
     * Inherit product -> product variant for attributes not specified in the variant.
     * @param product source
     * @param variant destination
     */
    private void inheritProductToVariant(Product product, ProductVariant variant) {
        this.inheritCommonAttributes(product, variant)
        setIfEmpty(variant, "repositories", product.repositories)
    }

    private void inheritProductToDoc(Product product, Doc doc) {
        setIfNull(doc, "buildEnv", product.buildEnv)
        setIfNull(doc, "makePrefix", product.makePrefix)
        setIfNull(doc, "makeRoot", product.makeRoot)
        setIfNull(doc, 'priority', product.priority)
        // makeTarget should not be inherited
        doc.variables.inheritFrom(product.variables)
    }

    private void inheritProductToCoverity(Product product, Coverity cov) {
        cov.variables.inheritFrom(product.variables)
        setIfNull(cov, 'buildEnv', product.buildEnv)
        setIfNull(cov, 'priority', product.priority)
    }

    private void inheritProductToUnitTest(Product product, UnitTest ut) {
        setIfNull(ut, "makePrefix", product.makePrefix)
        setIfNull(ut, "makeRoot", product.makeRoot)
        // makeTarget should not be inherited
        ut.variables.inheritFrom(product.variables)
        // csv data plots should not be inherited
        setIfNull(ut, "buildEnv", product.buildEnv)
        setIfNull(ut, "cache", product.cache)
        setIfNull(ut, "concurrentBuilds", product.concurrentBuilds)
        setIfEmpty(ut, "credentials", product.credentials)
        setIfNull(ut, "logParsing", product.logParsing)
        setIfNull(ut, "pm" , product.pm)
        setIfNull(ut, "techLead", product.techLead)
        setIfEmpty(ut, "buildNodes", product.buildNodes)
        // build timeout should not be inherited
        setIfEmpty(ut, "repositories", product.repositories)
        setIfNull(ut, "resources", product.resources)
        setIfNull(ut, "retentionPolicy", product.retentionPolicy)
        setIfNull(ut, "startedBy", product.startedBy)
        setIfNull(ut, "workspaceBrowsing", product.workspaceBrowsing)
        setIfNull(ut, 'priority', product.priority)
    }

    /**
     * Inherit attributes that need to come specifically from product variant to
     * test group and not just from "parent".
     * @param variant source
     * @param testGroup destination
     */
    private void inheritVariantToTestGroup(ProductVariant variant, TestGroup group) {
        setIfNull(group, "pm", variant.pm)
        setIfNull(group, "techLead", variant.techLead)
        setIfNull(group, 'priority', variant.priority)
        setIfEmpty(group, "credentials", variant.credentials)
    }

    private void inheritTestGroups(ITester tester) {
        tester.testGroups.each { TestGroup testGroup ->
            testGroup.variables.inheritFrom(tester.variables)
            testGroup.testContexts.each {TestContext testContext ->
                this.inheritTestGroupToTestContext(testGroup, testContext)
                this.inheritPublishOverSSH(testContext)
            }
        }
    }

    private void inheritReleasePackaging(Origin origin) {
        origin.releasePackaging.variables.inheritFrom(origin.variables)
        setIfNull(origin.releasePackaging, "logParsing", origin.logParsing)
        this.inheritPublishOverSSH(origin.releasePackaging)
    }

    private void inheritPublishOverSSH(IPublisherOverSSH parent) {
        parent.publishOverSSHList.each { PublishOverSSH publish ->
            publish.variables.inheritFrom(parent.variables)
        }
    }


    /**
     * Inherit test group -> test context for attributes not specified in the test context.
     * @param testGroup source
     * @param testContext destination
     */
    private void inheritTestGroupToTestContext(TestGroup group, TestContext context) {
        setIfEmpty(context, "watchers", group.watchers)
        setIfEmpty(context, "credentials", group.credentials)
        setIfNull(context, "coredumpHandling", group.coredumpHandling)
        setIfEmpty(context, "epgs", group.epgs)
        setIfNull(context, "image", group.image)
        setIfEmpty(context, "repositories", group.repositories)
        setIfNull(context, "pm", group.pm)
        setIfNull(context, "techLead", group.techLead)
        setIfNull(context, "testGroup", group)
        setIfNull(context, "logParsing", group.logParsing)
        setIfEmpty(context, "publishOverSSHList", group.publishOverSSHList)
        setIfNull(context, "buildTimeout", group.buildTimeout)
        setIfEmpty(context, "customBuildSteps", group.customBuildSteps)
        setIfNull(context, "resources", group.resources)
        setIfNull(context, "retentionPolicy", group.retentionPolicy)
        setIfNull(context, "testReport", group.testReport)
        setIfNull(context, "workspaceBrowsing", group.workspaceBrowsing)
        setIfNull(context, 'priority', group.priority)
        setIfZeroStr(context, "stbLabel", group.stbLabel)
        context.variables.inheritFrom(group.variables)
    }

    /**
     * Inherit common attributes from source to destination for attributes not
     * specified in destination. All attributes that are common for all
     * levels of inheritance belong here.
     * @param source
     * @param destination
     */
    private void inheritCommonAttributes(BaseCompilationStructureConfig source,
        BaseCompilationStructureConfig destination, boolean alwaysClone=false) {
        setIfEmpty(destination, "csvDataPlots", source.csvDataPlots, alwaysClone)
        setIfNull(destination, "buildEnv", source.buildEnv, alwaysClone)
        setIfNull(destination, "cache", source.cache, alwaysClone)
        setIfNull(destination, "concurrentBuilds", source.concurrentBuilds, alwaysClone)
        setIfEmpty(destination, "credentials", source.credentials, alwaysClone)
        setIfEmpty(destination, "customBuildSteps", source.customBuildSteps, alwaysClone)
        setIfNull(destination, "logParsing", source.logParsing, alwaysClone)
        setIfNull(destination, "makePrefix", source.makePrefix, alwaysClone)
        setIfNull(destination, "makeRoot", source.makeRoot, alwaysClone)
        setIfNull(destination, "makeTarget", source.makeTarget, alwaysClone)
        setIfNull(destination, "pm" , source.pm, alwaysClone)
        setIfNull(destination, "techLead", source.techLead, alwaysClone)
        setIfNull(destination, "incremental", source.incremental, alwaysClone)
        setIfEmpty(destination, "swUpgrades", source.swUpgrades, alwaysClone)
        setIfEmpty(destination, "publishOverSSHList", source.publishOverSSHList, alwaysClone)
        setIfEmpty(destination, "buildNodes", source.buildNodes, alwaysClone)
        setIfNull(destination, "buildTimeout", source.buildTimeout, alwaysClone)
        setIfEmpty(destination, "repositories", source.repositories, alwaysClone)
        setIfNull(destination, "resources", source.resources, alwaysClone)
        setIfNull(destination, "retentionPolicy", source.retentionPolicy, alwaysClone)
        setIfNull(destination, "startedBy", source.startedBy, alwaysClone)
        setIfNull(destination, "workspaceBrowsing", source.workspaceBrowsing, alwaysClone)
        setIfNull(destination, 'priority', source.priority, alwaysClone)
        destination.variables.inheritFrom(source.variables)
    }

    /**
     * Sets attributes that was not specified. The default values are context
     * sensitive and should therefore be done after inheritance.
     * @param project
     */
    private void setDefaultAttributes(Project project) {
        String defaultPolling = '@midnight'
        String defaultIncPolling = ' '
        String coverityDefaultStream = '${PRODUCT}'

        if (!project.trigger.valid) {
            project.trigger.polling = defaultPolling
        }
        if (!project.incTrigger.valid) {
            project.incTrigger.polling = defaultIncPolling
        }
        setIfZeroStr(project.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
        setIfZeroStr(project.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)

        project.origins.each { Origin origin ->

            Boolean defaultRepositoryConfigurable = origin.configurable

            if (!origin.trigger.valid) {
                origin.trigger.polling = defaultPolling
            }
            if (!origin.incTrigger.valid) {
                origin.incTrigger.polling = defaultIncPolling
            }

            setIfZeroStr(origin.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
            setIfZeroStr(origin.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)
            setRepositoryConfigurableIfMissing(origin.repositories, defaultRepositoryConfigurable)
            setIfNull(origin.releasePackaging, "buildTimeout", DEFAULT_RELEASE_PACKAGING_TIMEOUT)
            setIfNull(origin.releasePackaging, "resources", DEFAULT_RESOURCES)

            origin.products.each { Product product ->
                setIfZeroStr(product.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
                setIfZeroStr(product.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)
                setRepositoryConfigurableIfMissing(product.repositories, defaultRepositoryConfigurable)
                setIfZeroStr(product.coverity.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
                setIfZeroStr(product.coverity, "stream", coverityDefaultStream)
                setIfNull(product.coverity, "buildTimeout", DEFAULT_COVERITY_TIMEOUT)
                setIfNull(product.coverity, "workspaceBrowsing", new WorkspaceBrowsing(true))
                setIfNull(product.coverity, "resources", DEFAULT_RESOURCES)
                setIfZeroStr(product.doc.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
                setIfNull(product.doc, "buildTimeout", DEFAULT_DOCUMENTATION_TIMEOUT)
                setIfNull(product.doc, "makePrefix", DEFAULT_MAKE_PREFIX)
                setIfNull(product.doc, "makeRoot", DEFAULT_MAKE_ROOT)
                setIfNull(product.doc, "makeTarget", DEFAULT_DOC_MAKE_TARGET)
                setIfNull(product.doc, "resources", DEFAULT_RESOURCES)
                setIfNull(product.incremental, "cache", DEFAULT_CACHE.clone())
                setIfNull(product.incremental, "resources", DEFAULT_RESOURCES)
                setIfZeroStr(product.incremental.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)
                setIfZeroStr(product.unitTest.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
                setIfNull(product.unitTest, "buildTimeout", DEFAULT_UNIT_TEST_TIMEOUT)
                setIfNull(product.unitTest, "makeTarget", DEFAULT_UNIT_TEST_MAKE_TARGET)
                setIfZeroStr(product.unitTest.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)

                // Set values in product variants if needed.
                [ product.debug,
                  product.release,
                  product.production].each { ProductVariant prodVariant ->
                    setIfZeroStr(prodVariant.buildEnv, "env", DEFAULT_BUILD_ENV_ENV)
                    setIfZeroStr(prodVariant.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)
                    setRepositoryConfigurableIfMissing(prodVariant.repositories, defaultRepositoryConfigurable)
                    setMissingCredentialVariableName(prodVariant.credentials)
                    setIfNull(prodVariant.incremental, "cache", DEFAULT_CACHE.clone())
                    setIfNull(prodVariant.incremental, "resources", DEFAULT_RESOURCES)
                    setIfZeroStr(prodVariant.incremental.cache, "ccacheStorage", DEFAULT_CCACHE_STORAGE)

                    (prodVariant.testGroups + prodVariant.incremental.testGroups).each { TestGroup testGroup ->
                        setRepositoryConfigurableIfMissing(testGroup.repositories, defaultRepositoryConfigurable)
                        setIfNull(testGroup, "boxConfiguration", DEFAULT_BOX_CONFIGURATION)
                        setIfNull(testGroup, "productConfiguration", DEFAULT_PRODUCT_CONFIGURATION)
                        testGroup.testContexts.each { TestContext testContext ->
                            setRepositoryConfigurableIfMissing(testContext.repositories,
                                defaultRepositoryConfigurable)
                        }
                    }
                }
            }
        }
    }

    /**
     * Performs macro expansion of structure macros (PROJECT, ORIGIN, PRODUCT)
     * on all String based properties
     * @param project
     */
    protected void macroContextExpansion(project) {
        ObjectVisitor visitor = new ObjectVisitor<BaseConfig>(new SeedContextTransform(), BaseConfig.class)
        visitor.visit(project)
    }


    /**
     * Inherits the specified property on object from new value if the
     * properties current value is null.
     * @param o         object to be updated
     * @param property  name of property to be updated
     * @param newValue  new value
     * @param alwaysClone use clone() instead of inherit() also for BaseConfig values
     */
    protected static void setIfNull(BaseConfig o, String property, Object newValue, boolean alwaysClone=false) {
        if (o?."$property" == null) {
            o?."$property" = alwaysClone ? newValue.clone() : newValue
        }
    }

    protected static void setIfNull(BaseConfig o, String property, BaseConfig newValue, boolean alwaysClone=false) {
        if (o?."$property" == null) {
            o?."$property" = alwaysClone ? newValue.clone() : newValue.inherit()
        }
    }

    /**
     * Updates the specified property on object with a new string value if
     * the property is null or empty-string.
     * @param o         object to be updated
     * @param property  name of property to be updated
     * @param newValue  new string value
     */
    protected static void setIfZeroStr(Object o, String property, String newValue) {
        if (!o?."$property") {
            o?."$property" = newValue
        }
    }

    /**
     * Replaces a list property with a new list with inherited items of the
     * new value list, if the list property of the object is null or has no items.
     * @param o         object to be updated
     * @param property  name of (list)-property to be updated
     * @param newValue  new value (list)
     * @param alwaysClone use clone() instead of inherit() also for BaseConfig values
     */
    protected static void setIfEmpty(BaseConfig o, String property, Object newValue, boolean alwaysClone=false) {
        if (!o."$property" || o."$property".size() == 0) {
            o."$property" = newValue.clone()
        }
    }

    protected static void setIfEmpty(BaseConfig o, String property, BaseConfig newValue, boolean alwaysClone=false) {
        if (!o."$property" || o."$property".size() == 0) {
            o?."$property" = alwaysClone ? newValue.clone() : newValue.inherit()
        }
    }

    protected static void setMissingEmailPolicy(Object structureConfig) {
        if (structureConfig != null) {
            setDefaultEmailPolicyIfMissing(structureConfig.pm)
            setDefaultEmailPolicyIfMissing(structureConfig.techLead)
            structureConfig.watchers.each { Watcher watcher ->
                setDefaultEmailPolicyIfMissing(watcher)
            }
            [ "debug","production","release", "unitTest"].each { String productVariant ->
                if (structureConfig.hasProperty(productVariant)) {
                  setMissingEmailPolicy(structureConfig."${productVariant}")
              }
            }
        }
    }


    private setMissingDescription(BaseConfig config) {
        setIfNull(config, "description", new Description())
    }

    protected static void setDefaultEmailPolicyIfMissing(ContactInformation who) {
        setIfNull(who, "emailPolicy", new EmailPolicy(EmailPolicyWhen.FAILURE,
                EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER), true)
    }

    protected static void setMissingCredentialVariableName(CredentialList credentials) {
        credentials.getEnabled().each { Credential credential ->
            setDefaultCredentialVariableNameIfMissing(credential)
        }
    }

    protected static void setDefaultCredentialVariableNameIfMissing(Credential credential) {
        switch (credential.type) {
            case CredentialType.FILE:
               setIfZeroStr(credential, "variableName", "CREDENTIAL_FILE")
               break
            case CredentialType.TEXT:
               setIfZeroStr(credential, "variableName", "CREDENTIAL_TEXT")
               break
            case CredentialType.USERNAME_PASSWORD:
               setIfZeroStr(credential, "variableName", "CREDENTIAL")
               break
        }
    }

    protected static void setRepositoryConfigurableIfMissing(Repository[] repositories, Boolean configurable) {
        for (Repository repo in repositories) {
            setIfNull(repo, "configurable", configurable)
        }
    }

    protected static List removeAllNull(List list) {
        return (list - null)
    }
}
