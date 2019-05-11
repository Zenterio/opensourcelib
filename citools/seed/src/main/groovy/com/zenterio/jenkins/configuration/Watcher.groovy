package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Watcher extends ContactInformation {

    public Watcher(String name, String email, EmailPolicy emailPolicy) {
        super(name, email, emailPolicy)
    }

    public Watcher inherit() {
        return new Watcher(this.name, this.email,this.emailPolicy.inherit())
    }

    public static Watcher getTestData() {
        return new Watcher("Watcher", "watcher@mail.com", EmailPolicy.testData)
    }
}
