package com.zenterio.jenkins.configuration

class BuildNodeTest extends GroovyTestCase {

    public void testDeepClone() {
        BuildNode data = BuildNode.testData
        BuildNode clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

}
