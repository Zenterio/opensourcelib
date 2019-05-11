package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class Project extends BaseCompilationStructureConfig implements IProductVariantHolder {

    // Features
    BuildFlow buildFlow
    Coverity coverity
    Doc doc
    BuildFlow incBuildFlow
    Trigger trigger
    Trigger incTrigger
    ReleasePackaging releasePackaging

    // Structures
    List<Origin> origins

    // Product variants
    ProductVariant debug
    ProductVariant release
    ProductVariant production
    UnitTest unitTest


    /**
     *
     * @param name
     * @param pm
     * @param techLead
     * @param watchers
     * @param origins
     */
    public Project(String name,
        ProjectManager pm,
        TechLead techLead,
        ContactInformationCollection watchers,
        Origin[] origins) {
        super()
        this.name = name
        this.pm = pm
        this.techLead = techLead
        this.watchers = watchers

        setOrigins(origins)
        this.debug = null
        this.release = null
        this.production = null
        this.unitTest = null

        this.buildFlow = null
        this.coverity = null
        this.doc = null
        this.incBuildFlow = null
        this.trigger = null
        this.incTrigger = null
        this.releasePackaging = null
    }

    public Origin[] getOrigins() {
        return this.origins as Origin[]
    }

    public void setOrigins(Origin[] origins) {
        origins?.each { Origin origin -> origin.project = this }
        this.origins = origins
    }

    public void addOrigins(Origin[] origins) {
        if (!this.origins) {
            this.setOrigins(origins)
        } else {
            origins?.each { Origin origin -> origin.project = this }
            this.origins.addAll(origins)
        }
    }

    public static Project getTestData() {

        return new Project("PROJECT-NAME",
        ProjectManager.testData,
        TechLead.testData,
        ContactInformationCollection.testData,
        [Origin.testData] as Origin[]).with {
            buildFlow = BuildFlow.testData
            coverity = Coverity.testData
            doc = Doc.testData
            incBuildFlow = BuildFlow.testData
            csvDataPlots = [CsvDataPlot.testData] as CsvDataPlot[]
            releasePackaging = ReleasePackaging.testData
            variables = VariableCollection.testData
            unitTest = UnitTest.testData
            it
        }

    }
}
