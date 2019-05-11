package com.zenterio.jenkins.configuration

class CustomBuildStepTest extends GroovyTestCase {

    public void testEqual() {
        CustomBuildStep c1 = CustomBuildStep.testData
        CustomBuildStep c2 = CustomBuildStep.testData
        assert !c1.is(c2)
        assert c1 == c2
    }
}
