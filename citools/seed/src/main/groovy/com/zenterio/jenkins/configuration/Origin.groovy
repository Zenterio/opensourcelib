package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical(excludes="project")
@EqualsAndHashCode(callSuper=true, includeFields=true, excludes="project")
class Origin extends BaseCompilationStructureConfig implements IProductVariantHolder {

    Boolean configurable
    Boolean tagScm

    // Features
    BuildFlow buildFlow
    Coverity coverity
    Doc doc
    BuildFlow incBuildFlow
    Trigger trigger
    Trigger incTrigger
    ReleasePackaging releasePackaging

    // Structures
    Product[] products
    // Product variants
    ProductVariant debug
    ProductVariant release
    ProductVariant production
    UnitTest unitTest
    // Parent
    Project project

    /**
     *
     * @param name
     * @param configurable
     * @param tagScm
     * @param products
     * @param repositories
     * @param watchers
     */
    public Origin(String name, Boolean configurable, Boolean tagScm,
        Product[] products, Repository[] repositories,
        ContactInformationCollection watchers) {
        super()
        this.name = name
        this.configurable = configurable
        this.tagScm = tagScm
        this.products = products
        this.repositories = repositories
        this.watchers = watchers
        this.products.each { prod ->
            prod.setOrigin(this)
        }

        this.debug = null
        this.release = null
        this.production = null
        this.unitTest = null
        this.project = null

        this.buildFlow = null
        this.coverity = null
        this.doc = null
        this.incBuildFlow = null
        this.trigger = null
        this.incTrigger = null
        this.releasePackaging = null
    }

    public static Origin getTestData() {
        return new Origin("ORIGIN-NAME", false, true,
        [Product.testData] as Product[],
        [Repository.testData] as Repository[],
        ContactInformationCollection.testData).with({
            buildFlow = BuildFlow.testData
            coverity = Coverity.testData
            doc = Doc.testData
            incBuildFlow = BuildFlow.testData
            csvDataPlots = [CsvDataPlot.testData] as CsvDataPlot[]
            variables = VariableCollection.testData
            swUpgrades = SwUpgrades.testData
            releasePackaging = ReleasePackaging.testData
            unitTest = UnitTest.testData
            it
        })

    }

    public Boolean isIncrementalActive() {
        return products.any{ Product product -> product.isIncrementalActive()}
    }
}
