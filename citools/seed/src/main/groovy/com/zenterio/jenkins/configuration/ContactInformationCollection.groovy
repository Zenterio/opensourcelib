package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.models.job.JobEmailNotificationPolicy
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class ContactInformationCollection extends ArrayList<ContactInformation> {

    String[] getEmailList() {
        return this.collect{ ContactInformation w ->
            w.email
        }
    }

    public Object clone() {
        return this.collect{ ContactInformation w ->
            w.clone()
        } as ContactInformationCollection
    }

    public ContactInformationCollection filter(JobEmailNotificationPolicy jobPolicy) {
        return this.findAll { ContactInformation ci ->
                ci.emailPolicy.policies[jobPolicy.CORRESPONDING_EMAIL_POLICY_JOB_TYPE] != EmailPolicyWhen.NEVER
        }  as ContactInformationCollection
    }

    public ContactInformationCollection filter(EmailPolicyWhen policyWhen) {
        return this.findAll { ContactInformation ci ->
            EmailPolicyJobType.values().any { EmailPolicyJobType jobType ->
                ci.emailPolicy.policies[jobType] == policyWhen
            }
        } as ContactInformationCollection
    }

    public ContactInformationCollection filter(JobEmailNotificationPolicy jobPolicy, EmailPolicyWhen policyWhen) {
        return this.findAll { ContactInformation ci ->
            ci.emailPolicy.policies[jobPolicy.CORRESPONDING_EMAIL_POLICY_JOB_TYPE] == policyWhen
        } as ContactInformationCollection
    }

    public static ContactInformationCollection getTestData() {
        return [new Watcher("first watcher", "w1@example.com", EmailPolicy.testData),
                new Watcher("second watcher","second@example.com", EmailPolicy.testData)] as ContactInformationCollection
    }
}
