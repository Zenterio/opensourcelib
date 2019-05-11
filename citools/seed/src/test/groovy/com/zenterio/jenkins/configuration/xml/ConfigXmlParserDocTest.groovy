package com.zenterio.jenkins.configuration.xml

import groovy.util.XmlParser;

import com.zenterio.jenkins.configuration.Doc;

class ConfigXmlParserDocTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    /**
     * Implicitly enabled
     */
    void testParseDocImplicitlyEnabled() {
        def xml = """<doc/>"""
        def parsedXml = xp.parseText(xml)
        Doc result = this.parser.parse(parsedXml)
        assert result.enabled == true
        assert result.customBuildSteps.size() == 0
    }

    /**
     * Explicitly enabled
     */
    void testParseDocExplicitlyEnabled() {
        def xml = """<doc enabled="true"/>"""
        def parsedXml = xp.parseText(xml)
        Doc result = this.parser.parse(parsedXml)
        assert result.enabled == true
        assert result.customBuildSteps.size() == 0
    }

    /**
     * Disabled
     */
    void testParseDocDisabled() {
        def xml = """<doc enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        Doc result = this.parser.parse(parsedXml)
        assert result.enabled == false
        assert result.customBuildSteps.size() == 0
    }

    /**
     * Using custom build steps.
     */
    void testParseFullDoc() {
        def xml = """\
<doc enable="true">
    <publish-build-over-ssh enabled="false" />
    <publish-over-ssh enabled="false" />
    <build-env enabled="false" />
    <credential type="text" variable-name="TEXT_VAR_NAME" id="TEXT_ID"/>
    <custom-build-step />
    <custom-build-step />
    <make-prefix value="makeprefix"/>
    <make-root name="makeroot"/>
    <make-target name="maketarget"/>
    <resources name="a1"/>
    <variable name="var-name">var-value</variable>
</doc>
"""
        def parsedXml = xp.parseText(xml)
        Doc result = this.parser.parse(parsedXml)
        assert result.enabled == true
        assert result.publishOverSSHList.size() == 2
        assert result.buildEnv.enabled == false
        assert result.credentials[0].variableName == "TEXT_VAR_NAME"
        assert result.customBuildSteps.size() == 2
        assert result.makePrefix.value == "makeprefix"
        assert result.makeRoot.name == "makeroot"
        assert result.makeTarget.name == "maketarget"
        assert result.resources.enabled == true
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
    }
}
