package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.WorkspaceBrowsing

class ConfigXmlParserWorkspaceBrowsingTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    /**
     * Explicitly enabled
     */
    void testParseWorkspaceBrowsingExplicitlyEnabled() {
        def xml = """<workspace-browsing enabled="true"/>"""
        def parsedXml = xp.parseText(xml)
        WorkspaceBrowsing result = this.parser.parse(parsedXml)
        assert result.enabled == true
    }

    /**
     * Disabled
     */
    void testParseWorkspaceBrowsingDisabled() {
        def xml = """<workspace-browsing enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        WorkspaceBrowsing result = this.parser.parse(parsedXml)
        assert result.enabled == false
    }
}


