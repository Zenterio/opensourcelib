package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical(excludes="origin")
@EqualsAndHashCode(callSuper=true, includeFields=true, excludes="origin")
class Product extends BaseProduct implements IProductVariantHolder {

    // Features
    BuildFlow buildFlow
    Coverity coverity
    Doc doc
    BuildFlow incBuildFlow

    // Product variants
    ProductVariant debug
    ProductVariant release
    ProductVariant production
    UnitTest unitTest

    // Parent
    Origin origin

    /**
     * Alternative product name, should be customer friendly
     */
    String altName

    /**
     *
     * @param name
     */
    public Product(String name, String altName) {
        super()
        this.name = name
        this.altName = altName ?: name

        this.buildFlow = null
        this.coverity = null
        this.doc = null
        this.incBuildFlow = null

        this.debug = null
        this.release = null
        this.production = null
        this.unitTest = null
        this.origin = null
    }

    public void setDebug(ProductVariant debug) {
        // old
        this.debug?.product = null

        // new
        this.debug = debug
        this.debug?.product = this
        this.debug?.name = this.name
    }

    public void setRelease(ProductVariant release) {
        // old
        this.release?.product = null

        // new
        this.release = release
        this.release?.product = this
        this.release?.name = this.name
    }

    public void setProduction(ProductVariant production) {
        // old
        this.production?.product = null

        // new
        this.production = production
        this.production?.product = this
        this.production?.name = this.name
    }

    public void setUnitTest(UnitTest unitTest) {
        /// old
        this.unitTest?.product = null

        // new
        this.unitTest = unitTest
        this.unitTest?.product = this
        this.unitTest?.name = this.name
    }

    public Boolean isIncrementalActive() {
        return [debug, release, production, unitTest].any{ item -> item?.isIncrementalActive()}
    }

    public static Product getTestData() {
        Product product =  new Product("PRODUCT-NAME", "ALT-NAME")
        product.buildEnv = BuildEnv.testData
        product.buildFlow = BuildFlow.testData
        product.coverity = Coverity.testData
        product.csvDataPlots = [CsvDataPlot.testData] as CsvDataPlot[]
        product.incBuildFlow = BuildFlow.testData
        product.doc = Doc.testData
        product.variables = VariableCollection.testData
        product.swUpgrades = SwUpgrades.testData
        product.incremental = Incremental.testData

        product.debug = ProductVariant.testData
        product.release = ProductVariant.testData
        product.production = ProductVariant.testData
        product.unitTest = UnitTest.testData

        return product
    }
}
