package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class ConcurrentBuilds extends BaseConfig {
    /**
     * True if jenkins should allow concurrent builds
     */
    Boolean enabled

    /**
     *
     * @param enabled    If Concurrent builds should be enable or not.
     */
    public ConcurrentBuilds(Boolean enabled) {
        this.enabled = enabled
    }

    public static ConcurrentBuilds getTestData() {
        return new ConcurrentBuilds(true)
    }
}
