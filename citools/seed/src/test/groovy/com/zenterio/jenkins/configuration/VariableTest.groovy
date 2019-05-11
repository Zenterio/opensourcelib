package com.zenterio.jenkins.configuration

class VariableTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        Variable variable = Variable.testData
        Variable clone = variable.clone()

        assert variable == clone
        assert !variable.is(clone)
    }
    
}
