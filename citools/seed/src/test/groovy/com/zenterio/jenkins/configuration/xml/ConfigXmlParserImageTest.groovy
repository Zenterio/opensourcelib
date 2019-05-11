package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Image

class ConfigXmlParserImageTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseImage() {
        def xml="""<image artifact="PATH"/>"""
        def parsedXml = xp.parseText(xml)
        Image result = this.parser.parse(parsedXml)
        assert result.artifact == "PATH"
        assert result.enabled == true
    }

    void testParseImageDisabled() {
        def xml="""<image enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        Image result = this.parser.parse(parsedXml)
        assert result.enabled == false
    }
}


