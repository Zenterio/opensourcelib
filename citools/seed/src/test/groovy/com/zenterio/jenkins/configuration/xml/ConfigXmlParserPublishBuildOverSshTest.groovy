package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.ConfigError
import com.zenterio.jenkins.configuration.PublishBuildOverSSH

class ConfigXmlParserPublishBuildOverSSHTest extends GroovyTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    @Override
    protected void setUp() throws Exception {
        this.xp = new XmlParser(false,true)
        this.parser = new ConfigXmlParser()
    }

    protected PublishBuildOverSSH parse(String xml) {
        return this.parser.parse(this.xp.parseText(xml))
    }

    void testParseWithAllAttributesValid() {
        def xml = """<publish-build-over-ssh server="SERVER"
                      artifact-pattern="ARTIFACT"
                      root-dir="ROOT_DIR"
                      number-of-builds-to-keep="1"
                      product-alt-name="PRODUCT"
                      enabled="false" retry-times="2"
                      retry-delay-ms="111"
                      label="LABEL" />"""
        PublishBuildOverSSH result = this.parse(xml)

        assert !result.enabled
        assert result.server == 'SERVER'
        assert result.artifactPattern == 'ARTIFACT'
        assert result.rootDir == 'ROOT_DIR'
        assert result.numberOfBuildsToKeep == 1
        assert result.productAltName == 'PRODUCT'
        assert result.retryTimes == 2
        assert result.retryDelay == 111
        assert result.label == 'LABEL'
    }
}
