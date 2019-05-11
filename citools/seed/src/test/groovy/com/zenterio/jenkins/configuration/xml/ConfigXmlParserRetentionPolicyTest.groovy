package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.RetentionPolicy

class ConfigXmlParserRetentionPolicyTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }


    void testShortDurationDefaultSaveArtifacts() {
        def xml = """<retention-policy duration="short"/>"""
        def parsedXml = xp.parseText(xml)
        RetentionPolicy policy = this.parser.parse(parsedXml) as RetentionPolicy
        assert policy.daysToKeep == -1
        assert policy.numToKeep == 10
        assert policy.artifactDaysToKeep == -1
        assert policy.artifactNumToKeep == 10
    }

    void testMediumDurationDefaultSaveArtifacts() {
        def xml = """<retention-policy duration="medium"/>"""
        def parsedXml = xp.parseText(xml)
        RetentionPolicy policy = this.parser.parse(parsedXml) as RetentionPolicy
        assert policy.daysToKeep == -1
        assert policy.numToKeep == 30
        assert policy.artifactDaysToKeep == -1
        assert policy.artifactNumToKeep == 30
    }

    void testLongDurationSaveArtifactsIsTrue() {
        def xml = """<retention-policy duration="long" save-artifacts="true"/>"""
        def parsedXml = xp.parseText(xml)
        RetentionPolicy policy = this.parser.parse(parsedXml) as RetentionPolicy
        assert policy.daysToKeep == -1
        assert policy.numToKeep == 100
        assert policy.artifactDaysToKeep == -1
        assert policy.artifactNumToKeep == 100
    }

    void testVeryLongDurationSaveArtifactsIsFalse() {
        def xml = """<retention-policy duration="very-long" save-artifacts="false"/>"""
        def parsedXml = xp.parseText(xml)
        RetentionPolicy policy = this.parser.parse(parsedXml) as RetentionPolicy
        assert policy.daysToKeep == -1
        assert policy.numToKeep == 200
        assert policy.artifactDaysToKeep == -1
        assert policy.artifactNumToKeep == 1
    }

    void testInfiniteDurationDefaultSaveArtifacts() {
        def xml = """<retention-policy duration="infinite"/>"""
        def parsedXml = xp.parseText(xml)
        RetentionPolicy policy = this.parser.parse(parsedXml) as RetentionPolicy
        assert policy.daysToKeep == -1
        assert policy.numToKeep == -1
        assert policy.artifactDaysToKeep == -1
        assert policy.artifactNumToKeep == -1
    }
}
