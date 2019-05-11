package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.TestSuite

class ConfigXmlParserTestSuiteTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseTestSuite() {
        def xml="""<test-suite path="PATH"/>"""
        def parsedXml = xp.parseText(xml)
        TestSuite result = this.parser.parse(parsedXml)
        assert result.path == "PATH"
    }
}


