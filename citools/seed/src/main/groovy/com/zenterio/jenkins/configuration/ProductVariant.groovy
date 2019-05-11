package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.buildtype.BuildTypeDebug
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

/**
 * ProductVariant to product representing configuration related to debug-builds
 * of the product.
 */
@Canonical(excludes="product")
@EqualsAndHashCode(callSuper=true, includeFields=true, excludes="product")
class ProductVariant extends BaseProduct implements ITester {

    BuildType buildType
    Boolean enabled
    Product product
    TestGroup[] testGroups

    /**
     * Default constructor
     */
    public ProductVariant(buildType, enabled = true) {
        super()
        this.buildType = buildType
        this.enabled = enabled ?: false
        this.product = null
        this.testGroups = new TestGroup[0]
    }

    /**
     * Copy constructor
     * @param other
     */
    public ProductVariant(ProductVariant other) {
        super(other)
        this.buildType = other.buildType?.clone()
        this.enabled = other.enabled
        this.product = other.product
        this.testGroups = other.testGroups.collect{ tst -> tst?.clone() } as TestGroup[]
    }

    public static ProductVariant getTestData() {
        ProductVariant prodVariant = new ProductVariant(new BuildTypeDebug(), true)
        prodVariant.buildEnv = BuildEnv.testData
        prodVariant.csvDataPlots = [CsvDataPlot.testData] as CsvDataPlot[]
        prodVariant.customBuildSteps.add(CustomBuildStep.testData)
        prodVariant.description = Description.testData
        prodVariant.makeRoot = MakeRoot.testData
        prodVariant.makeTarget = MakeTarget.testData
        prodVariant.pm = ProjectManager.testData
        prodVariant.repositories = [Repository.testData] as Repository[]
        prodVariant.swUpgrades = SwUpgrades.testData
        prodVariant.techLead = TechLead.testData
        prodVariant.watchers = ContactInformationCollection.testData
        prodVariant.testGroups = [TestGroup.testData] as TestGroup[]
        prodVariant.incremental = Incremental.testData
        prodVariant.variables = VariableCollection.testData
        prodVariant.publishOverSSHList = PublishOverSSHList.testData
        return prodVariant
    }

    public Object clone() throws CloneNotSupportedException {
        return new ProductVariant(this)
    }

    @Override
    public Origin getOrigin() {
        return this.product?.origin
    }

    public Boolean isIncrementalActive() {
        return this.enabled && this.incremental?.enabled
    }
}
