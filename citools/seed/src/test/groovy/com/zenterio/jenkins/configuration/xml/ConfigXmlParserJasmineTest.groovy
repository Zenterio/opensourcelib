package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Jasmine

class ConfigXmlParserJasmineTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    public void testDefaultAttributes() {
        def xml = '<jasmine repository="repo" config-file="conf.json" />'
        def parsedXml = xp.parseText(xml)
        Jasmine jasmine = parser.parseJasmine(parsedXml)
        assert jasmine.repository == 'repo'
        assert jasmine.configFile == 'conf.json'
        assert jasmine.disableRCU
        assert jasmine.disableRCUCheck
    }

    public void testExplicitAttributes() {
        def xml = '<jasmine repository="repo2" config-file="other_conf.json" disable-rcu="false" disable-rcu-check="false" />'
        def parsedXml = xp.parseText(xml)
        Jasmine jasmine = parser.parseJasmine(parsedXml)
        assert jasmine.repository == 'repo2'
        assert jasmine.configFile == 'other_conf.json'
        assert !jasmine.disableRCU
        assert !jasmine.disableRCUCheck
    }
}
