package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class CredentialList extends ArrayList<Credential> {

    public CredentialList clone() {
        return this.collect{ Credential credential ->
            credential.clone()
        } as CredentialList
    }

    public CredentialList getEnabled() {
        return this.findAll{ Credential credential -> credential.enabled } as CredentialList
    }

    public static CredentialList getTestData() {
        CredentialList data = new CredentialList()
        data.add(new Credential(CredentialType.FILE, 'file-test-credential', null, true))
        data.add(new Credential(CredentialType.TEXT, 'text-test-credential', null, true))
        data.add(new Credential(CredentialType.USERNAME_PASSWORD, 'up-test-credential', null, false))
        return data
    }
}
