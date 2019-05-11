package com.zenterio.jenkins.configuration

class UnitTestTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        UnitTest data = UnitTest.testData
        UnitTest clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

    public void testIsIncrementalActive() {
        UnitTest ut = UnitTest.testData
        Product product = Product.testData
        product.setUnitTest(ut)

        ut.enabled = true
        product.incremental.enabled = true
        assert ut.isIncrementalActive() == true

        ut.enabled = true
        product.incremental.enabled = false
        assert ut.isIncrementalActive() == false

        ut.enabled = false
        product.incremental.enabled = true
        assert ut.isIncrementalActive() == false
    }
}
