package com.zenterio.jenkins.configuration

class IncrementalTest extends GroovyTestCase {

    public void testDeepClone() {
        Incremental data = Incremental.testData
        Incremental clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }
}
