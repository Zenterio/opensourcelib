package com.zenterio.jenkins.configuration

class CcacheSizeTest extends GroovyTestCase {

    public void testStringConversion() {
        CcacheSize.values().each({ CcacheSize size ->
            assert CcacheSize.getFromString("${size}") == size
        })
    }
}
