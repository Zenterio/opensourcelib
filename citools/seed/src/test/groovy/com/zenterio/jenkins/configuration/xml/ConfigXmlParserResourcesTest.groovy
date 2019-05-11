package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Resources

class ConfigXmlParserResourcesTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false, true)
        this.parser = new ConfigXmlParser()
    }

    public void testEnabledResources() {
        def xml = """<resources enabled="true" name="a1"/>"""
        Resources resources = this.parse(xml)
        assert resources.enabled == true
    }

    public void testDisabledResources() {
        def xml = """<resources enabled="false"/>"""
        Resources resources = this.parse(xml)
        assert resources.enabled == false
    }

    public void testEnabledResourcesIsDefault() {
        def xml = """<resources name="a1"/>"""
        Resources resources = this.parse(xml)
        assert resources.enabled == true
    }

    public void testResourcesWithName() {
        def xml = """<resources name="a1"/>"""
        Resources resources = this.parse(xml)
        assert resources.name == "a1"
    }

    public void testResourcesWithLabel() {
        def xml = """<resources label="a"/>"""
        Resources resources = this.parse(xml)
        assert resources.label == "a"
    }

    public void testResourcesWithQuanitity() {
        def xml = """<resources label="a" quantity="4"/>"""
        Resources resources = this.parse(xml)
        assert resources.quantity == 4
    }

    public void testFailWhenQuanitityNotInteger() {
        def xml = """<resources label="a" quantity="not integer"/>"""
        shouldFail {
            this.parse(xml)
        }
    }

    public void testFailWhenNoneOfNameOrLabelSpecified() {
        def xml = """<resources/>"""
        shouldFail {
            this.parse(xml)
        }
    }

    public void testFailWhenNameAndLabelSpecified() {
        def xml = """<resources name="a1" label="a"/>"""
        shouldFail {
            this.parse(xml)
        }
    }

    private Resources parse(String xml) {
        def parsedXml = this.xp.parseText(xml)
        return this.parser.parse(parsedXml)
    }

}
