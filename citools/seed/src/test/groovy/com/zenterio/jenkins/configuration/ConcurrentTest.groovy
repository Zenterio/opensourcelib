package com.zenterio.jenkins.configuration

class ConcurrentTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        ConcurrentBuilds concurrent = ConcurrentBuilds.testData
        ConcurrentBuilds clone = concurrent.clone()

        assert concurrent == clone
        assert !concurrent.is(clone)
    }
}
