package com.zenterio.jenkins.configuration

class XmlToCsvTest extends GroovyTestCase {

    public void testDeepClone() {
         XmlToCsv original =  XmlToCsv.testData
         XmlToCsv clone = original.clone()

        assert original == clone
        assert !original.data[0].is(clone.data[0])
    }
}
