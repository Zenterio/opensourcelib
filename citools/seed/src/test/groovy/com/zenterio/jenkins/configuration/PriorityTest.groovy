package com.zenterio.jenkins.configuration

class PriorityTest extends GroovyTestCase {

    public void testStringConversion() {
        Priority.values().each({ Priority level ->
            assert Priority.getFromString("${level}") == level
        })
    }
}
