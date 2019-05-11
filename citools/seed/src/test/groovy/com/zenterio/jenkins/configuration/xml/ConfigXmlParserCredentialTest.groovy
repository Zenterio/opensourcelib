package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConfigError
import com.zenterio.jenkins.configuration.Credential
import com.zenterio.jenkins.configuration.CredentialType

class ConfigXmlParserCredentialTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false, true)
        this.parser = new ConfigXmlParser()
    }

    public void testTextCredential() {
        def xml = """<credential type="text" id="text-id"/>"""
        Credential credential = this.parse(xml)
        assert credential.type == CredentialType.TEXT
        assert credential.id == "text-id"
        assert credential.enabled == true
    }

    public void testFileCredential() {
        def xml = """<credential type="file" id="file-id"/>"""
        Credential credential = this.parse(xml)
        assert credential.type == CredentialType.FILE
        assert credential.id == "file-id"
        assert credential.enabled == true
    }

    public void testUsernamePasswordCredential() {
        def xml = """<credential type="username-password" id="username-password-id"/>"""
        Credential credential = this.parse(xml)
        assert credential.type == CredentialType.USERNAME_PASSWORD
        assert credential.id == "username-password-id"
        assert credential.enabled == true
    }

    public void testCanBeDisabled() {
        def xml = """<credential type="text" id="text-id" enabled="false"/>"""
        Credential credential = this.parse(xml)
        assert credential.type == CredentialType.TEXT
        assert credential.id == "text-id"
        assert credential.enabled == false
    }

    public void testThrowsOnInvalidType() {
        def xml = """<credential type="invalid" id="id"/>"""
        shouldFail(IllegalArgumentException) {
            this.parse(xml)
        }
    }

    private Credential parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

}
