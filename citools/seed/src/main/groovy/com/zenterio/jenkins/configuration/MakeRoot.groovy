package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class MakeRoot extends BaseConfig {

    String name

    MakeRoot(String name) {
        this.name = name ?: ""
    }

    public static MakeRoot getTestData() {
        return new MakeRoot("Test Root")
    }
}
