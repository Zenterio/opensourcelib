package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConcurrentBuilds

class ConfigXmlParserConcurrentBuildsTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false, true)
        this.parser = new ConfigXmlParser()
    }

    public void testEnabledConcurrent() {
        def xml = """<concurrent-builds enabled="true"/>"""
        ConcurrentBuilds concurrentBuilds = this.parse(xml)
        assert concurrentBuilds.enabled == true
    }

    public void testDisabledConcurrent() {
        def xml = """<concurrent-builds enabled="false"/>"""
        ConcurrentBuilds concurrentBuilds = this.parse(xml)
        assert concurrentBuilds.enabled == false
    }

    public void testDisabledConcurrentIsDefault() {
        def xml = """<concurrent-builds/>"""
        ConcurrentBuilds concurrentBuilds = this.parse(xml)
        assert concurrentBuilds.enabled == true
    }

    private ConcurrentBuilds parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

}
