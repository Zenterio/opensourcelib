package com.zenterio.jenkins.configuration

class PublishOverSSHListTest extends GroovyTestCase {

    public void testDeepCopy() {
        PublishOverSSHList list = PublishOverSSHList.testData
        PublishOverSSHList clone = list.clone()
        assert list == clone
        assert !list.is(clone)
    }

    public void testGetEnabled() {
        PublishOverSSHList list = PublishOverSSHList.testData
        PublishOverSSHList expected = [new PublishOverSSH(true, 'Server', null, null, null, null),
                                       new PublishOverSSH(true, 'Server', null, null, null, null)] as PublishOverSSHList
        PublishOverSSHList result = list.getEnabled()
        assert result == expected
    }
}
