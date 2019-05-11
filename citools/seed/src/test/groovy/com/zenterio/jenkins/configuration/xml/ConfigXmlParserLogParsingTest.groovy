package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.LogParsing
import groovy.util.XmlParser;


class ConfigXmlParserLogParsingTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseLogParsingEmpty() {
        def xml = """<log-parsing />"""
        def parsedXml = xp.parseText(xml)
        LogParsing result = this.parser.parse(parsedXml)
        assert result.configurationFile == null
        assert result.enabled == true
    }

    void testParseLogParsingDisabled() {
        def xml = """<log-parsing enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        LogParsing result = this.parser.parse(parsedXml)
        assert result.configurationFile == null
        assert result.enabled == false
    }

    void testParseLogParsingImplicitEnable() {
        def xml = """<log-parsing config="config.cfg"/>"""
        def parsedXml = xp.parseText(xml)
        LogParsing result = this.parser.parse(parsedXml)
        assert result.configurationFile == "config.cfg"
        assert result.enabled == true
    }
}


