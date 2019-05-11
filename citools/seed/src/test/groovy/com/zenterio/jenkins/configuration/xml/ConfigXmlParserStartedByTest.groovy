package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.StartedBy

class ConfigXmlParserStartedByTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false, true)
        this.parser = new ConfigXmlParser()
    }

    public void testEnabledStartedBy() {
        def xml = """<started-by enabled="true"/>"""
        StartedBy startedBy = this.parse(xml)
        assert startedBy.enabled == true
    }

    public void testDisabledStartedBy() {
        def xml = """<started-by enabled="false"/>"""
        StartedBy startedBy = this.parse(xml)
        assert startedBy.enabled == false
    }

    public void testEnabledStartedByIsDefault() {
        def xml = """<started-by/>"""
        StartedBy startedBy = this.parse(xml)
        assert startedBy.enabled == true
    }

    private StartedBy parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

}
