package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConfigError
import com.zenterio.jenkins.configuration.PublishOverSSH
import com.zenterio.jenkins.configuration.TransferSet

class ConfigXmlParserPublishOverSSHTest extends GroovyTestCase {

    class StubParseTransferSetParser extends ConfigXmlParser {
        List<Node> nodes = []

        @Override
        TransferSet parseTransferSet(Node node) {
            nodes.add(node)
            return null
        }
    }

    XmlParser xp = null
    ConfigXmlParser parser = null

    @Override
    protected void setUp() throws Exception {
        this.xp = new XmlParser(false,true)
        this.parser = new StubParseTransferSetParser()
    }

    protected PublishOverSSH parse(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    void testParseWithAllAttributesValidAndNoChildren() {
        def xml = """<publish-over-ssh server="SERVER" enabled="false" retry-times="2" retry-delay-ms="111" label="LABEL" />"""
        PublishOverSSH result = this.parse(xml)

        assert result.server == 'SERVER'
        assert !result.enabled
        assert result.retryTimes == 2
        assert result.retryDelay == 111
        assert result.label == 'LABEL'
        assert result.transferSets.size() == 0
    }

    void testParseWithDefaultAttributeValues() {
        def xml = """<publish-over-ssh server="SERVER" />"""
        PublishOverSSH result = this.parse(xml)

        assert result.server == 'SERVER'
        assert result.enabled
        assert result.retryTimes == 0
        assert result.retryDelay == 10000
        assert result.label == ''
        assert result.transferSets.size() == 0
    }

    void testParseChildren() {
        def xml = """<publish-over-ssh server="SERVER" ><transfer-set /><transfer-set /></publish-over-ssh>"""
        PublishOverSSH result = this.parse(xml)
        assert result.transferSets.size() == 2
        assert result.transferSets[0] == null
        assert result.transferSets[0] == null

        StubParseTransferSetParser stub_parser = this.parser as StubParseTransferSetParser
        assert stub_parser.nodes.size() == 2
        assert stub_parser.nodes[0].name() == 'transfer-set'
        assert stub_parser.nodes[1].name() == 'transfer-set'
    }

    void testParseVariables() {
        String xml = """\
<publish-over-ssh server="SERVER">
    <variable name="var-name">var-value</variable>
</publish-over-ssh>"""
        PublishOverSSH result = this.parse(xml)
        assert result.variables[0].name == "var-name"
        assert result.variables[0].value == "var-value"
    }
    void testParseBadChild() {
        def xml = """<publish-over-ssh server="SERVER" ><bad-child /></publish-over-ssh>"""
        shouldFail(ConfigError, {
            this.parse(xml)
        })
    }
}
