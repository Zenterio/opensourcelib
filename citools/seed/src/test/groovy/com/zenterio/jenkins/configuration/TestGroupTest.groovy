package com.zenterio.jenkins.configuration

class TestGroupTest extends GroovyTestCase {

    public void testDeepClone() {
        TestGroup group = TestGroup.testData
        TestGroup clone = group.clone()

        assert group == clone
        assert !group.epgs.is(clone.epgs)
        assert !group.epgs[0].is(clone.epgs[0])
        assert !group.image.is(clone.image)
        assert !group.logParsing.is(clone.logParsing)
        assert !group.repositories.is(clone.repositories)
        assert !group.repositories[0].is(clone.repositories[0])
        assert !group.testContexts.is(clone.testContexts)
        assert !group.testContexts[0].is(clone.testContexts[0])
        assert !group.watchers[0].is(clone.watchers[0])
        assert !group.pm.is(clone.pm)
        assert !group.techLead.is(clone.techLead)
    }
}
