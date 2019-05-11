package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Variable

class ConfigXmlParserVariableTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false, true)
        this.parser = new ConfigXmlParser()
    }

    public void testVariable() {
        def xml = """<variable name="NAME">VALUE</variable>"""
        Variable variable = this.parse(xml)
        assert variable.name == "NAME"
        assert variable.value == "VALUE"
    }

    private Variable parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

}
