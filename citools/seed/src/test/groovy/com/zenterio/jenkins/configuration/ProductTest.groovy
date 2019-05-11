package com.zenterio.jenkins.configuration

class ProductTest extends GroovyTestCase {

    public void testDeepClone() {
        Product product = Product.testData

        shouldFail(CloneNotSupportedException) {
            def clone = product.clone()
        }
    }

    public void testIncrementalIsInActive() {
        Product product = Product.testData

        product.debug.incremental.enabled = false
        product.release.incremental.enabled = false
        product.production.incremental.enabled = false
        product.incremental.enabled = false
        product.unitTest.enabled = false
        assert product.isIncrementalActive() == false

        product.debug.incremental.enabled = false
        product.release.incremental.enabled = false
        product.production.incremental.enabled = false
        product.incremental.enabled = false
        product.unitTest.enabled = true
        assert product.isIncrementalActive() == false

        product.debug.incremental.enabled = false
        product.release.incremental.enabled = false
        product.production.incremental.enabled = false
        product.incremental.enabled = true
        product.unitTest.enabled = false
        assert product.isIncrementalActive() == false

        product.debug.incremental.enabled = false
        product.release.incremental.enabled = false
        product.production.incremental.enabled = true
        product.incremental.enabled = false
        product.unitTest.enabled = false
        assert product.isIncrementalActive() == true

        product.debug.incremental.enabled = false
        product.release.incremental.enabled = false
        product.production.incremental.enabled = false
        product.incremental.enabled = true
        product.unitTest.enabled = true
        assert product.isIncrementalActive() == true

    }
}
