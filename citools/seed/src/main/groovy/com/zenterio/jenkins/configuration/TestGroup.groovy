package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class TestGroup extends BaseStructureConfig {

    TestGroupType type
    CustomBuildStepList customBuildSteps
    Description description
    Boolean enabled
    String testRoot
    String stbLabel
    String boxConfiguration
    String productConfiguration

    CredentialList credentials
    Boolean coredumpHandling
    Epg[] epgs
    LogParsing logParsing
    Image image
    Repository[] repositories
    TestReport testReport
    TestContext[] testContexts


    public TestGroup(String name, TestGroupType type, Description description, String testRoot, String stbLabel,
                     String boxConfiguration, String productConfiguration, Repository[] repositories,
                     TestContext[] testContexts, Image image, LogParsing logParsing, Boolean enabled,
                     Boolean coredumpHandling, Epg[] epgs, ContactInformationCollection watchers) {
        super()
        this.name = name
        this.type = type
        this.customBuildSteps = new CustomBuildStepList()
        this.description = description
        this.enabled = enabled?:false
        this.testRoot = testRoot
        this.stbLabel = stbLabel
        this.productConfiguration = productConfiguration
        this.boxConfiguration = boxConfiguration

        this.credentials = new CredentialList()
        this.coredumpHandling = coredumpHandling
        this.epgs = epgs
        this.image = image
        this.logParsing = logParsing
        this.repositories = repositories
        this.testContexts = testContexts
        testContexts.each { context ->
            context.setTestGroup(this)
        }
        this.testReport = null
        this.watchers = watchers

        this.pm = null
        this.techLead = null
    }

    /**
     * Copy constructor
     * @param other
     */
    public TestGroup(TestGroup other){
        super(other)
        this.name = other.name
        this.type = other.type
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.description = other.description?.clone()
        this.enabled = other.enabled
        this.testRoot = other.testRoot
        this.stbLabel = other.stbLabel
        this.boxConfiguration = other.boxConfiguration
        this.productConfiguration = other.productConfiguration

        this.credentials = other.credentials?.clone()
        this.coredumpHandling = other.coredumpHandling
        this.epgs = other.epgs.collect{ epg -> epg?.clone() } as Epg[]
        this.image = other.image?.clone()
        this.logParsing = other.logParsing?.clone()
        this.repositories = other.repositories.collect{ r -> r?.clone() } as Repository[]
        this.testContexts = other.testContexts.collect{ t -> t?.clone() } as TestContext[]
        this.testReport = other.testReport?.clone()
        this.watchers=other.watchers?.clone()

        this.pm = other.pm?.clone()
        this.techLead = other.techLead?.clone()
    }

    public Object clone() throws CloneNotSupportedException {
        return new TestGroup(this)
    }

    public static TestGroup getTestData() {
        TestGroup group = new TestGroup("GROUP-NAME", TestGroupType.KAZAM,
                Description.testData, "TEST-ROOT", "STB-LABEL",
                "BOX-CONFIGURATION", "PRODUCT-CONFIGURATION",
                [Repository.testData] as Repository[],
                [TestContext.testData] as TestContext[],
                Image.testData,
                LogParsing.testData,
                true,
                true,
                [Epg.testData] as Epg[],
                ContactInformationCollection.testData)
        group.testReport = TestReport.testData
        group.techLead = TechLead.testData
        group.pm = ProjectManager.testData

        return group
    }
}
