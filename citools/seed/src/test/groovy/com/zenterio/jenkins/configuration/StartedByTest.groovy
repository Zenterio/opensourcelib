package com.zenterio.jenkins.configuration

class StartedByTest extends GroovyTestCase {

    public void testDeepClone() {
        StartedBy data = StartedBy.testData
        StartedBy clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

}
