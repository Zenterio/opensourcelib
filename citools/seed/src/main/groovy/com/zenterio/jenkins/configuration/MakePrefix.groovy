package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class MakePrefix extends BaseConfig {

    String value

    MakePrefix(String value) {
        this.value = value ?: ""
    }

    public static MakePrefix getTestData() {
        return new MakePrefix("Test Prefix")
    }
}
