package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Incremental

class ConfigXmlParserIncrementalTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    protected Incremental parse(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    /**
     * Implicitly enabled
     */
    void testParseIncrementalImplicitlyEnabled() {
        def xml = """<incremental/>"""
        Incremental result = this.parse(xml)
        assert result.enabled == true
    }

    /**
     * Explicitly enabled
     */
    void testParseIncrementalExplicitlyEnabled() {
        def xml = """<incremental enabled="true"/>"""
        Incremental result = this.parse(xml)
        assert result.enabled == true
    }

    /**
     * Disabled
     */
    void testParseIncrementalDisabled() {
        def xml = """<incremental enabled="false"/>"""
        Incremental result = this.parse(xml)
        assert result.enabled == false
    }

    void testParseIncrementalWithCcache() {
        def xml = """<incremental><cache/></incremental>"""
        Incremental result = this.parse(xml)
        assert result.enabled == true
        assert result.cache.ccacheEnabled == true
    }

    void testParseIncrementalWithResources() {
        def xml = """<incremental><resources name="a"/></incremental>"""
        Incremental result = this.parse(xml)
        assert result.enabled == true
        assert result.resources.enabled == true
    }

    void testParseVariables() {
        String xml = """\
<incremental>
    <variable name="var-name">var-value</variable>
</incremental>"""
        Incremental result = this.parse(xml)
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
    }
}
