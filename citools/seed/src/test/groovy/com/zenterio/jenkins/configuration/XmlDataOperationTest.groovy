package com.zenterio.jenkins.configuration

class XmlDataOperationTest extends GroovyTestCase {

    public void testStringConversion() {
        XmlDataOperation.values().each({ XmlDataOperation op ->
            assert XmlDataOperation.getFromString("${op}") == op
        })
    }
}
