package com.zenterio.jenkins.configuration

class PublishTestReportOverSSHTest extends GroovyTestCase {

    public void testDeepClone() {
        PublishTestReportOverSSH data = PublishTestReportOverSSH.testData
        PublishTestReportOverSSH clone = data.clone()

        assert data == clone
        assert !data.is(clone)
    }

    public void testDefaultValues() {
        PublishTestReportOverSSH publish =
            new PublishTestReportOverSSH(null, 'name', 'server', "reportFile.xml", null,
                                         "suite", null, null, null)
        assert publish.enabled
        assert publish.name == 'name'
        assert publish.server == 'server'
        assert publish.reportFilePattern == 'reportFile.xml'
        assert publish.removePrefix == ''
        assert publish.suiteName == 'suite'
        assert publish.retryTimes == 0
    }

}
