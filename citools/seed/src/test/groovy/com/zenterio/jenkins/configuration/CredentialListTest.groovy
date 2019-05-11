package com.zenterio.jenkins.configuration

class CredentialListTest extends GroovyTestCase {

    public void testDeepCopy() {
        CredentialList list = CredentialList.testData
        CredentialList clone = list.clone()
        assert list == clone
        assert !list.is(clone)
    }

    public void testGetEnabled() {
        CredentialList list = CredentialList.testData
        CredentialList expected = [new Credential(CredentialType.FILE, 'file-test-credential', null, true),
                                   new Credential(CredentialType.TEXT, 'text-test-credential', null, true)] as CredentialList
        CredentialList result = list.getEnabled()
        assert result == expected
    }
}
