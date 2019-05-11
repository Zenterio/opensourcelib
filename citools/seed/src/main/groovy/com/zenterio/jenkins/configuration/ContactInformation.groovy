package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class ContactInformation extends BaseConfig {

    String name
    String email
    EmailPolicy emailPolicy

    public ContactInformation(String name, String email, EmailPolicy emailPolicy) {
        this.name = name
        this.email = email
        this.emailPolicy = emailPolicy
    }
}
