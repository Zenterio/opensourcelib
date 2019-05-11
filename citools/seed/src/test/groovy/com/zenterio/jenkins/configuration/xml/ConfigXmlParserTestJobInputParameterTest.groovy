package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Image
import com.zenterio.jenkins.configuration.TestJobInputParameter

class ConfigXmlParserTestJobInputParameterTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseTestJobInputParameter() {
        def xml="""<test-job-input-parameter name="NAME" default="DEFAULT" description="DESCRIPTION"/>"""
        def parsedXml = xp.parseText(xml)
        TestJobInputParameter result = this.parser.parse(parsedXml)
        assert result.name == "NAME"
        assert result.defaultValue == "DEFAULT"
        assert result.description == "DESCRIPTION"
    }

    void testParseTestJobInputParameterWithoutDescription() {
        def xml="""<test-job-input-parameter name="NAME" default="DEFAULT"/>"""
        def parsedXml = xp.parseText(xml)
        TestJobInputParameter result = this.parser.parse(parsedXml)
        assert result.name == "NAME"
        assert result.defaultValue == "DEFAULT"
        assert result.description == null
    }
}


