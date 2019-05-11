package com.zenterio.jenkins.configuration

class ProductVariantTest extends GroovyTestCase {

    public void testDeepClone() {
        ProductVariant prodVariant = ProductVariant.testData
        ProductVariant clone = prodVariant.clone()
        assert prodVariant == clone
        assert !prodVariant.incremental.is(clone.incremental)
        assert !prodVariant.csvDataPlots[0].is(clone.csvDataPlots[0])
        assert !prodVariant.customBuildSteps[0].is(clone.customBuildSteps[0])
        assert !prodVariant.description.is(clone.description)
        assert !prodVariant.makeRoot.is(clone.makeRoot)
        assert !prodVariant.makeTarget.is(clone.makeTarget)
        assert !prodVariant.pm.is(clone.pm)
        assert !prodVariant.repositories[0].is(clone.repositories[0])
        assert !prodVariant.techLead.is(clone.techLead)
        assert !prodVariant.watchers[0].is(clone.watchers[0])
        assert !prodVariant.testGroups[0].is(clone.testGroups[0])
    }

    public void testIsIncrementalActive() {
        ProductVariant prodVariant = ProductVariant.testData

        prodVariant.enabled = true
        prodVariant.incremental.enabled = true
        assert prodVariant.isIncrementalActive() == true

        prodVariant.enabled = false
        prodVariant.incremental.enabled = true
        assert prodVariant.isIncrementalActive() == false

        prodVariant.enabled = true
        prodVariant.incremental.enabled = false
        assert prodVariant.isIncrementalActive() == false
    }
}
