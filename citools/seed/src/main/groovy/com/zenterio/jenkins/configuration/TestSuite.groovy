package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class TestSuite extends BaseConfig {
    String path

    public TestSuite(String path) {
        this.path = path
    }

    public static TestSuite getTestData() {
        return new TestSuite("TestSuite")
    }
}
