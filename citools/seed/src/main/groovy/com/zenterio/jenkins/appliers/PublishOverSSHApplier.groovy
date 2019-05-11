package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.configuration.ConfigAction
import com.zenterio.jenkins.configuration.TransferSet
import com.zenterio.jenkins.configuration.IPublisherOverSSH
import com.zenterio.jenkins.configuration.PublishBuildOverSSH
import com.zenterio.jenkins.configuration.PublishOverSSHList
import com.zenterio.jenkins.configuration.PublishOverSSH
import com.zenterio.jenkins.configuration.PublishTestReportOverSSH
import com.zenterio.jenkins.configuration.ProductVariant
import com.zenterio.jenkins.configuration.TestGroup
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobPublishOverSSHListModel
import com.zenterio.jenkins.postbuild.PublishBuildOverSSHScriptlet
import com.zenterio.jenkins.postbuild.PublishTestReportOverSSHScriptlet
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.jobtype.JobType

import groovy.util.logging.Log

@Log
class PublishOverSSHApplier {

    protected String scriptletsDirectory
    protected ProductVariant prodVariant
    protected BuildType buildType
    protected JobType jobType

    public PublishOverSSHApplier(String scriptletsDirectory,
            ProductVariant prodVariant,
            JobType jobType, BuildType buildType) {
        this.scriptletsDirectory = scriptletsDirectory
        this.prodVariant = prodVariant
        this.buildType = buildType
        this.jobType = jobType
    }

    /**
     * Default implementation
     * @param publish object with publishOverSSHList property
     * @param job Job model to apply the publishing to.
     */
    public void apply(IPublisherOverSSH publish, IModel job) {
        PublishOverSSHList lst = publish.publishOverSSHList.getEnabled()
        job << new JobPublishOverSSHListModel(lst.collect { this.convert(it) } as PublishOverSSHList)
    }


    /**
     * Specialization for prodVariants
     * @param job Job model to apply the publishing to.
     */
    public void applyProductVariant(IModel job) {
        assert this.prodVariant != null

        PublishOverSSHList lst = this.prodVariant.publishOverSSHList.getEnabled()
        job << new JobPublishOverSSHListModel(lst.collect { this.convert(it) } as PublishOverSSHList)
    }

    /**
     * Specialization for test context
     * @param context Test context holding publish over SSH information
     * @param job Job model to apply the publishing to.
     */
    public void applyTestContext(TestContext context, IModel job) {
        PublishOverSSHList lst = context.publishOverSSHList.getEnabled()
        job << new JobPublishOverSSHListModel(lst.collect { this.convert(it) } as PublishOverSSHList)
    }


    /**
     * Default covertion function, does nothing
     * @param standard
     */
    protected PublishOverSSH convert(PublishOverSSH standard) {
        return standard
    }

    /**
     * Converts a PublishBuildOverSSH to standard PublishOverSSH
     * @param build
     */
    protected PublishOverSSH convert(PublishBuildOverSSH build) {
        return new PublishOverSSH(build).with {
            String command = (new PublishBuildOverSSHScriptlet(
                new FileScriptlet(this.scriptletsDirectory, "publish-build-over-ssh.sh"),
                build, this.shouldPrepareTestReport(build), this.jobType, this.buildType)
            ).getContent()
            TransferSet tfs = new TransferSet(build.artifactPattern,
                'workspace/${JOB_BASE_NAME}_${BUILD_ID}',
                build.removePrefix,
                null, null, null,
                false, false, false,
                null, null,
                command)
            it.transferSets.add(tfs)
            it
        }
    }

    /**
     * Returns true if the build can be matched with a PublishTestReportOverSSH
     * in the prodVariants test context.
     * @param build
     */
    protected Boolean shouldPrepareTestReport(PublishBuildOverSSH build) {
        return this.prodVariant?.testGroups.any { TestGroup tg ->
            tg.enabled && tg.testContexts.any { TestContext tc ->
                tc.enabled && tc.publishOverSSHList.any { publish ->
                    publish.enabled && this.isPair(build, publish)
                }
            }
        }
    }

    /**
     * Returns true if the they are paired
     * @param build
     * @param testReport
     */
    protected Boolean isPair(PublishBuildOverSSH build, PublishTestReportOverSSH testReport) {
        return (build.name == testReport.name &&
            build.server == testReport.server)
    }

    /**
     * Default matcher, can never match
     * @param first
     * @param second
     */
    protected Boolean isPair(PublishOverSSH first, PublishOverSSH second) {
        return false
    }


    /**
     * Converts a PublishTestReportOverSSH to standard PublishOverSSH
     * @param testReport
     */
    protected PublishOverSSH convert(PublishTestReportOverSSH testReport) {

        assert this.prodVariant != null

        PublishBuildOverSSH build = this.prodVariant.publishOverSSHList.find { it ->
            it.class == PublishBuildOverSSH &&
            it.name == testReport.name &&
            it.server == testReport.server &&
            it.enabled
        }

        if (build == null) {
            String msg = "Could not find a matching 'publish-build-over-ssh' to " +
                "'publish-test-report-over-ssh' with name ${testReport.name} " +
                "and server ${testReport.server} that is enabled."
            throw new Exception(msg)
        }

        return new PublishOverSSH(testReport).with {

            TransferSet tfs_buildinfo = new TransferSet("source/build-info.txt",
                'workspace/${JOB_BASE_NAME}_${BUILD_ID}',
                '',
                null, null, null,
                false, false, false,
                null, null, null)
            it.transferSets.add(tfs_buildinfo)
            String command = (new PublishTestReportOverSSHScriptlet(
                new FileScriptlet(this.scriptletsDirectory, "publish-test-report-over-ssh.sh"),
                build, testReport, this.jobType, this.buildType)
            ).getContent()
            TransferSet tfs = new TransferSet(testReport.reportFilePattern,
                'workspace/${JOB_BASE_NAME}_${BUILD_ID}',
                testReport.removePrefix,
                null, null, null,
                false, false, false,
                null, null,
                command)
            it.transferSets.add(tfs)
            it
        }
    }
}
