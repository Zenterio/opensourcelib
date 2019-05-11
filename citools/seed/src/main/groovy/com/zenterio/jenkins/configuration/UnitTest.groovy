package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical(excludes="product")
@EqualsAndHashCode(callSuper=true, includeFields=true, excludes="product")
class UnitTest extends BaseStructureConfig {

    Boolean builtIn
    Boolean enabled

    BuildEnv buildEnv
    BuildNodeList buildNodes
    CsvDataPlot[] csvDataPlots
    Cache cache
    CredentialList credentials
    CustomBuildStepList customBuildSteps
    Description description
    LogParsing logParsing
    MakePrefix makePrefix
    MakeRoot makeRoot
    MakeTarget makeTarget
    Repository[] repositories
    StartedBy startedBy

    Product product

    UnitTest(Boolean builtIn, Boolean enabled) {
        super()
        this.builtIn = builtIn
        this.enabled = enabled
        this.buildNodes = new BuildNodeList()
        this.csvDataPlots = new CsvDataPlot[0]
        this.cache = null
        this.credentials = new CredentialList()
        this.customBuildSteps = new CustomBuildStepList()
        this.description = null
        this.logParsing = null
        this.makePrefix = null
        this.makeRoot = null
        this.makeTarget = null
        this.repositories = new Repository[0]
        this.startedBy = null
        this.product = null
        this.buildEnv = null
    }

    /**
     * Copy constructor
     * @param other
     */
    UnitTest(UnitTest other) {
        super(other)
        this.builtIn = other.builtIn
        this.enabled = other.enabled
        this.buildNodes = other.buildNodes?.clone()
        this.csvDataPlots = other.csvDataPlots.collect{ it?.clone() } as CsvDataPlot[]
        this.cache = other.cache?.clone()
        this.credentials = other.credentials?.clone()
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.description = other.description?.clone()
        this.logParsing = other.logParsing?.clone()
        this.makePrefix = other.makePrefix?.clone()
        this.makeRoot = other.makeRoot?.clone()
        this.makeTarget = other.makeTarget?.clone()
        this.repositories = other.repositories.collect { r -> r?.clone() } as Repository[]
        this.startedBy = other.startedBy?.clone()
        this.product = other.product
        this.buildEnv = other.buildEnv?.clone()
    }

    public Object clone() throws CloneNotSupportedException {
        return new UnitTest(this)
    }

    public Origin getOrigin() {
        return this.product?.origin
    }

    public Boolean isIncrementalActive() {
        return this.enabled && this.product?.incremental?.enabled
    }

    public static UnitTest getTestData() {
        UnitTest data = new UnitTest(true, true)
        data.buildNodes = BuildNodeList.testData
        data.csvDataPlots = [CsvDataPlot.testData] as CsvDataPlot[]
        data.customBuildSteps.add(CustomBuildStep.testData)
        data.description = Description.testData
        data.makePrefix = MakePrefix.testData
        data.makeRoot = MakeRoot.testData
        data.makeTarget = MakeTarget.testData
        data.pm = ProjectManager.testData
        data.repositories = [Repository.testData] as Repository[]
        data.startedBy = StartedBy.testData
        data.techLead = TechLead.testData
        data.watchers = ContactInformationCollection.testData
        data.variables = VariableCollection.testData
        data.publishOverSSHList = PublishOverSSHList.testData
        data.buildEnv = BuildEnv.testData
        return data
    }

}
