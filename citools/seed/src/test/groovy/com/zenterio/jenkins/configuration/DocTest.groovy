package com.zenterio.jenkins.configuration

class DocTest extends GroovyTestCase {

    public void testDeepClone() {
        Doc parent = Doc.testData
        Doc clone = parent.clone()
        assert parent == clone
        assert !parent.is(clone)
    }
}
