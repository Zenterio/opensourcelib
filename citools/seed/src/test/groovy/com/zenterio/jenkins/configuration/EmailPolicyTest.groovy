package com.zenterio.jenkins.configuration


class EmailPolicyTest extends GroovyTestCase {

    public void testDeepClone() {
        EmailPolicy parent = EmailPolicy.testData
        EmailPolicy child = parent.clone()
        assert parent == child
        assert !parent.is(child)
    }

    public void testInherit() {
        EmailPolicy parent = new EmailPolicy(EmailPolicyWhen.FAILURE, EmailPolicyWhen.ALWAYS, EmailPolicyWhen.SUCCESS, EmailPolicyWhen.FAILURE)
        EmailPolicy child = parent.inherit()
        assert child.policies[EmailPolicyJobType.SLOW_FEEDBACK] == EmailPolicyWhen.NEVER
        assert child.policies[EmailPolicyJobType.FAST_FEEDBACK] == EmailPolicyWhen.NEVER
        assert child.policies[EmailPolicyJobType.UTILITY] == EmailPolicyWhen.SUCCESS
        assert child.policies[EmailPolicyJobType.TEST] == EmailPolicyWhen.NEVER
    }
}
