package com.zenterio.jenkins.configuration

class CoverityTest extends GroovyTestCase {

    public void testDeepClone() {
        Coverity coverity = Coverity.testData
        Coverity clone = coverity.clone()
        assert coverity == clone
        assert !coverity.is(clone)
    }
    
}
