package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.BuildTimeout
import com.zenterio.jenkins.configuration.BuildTimeoutPolicy;
import com.zenterio.jenkins.configuration.ConfigError

class ConfigXmlParserBuildTimeoutTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    /**
     * Check that and illegal policystring is an error
     */
    void testParseBuildBadPolicyThrowException() {
        def xml = """<build-timeout policy="bad_policy" minutes="0" />"""
        def parsedXml = xp.parseText(xml)
        shouldFail(ConfigError) {
            BuildTimeout result = this.parser.parse(parsedXml)
        }
    }

    /**
     * enabled=false
     */
    void testParseBuildTimeoutDisabled() {
        def xml = """<build-timeout enabled="false" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml) as BuildTimeout
        assert !result.enabled
    }

    /**
     * Check absolute policy
     * This requires that minutes is set and an integer
     */
    void testParseBuildTimeoutAbsolute() {
        def xml = """<build-timeout policy="absolute" minutes="5" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ABSOLUTE
        assert result.minutes == 5
        assert result.failBuild == false
        assert result.configurable == false
        assert result.enabled
    }

    /**
     * Check elastic policy
     * This requires that minutes is set and an integer
     */
    void testParseBuildTimeoutElastic() {
        def xml = """<build-timeout policy="elastic" minutes="5" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ELASTIC
        assert result.minutes == 5
        assert result.failBuild == false
        assert result.configurable == false
        assert result.enabled
    }

    /**
     * Check that we can explicitly set fail-build to false
     */
    void testParseBuildTimeoutFailFalse() {
        def xml = """<build-timeout policy="absolute" minutes="5" fail-build="false" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ABSOLUTE
        assert result.minutes == 5
        assert result.failBuild == false
        assert result.configurable == false
        assert result.enabled
    }

    /**
     * Check that we can explicitly set fail-build to true
     */
    void testParseBuildTimeoutFailTrue() {
        def xml = """<build-timeout policy="absolute" minutes="5" fail-build="true" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ABSOLUTE
        assert result.minutes == 5
        assert result.failBuild == true
        assert result.configurable == false
        assert result.enabled
    }

    /**
     * Check that we can explicitly set configurable to false
     */
    void testParseBuildTimeoutConfigurableFalse() {
        def xml = """<build-timeout policy="absolute" minutes="5" configurable="false" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ABSOLUTE
        assert result.minutes == 5
        assert result.failBuild == false
        assert result.configurable == false
        assert result.enabled
    }

    /**
     * Check that we can explicitly set configurable to true
     */
    void testParseBuildTimeoutConfigurableTrue() {
        def xml = """<build-timeout policy="absolute" minutes="5" configurable="true" />"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ABSOLUTE
        assert result.minutes == 5
        assert result.failBuild == false
        assert result.configurable == true
        assert result.enabled
    }

    /**
     * Check that we can explicitly set all configuration options to non-standard values
     */
    void testParseBuildTimeoutSetAllOptions() {
        def xml = """<build-timeout policy="absolute" minutes="10" configurable="true" fail-build="true"/>"""
        def parsedXml = xp.parseText(xml)
        BuildTimeout result = this.parser.parse(parsedXml)
        assert result.policy == BuildTimeoutPolicy.ABSOLUTE
        assert result.minutes == 10
        assert result.failBuild == true
        assert result.configurable == true
        assert result.enabled
    }

    /**
     * Check that minutes not a valid integer is an error
     */
    void testParseBuildNonIntegerMinutesThrowException() {
        def xml = """<build-timeout policy="absolute" minutes="five" />"""
        def parsedXml = xp.parseText(xml)
        shouldFail(IllegalArgumentException) {
            BuildTimeout result = this.parser.parse(parsedXml)
        }
    }

    /**
     * Check that missing minutes is an error
     */
    void testParseBuildNoMinutesThrowException() {
        def xml = """<build-timeout policy="absolute" />"""
        def parsedXml = xp.parseText(xml)
        shouldFail(IllegalArgumentException) {
            BuildTimeout result = this.parser.parse(parsedXml)
        }
    }
}
