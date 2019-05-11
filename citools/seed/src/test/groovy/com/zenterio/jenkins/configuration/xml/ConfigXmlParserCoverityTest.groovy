package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.buildtype.BuildTypeDebug
import com.zenterio.jenkins.buildtype.BuildTypeProduction
import com.zenterio.jenkins.buildtype.BuildTypeRelease
import com.zenterio.jenkins.configuration.ConfigError
import com.zenterio.jenkins.configuration.CredentialType
import com.zenterio.jenkins.configuration.Upstream
import com.zenterio.jenkins.configuration.Aggressiveness
import groovy.util.XmlParser

import com.zenterio.jenkins.configuration.Coverity

class ConfigXmlParserCoverityTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    protected Coverity parseCoverity(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    /**
     * Valid attributes: stream : string, enabled: bool
     */
    void testParseCoverityWithStreamAndEnabled() {
        def xml = """<coverity stream="STREAM" enabled="true"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.stream == "STREAM"
        assert result.enabled == true
    }

    /**
     * If only stream is provided, Coverity is enabled.
     */
    void testParseCoverityWithOnlyStream() {
        def xml = """<coverity stream="STREAM" />"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == "STREAM"
    }

    /**
     * Coverity can be disabled even with valid stream
     */
    void testParseCoverityWithStreamAndDisabled() {
        def xml = """<coverity stream="STREAM" enabled="false"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == false
        assert result.stream == "STREAM"
    }

    /**
     * If tag is used without attributes, Coverity will be enabled
     * with empty string stream.
     */
    void testParseDefaultAttributesIfTagPresent() {
        def xml = """<coverity />"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.upstream == Upstream.TRUE
        assert result.aggressiveness == Aggressiveness.LOW
        assert result.buildType.class == BuildTypeDebug
    }

    void testParseCoverityUpstreamFalse() {
        def xml = """<coverity upstream="false"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.upstream == Upstream.FALSE
    }

    void testParseCoverityUpstreamAsync() {
        def xml = """<coverity upstream="async"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.upstream == Upstream.ASYNC
    }

    void testParseCoverityUpstreamTrue() {
        def xml = """<coverity upstream="true"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.upstream == Upstream.TRUE
    }

    void testParseCoverityAggressivenessLow() {
        def xml = """<coverity aggressiveness-level="low"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.aggressiveness == Aggressiveness.LOW
    }

    void testParseCoverityAggressivenessMedium() {
        def xml = """<coverity aggressiveness-level="medium"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.aggressiveness == Aggressiveness.MEDIUM
    }

    void testParseCoverityAggressivenessHigh() {
        def xml = """<coverity aggressiveness-level="high"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.aggressiveness == Aggressiveness.HIGH
    }

    void testParseCoverityBuildTypeDebug() {
        def xml = """<coverity build-type="debug"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.buildType.class == BuildTypeDebug
    }

    void testParseCoverityBuildTypeProduction() {
        def xml = """<coverity build-type="production"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.buildType.class == BuildTypeProduction
    }

    void testParseCoverityBuildTypeRelease() {
        def xml = """<coverity build-type="release"/>"""
        Coverity result = this.parseCoverity(xml)
        assert result.enabled == true
        assert result.stream == ""
        assert result.buildType.class == BuildTypeRelease
    }

    /**
     *
     */
    void testParseCoverityInvalidAttributesThrowsException() {
        def xml = """<coverity enabled="true" upstream="wrong" />"""
        try {
            Coverity result = this.parseCoverity(xml)
        } catch (ConfigError e) {
            assert e.getMessage() == "Bad upstream attribute (wrong), should be true, false or async"
        }
    }

    /**
     *
     **/
    void testParseCoverityWithMultipleCustomBuildSteps() {
        String xml = """\
<coverity>
<custom-build-step>step1</custom-build-step>
<custom-build-step>step2</custom-build-step>
</coverity>"""

        Coverity result = this.parseCoverity(xml)
        assert result?.customBuildSteps?.size() == 2
        assert result.customBuildSteps[0].code == "step1"
        assert result.customBuildSteps[1].code == "step2"
    }

    void testParseCoverityWithCredential() {
        String xml = """\
<coverity>
    <credential type="text" variable-name="TEXT_VAR_NAME" id="TEXT_ID"/>
    <credential type="file" variable-name="FILE_VAR_NAME" id="FILE_ID"/>
    <credential type="username-password" variable-name="UP_VAR_NAME" id="UP_ID"/>
</coverity>"""
        Coverity result = this.parseCoverity(xml)
        assert result.credentials[0].id == "TEXT_ID"
        assert result.credentials[0].variableName == "TEXT_VAR_NAME"
        assert result.credentials[0].type == CredentialType.TEXT

        assert result.credentials[1].id == "FILE_ID"
        assert result.credentials[1].variableName == "FILE_VAR_NAME"
        assert result.credentials[1].type == CredentialType.FILE

        assert result.credentials[2].id == "UP_ID"
        assert result.credentials[2].variableName == "UP_VAR_NAME"
        assert result.credentials[2].type == CredentialType.USERNAME_PASSWORD
    }

    void testParseCoverityWithoutCredential() {
        String xml = """\
<coverity></coverity>"""
        Coverity result = this.parseCoverity(xml)
        assert result.credentials.size() == 0
    }

    void testParseVariables() {
        String xml = """\
<coverity>
    <variable name="var-name">var-value</variable>
</coverity>"""
        Coverity result = this.parseCoverity(xml)
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
    }

    void testParseCoverityWithResources() {
        def xml = """<coverity><resources name="a"/></coverity>"""
        Coverity result = this.parseCoverity(xml)
        assert result.resources.enabled == true
    }
    
    void testParseCoverityWithBuildEnv() {
        String xml = """\
<coverity>
    <build-env enabled="true" env="image"/>
</coverity>"""

        Coverity result = this.parseCoverity(xml)
        assert result.buildEnv.enabled == true
        assert result.buildEnv.env == "image"
    }
}
