package com.zenterio.jenkins.configuration

class TestContextTest extends GroovyTestCase {

    public void testDeepClone() {
        TestContext testContext = TestContext.getTestData(true, Upstream.FALSE)
        TestContext clone = testContext.clone()

        assert testContext == clone
        assert testContext.csvDataPlots == clone.csvDataPlots
        assert testContext.description == clone.description
        assert testContext.duration == clone.duration
        assert testContext.testSuites == clone.testSuites
        assert testContext.upstream == clone.upstream
        assert testContext.polling == clone.polling
        assert testContext.epgs == clone.epgs
        assert testContext.repositories == clone.repositories
        assert testContext.inputParameters == clone.inputParameters
        assert testContext.xmlToCsvs == clone.xmlToCsvs
        assert testContext.testCommandArgs == clone.testCommandArgs
        assert testContext.jasmine == clone.jasmine
        assert testContext.name == clone.name
        assert testContext.stbLabel == clone.stbLabel
        assert clone.testGroup == null

        assert !testContext.is(clone)
        assert !testContext.csvDataPlots[0].is(clone.csvDataPlots[0])
        assert !testContext.duration.is(clone.duration)
        assert !testContext.epgs[0].is(clone.epgs[0])
        assert !testContext.logParsing.is(clone.logParsing)
        assert !testContext.repositories[0].is(clone.repositories[0])
        assert !testContext.testSuites[0].is(clone.testSuites[0])
        assert !testContext.pm.is(clone.pm)
        assert !testContext.techLead.is(clone.techLead)
        assert !testContext.xmlToCsvs[0].is(clone.xmlToCsvs[0])
    }

    public void testThrowsExceptionIfUpstreamAndRepositoriesAreBothSet() {
        String msg = shouldFail {
            TestContext.getTestData(true, Upstream.TRUE)
        }
        assert msg.contains('Upstream')
    }
}
