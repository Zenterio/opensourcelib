package com.zenterio.jenkins.configuration

class RepositoryTest extends GroovyTestCase {

    public void testDeepClone() {
        Repository data = Repository.testData
        Repository clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

}
