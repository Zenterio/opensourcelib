package com.zenterio.jenkins.configuration


class TestCommandArgsTest extends GroovyTestCase {

    public void testDeepClone() {
        TestCommandArgs tca = TestCommandArgs.testData
        TestCommandArgs clone = tca.clone()
        assert tca == clone
        assert !tca.is(clone)
    }

}
