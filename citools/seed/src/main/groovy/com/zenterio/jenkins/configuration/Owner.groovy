package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Owner extends ContactInformation {

    String group

    public Owner(String name, String email, EmailPolicy emailPolicy, String group) {
        super(name, email, emailPolicy)
        if (!group.matches("[a-z0-9_]+")) {
            throw new IllegalArgumentException("Owner group name may only contain lowercase letters and underscores")
        }
        this.group = group
    }

    public Owner inherit() {
        return new Owner(this.name, this.email,this.emailPolicy.inherit(), this.group)
    }

    public static Owner getTestData() {
        return new Owner("Owner", "owner@mail.com", EmailPolicy.testData, "owners")
    }
}
