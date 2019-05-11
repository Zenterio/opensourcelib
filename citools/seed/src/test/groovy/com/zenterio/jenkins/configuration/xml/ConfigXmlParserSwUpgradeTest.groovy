package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.SwUpgrade
import groovy.util.XmlParser

class ConfigXmlParserSwUpgradeTest extends GroovyTestCase
{

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    void testParseSwUpgrade() {
        def xml="""<sw-upgrade offset="2"/>"""
        def parsedXml = xp.parseText(xml)
        SwUpgrade result = this.parser.parse(parsedXml)
        assert result.offset == 2
        assert result.enabled == true
    }

    void testParseSwUpgradeDisabled() {
        def xml="""<sw-upgrade enabled="false"/>"""
        def parsedXml = xp.parseText(xml)
        SwUpgrade result = this.parser.parse(parsedXml)
        assert result.enabled == false
    }

    void testParseSwUpgradeNonIntegerOffsetShouldFail() {
        def xml="""<sw-upgrade offset="none"/>"""
        def parsedXml = xp.parseText(xml)
        shouldFail(IllegalArgumentException) {
            SwUpgrade result = this.parser.parse(parsedXml)
        }
    }

    void testParseSwUpgradeZeroOffsetShouldFail() {
        def xml="""<sw-upgrade offset="0"/>"""
        def parsedXml = xp.parseText(xml)
        shouldFail(IllegalArgumentException) {
            SwUpgrade result = this.parser.parse(parsedXml)
        }
    }

    void testParseSwUpgradeNegativeOffsetShouldFail() {
        def xml="""<sw-upgrade offset="-4"/>"""
        def parsedXml = xp.parseText(xml)
        shouldFail(IllegalArgumentException) {
            SwUpgrade result = this.parser.parse(parsedXml)
        }
    }
}


