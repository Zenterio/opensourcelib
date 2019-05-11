package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class TestReport extends BaseConfig {

    TestReportType type

    /**
     *
     * @param type    The type of the test report
     */
    public TestReport(TestReportType type) {
        this.type = type
    }

    public static TestReport getTestData() {
        return new TestReport(TestReportType.JUNIT)
    }
}
