package com.zenterio.jenkins.models.job

/**
 * This tests a basic @TupleConstructor element.
 */
class JobEmailNotificationJenkinsReceiversTest extends GroovyTestCase {
    JobEmailNotificationJenkinsReceivers receivers

    @Override
    void setUp() throws Exception {
        this.receivers = new JobEmailNotificationJenkinsReceivers(true, false, null)
    }

    public void testConstructorOrder() {
        assert this.receivers.requester == true
        assert this.receivers.developers == false
        assert this.receivers.culprits == null
    }

    public void testValuesAreImmutable() {
        ["requester", "developers", "culprits"].each { String field ->
            this.shouldFail(ReadOnlyPropertyException) {
                this.receivers."${field}" = false
            }
        }
    }
}