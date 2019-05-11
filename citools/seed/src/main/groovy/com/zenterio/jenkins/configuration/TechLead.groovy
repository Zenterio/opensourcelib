package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class TechLead extends ContactInformation {

    public TechLead(String name, String email, EmailPolicy emailPolicy) {
        super(name, email, emailPolicy)
    }

    public TechLead inherit() {
        return new TechLead(this.name, this.email, this.emailPolicy?.inherit())
    }

    public static TechLead getTestData() {
        return new TechLead("Tech Lead", "tech.lead@mail.com", EmailPolicy.testData)
    }
}
