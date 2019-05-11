package com.zenterio.jenkins.configuration

class JasmineTest extends GroovyTestCase {


    public void testDeepClone() {
        Jasmine jasmine = Jasmine.testData
        Jasmine clone = jasmine.clone()
        assert jasmine == clone
        assert !jasmine.is(clone)
    }

    public void testDefaultArguments() {
        Jasmine jasmine = new Jasmine('repo', 'conf.json')
        assert jasmine.repository == 'repo'
        assert jasmine.configFile == 'conf.json'
        assert jasmine.url == null
        assert jasmine.disableRCU
        assert jasmine.disableRCUCheck
    }

    public void testBadNullRepositoryArgument() {
        shouldFail(IllegalArgumentException, {
            new Jasmine(null, 'conf.json')
        })
    }

    public void testBadEmptyRepositoryArgument() {
        shouldFail(IllegalArgumentException, {
            new Jasmine('repo', null)
        })
    }

    public void testBadNullConfigFileArgument() {
        shouldFail(IllegalArgumentException, {
            new Jasmine('repo', null)
        })
    }

    public void testBadEmptyConfigFileArgument() {
        shouldFail(IllegalArgumentException, {
            new Jasmine('repo', '')
        })
    }

    public void testDisableRCUFalse() {
        Jasmine jasmine = new Jasmine('repo', 'conf.json', null, false)
        assert !jasmine.disableRCU
    }

    public void testDisableRCUCheckFalse() {
        Jasmine jasmine = new Jasmine('repo', 'conf.json', null, null, false)
        assert !jasmine.disableRCUCheck
    }

    public void testNullBooleanArgumentDefaultsToFalse() {
        Jasmine jasmine = new Jasmine('repo', 'conf.json', null, null, null)
        assert !jasmine.disableRCU
        assert !jasmine.disableRCUCheck
    }
}
