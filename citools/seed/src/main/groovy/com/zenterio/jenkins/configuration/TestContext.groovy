package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical(excludes = 'testGroup')
@EqualsAndHashCode(callSuper=true, includeFields=true, excludes="testGroup")
class TestContext extends BaseStructureConfig {

    CredentialList credentials
    CsvDataPlot[] csvDataPlots
    CustomBuildStepList customBuildSteps
    Description description
    Duration duration
    TestSuite[] testSuites
    Upstream upstream
    String polling
    String periodic
    Boolean enabled
    Boolean coredumpHandling
    Epg[] epgs
    Image image
    LogParsing logParsing
    Repository[] repositories
    TestJobInputParameter[] inputParameters
    TestCommandArgs testCommandArgs
    TestReport testReport
    XmlToCsv[] xmlToCsvs
    Jasmine jasmine
    ContactInformationCollection owners
    String stbLabel

    // Parent test group
    TestGroup testGroup

    public TestContext(String name, CsvDataPlot[] csvDataPlots, Description description, Duration duration,
                       TestSuite[] testSuites, Upstream upstream, String polling, String periodic,
                       Boolean enabled, Boolean coredumpHandling, Epg[] epgs, Image image, LogParsing logParsing,
                       Repository[] repositories, ContactInformationCollection watchers,
                       TestJobInputParameter[] inputParameters, TestCommandArgs testCommandArgs,
                       XmlToCsv[] xmlToCsvs) throws Exception {
        super()
        if (upstream == Upstream.TRUE && (repositories?.length > 0)) {
            throw new Exception("Upstream can not be set to true and at the same time " +
                "set context specific repositories.")
        }
        this.name = name
        this.customBuildSteps = new CustomBuildStepList()
        this.credentials = new CredentialList()
        this.csvDataPlots = csvDataPlots ?: new CsvDataPlot[0]
        this.description = description
        this.duration = duration
        this.testSuites = testSuites
        this.upstream = upstream
        this.polling = polling
        this.periodic = periodic
        this.enabled = enabled
        this.coredumpHandling = coredumpHandling
        this.epgs = epgs ?: new Epg[0]
        this.image = image
        this.logParsing = logParsing
        this.repositories = repositories ?: new Repository[0]
        this.watchers = watchers
        this.inputParameters = inputParameters
        this.testCommandArgs = testCommandArgs
        this.testReport = null
        this.xmlToCsvs = xmlToCsvs ?: new XmlToCsv[0]
        this.jasmine = null
        this.owners = null
        this.testGroup = null
        this.stbLabel = null
    }

    /**
     * Copy constructor
     *
     */
    public TestContext(TestContext other){
        super(other)
        this.credentials = other.credentials?.clone()
        this.csvDataPlots = other.csvDataPlots.collect({ it?.clone() }) as CsvDataPlot[]
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.description = other.description?.clone()
        this.duration = other.duration?.clone()
        this.testSuites = other.testSuites.collect{ t -> t?.clone() } as TestSuite[]
        this.upstream = other.upstream
        this.polling = other.polling
        this.periodic = other.periodic
        this.enabled = other.enabled
        this.coredumpHandling = other.coredumpHandling
        this.epgs = other.epgs.collect{ epg -> epg?.clone() } as Epg[]
        this.logParsing = other.logParsing?.clone()
        this.image = other.image?.clone()
        this.repositories = other.repositories.collect{ r -> r?.clone() } as Repository[]
        this.inputParameters = other.inputParameters?.clone()
        this.testCommandArgs = other.testCommandArgs?.clone()
        this.testReport = other.testReport?.clone()
        this.xmlToCsvs = other.xmlToCsvs.collect({ it?.clone() }) as XmlToCsv[]
        this.jasmine = other.jasmine?.clone()
        this.stbLabel = other.stbLabel

        //this.testGroup = other.testGroup
    }

    public Object clone() throws CloneNotSupportedException {
        return new TestContext(this)
    }

    public static TestContext getTestData(withRepo=false, upstream=Upstream.TRUE) {
        Repository[] repositories = (withRepo) ? [Repository.testData] as Repository[] : null
        TestContext context = new TestContext("TestContextName",
                [CsvDataPlot.testData] as CsvDataPlot[],
                Description.testData,
                Duration.testData,
                [TestSuite.testData] as TestSuite[],
                upstream, "poll string", "periodic string",
                true,
                true,
                [Epg.testData] as Epg[], Image.testData, LogParsing.testData,
                repositories,
                ContactInformationCollection.testData,
                [TestJobInputParameter.testData] as TestJobInputParameter[],
                TestCommandArgs.testData,
                [XmlToCsv.testData] as XmlToCsv[])

        context.pm = ProjectManager.testData
        context.techLead = TechLead.testData
        context.jasmine = Jasmine.testData
        context.stbLabel = "STB-LABEL"
        context.testReport = TestReport.testData
        context.publishOverSSHList = PublishOverSSHList.testData
        return context
    }
}
