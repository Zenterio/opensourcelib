package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class ProjectManager extends ContactInformation {

    public ProjectManager(String name, String email, EmailPolicy emailPolicy) {
        super(name, email, emailPolicy)
    }

    public ProjectManager inherit() {
        return new ProjectManager(this.name, this.email,this.emailPolicy?.inherit())
    }

    public static ProjectManager getTestData() {
        return new ProjectManager("Project Manager", "project.manager@mail.com", EmailPolicy.testData)
    }
}
