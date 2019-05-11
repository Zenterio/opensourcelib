package com.zenterio.jenkins.configuration.xml

import com.zenterio.jenkins.configuration.Cache
import com.zenterio.jenkins.configuration.CcacheSize
import org.xml.sax.SAXParseException

class ConfigXmlParserCacheTest extends ConfigXmlParserTestCase {

    XmlParser xp = null
    ConfigXmlParser parser = null

    protected void setUp() {
        super.setUp("cache")
    }

    public void testEnabledCcache() {
        def xml = """<cache ccache-enabled="true"/>"""
        Cache cache = this.parse(xml)
        assert cache.ccacheEnabled == true
    }

    public void testDisabledCcache() {
        def xml = """<cache ccache-enabled="false"/>"""
        Cache cache = this.parse(xml)
        assert cache.ccacheEnabled == false
    }

    public void testEnabledCcacheIsDefault() {
        def xml = """<cache/>"""
        Cache cache = this.parse(xml)
        assert cache.ccacheEnabled == true
    }

    public void testPublishCcache() {
        def xml = """<cache ccache-publish="true"/>"""
        Cache cache = this.parse(xml)
        assert cache.ccachePublish == true
    }

    public void testDoNotPublishCcache() {
        def xml = """<cache ccache-publish="false"/>"""
        Cache cache = this.parse(xml)
        assert cache.ccachePublish == false
    }

    public void testPublishMcache() {
        def xml = """<cache mcache-publish="true"/>"""
        Cache cache = this.parse(xml)
        assert cache.mcachePublish == true
    }

    public void testDoNotPublishMcache() {
        def xml = """<cache mcache-publish="false"/>"""
        Cache cache = this.parse(xml)
        assert cache.mcachePublish == false
    }

    public void testPublishIsDefault() {
        def xml = """<cache/>"""
        Cache cache = this.parse(xml)
        assert cache.ccachePublish == true
        assert cache.mcachePublish == true
    }

    public void testAllConfigurableSizes() {
        for (CcacheSize size: CcacheSize.values()) {
            if (size == CcacheSize.OVER_SIZE) {
                // OVER_SIZE can not be used in configuration.
                continue
            }
            def xml = """<cache ccache-size="${size.toString().toLowerCase()}" />"""
            Cache cache = this.parse(xml)
            assert cache.ccacheSize == size
        }
    }

    public void testOverSizeIsNotAvailableFromConfiguration() {
        def xml = """<cache ccache-size="${CcacheSize.OVER_SIZE.toString().toLowerCase()}">"""
        shouldFail(SAXParseException) {
            this.parse(xml)
        }
    }

    public void testSizeDefaultIsMedium() {
        def xml = """<cache/>"""
        Cache cache = this.parse(xml)
        assert cache.ccacheSize == CcacheSize.MEDIUM
    }

    public void testStorage() {
        String storage = "storage"
        def xml = """<cache ccache-storage="${storage}"/>"""
        Cache cache = this.parse(xml)
        assert cache.ccacheStorage == storage
    }

}
