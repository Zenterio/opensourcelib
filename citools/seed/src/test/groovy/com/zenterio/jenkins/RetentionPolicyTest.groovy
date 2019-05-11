package com.zenterio.jenkins


class RetentionPolicyTest extends GroovyTestCase {
    @Override
    protected void setUp() throws Exception {
        super.setUp()

    }

    void testDeepCopy() {
        RetentionPolicy policy = RetentionPolicy.testData
        RetentionPolicy clone = policy.clone()
        assert policy == clone
        assert !policy.is(clone)
    }

    void testNumToKeepGetterReturnsSavedValue() {
        RetentionPolicy policy = new RetentionPolicy(RetentionPolicyType.MEDIUM, true)
        assert policy.numToKeep == RetentionPolicyType.MEDIUM.value
    }

    void testDaysToKeepGetterReturnsMinusOne() {
        RetentionPolicy policy = new RetentionPolicy(RetentionPolicyType.MEDIUM, true)
        assert policy.daysToKeep == -1
    }

    void testArtifactDaysGetterReturnsMinusOne() {
        RetentionPolicy policy = new RetentionPolicy(RetentionPolicyType.MEDIUM, true)
        assert policy.artifactDaysToKeep == -1
    }

    void testArtifactNumToKeepGetterReturnsSavedValueIfSaveArtifactsIsTrue() {
        RetentionPolicy policy = new RetentionPolicy(RetentionPolicyType.MEDIUM, true)
        assert policy.artifactNumToKeep == RetentionPolicyType.MEDIUM.value
    }

    void testArtifactNumToKeepGetterReturns1IfSaveArtifactsIsFalse() {
        RetentionPolicy policy = new RetentionPolicy(RetentionPolicyType.MEDIUM, false)
        assert policy.artifactNumToKeep == 1
    }
}
