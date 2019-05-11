package com.zenterio.jenkins.configuration.xml

import groovy.util.XmlParser

import com.zenterio.jenkins.configuration.ReleasePackaging
import com.zenterio.jenkins.configuration.BuildTimeout
import com.zenterio.jenkins.configuration.BuildTimeoutPolicy
import com.zenterio.jenkins.configuration.Repository

class ConfigXmlParserReleasePackagingTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    protected ReleasePackaging parseReleasePackaging(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    /**
     * If tag is used without attributes, ReleasePackaging will be enabled
     * with no custom build-steps.
     */
    void testParseDefaultAttributesIfTagPresent() {
        def xml = """<release-packaging />"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.configurable == true
        assert result.enabled == true
        assert result.customBuildSteps?.size() == 0
        assert result.buildTimeout == null
    }

    /**
     * Non-configurable
     */
     void testParseConfigurable() {
         def xml = """<release-packaging configurable="false"/>"""
         ReleasePackaging result = this.parseReleasePackaging(xml)
         assert result.configurable == false
     }

    /**
     * Disabled
     */
    void testParseDisabled() {
        def xml = """<release-packaging enabled="false"/>"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.enabled == false
    }

    /**
     * Custom build steps
     **/
    void testParseReleasePackagingWithMultipleCustomBuildSteps() {
        String xml = """\
<release-packaging>
<custom-build-step>step1</custom-build-step>
<custom-build-step>step2</custom-build-step>
</release-packaging>"""

        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result?.customBuildSteps?.size() == 2
        assert result.customBuildSteps[0].code == "step1"
        assert result.customBuildSteps[1].code == "step2"
    }

    /**
     * Publish over SSH
     */
    void testParseReleasePackagingWithPublishOverSsh() {
        String xml = """
<release-packaging>
<publish-over-ssh server="SERVER" >
<transfer-set src="src"/>
</publish-over-ssh>
</release-packaging>"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.publishOverSSHList.size() == 1
    }

    /**
     * Build timeout
     */
    void testParseReleasePackagingWithBuildTimeout() {
        String xml = """
<release-packaging>
<build-timeout policy="absolute" minutes="5" />
</release-packaging>"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.buildTimeout == new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 5)
    }

    /**
     * Description
     */
    void testParseReleasePackagingWihDescription() {
        String xml = "<release-packaging><description>DESC</description></release-packaging>"
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.description.description == "DESC"
    }

    /**
     * Credentials
     */
    void testParseReleasePackagingWithCredentials() {
        String xml = """
<release-packaging>
    <credential type="text" variable-name="TEXT_VAR_NAME" id="TEXT_ID"/>
</release-packaging>"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.credentials[0].variableName == "TEXT_VAR_NAME"
    }

    /**
     * Repositories
     */
    void testParseReleasePackagingWithRepositories() {
        String xml = """
<release-packaging>
    <repository name="NAME" dir="DIR" remote="REMOTE" branch="BRANCH"/>
</release-packaging>"""
                ReleasePackaging result = this.parseReleasePackaging(xml)
                Repository p = result.repositories[0]
                assert p.name == "NAME"
                assert p.directory == "DIR"
                assert p.branch == "BRANCH"
                assert p.remote == "REMOTE"
    }

    void testParseVariables() {
        String xml = """\
    <release-packaging>
        <variable name="var-name">var-value</variable>
    </release-packaging>"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
    }

    void testParseCoverityWithResources() {
        String xml = """\
    <release-packaging>
        <resources name="a1"/>
    </release-packaging>"""
        ReleasePackaging result = this.parseReleasePackaging(xml)
        assert result.resources.enabled == true
    }
}
