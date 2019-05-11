package com.zenterio.jenkins.configuration


class WatcherTest extends GroovyTestCase {

    public void testDeepClone() {
        Watcher parent = Watcher.testData
        Watcher child = parent.clone()
        assert parent == child
        assert !parent.is(child)
        assert !parent.emailPolicy.is(child.emailPolicy)
    }

    public void testInherit() {
        Watcher parent = Watcher.testData
        Watcher child = parent.inherit()
        assert parent.name == child.name
        assert parent.email == child.email
        assert parent.emailPolicy.policies[EmailPolicyJobType.UTILITY] == EmailPolicyWhen.SUCCESS
        assert parent.emailPolicy.policies[EmailPolicyJobType.SLOW_FEEDBACK] != EmailPolicyWhen.NEVER
        assert parent.emailPolicy.policies[EmailPolicyJobType.FAST_FEEDBACK] != EmailPolicyWhen.NEVER
        assert child.emailPolicy.policies[EmailPolicyJobType.UTILITY] == EmailPolicyWhen.SUCCESS
        assert child.emailPolicy.policies[EmailPolicyJobType.SLOW_FEEDBACK] == EmailPolicyWhen.NEVER
        assert child.emailPolicy.policies[EmailPolicyJobType.FAST_FEEDBACK] == EmailPolicyWhen.NEVER
    }
}
