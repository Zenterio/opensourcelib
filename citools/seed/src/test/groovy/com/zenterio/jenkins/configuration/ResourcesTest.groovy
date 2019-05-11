package com.zenterio.jenkins.configuration

class ResourcesTest extends GroovyTestCase {

    public void testDeepClone() {
        Resources data = Resources.testData
        Resources clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

}
