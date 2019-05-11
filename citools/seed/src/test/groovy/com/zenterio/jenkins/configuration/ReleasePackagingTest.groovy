package com.zenterio.jenkins.configuration

class ReleasePackagingTest extends GroovyTestCase {

    public void testDeepClone() {
        ReleasePackaging rp = ReleasePackaging.testData
        ReleasePackaging clone = rp.clone()
        assert rp == clone
        assert !rp.customBuildSteps[0].is(clone.customBuildSteps[0])
        assert !rp.publishOverSSHList.is(clone.publishOverSSHList)
        assert !rp.repositories[0].is(clone.repositories[0])
    }
}
