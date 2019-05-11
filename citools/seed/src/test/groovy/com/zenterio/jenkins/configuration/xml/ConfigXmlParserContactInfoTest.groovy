package com.zenterio.jenkins.configuration.xml

import groovy.util.XmlParser;

class ConfigXmlParserContactInfoTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null
    final private static subClasses = ["pm", "techlead", "watcher"]

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

   void testParseContactInfo() {
       subClasses.each { subClass ->
            def parsedXml = xp.parseText("""<${subClass} name="NAME" email="EMAIL"/>""")
            def result = this.parser.parse(parsedXml)
            assert result.name == "NAME"
            assert result.email == "EMAIL"
            assert result.emailPolicy == null
        }
    }

    void testParseContactInfoFull() {
        subClasses.each { subClass ->
            String xml = """
<${subClass} name="NAME" email="EMAIL">
<email-policy />
</${subClass}>
"""
            def parsedXml = xp.parseText(xml)
            def result = this.parser.parse(parsedXml)
            assert result.name == "NAME"
            assert result.email == "EMAIL"
            assert result.emailPolicy != null
        }
    }

}


