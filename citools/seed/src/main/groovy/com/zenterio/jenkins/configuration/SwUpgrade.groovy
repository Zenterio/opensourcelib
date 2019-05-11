package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class SwUpgrade extends BaseConfig {
    int offset
    Boolean enabled

    public SwUpgrade(int offset, Boolean enabled) throws IllegalArgumentException {
        this.enabled = enabled ?: false
        this.offset = offset
    }

    public static SwUpgrade getTestData() {
        return new SwUpgrade(3, true)
    }
}
