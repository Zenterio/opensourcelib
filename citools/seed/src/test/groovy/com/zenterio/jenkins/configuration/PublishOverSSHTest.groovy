package com.zenterio.jenkins.configuration

class PublishOverSSHTest extends GroovyTestCase {
    public void testDefaultValues() {
        PublishOverSSH publish = new PublishOverSSH(null, 'server', null, null, null, null)
        assert publish.enabled
        assert publish.server == 'server'
        assert publish.retryTimes == 0
        assert publish.retryDelay == 10000
        assert publish.label == ""
        assert publish.transferSets.size() == 0
    }

    public void testNullServer() {
        shouldFail(IllegalArgumentException, {
            PublishOverSSH publish = new PublishOverSSH(null, null, null, null, null, null)
        })
    }

    public void testEnabledFalse() {
        PublishOverSSH publish = new PublishOverSSH(false, 'server', null, null, null, null)
        assert !publish.enabled
    }

    public void testCloneWithoutTransferSets() {
        PublishOverSSH publish = new PublishOverSSH(null, 'server', null, null, null, null)
        PublishOverSSH clone = publish.clone()
        assert publish == clone
        assert !publish.is(clone)
        assert publish.enabled == clone.enabled
        assert publish.server == clone.server
        assert publish.retryTimes == clone.retryTimes
        assert publish.retryDelay == clone.retryDelay
        assert publish.label == clone.label
        assert publish.transferSets == clone.transferSets
    }

    public void testCloneWithTransferSets() {
        PublishOverSSH publish = PublishOverSSH.testData
        PublishOverSSH clone = publish.clone()
        assert publish == clone
        assert publish.transferSets == clone.transferSets
        assert !publish.transferSets.is(clone.transferSets)

        for (int i = 0; i < 2; ++i) {
            assert publish.transferSets[i] == clone.transferSets[i]
            assert !publish.transferSets[i].is(clone.transferSets[i])
        }
    }
}
