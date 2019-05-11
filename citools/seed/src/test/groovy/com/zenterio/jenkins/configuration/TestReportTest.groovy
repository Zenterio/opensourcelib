package com.zenterio.jenkins.configuration

class TestReportTest extends GroovyTestCase {

    public void testEqual() {
        TestReport tr1 = TestReport.testData
        TestReport tr2 = TestReport.testData
        assert !tr1.is(tr2)
        assert tr1 == tr2
    }
}
