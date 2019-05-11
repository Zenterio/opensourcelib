package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class ContactFile extends ContactInformation {

    /**
     *
     * @param path This path should be relative the root of the jenkins workspace
     * @param emailPolicy
     */
    ContactFile(String path, EmailPolicy emailPolicy) {
        super("FileContact<path='${path}'>", """\${FILE,path="${path}"}""", emailPolicy)
    }
}
