package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.CredentialType
import com.zenterio.jenkins.configuration.TestGroup

class ConfigXmlParserTestGroupTest extends GroovyTestCase
{
    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    private TestGroup parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

    void testParseMinimalTestGroup() {
        String xml="""
<test-group name="NAME" type="kazam" test-root="test root" stb-label="box label"
box-configuration="box config" product-configuration="product configuration">
<repository name="repo"/>
<test-context/>
</test-group>
"""
        TestGroup result = this.parse(xml)
        assert result.name == "NAME"
        assert result.description == null
        assert result.testRoot == "test root"
        assert result.stbLabel == "box label"
        assert result.boxConfiguration == "box config"
        assert result.productConfiguration == "product configuration"
        assert result.enabled == true
        assert result.credentials.size() == 0
        assert result.coredumpHandling == true
        assert result.epgs.length == 0
        assert result.image == null
        assert result.logParsing == null
        assert result.repositories.length == 1
        assert result.testContexts.length == 1
    }

    void testParseFullTestGroup() {
        String xml="""
<test-group name="NAME" type="kazam" test-root="root test" stb-label="label box"
            box-configuration="box config"
            product-configuration="product configuration"
            coredump-handling="false"
            enabled="false">
    <publish-over-ssh enabled="false"/>
    <publish-test-report-over-ssh enabled="false" />
    <build-timeout enabled="false"/>
    <credential type="text" variable-name="TEXT_VAR_NAME" id="TEXT_ID"/>
    <credential type="file" variable-name="FILE_VAR_NAME" id="FILE_ID"/>
    <custom-build-step enabled="false" />
    <description>A description</description>
    <epg/>
    <epg/>
    <image artifact="kfs.zmg"/>
    <log-parsing config="config_file.cfg"/>
    <resources name="a1"/>
    <repository name="repo1"/>
    <repository name="repo2"/>
    <retention-policy duration="infinite" />
    <test-context/>
    <test-context/>
    <test-report type="junit" />
    <variable name="var-name">var-value</variable>
    <watcher name="name" email="email"/>
    <workspace-browsing enabled="false" />
</test-group>
"""
        TestGroup result = this.parse(xml)
        assert result.name == "NAME"
        assert result.testRoot == "root test"
        assert result.stbLabel == "label box"
        assert result.enabled == false

        assert result.publishOverSSHList.size() == 2
        assert result.buildTimeout.enabled == false
        assert result.credentials.size() == 2
        assert result.credentials[0].type == CredentialType.TEXT
        assert result.credentials[0].variableName == "TEXT_VAR_NAME"
        assert result.credentials[0].id == "TEXT_ID"
        assert result.credentials[1].type == CredentialType.FILE
        assert result.credentials[1].variableName == "FILE_VAR_NAME"
        assert result.credentials[1].id == "FILE_ID"
        assert result.customBuildSteps.size() == 1
        assert result.description.description == "A description"
        assert result.coredumpHandling == false
        assert result.epgs.length == 2
        assert result.image.artifact == "kfs.zmg"
        assert result.logParsing.configurationFile == "config_file.cfg"
        assert result.resources.enabled == true
        assert result.repositories.length == 2
        assert result.retentionPolicy.numToKeep == -1
        assert result.testContexts.length == 2
        assert result.testContexts[0].coredumpHandling == null
        assert result.testContexts[1].coredumpHandling == null
        assert result.boxConfiguration == "box config"
        assert result.productConfiguration == "product configuration"
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
        assert result.watchers.size() == 1
        assert result.workspaceBrowsing.enabled == false
    }
}
