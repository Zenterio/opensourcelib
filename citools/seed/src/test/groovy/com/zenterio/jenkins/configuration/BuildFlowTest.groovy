package com.zenterio.jenkins.configuration

class BuildFlowTest extends GroovyTestCase {

    public void testDeepClone() {
        BuildFlow data = BuildFlow.testData
        BuildFlow clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

}
