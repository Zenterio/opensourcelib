package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Variable extends BaseConfig {

    String name
    String value

    public Variable(String name, String value) {
        this.name = name
        this.value = value
    }

    public static Variable getTestData() {
        return new Variable("name", "value")
    }
}
