package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class EmailPolicy extends BaseConfig {

    def policies

    public EmailPolicy(EmailPolicyWhen slowFeedback, EmailPolicyWhen fastFeedback, EmailPolicyWhen utility, EmailPolicyWhen test) {
        this.policies = [(EmailPolicyJobType.SLOW_FEEDBACK):slowFeedback,
                         (EmailPolicyJobType.FAST_FEEDBACK):fastFeedback,
                         (EmailPolicyJobType.UTILITY):utility,
                         (EmailPolicyJobType.TEST):test]
    }

    public EmailPolicy inherit() {
        return new EmailPolicy(EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER, this.policies[EmailPolicyJobType.UTILITY], EmailPolicyWhen.NEVER)
    }

    public static EmailPolicy getTestData() {
        return new EmailPolicy(EmailPolicyWhen.FAILURE, EmailPolicyWhen.ALWAYS, EmailPolicyWhen.SUCCESS, EmailPolicyWhen.FAILURE)
    }
}
