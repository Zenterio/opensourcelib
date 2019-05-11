package com.zenterio.jenkins.configuration.xml

import groovy.util.XmlParser;

import com.zenterio.jenkins.configuration.Epg;

class ConfigXmlParserEpgTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseEpg() {
        def xml="""<epg path="PATH"/>"""
        def parsedXml = xp.parseText(xml)
        Epg result = this.parser.parse(parsedXml)
        assert result.path == "PATH"
    }
}


