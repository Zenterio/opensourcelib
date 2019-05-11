package com.zenterio.jenkins.configuration

class BuildTimeoutTest extends GroovyTestCase {

    void testDefaultArguments() {
        BuildTimeout buildTimeout = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 10)
        assert buildTimeout.policy == BuildTimeoutPolicy.ABSOLUTE
        assert buildTimeout.minutes == 10
        assert !buildTimeout.failBuild
        assert !buildTimeout.configurable
        assert buildTimeout.enabled
    }

    void testCreateDisabledBuildTimeout() {
        BuildTimeout buildTimeout = new BuildTimeout(null, null, null, null, false)
        assert !buildTimeout.enabled
    }

    void testTooLowMinutesArgument() {
        shouldFail(IllegalArgumentException, {
            new BuildTimeout(BuildTimeoutPolicy.ELASTIC, 0)
        })
    }

    void testTooLowMinutesArgumentEnabledFalse() {
        BuildTimeout buildTimeout = new BuildTimeout(BuildTimeoutPolicy.ELASTIC, 0, false, false, false)
        assert !buildTimeout.enabled
    }

    void testTooLowMinutesArgumentForAbsolutePolicyThrowsExceptionWhenEnabledTrue() {
        shouldFail(IllegalArgumentException, {
            new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 2)
        })
    }

    void testTooLowMinutesArgumentForAbsolutePolicyDoesNotThrowsExceptionWhenEnabledFalse() {
        BuildTimeout buildTimeout = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 2, false, false, false)
        assert !buildTimeout.enabled
    }

    void testLessThanThreeMinutesForElasticPolicy() {
        BuildTimeout buildTimeout = new BuildTimeout(BuildTimeoutPolicy.ELASTIC, 2)
        assert buildTimeout.policy == BuildTimeoutPolicy.ELASTIC
        assert buildTimeout.minutes == 2
    }

    void testThatNullMinutesArgThrowsExceptionWhenEnabledIsTrue() {
        shouldFail(IllegalArgumentException, {
            new BuildTimeout(BuildTimeoutPolicy.ELASTIC, null, false, false, true)
        })
    }

    void testThatNullMinutesArgDoesNotThrowsExceptionWhenEnabledIsFalse() {
        BuildTimeout buildTimeout = new BuildTimeout(BuildTimeoutPolicy.ELASTIC, null, false, false, false)
        assert !buildTimeout.enabled
    }

    void testThatNullPolicyThrowsExceptionWhenEnabledIsTrue() {
        shouldFail(IllegalArgumentException, {
            new BuildTimeout(null, 10, false, false, true)
        })
    }

    void testThatNullPolicyDoesNotThrowsExceptionWhenEnabledIsFalse() {
        BuildTimeout buildTimeout = new BuildTimeout(null, 10, false, false, false)
        assert !buildTimeout.enabled
    }
}
