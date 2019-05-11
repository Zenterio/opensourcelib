package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper = true, includeFields = true)
@AutoClone
class StartedBy extends BaseConfig {
    /**
     * True if StartedBy username should be added to build name
     */
    Boolean enabled
    /**
     *
     * @param enabled if startedBy should be enabled or not.
     */
    public StartedBy(Boolean enabled) {
        this.enabled = enabled
    }

    public static StartedBy getTestData() {
        return new StartedBy(true)
    }

    @Override
    public String toString() {
        return this.enabled.toString()
    }
}
