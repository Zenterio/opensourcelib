package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class WorkspaceBrowsing extends BaseConfig {

    // Properties
    Boolean enabled

    public WorkspaceBrowsing(Boolean enabled = true ) {
        this.enabled = enabled ?: false

    }

    public static WorkspaceBrowsing getTestData() {
        WorkspaceBrowsing data = new WorkspaceBrowsing(false)
        return data
    }
}
