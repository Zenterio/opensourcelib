package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.EmailPolicyJobType


/**
 * Email notification policy
 *
 * This class should not be instantiated outside itself,
 * instead there are three instances
 * made available using static class variables.
 *
 * Each instance corresponds to a class of jobs.
 *
 * The value of each instance is a mail policy that defines who should be emailed
 * depending on the result of the build.
 */
class JobEmailNotificationPolicy {

    /**
     * This class of jobs corresponds to an email policy used by ContactInformation derivatives.
     */
    final EmailPolicyJobType CORRESPONDING_EMAIL_POLICY_JOB_TYPE

    /**
     * The following policies correspond directly to Jenkins email triggers.
     */
    final JobEmailNotificationJenkinsReceivers failure
    final JobEmailNotificationJenkinsReceivers aborted
    final JobEmailNotificationJenkinsReceivers fixed
    final JobEmailNotificationJenkinsReceivers success
    final JobEmailNotificationJenkinsReceivers always
    final JobEmailNotificationJenkinsReceivers never

    /**
     * Private constructor to avoid creating new instances except those supplied by class variables below.
     */
    private JobEmailNotificationPolicy(EmailPolicyJobType CorrespondingEmailPolicyJobType,
                                       Boolean sendToDevelopers) {
        this.CORRESPONDING_EMAIL_POLICY_JOB_TYPE = CorrespondingEmailPolicyJobType
        this.failure = new JobEmailNotificationJenkinsReceivers(false, sendToDevelopers, false)
        this.aborted = new JobEmailNotificationJenkinsReceivers(false, sendToDevelopers, false)
        this.fixed = new JobEmailNotificationJenkinsReceivers(false, sendToDevelopers, sendToDevelopers)
        this.success = new JobEmailNotificationJenkinsReceivers(false, false, false)
        this.always = new JobEmailNotificationJenkinsReceivers(true, false, false)
        this.never = new JobEmailNotificationJenkinsReceivers(false, false, false)
    }
    /**
     * Utility jobs, e.g. sign.
     */
    static public final JobEmailNotificationPolicy UTILITY = new JobEmailNotificationPolicy(
            EmailPolicyJobType.UTILITY, false)

    /**
     * Incremental test jobs like kazam and jasmine tests.
     */
    static public final JobEmailNotificationPolicy TEST_ROOT_CAUSE = new JobEmailNotificationPolicy(
            EmailPolicyJobType.TEST, true)

    /**
     * Nightly test jobs
     */
    static public final JobEmailNotificationPolicy TEST_CONTROL = new JobEmailNotificationPolicy(
            EmailPolicyJobType.TEST, false)
    /**
     * The fast feedback loop is incremental builds and/or fast smoke tests.
     * This is for compilation and test jobs that can fail because of problems
     * with the product.
     */
    static public final JobEmailNotificationPolicy FAST_FEEDBACK_ROOT_CAUSE = new JobEmailNotificationPolicy(
            EmailPolicyJobType.FAST_FEEDBACK, true)

    /**
     * The fast feedback loop is incremental builds and/or fast smoke tests.
     * These are for control jobs, they aggregate failures from several other jobs.
     */
    static public final JobEmailNotificationPolicy FAST_FEEDBACK_CONTROL = new JobEmailNotificationPolicy(
            EmailPolicyJobType.FAST_FEEDBACK, false)

    /**
     * The slow feedback loop is a clean build with longer running automatic tests.
     */
    static public final JobEmailNotificationPolicy SLOW_FEEDBACK = new JobEmailNotificationPolicy(
            EmailPolicyJobType.SLOW_FEEDBACK, false)

}
