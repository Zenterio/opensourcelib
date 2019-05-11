package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class TestJobInputParameter extends BaseConfig {
    String name
    String defaultValue
    String description

    public TestJobInputParameter(String name, String defaultValue, String description) {
        this.name = name
        this.defaultValue = defaultValue
        this.description = description
    }

    public static TestJobInputParameter getTestData() {
        return new TestJobInputParameter("NAME", "default", "description")
    }
}
