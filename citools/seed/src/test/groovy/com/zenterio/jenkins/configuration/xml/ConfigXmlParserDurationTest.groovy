package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Duration
import groovy.util.XmlParser

class ConfigXmlParserDurationTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseDuration() {
        def xml="""<duration time="06:28:32"/>"""
        def parsedXml = xp.parseText(xml)
        Duration result = this.parser.parse(parsedXml)
        assert result.time == "06:28:32"
    }
}


