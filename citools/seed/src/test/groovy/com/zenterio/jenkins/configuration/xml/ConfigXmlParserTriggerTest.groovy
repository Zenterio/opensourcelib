package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Trigger
import groovy.util.XmlParser;


class ConfigXmlParserTriggerTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseTriggerEmpty() {
        def xml = """<trigger />"""
        def parsedXml = xp.parseText(xml)
        Trigger result = this.parser.parse(parsedXml)
        assert result.polling == null
        assert result.periodic == null
        assert result.valid == false
        assert result.enabled == true
    }

    void testParseTriggerDisabled() {
        def xml = """<trigger enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        Trigger result = this.parser.parse(parsedXml)
        assert result.polling == null
        assert result.periodic == null
        assert result.valid == false
        assert result.enabled == false
    }

    void testParseTriggerCustomPoll() {
        def xml = """<trigger polling="custompolling"/>"""
        def parsedXml = xp.parseText(xml)
        Trigger result = this.parser.parse(parsedXml)
        assert result.polling == "custompolling"
        assert result.periodic == null
        assert result.valid == true
        assert result.enabled == true
    }

    void testParseTriggerCustomPerodic() {
        def xml = """<trigger periodic="buildtimes"/>"""
        def parsedXml = xp.parseText(xml)
        Trigger result = this.parser.parse(parsedXml)
        assert result.polling == null
        assert result.periodic == "buildtimes"
        assert result.valid == true
        assert result.enabled == true
    }
}


