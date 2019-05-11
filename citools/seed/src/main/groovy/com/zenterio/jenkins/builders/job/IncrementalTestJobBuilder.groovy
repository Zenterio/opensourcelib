package com.zenterio.jenkins.builders.job

import com.zenterio.jenkins.DisplayName
import com.zenterio.jenkins.JenkinsUrl
import com.zenterio.jenkins.JobName
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.configuration.*
import com.zenterio.jenkins.jobtype.JobTypeIncrementalTestBuild
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobCopyArtifactsFromBuildNumberModel
import com.zenterio.jenkins.models.job.JobEmailNotificationModel
import com.zenterio.jenkins.models.job.JobEmailNotificationPolicy
import com.zenterio.jenkins.models.job.JobModel

class IncrementalTestJobBuilder extends TestJobBuilder{

    private static final String EMAIL_LIST_FILE = 'authors.txt'
    private static final String COPY_TO_DIRECTORY = 'source'

    IncrementalTestJobBuilder(ProductVariant product,
                              TestContext testContext,
                              String scriptletsDirectory,
                              JenkinsUrl url,
                              JobName jobName,
                              DisplayName displayName,
                              BuildTimeout buildTimeout,
                              JobTypeIncrementalTestBuild jobType,
                              JobModel parentJob) {
        super(product,
                testContext,
                scriptletsDirectory,
                url,
                jobName,
                displayName,
                buildTimeout,
                jobType,
                parentJob)
    }

    @Override
    IModel build() {
        IModel job = super.build()
        return job

    }

    @Override
    protected void addWatchers(IModel job, ContactInformationCollection watchers, ContactInformationCollection owners) {

        job << new JobCopyArtifactsFromBuildNumberModel(
                this.parentJob,
                "\${kfs_build_number}",
                "result/${EMAIL_LIST_FILE}",
                COPY_TO_DIRECTORY,
                true)

        ContactInformationCollection incrementalTestWatchers = watchers +
                new ContactFile('source/authors.txt', new EmailPolicy(EmailPolicyWhen.NEVER, EmailPolicyWhen.FAILURE, EmailPolicyWhen.FAILURE, EmailPolicyWhen.FAILURE))
        job << new JobEmailNotificationModel(JobEmailNotificationPolicy.TEST_ROOT_CAUSE,
                incrementalTestWatchers, this.product.pm, this.product.techLead, "", owners)
    }
}
