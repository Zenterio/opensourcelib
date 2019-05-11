package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class MakeTarget extends BaseConfig {

    String name

    MakeTarget(String name) {
        this.name = name ?: ""
    }

    public static MakeTarget getTestData() {
        return new MakeTarget("Test Target")
    }
}
