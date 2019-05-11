package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.buildtype.BuildTypeDebug
import com.zenterio.jenkins.configuration.CsvDataPlot
import com.zenterio.jenkins.configuration.Epg
import com.zenterio.jenkins.configuration.IPublisherOverSSH
import com.zenterio.jenkins.configuration.PublishBuildOverSSH
import com.zenterio.jenkins.configuration.PublishOverSSHList
import com.zenterio.jenkins.configuration.PublishOverSSH
import com.zenterio.jenkins.configuration.PublishTestReportOverSSH
import com.zenterio.jenkins.configuration.ProductVariant
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.configuration.TestGroup
import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.configuration.TestGroupType
import com.zenterio.jenkins.configuration.TestJobInputParameter
import com.zenterio.jenkins.configuration.TestSuite
import com.zenterio.jenkins.configuration.TransferSet
import com.zenterio.jenkins.configuration.Upstream
import com.zenterio.jenkins.configuration.XmlToCsv
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.job.JobPublishOverSSHListModel
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.jobtype.JobTypeCompile

public class PublishOverSSHApplierTest extends GroovyTestCase {

    PublishOverSSHApplier applier

    final String NAME = "NAME"
    final String SERVER = "SERVER"

    @Override
    protected void setUp() {
        this.applier = new PublishOverSSHApplier("scriptlets",
            new ProductVariant(new BuildTypeDebug()),
            new JobTypeCompile(),
            new BuildTypeDebug())
    }

    /**
     * @param tgEnabled     test group enabled
     * @param tcEnabled     test context enabled
     * @param trEnabled     test report enabled
     */
    protected void setUpApplier(boolean tgEnabled=true, tcEnabled=true, trEnabled=true) {
        this.applier.prodVariant.testGroups = this.getTestGroup(tgEnabled, tcEnabled)
        this.applier.prodVariant.testGroups[0].testContexts[0].publishOverSSHList.add(
            this.getTestReport(trEnabled))
    }

    protected PublishBuildOverSSH getBuild() {
        return new PublishBuildOverSSH(
            true, NAME, SERVER, "prefix/artifacts", "prefix", "rootDir", 2, "product",
            null, null, null)
    }

    protected PublishTestReportOverSSH getTestReport(boolean enabled=true) {
        return new PublishTestReportOverSSH(
            enabled, NAME, SERVER, "prefix/report.xml", "prefix", "Test suite",
            null, null, null)
    }

    protected PublishOverSSH getPublish(boolean enabled=true) {
        return PublishOverSSH.testData.with {
            it.enabled = enabled
            it
        }
    }

    protected TestGroup getTestGroup(boolean tgEnabled=true, boolean tcEnabled=true) {
        TestContext tc = new TestContext("tc", [] as CsvDataPlot[],
            null, null, null, Upstream.TRUE, null, null,
            tcEnabled,
            null, null, null, null,
            [] as Repository[],
            null, null,
            null, [] as XmlToCsv[])
        return new TestGroup("tg", TestGroupType.KAZAM, null, "testroot", "stb",
            "box", "product", null,
            [tc] as TestContext[],
            null, null,
            tgEnabled,
            null, null, null)
    }

    void testConvertDefault() {
        PublishOverSSH publish = PublishOverSSH.testData
        assert this.applier.convert(publish) == publish
    }

    void testConvertPublishBuildWithoutMatchingTestReportGivesNoTestSummary() {
        PublishBuildOverSSH build = this.getBuild()
        PublishOverSSH converted = this.applier.convert(build)

        assert converted.server == SERVER
        assert converted.transferSets.size() == 1
        assert converted.transferSets[0].removePrefix == build.removePrefix
        assert converted.transferSets[0].command.contains("# PREPARE_FOR_TEST_REPORT=false")
    }

    void testConvertPublishBuildWithMatchingTestReportGivesTestSummary() {
        PublishBuildOverSSH build = this.getBuild()
        this.setUpApplier()
        PublishOverSSH converted = this.applier.convert(build)

        assert converted.transferSets.size() == 1
        assert converted.transferSets[0].removePrefix == build.removePrefix
        assert converted.transferSets[0].command.contains("# PREPARE_FOR_TEST_REPORT=true")
    }

    void testShouldPrepareTestReport() {
        PublishBuildOverSSH build = this.getBuild()
        this.setUpApplier()

        assert this.applier.shouldPrepareTestReport(build)
    }

    void testShouldNotPrepareTestReportIfBuildNameMissmatch() {
        PublishBuildOverSSH build = this.getBuild()
        this.setUpApplier()
        build.name = ""

        assert !this.applier.shouldPrepareTestReport(build)
    }

    void testShouldNotPrepareTestReportIfTestGroupDisabled() {
        PublishBuildOverSSH build = this.getBuild()
        this.setUpApplier(false)

        assert !this.applier.shouldPrepareTestReport(build)
    }

    void testShouldNotPrepareTestReportIfTestContextDisabled() {
        PublishBuildOverSSH build = this.getBuild()
        this.setUpApplier(true, false)

        assert !this.applier.shouldPrepareTestReport(build)
    }

    void testShouldNotPrepareTestReportIfTestPublishingDisabled() {
        PublishBuildOverSSH build = this.getBuild()
        this.setUpApplier(true, true, false)

        assert !this.applier.shouldPrepareTestReport(build)
    }

    void testShouldNotPrepareTestReportIfProductVariantIsNotSet() {
        PublishBuildOverSSH build = this.getBuild()
        this.applier.prodVariant = null

        assert !this.applier.shouldPrepareTestReport(build)
    }

    void testIsPair() {
        PublishBuildOverSSH build = this.getBuild()
        PublishTestReportOverSSH testReport = this.getTestReport()

        assert this.applier.isPair(build, testReport)

        build.name = ""
        assert !this.applier.isPair(build, testReport)
    }

    void testConvertPublishTestReport() {
        PublishTestReportOverSSH testReport = this.getTestReport()
        this.applier.prodVariant.publishOverSSHList.add(this.getPublish())
        this.applier.prodVariant.publishOverSSHList.add(this.getBuild())
        PublishOverSSH converted = this.applier.convert(testReport)

        assert converted.server == SERVER
        assert converted.transferSets.size() == 2
        converted.transferSets[1].removePrefix == testReport.removePrefix
    }

    void testConvertPublishTestReportThrowsExceptionOnNoMatchingBuild() {
        PublishTestReportOverSSH testReport = this.getTestReport()
        String msg = shouldFail {
            this.applier.convert(testReport)
        }
        assert msg.contains('name NAME and server SERVER')
    }

    void testConvertPublishTestReportThrowsExceptionOnDisabledMatchingBuild() {
        PublishTestReportOverSSH testReport = this.getTestReport()
        PublishBuildOverSSH build = this.getBuild()
        build.enabled = false
        this.applier.prodVariant.publishOverSSHList.add(build)
        String msg = shouldFail {
            this.applier.convert(testReport)
        }
        assert msg.contains('name NAME and server SERVER')
    }

}
