package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConfigError
import com.zenterio.jenkins.configuration.PublishTestReportOverSSH

class ConfigXmlParserPublishTestReportOverSSHTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    @Override
    protected void setUp() throws Exception {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    protected PublishTestReportOverSSH parse(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    void testParseWithAllAttributesValid() {
        def xml = """<publish-test-report-over-ssh server="SERVER"
                      report-file-pattern="REPORT"
                      suite-name="SUITE"
                      enabled="false" retry-times="2"
                      retry-delay-ms="111"
                      label="LABEL" />"""
        PublishTestReportOverSSH result = this.parse(xml)

        assert !result.enabled
        assert result.server == 'SERVER'
        assert result.reportFilePattern == 'REPORT'
        assert result.suiteName == 'SUITE'
        assert result.retryTimes == 2
        assert result.retryDelay == 111
        assert result.label == 'LABEL'
    }
}
