package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.models.job.JobEmailNotificationPolicy

class ContactInformationCollectionTest extends GroovyTestCase {

    ContactInformationCollection collection
    ContactInformationCollection sparseWatcherList
    ContactInformationCollection denseWatcherList

    @Override
    protected void setUp() {
        this.collection = ContactInformationCollection.testData
        this.sparseWatcherList = [
                new ContactInformation("A sparse name","A sparse email", new EmailPolicy(EmailPolicyWhen.FAILURE, EmailPolicyWhen.NEVER, EmailPolicyWhen.NEVER, EmailPolicyWhen.FAILURE)),
                new ContactInformation("B sparse name","B sparse email", new EmailPolicy(EmailPolicyWhen.SUCCESS, EmailPolicyWhen.ALWAYS, EmailPolicyWhen.NEVER, EmailPolicyWhen.FAILURE))
        ] as ContactInformationCollection
        this.denseWatcherList = [
                new ContactInformation("A dense name","A dense email", new EmailPolicy(EmailPolicyWhen.FAILURE, EmailPolicyWhen.FAILURE, EmailPolicyWhen.NEVER, EmailPolicyWhen.FAILURE)),
                new ContactInformation("B dense name","B dense email", new EmailPolicy(EmailPolicyWhen.SUCCESS, EmailPolicyWhen.ALWAYS, EmailPolicyWhen.NEVER, EmailPolicyWhen.FAILURE)),
                new ContactInformation("C dense name","C dense email", new EmailPolicy(EmailPolicyWhen.ALWAYS, EmailPolicyWhen.NEVER, EmailPolicyWhen.SUCCESS, EmailPolicyWhen.FAILURE))
        ] as ContactInformationCollection
    }

    public void testGetEmailList() {
        assert this.collection.getEmailList().size() == 2
        assert this.collection.getEmailList().join(' ') == 'w1@example.com second@example.com'
    }

    public void testDeepClone() {
        ContactInformationCollection clone = this.collection.clone()

        assert this.collection == clone
        this.collection.eachWithIndex { ContactInformation original, int i ->
            assert !original.is(clone[i])
        }
    }

    public void testFilterOnJobType() {
        ContactInformationCollection sparseSlow = sparseWatcherList.filter(JobEmailNotificationPolicy.SLOW_FEEDBACK)
        ContactInformationCollection sparseFast = sparseWatcherList.filter(JobEmailNotificationPolicy.FAST_FEEDBACK_CONTROL)
        ContactInformationCollection sparseUtility = sparseWatcherList.filter(JobEmailNotificationPolicy.UTILITY)
        ContactInformationCollection sparseTest = sparseWatcherList.filter(JobEmailNotificationPolicy.TEST_CONTROL)
        ContactInformationCollection denseSlow = denseWatcherList.filter(JobEmailNotificationPolicy.SLOW_FEEDBACK)
        ContactInformationCollection denseFast = denseWatcherList.filter(JobEmailNotificationPolicy.FAST_FEEDBACK_ROOT_CAUSE)
        ContactInformationCollection denseUtility = denseWatcherList.filter(JobEmailNotificationPolicy.UTILITY)
        ContactInformationCollection denseTest = denseWatcherList.filter(JobEmailNotificationPolicy.TEST_ROOT_CAUSE)

        assert sparseSlow.getEmailList().size() == 2
        assert sparseFast.getEmailList().size() == 1
        assert sparseUtility.getEmailList().size() == 0
        assert sparseTest.getEmailList().size() == 2
        assert denseSlow.getEmailList().size() == 3
        assert denseFast.getEmailList().size() == 2
        assert denseUtility.getEmailList().size() == 1
        assert denseTest.getEmailList().size() == 3
    }

    public void testFilterOnEmailPolicyWhen() {
        ContactInformationCollection sparseNever = sparseWatcherList.filter(EmailPolicyWhen.NEVER)
        ContactInformationCollection sparseSuccess = sparseWatcherList.filter(EmailPolicyWhen.SUCCESS)
        ContactInformationCollection sparseFailure = sparseWatcherList.filter(EmailPolicyWhen.FAILURE)
        ContactInformationCollection sparseAlways = sparseWatcherList.filter(EmailPolicyWhen.ALWAYS)
        ContactInformationCollection denseNever = denseWatcherList.filter(EmailPolicyWhen.NEVER)
        ContactInformationCollection denseSuccess = denseWatcherList.filter(EmailPolicyWhen.SUCCESS)
        ContactInformationCollection denseFailure = denseWatcherList.filter(EmailPolicyWhen.FAILURE)
        ContactInformationCollection denseAlways = denseWatcherList.filter(EmailPolicyWhen.ALWAYS)

        assert sparseNever.getEmailList().size() == 2
        assert sparseSuccess.getEmailList().size() == 1
        assert sparseFailure.getEmailList().size() == 2
        assert sparseAlways.getEmailList().size() == 1
        assert denseNever.getEmailList().size() == 3
        assert denseSuccess.getEmailList().size() == 2
        assert denseFailure.getEmailList().size() == 3
        assert denseAlways.getEmailList().size() == 2
    }
    public void testFilterOnBoth() {
        ContactInformationCollection sparseSlowFail = sparseWatcherList.filter(JobEmailNotificationPolicy.SLOW_FEEDBACK,
                EmailPolicyWhen.FAILURE)
        ContactInformationCollection sparseSlowAlways =sparseWatcherList.filter(JobEmailNotificationPolicy.SLOW_FEEDBACK,
                EmailPolicyWhen.ALWAYS)
        ContactInformationCollection denseFastAlways = denseWatcherList.filter(JobEmailNotificationPolicy.FAST_FEEDBACK_CONTROL,
                EmailPolicyWhen.ALWAYS)
        ContactInformationCollection denseUtilityNever = denseWatcherList.filter(JobEmailNotificationPolicy.UTILITY,
                EmailPolicyWhen.NEVER)

        assert sparseSlowFail.getEmailList().size() == 1
        assert sparseSlowAlways.getEmailList().size() == 0
        assert denseFastAlways.getEmailList().size() == 1
        assert denseUtilityNever.getEmailList().size() == 2
    }
}
