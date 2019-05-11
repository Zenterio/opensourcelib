package com.zenterio.jenkins.configuration

class OriginTest extends GroovyTestCase {

    public void testDeepClone() {
        Origin origin = Origin.testData

        shouldFail(CloneNotSupportedException) {
            def clone = origin.clone()
        }
    }

}
